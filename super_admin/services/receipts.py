# reciept.py
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from super_admin.utils import render_pdf_from_template
from super_admin.models import Enrolled
from datetime import datetime


def _format_receipt_date(receipt) -> str:
    """
    Returns dd/mm/YYYY string.
    - Prefer receipt.transaction_date (string) if present (tries common formats).
    - Fallback to receipt.transactiontime (DateTimeField).
    """
    s = getattr(receipt, "transaction_date", "") or ""
    s = s.strip()
    if s:
        # try a few common input formats your UI might send
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime("%d/%m/%Y")
            except ValueError:
                continue
        # if parsing fails, return raw string
        return s

    # fallback: DB timestamp
    ts = getattr(receipt, "transactiontime", None)
    if ts:
        try:
            return timezone.localtime(ts).strftime("%d/%m/%Y")
        except Exception:
            return ts.strftime("%d/%m/%Y")
    return "-"


def _inr_words(amount) -> str:
    """Return simple INR wording; keep lightweight and robust."""
    try:
        n = float(amount or 0)
    except Exception:
        n = 0
    return f"Rupees {n:,.2f} only"

def _program_name_from_student(student):
    """Fetch latest enrolled course name for a student; fallback '-'."""
    enr = (
        Enrolled.objects
        .filter(student=student)
        .select_related("course")
        .order_by("-id")
        .first()
    )
    return enr.course.name if enr and enr.course else "-"

def _build_receipt_context(student, receipt, *, title: str):
    """Common context for both Course and Additional receipts."""
    return {
        "student": student,
        "receipt": receipt,
        "now": timezone.now(),
        "amount_in_words": _inr_words(getattr(receipt, "paidamount", 0)),
        "program_name": _program_name_from_student(student),
        "title": title,  # used when template shows a dynamic heading
    }

def generate_receipt_pdf(student, receipt) -> bytes:
    """
    Render the Course Fee Payment Receipt PDF.
    Uses your existing template: emails/payment_receipt.html
    """
    ctx = _build_receipt_context(student, receipt, title="Course Fee Payment Receipt")
    # If your template already looks exactly as you want, keep it:
    return render_pdf_from_template("emails/payment_receipt.html", ctx)

def email_payment_receipt(student, receipt, pdf_bytes: bytes, cc=None):
    """
    Email Course Fee Payment Receipt PDF.
    Keeps original signature so existing code continues to work.
    """
    subject = f"Payment Receipt – {receipt.transactionID}"
    body = (
        f"Dear {student.name or 'Student'},\n\n"
        "Thank you for your payment. Please find your receipt attached.\n\n"
        "Regards,\nCIIS Accounts Team"
    )
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", getattr(settings, "EMAIL_HOST_USER", None)),
        to=[student.email],
        cc=cc or [],
    )
    msg.attach(f"Receipt_{receipt.transactionID}.pdf", pdf_bytes, "application/pdf")
    msg.send(fail_silently=False)

def generate_additional_receipt_pdf(student, receipt) -> bytes:
    """
    Render the Additional Fee Payment Receipt PDF.

    OPTION A (recommended): Use a separate template so you can tweak the title/wording:
        return render_pdf_from_template("emails/additional_payment_receipt.html", ctx)

    OPTION B: Reuse the same template as course receipt and only change the title:
        return render_pdf_from_template("emails/payment_receipt.html", ctx)
    """
    ctx = _build_receipt_context(student, receipt, title="Additional Fee Payment Receipt")
    # Choose A or B. Defaulting to a separate template:
    return render_pdf_from_template("emails/additional_payment_receipt.html", ctx)

def email_additional_payment_receipt(student, receipt, pdf_bytes: bytes, cc=None):
    """
    Email Additional Fee Payment Receipt PDF.
    """
    subject = f"Additional Payment Receipt – {receipt.transactionID}"
    body = (
        f"Dear {student.name or 'Student'},\n\n"
        "Please find your additional fee receipt attached.\n\n"
        "Regards,\nCIIS Accounts Team"
    )
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", getattr(settings, "EMAIL_HOST_USER", None)),
        to=[student.email],
        cc=cc or [],
    )
    msg.attach(f"Additional_Receipt_{receipt.transactionID}.pdf", pdf_bytes, "application/pdf")
    msg.send(fail_silently=False)

def generate_receipt_pdf_generic(student, receipt, *, title: str, template_name: str) -> bytes:
    """
    Generic renderer if you ever want to consolidate calls.
    """
    ctx = _build_receipt_context(student, receipt, title=title)
    return render_pdf_from_template(template_name, ctx)

def email_receipt_generic(student, receipt, pdf_bytes: bytes, *, subject_prefix: str, filename_prefix: str, cc=None):
    """
    Generic email helper for receipts; keeps API consistent.
    """
    subject = f"{subject_prefix} – {receipt.transactionID}"
    body = (
        f"Dear {student.name or 'Student'},\n\n"
        "Please find your receipt attached.\n\n"
        "Regards,\nCIIS Accounts Team"
    )
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", getattr(settings, "EMAIL_HOST_USER", None)),
        to=[student.email],
        cc=cc or [],
    )
    msg.attach(f"{filename_prefix}_{receipt.transactionID}.pdf", pdf_bytes, "application/pdf")
    msg.send(fail_silently=False)
