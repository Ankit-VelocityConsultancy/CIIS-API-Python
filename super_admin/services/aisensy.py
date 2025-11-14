# services/aisensy.py
from typing import List, Optional, Dict, Any
import re
import requests
import logging
from django.conf import settings

# Use your app logger so it goes to your configured handlers
logger = logging.getLogger(__name__)
logger = logging.getLogger('student_registration')
handler = logging.FileHandler('student_registration.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger = logging.getLogger('student_registration')

class AiSensyError(Exception):
    """Raised when AiSensy request fails or message is not accepted for delivery."""
    pass


def _normalize_destination(phone: str) -> str:
    """
    Return digits-only destination WITHOUT '+' and prefixed with settings.AISENSY_COUNTRY_CODE.
    """
    digits = re.sub(r"\D", "", phone or "")
    cc = re.sub(r"\D", "", str(getattr(settings, "AISENSY_COUNTRY_CODE", "") or ""))

    if not cc:
        raise AiSensyError("AISENSY_COUNTRY_CODE is not configured.")
    if not digits:
        raise AiSensyError("Empty destination phone.")

    if not digits.startswith(cc):
        if digits.startswith("0"):
            digits = digits[1:]
        if len(digits) == 10:
            digits = f"{cc}{digits}"
        else:
            digits = f"{cc}{digits}"

    if not digits.isdigit():
        raise AiSensyError(f"Destination normalization failed: {digits!r}")

    return digits


def _validate_param_count(campaign_key: str, params: List[str]) -> Dict[str, Any]:
    campaigns = getattr(settings, "AISENSY_CAMPAIGNS", {})
    if campaign_key not in campaigns:
        raise AiSensyError(f"Unknown campaign key '{campaign_key}'")
    info = campaigns[campaign_key]
    expected = int(info.get("param_count", 0))
    if expected and len(params) != expected:
        raise AiSensyError(
            f"Template params count mismatch for '{info['name']}': "
            f"expected {expected}, got {len(params)}"
        )
    return info


def send_aisensy_message(
    *,
    phone: str,
    template_params: List[str],
    campaign_key: str,
    source: str = "ciis",
    media: Optional[Dict[str, Any]] = None,
    buttons: Optional[List[Any]] = None,
    carousel_cards: Optional[List[Any]] = None,
    location: Optional[Dict[str, Any]] = None,
    attributes: Optional[Dict[str, Any]] = None,
    params_fallback_override: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Send a WhatsApp template via AiSensy. Returns raw provider response dict.
    Raises AiSensyError on HTTP or logical failure.
    """
    if not getattr(settings, "AISENSY_API_KEY", ""):
        raise AiSensyError("AISENSY_API_KEY not configured.")

    destination = _normalize_destination(phone)
    camp_info = _validate_param_count(campaign_key, template_params)

    payload = {
        "apiKey": settings.AISENSY_API_KEY,
        "campaignName": camp_info["name"],
        "destination": destination,
        "userName": settings.AISENSY_USERNAME,
        "templateParams": template_params,
        "source": source,
        "media": media or {},
        "buttons": buttons or [],
        "carouselCards": carousel_cards or [],
        "location": location or {},
        "attributes": attributes or {},
        "paramsFallbackValue": {
            **camp_info.get("fallback", {}),
            **(params_fallback_override or {}),
        },
    }

    # Log request (redact key)
    safe_payload = {**payload, "apiKey": "***redacted***"}
    logger.debug("AiSensy request -> %s", safe_payload)

    try:
        url = getattr(settings, "AISENSY_API_URL", None) or "https://backend.aisensy.com/campaign/t1/api/v2"
        resp = requests.post(url, json=payload, timeout=15)
    except requests.RequestException as e:
        logger.exception("AiSensy network error")
        raise AiSensyError(f"Network error calling AiSensy: {e}")

    if resp.status_code != 200:
        logger.error("AiSensy HTTP %s: %s", resp.status_code, resp.text)
        raise AiSensyError(f"AiSensy HTTP {resp.status_code}: {resp.text}")

    try:
        data = resp.json()
    except ValueError:
        logger.error("AiSensy invalid JSON: %s", resp.text[:500])
        raise AiSensyError(f"Invalid JSON from AiSensy: {resp.text[:500]}")

    # Log response
    logger.debug("AiSensy response <- %s", data)

    success_str = str(data.get("success", "")).lower()
    status_str = str(data.get("status", "")).lower()
    errors_in_body = data.get("errors") or data.get("error")

    if errors_in_body:
        logger.error("AiSensy provider error: %s", errors_in_body)
        raise AiSensyError(f"Provider error: {errors_in_body} | resp={data}")

    if not (success_str == "true" or status_str in {"queued", "success"}):
        logger.error("AiSensy logical failure: %s", data)
        raise AiSensyError(
            f"AiSensy accepted HTTP but not message. Response={data} Campaign={camp_info['name']}"
        )

    # Annotate for convenience
    data["_normalized_destination"] = destination
    data["_campaign_name"] = camp_info["name"]
    return data


# ---------- Template builders ----------

def build_new_campaign_params(*, first_name: str) -> List[str]:
    """
    'New Campaign' template (1 param):
      {{1}} -> FirstName
    """
    first = (first_name or "user").strip().split()[0]
    return [first]


def build_exam_details_params(
    *,
    student_name: str,
    subject_name: str,
    studypattern: str,
    semyear: str,
    portal_url: str,
    email: str,
    mobile: str,
    start_date: str,
    end_date: str,
    start_time: str,
    end_time: str,
) -> List[str]:
    """
    'Exam Details' template (5 params):
      {{1}} -> FirstName
      {{2}} -> "<subject_name> <studypattern> <semyear>"
      {{3}} -> portal_url
      {{4}} -> "email / mobile"
      {{5}} -> "<start_date> to <end_date> <start_time>-<end_time>"
    """
    first = (student_name or "Student").strip().split()[0]
    exam_label = " ".join(x for x in [subject_name, studypattern, semyear] if x).strip()
    creds = f"{email} / {mobile}"
    schedule = f"{start_date} to {end_date} {start_time}-{end_time}"
    return [first, exam_label, portal_url, creds, schedule]


def build_exam_reassign_params(
    *,
    student_name: str,
    subject_name: str,
    studypattern: str,
    semyear: str,
    portal_url: str,
    email: str,
    mobile: str,
    start_date: str,
    end_date: str,
    start_time: str,
    end_time: str,
) -> List[str]:
    """
    'CIIS Exam Reassign' template (5 params):
      {{1}} -> FirstName
      {{2}} -> "<subject_name> <studypattern> <semyear>"
      {{3}} -> portal_url
      {{4}} -> "email / mobile"
      {{5}} -> "New schedule: <start_date> to <end_date> <start_time>-<end_time>"
    """
    first = (student_name or "Student").strip().split()[0]
    exam_label = " ".join(x for x in [subject_name, studypattern, semyear] if x).strip()
    creds = f"{email} / {mobile}"
    schedule = f"{start_date} to {end_date} {start_time}-{end_time}"
    return [first, exam_label, portal_url, creds, schedule]
