# signals.py
import json
import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from .models import Leads, Common_Lead_Label_Tags
from .middleware import get_current_user

logger = logging.getLogger("django")  # This logs to ankit.log

# Fields to audit
TRACKED_FIELDS = [
    "first_name", "last_name", "landline", "mobile",
    "mobile_one", "mobile_two", "mobile_three",
    "email", "email_one", "email_two", "email_three",
    "followup_date", "mobile_numbers", "email_addresses",
    "owner", "co_owner", "lead_status", "lead_source",
    "lead_categories", "lead_color", "university",
    "common_lead_label_tags",
]

# Fields to exclude from snapshots/compare
EXCLUDE_FIELDS = {
    "id", "created_at", "updated_at", "lead_comments", "activity_log"
}

# Human display for FKs
RELATED_DISPLAY = {
    "owner":           lambda o: (getattr(o, "get_full_name", lambda: "")() or getattr(o, "email", None) or f"User ID: {o.id}"),
    "co_owner":        lambda o: (getattr(o, "get_full_name", lambda: "")() or getattr(o, "email", None) or f"User ID: {o.id}"),
    "lead_status":     lambda o: getattr(o, "name", None) or f"Status ID: {o.id}",
    "lead_source":     lambda o: getattr(o, "name", None) or f"Source ID: {o.id}",
    "lead_categories": lambda o: getattr(o, "name", None) or f"Category ID: {o.id}",
    "lead_color":      lambda o: getattr(o, "name", None) or f"Color ID: {o.id}",
    "university":      lambda o: getattr(o, "university_name", None) or f"University ID: {o.id}",
}

# Pretty labels
FIELD_LABEL = {
    "first_name": "First Name",
    "last_name": "Last Name",
    "landline": "Landline",
    "mobile": "Mobile",
    "mobile_one": "Mobile One",
    "mobile_two": "Mobile Two",
    "mobile_three": "Mobile Three",
    "email": "Email",
    "email_one": "Email One",
    "email_two": "Email Two",
    "email_three": "Email Three",
    "followup_date": "Follow-up Date",
    "mobile_numbers": "Mobile Numbers",
    "email_addresses": "Email Addresses",
    "owner": "Owner",
    "co_owner": "Co-owner",
    "lead_status": "Lead Status",
    "lead_source": "Source",
    "lead_categories": "Category",
    "lead_color": "Color",
    "university": "University",
    "common_lead_label_tags": "Tags",
}

def _user_display(user):
    """Return a friendly display string for a user."""
    if not user or not getattr(user, "is_authenticated", False):
        return "System"

    # Prefer full name, then email, then username, then ID
    try:
        full = getattr(user, "get_full_name", lambda: "")()
        if full:
            return full
    except Exception:
        pass

    email = getattr(user, "email", None)
    if email:
        return email

    username = getattr(user, "username", None)
    if username:
        return username

    return f"User ID: {getattr(user, 'id', 'unknown')}"

def _fk_display(instance, field_name, value_id):
    """Return human display for a FK value by ID."""
    if value_id in (None, "", 0):
        return "None"

    model = instance._meta.get_field(field_name).related_model
    try:
        obj = model.objects.get(pk=value_id)
        return RELATED_DISPLAY.get(field_name, str)(obj)
    except ObjectDoesNotExist:
        return f"Deleted {FIELD_LABEL.get(field_name, field_name)} (ID: {value_id})"

def _tags_display(value):
    """
    Convert the JSON/list of tag IDs into a readable list of tag names.
    Example output: "[Important, Follow-up]"
    """
    if value in (None, [], "", "null"):
        return "[]"

    # If stored as a JSON string, try to decode
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            # Not JSON—just show as-is
            return str(value)

    if not isinstance(value, list):
        return str(value)

    names = list(
        Common_Lead_Label_Tags.objects
        .filter(id__in=value)
        .values_list("name", flat=True)
    )
    # Optional deterministic ordering:
    # names.sort(key=lambda s: s.lower())
    return "[" + ", ".join(names) + "]"

def _display(instance, field_name, value):
    """Convert any field's value into a readable string for logs."""
    # FKs
    if field_name in RELATED_DISPLAY:
        if hasattr(value, "pk"):  # already fetched object
            return RELATED_DISPLAY[field_name](value)
        return _fk_display(instance, field_name, value)

    # Special-case tags: show names, not IDs
    if field_name == "common_lead_label_tags":
        return _tags_display(value)

    if value is None:
        return "None"

    # Dates
    if hasattr(value, "strftime"):
        return value.strftime("%d-%m-%Y")

    # Other JSON-ish fields
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)

    return str(value)

def _format_change_message(field_name, old_value, new_value):
    """Return a human sentence for a single change."""
    label = FIELD_LABEL.get(field_name, field_name.replace("_", " ").title())

    if old_value == "None" and new_value != "None":
        return f"{label} was set to {new_value}"
    elif old_value != "None" and new_value == "None":
        return f"{label} was removed (was {old_value})"
    else:
        return f"{label} was changed from {old_value} to {new_value}"

@receiver(pre_save, sender=Leads)
def leads_pre_save_snapshot(sender, instance: Leads, **kwargs):
    """Take a snapshot of old values before saving."""
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance.__old_state__ = {
                f.name: getattr(old, f.name)
                for f in sender._meta.fields
                if f.name not in EXCLUDE_FIELDS
            }
        except sender.DoesNotExist:
            instance.__old_state__ = None
    else:
        instance.__old_state__ = None

@receiver(post_save, sender=Leads)
def leads_post_save_audit(sender, instance: Leads, created, **kwargs):
    """Append human-readable audit entries after saving."""
    if getattr(instance, "__audit_done__", False):
        return

    # Who did it?
    try:
        actor = get_current_user()
        actor_name = _user_display(actor)
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        actor_name = "System"

    timestamp = timezone.localtime().strftime("%d-%m-%Y %H:%M:%S")
    msgs = []

    if created:
        msgs.append(f"{timestamp} — New lead was created by {actor_name}")
    else:
        old = getattr(instance, "__old_state__", None) or {}
        changes = []

        for field in TRACKED_FIELDS:
            # Skip non-existent/excluded fields
            try:
                instance._meta.get_field(field)
                if field in EXCLUDE_FIELDS:
                    continue
            except Exception:
                continue

            old_val = old.get(field, None)
            new_val = getattr(instance, field)

            # Skip identical values
            if old_val == new_val:
                continue

            # Avoid false positives for followup_date (date-only compare)
            if field == "followup_date":
                if old_val and new_val:
                    try:
                        if old_val.date() == new_val.date():
                            continue
                    except Exception:
                        # if any isn't date/datetime, fall through
                        pass
                elif old_val is None and new_val is None:
                    continue

            # Humanize values
            old_disp = _display(instance, field, old_val)
            new_disp = _display(instance, field, new_val)

            # Build this field's change sentence
            changes.append(_format_change_message(field, old_disp, new_disp))

        # Final message(s)
        if changes:
            if len(changes) == 1:
                msgs.append(f"{timestamp} — {changes[0]} by {actor_name}")
            else:
                changes_list = "\n  • " + "\n  • ".join(changes)
                msgs.append(f"{timestamp} — Multiple changes made by {actor_name}:{changes_list}")

    # Persist audit
    if msgs:
        new_log = (instance.activity_log or []) + msgs
        instance.__audit_done__ = True
        # Update to avoid recursion
        sender.objects.filter(pk=instance.pk).update(activity_log=new_log)
