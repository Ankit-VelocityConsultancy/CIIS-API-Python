def safe_value(val):
    if val is None:
        return ""
    val_str = str(val).strip().lower()
    if val_str in ["nan", "null"]:
        return ""
    return str(val).strip()
  
import math


def safe_value_serializer(val):
    if val is None:
        return ""
    if isinstance(val, float) and math.isnan(val):
        return ""
    val_str = str(val).strip().lower()
    if val_str in ["nan", "null", "none"]:
        return ""
    return str(val).strip()

# super_admin/utils.py
import hashlib
import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import ExamFileUpload

# =========================
# Fixed column sets (exact order)
# =========================

# For set_exam_for_subject (single-subject uploads/downloads)
SINGLE_HEADERS = [
    'Question', 'Question Type', 'Marks', 'Difficulty Level',
    'Option 1', 'Option 2', 'Option 3', 'Option 4', 'Answer'
]

# For bulk_exam_upload (bulk uploads/downloads)
BULK_HEADERS = [
    'COURSE', 'STREAM', 'SUBSTREAM', 'SESSION', 'MODE', 'YEAR/SEMESTER',
    'SUBJECT NAME', 'TYPE OF EXAM', 'QUESTION TYPE', 'DIFFICULTY LEVEL',
    'QUESTION', 'OPTION 1', 'OPTION 2', 'OPTION 3', 'OPTION 4',
    'ANSWER', 'MARKS', 'EXAM DURATION', 'PASSING MARKS'
]

# =========================
# Validators (presence-only)
# =========================
# Keep validators aligned with your fixed upload formats:
REQUIRED_SINGLE_COLUMNS = SINGLE_HEADERS
REQUIRED_BULK_COLUMNS   = BULK_HEADERS


def calculate_file_hash(file) -> str:
    if isinstance(file, InMemoryUploadedFile):
        pos = file.tell()
        file.seek(0)
        h = hashlib.sha256()
        for chunk in file.chunks():
            h.update(chunk)
        file.seek(pos)
        return h.hexdigest()
    else:
        data = file.read()
        file.seek(0)
        return hashlib.sha256(data).hexdigest()


def check_file_exists(university_id: int, file_hash: str, upload_type: str) -> bool:
    return ExamFileUpload.objects.filter(
        university_id=university_id, file_hash=file_hash, upload_type=upload_type
    ).exists()


def save_file_metadata(university_id: int, file, file_hash: str, upload_type: str, username: str = None):
    return ExamFileUpload.objects.create(
        university_id=university_id,
        file_name=file.name if hasattr(file, 'name') else str(file),
        file_size=getattr(file, 'size', 0) or 0,
        file_hash=file_hash,
        upload_type=upload_type,
        uploaded_by=username or "System",
    )


def validate_excel_file(file):
    """Validate BULK upload format (19 fixed columns)."""
    try:
        df = pd.read_excel(file)
    except Exception as e:
        return None, f"Invalid or unreadable Excel file: {e}"
    missing = [c for c in REQUIRED_BULK_COLUMNS if c not in df.columns]
    if missing:
        return None, f"Missing required columns: {', '.join(missing)}"
    return df, None


# =========================
# Row builders for download
# =========================
def build_single_row(exam, q):
    """
    For set_exam_for_subject downloads (SINGLE_HEADERS order).
    """
    return [
        q.question or '',
        q.type or '',
        q.marks or '',
        q.difficultylevel or '',
        q.option1 or '',
        q.option2 or '',
        q.option3 or '',
        q.option4 or '',
        (q.answer or '').lower(),
    ]


def build_bulk_row(exam, q):
    """
    For bulk_exam_upload downloads (BULK_HEADERS order).
    """
    return [
        getattr(exam.course, 'name', ''),
        getattr(exam.stream, 'name', ''),
        getattr(exam.substream, 'name', '') if exam.substream_id else '',
        exam.session or '',
        exam.studypattern or '',
        exam.semyear or '',
        getattr(exam.subject, 'name', ''),
        exam.examtype or '',
        q.type or '',
        q.difficultylevel or '',
        q.question or '',
        q.option1 or '',
        q.option2 or '',
        q.option3 or '',
        q.option4 or '',
        (q.answer or '').lower(),
        q.marks or '',
        exam.examduration or '',
        exam.passingmarks or '',
    ]
    
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_pdf_from_template(template_path: str, context: dict) -> bytes:
    """
    Render Django template to PDF bytes using xhtml2pdf.
    """
    html = get_template(template_path).render(context)
    out = BytesIO()
    result = pisa.CreatePDF(html, dest=out, encoding="UTF-8")
    if result.err:
        raise ValueError("PDF render failed")
    return out.getvalue()
