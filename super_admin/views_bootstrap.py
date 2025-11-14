import logging
import time
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import (
    University, SessionNames, BankNames, FeeReceiptOptions, PaymentModes, Countries,
    default_permissions, super_admin_permissions
)
from .api_serializers import (
    UniversitySerializer, SessionNamesSerializer, BankNamesSerializer,
    FeeReceiptOptionsSerializer, PaymentModesSerializer, CountrySerializer
)

logger = logging.getLogger(__name__)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_register_bootstrap(request):
    """
    ONE CALL: returns all dropdown data needed by Student Registration + permissions.

    Response:
    {
      "data": {
        "universities": [...],
        "sessions": [...],
        "banks": [...],
        "fee_receipt_options": [...],
        "payment_modes": [...],
        "countries": [...]
      },
      "permissions": {...}
    }
    """
    user = request.user
    t0 = time.monotonic()
    email = getattr(user, "email", str(user))

    logger.info("[bootstrap] START user=%s", email)

    try:
        payload = {"data": {}}

        with transaction.atomic():  # neat grouping; not strictly required for reads
            # Universities
            universities = University.objects.all()
            payload["data"]["universities"] = UniversitySerializer(universities, many=True).data

            # Sessions
            sessions = SessionNames.objects.all()
            payload["data"]["sessions"] = SessionNamesSerializer(sessions, many=True).data

            # Banks
            banks = BankNames.objects.all()
            payload["data"]["banks"] = BankNamesSerializer(banks, many=True).data

            # Fee receipt options
            fee_opts = FeeReceiptOptions.objects.all()
            payload["data"]["fee_receipt_options"] = FeeReceiptOptionsSerializer(fee_opts, many=True).data

            # Payment modes
            modes = PaymentModes.objects.all()
            payload["data"]["payment_modes"] = PaymentModesSerializer(modes, many=True).data

            # Countries
            countries = Countries.objects.all()
            payload["data"]["countries"] = CountrySerializer(countries, many=True).data

        # payload["permissions"] = _effective_permissions(user)

        dt = (time.monotonic() - t0) * 1000.0
        logger.info(
            "[bootstrap] OK user=%s ms=%.1f counts={universities:%d,sessions:%d,banks:%d,fee_receipt_options:%d,payment_modes:%d,countries:%d}",
            email, dt,
            len(payload["data"]["universities"]),
            len(payload["data"]["sessions"]),
            len(payload["data"]["banks"]),
            len(payload["data"]["fee_receipt_options"]),
            len(payload["data"]["payment_modes"]),
            len(payload["data"]["countries"]),
        )
        return Response(payload, status=status.HTTP_200_OK)

    except Exception as e:
        dt = (time.monotonic() - t0) * 1000.0
        # exception() logs stacktrace with ERROR level
        logger.exception("[bootstrap] FAIL user=%s ms=%.1f error=%s", email, dt, str(e))
        return Response(
            {"error": "Internal server error while building bootstrap payload."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# for leads module page 



import logging, time
from django.db import transaction
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import (
    User, Source, Common_Lead_Label_Tags, Categories, Color, RoleStatus,
    Countries, States, University,
    default_permissions, super_admin_permissions
)
from .api_serializers import *
from .role_serializers import *
from .jobportal_serializers import *

logger = logging.getLogger(__name__)


def _effective_permissions(user):
    """Return the effective permissions dict for the current user."""
    if getattr(user, "is_superuser", False):
        return super_admin_permissions
    role = getattr(user, "role", None)
    if role and role.permissions:
        return role.permissions
    return default_permissions


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lead_bootstrap(request):
    """
    ONE CALL for New Lead page dropdowns + permissions.
    Response schema:
    {
      "data": {
        "users": [...],
        "sources": [...],
        "lead_label_tags": [...],
        "categories": [...],
        "colors": [...],
        "statuses": [...],
        "countries": [...],
        "states": [...],          # full list (frontend filters by country)
        "universities": [...]
      },
      "permissions": { ... }      # effective permissions for current user
    }
    """
    t0 = time.monotonic()
    user = request.user
    email = getattr(user, "email", str(user))

    logger.info("[lead_bootstrap] START user=%s", email)

    try:
        payload = {"data": {}}

        # ----- users (same logic as get_lead_user) -----
        is_superuser = user.is_superuser
        if is_superuser:
            users_qs = User.objects.filter(
                is_student=False, role__isnull=False,
                role__permissions__contains={"leads_menu": "yes"}
            )
        else:
            users_qs = User.objects.filter(
                is_student=False, role__isnull=False,
                role__permissions__contains={"leads_menu": "yes"}
            ).filter(
                Q(assigned_by=user) |
                Q(assigned_by__assigned_by=user) |
                Q(id=user.id)
            )

        with transaction.atomic():
            # Users
            payload["data"]["users"] = UserSerializer(users_qs, many=True).data

            # Sources
            sources = Source.objects.all()
            payload["data"]["sources"] = SourceSerializer(sources, many=True).data

            # Tags
            tags = Common_Lead_Label_Tags.objects.all()
            payload["data"]["lead_label_tags"] = CommonLeadLabelTagsSerializer(tags, many=True).data

            # Categories
            categories = Categories.objects.all()
            payload["data"]["categories"] = CategoriesSerializer(categories, many=True).data

            # Colors
            colors = Color.objects.all()
            payload["data"]["colors"] = ColorSerializer(colors, many=True).data

            # Statuses
            statuses = RoleStatus.objects.all()
            payload["data"]["statuses"] = RoleStatusSerializer(statuses, many=True).data

            # Countries & States (full lists; client filters by country)
            countries = Countries.objects.all()
            states = States.objects.all()
            payload["data"]["countries"] = CountrySerializer(countries, many=True).data
            payload["data"]["states"] = StatesSerializer(states, many=True).data

            # Universities
            universities = University.objects.all()
            payload["data"]["universities"] = UniversitySerializer(universities, many=True).data

        # Effective permissions for the logged-in user
        payload["permissions"] = _effective_permissions(user)

        dt = (time.monotonic() - t0) * 1000.0
        logger.info(
            "[lead_bootstrap] OK user=%s ms=%.1f", email, dt
        )
        return Response(payload, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("[lead_bootstrap] FAIL user=%s error=%s", email, str(e))
        return Response(
            {"error": "Internal server error while building lead bootstrap payload."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
