"""
Contact form endpoint.

We don't run our own mail server. Two delivery modes are supported, tried in
order:

1. **Resend** (recommended) — set ``RESEND_API_KEY``. The free tier covers
   100 emails/day which is more than enough for a chapter contact form.
   Until you verify a sending domain at https://resend.com, keep
   ``CONTACT_FROM_EMAIL`` at ``onboarding@resend.dev`` (their shared test
   sender). Once a domain is verified, swap to ``contact@yourdomain.com``.

2. **SMTP fallback** — set ``CONTACT_SMTP_HOST``, ``CONTACT_SMTP_PORT``,
   ``CONTACT_SMTP_USER``, ``CONTACT_SMTP_PASSWORD``. Useful for Gmail app
   passwords or any standard SMTP provider.

Both modes require ``CONTACT_TO_EMAIL`` (the inbox messages land in). If
no delivery method is configured, we log the message and return 503 so the
frontend can show a friendly fallback.

All config is read through ``core.config.settings`` (pydantic-settings)
rather than ``os.getenv`` so values from ``.env`` are honoured locally.
"""
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class ContactMessage(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)


def _build_email_body(payload: ContactMessage) -> str:
    return (
        f"New contact-form submission from the AI Student Chapter website.\n\n"
        f"Name:    {payload.name}\n"
        f"Email:   {payload.email}\n"
        f"Subject: {payload.subject}\n\n"
        f"---\n{payload.message}\n"
    )


def _send_via_resend(payload: ContactMessage, to_email: str, from_email: str) -> bool:
    if not settings.RESEND_API_KEY:
        return False
    try:
        resp = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": from_email,
                "to": [to_email],
                "reply_to": str(payload.email),
                "subject": f"[Chapters Contact] {payload.subject}",
                "text": _build_email_body(payload),
            },
            timeout=10.0,
        )
        if resp.status_code >= 400:
            logger.warning("Resend rejected message: %s %s", resp.status_code, resp.text)
            return False
        return True
    except httpx.HTTPError as exc:
        logger.warning("Resend request failed: %s", exc)
        return False


def _send_via_smtp(payload: ContactMessage, to_email: str, from_email: str) -> bool:
    host = settings.CONTACT_SMTP_HOST
    if not host:
        return False

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Reply-To"] = str(payload.email)
    msg["Subject"] = f"[Chapters Contact] {payload.subject}"
    msg.attach(MIMEText(_build_email_body(payload), "plain"))

    try:
        with smtplib.SMTP(host, settings.CONTACT_SMTP_PORT, timeout=15) as server:
            server.starttls()
            if settings.CONTACT_SMTP_USER and settings.CONTACT_SMTP_PASSWORD:
                server.login(settings.CONTACT_SMTP_USER, settings.CONTACT_SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except (smtplib.SMTPException, OSError) as exc:
        logger.warning("SMTP send failed: %s", exc)
        return False


@router.post("", status_code=202)
async def submit_contact(payload: ContactMessage):
    to_email = settings.CONTACT_TO_EMAIL
    from_email = settings.CONTACT_FROM_EMAIL or "onboarding@resend.dev"
    if not to_email:
        logger.error("CONTACT_TO_EMAIL is not configured")
        raise HTTPException(
            status_code=503,
            detail="Contact form is not configured. Please email the chapter directly.",
        )

    if _send_via_resend(payload, to_email, from_email):
        return {"status": "sent", "via": "resend"}
    if _send_via_smtp(payload, to_email, from_email):
        return {"status": "sent", "via": "smtp"}

    logger.error(
        "Contact form delivery failed (no provider configured). Payload from %s: %s",
        payload.email,
        payload.subject,
    )
    raise HTTPException(
        status_code=503,
        detail="Email delivery is temporarily unavailable. Please try again later.",
    )
