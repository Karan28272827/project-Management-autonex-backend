"""
Email service — sends transactional emails via Brevo (formerly Sendinblue).
Uses their HTTP API, so no extra packages are needed (just urllib).
Free tier: 300 emails/day.

Required env vars:
  BREVO_API_KEY   — API key from Brevo dashboard (Settings → API Keys)
  MAIL_FROM       — Verified sender email address
  MAIL_FROM_NAME  — Display name (default: "Autonex AI")
"""
import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def _send(*, to_email: str, to_name: str, subject: str, html_body: str) -> None:
    """Send a single HTML email via Brevo API. Raises RuntimeError on failure."""
    api_key   = os.getenv("BREVO_API_KEY", "")
    from_addr = os.getenv("MAIL_FROM", "")
    from_name = os.getenv("MAIL_FROM_NAME", "Autonex AI")

    if not api_key:
        raise RuntimeError("BREVO_API_KEY is not configured")
    if not from_addr:
        raise RuntimeError("MAIL_FROM is not configured")

    payload = json.dumps({
        "sender":      {"name": from_name, "email": from_addr},
        "to":          [{"email": to_email, "name": to_name}],
        "subject":     subject,
        "htmlContent": html_body,
        # Disable click tracking so Brevo doesn't wrap reset links in
        # its sendibt2.com redirect, which truncates the token parameter.
        "trackClicks": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        BREVO_API_URL,
        data=payload,
        headers={
            "api-key":      api_key,
            "Content-Type": "application/json",
            "Accept":       "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            logger.info("[email] Brevo accepted message to %s: %s", to_email, body)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        logger.error("[email] Brevo API error %s: %s", exc.code, detail)
        raise RuntimeError(f"Brevo API error {exc.code}: {detail}") from exc
    except OSError as exc:
        raise RuntimeError(f"Could not reach Brevo API: {exc}") from exc


# ── Password reset ────────────────────────────────────────────────────────────

def send_password_reset_email(*, to_email: str, to_name: str, reset_link: str) -> None:
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f7; margin: 0; padding: 0; }}
    .container {{ max-width: 560px; margin: 40px auto; background: #fff; border-radius: 8px;
                  padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    h2 {{ color: #1a1a2e; margin-top: 0; }}
    .btn {{ display: inline-block; margin-top: 24px; background: #4f46e5; color: #fff !important;
            text-decoration: none; padding: 12px 28px; border-radius: 6px; font-size: 15px; }}
    p {{ color: #374151; line-height: 1.6; }}
    .note {{ font-size: 13px; color: #6b7280; margin-top: 20px; }}
    .footer {{ margin-top: 32px; font-size: 12px; color: #9ca3af;
               border-top: 1px solid #e5e7eb; padding-top: 16px; }}
  </style>
</head>
<body>
  <div class="container">
    <h2>Reset your Autonex AI password</h2>
    <p>Hi {to_name.split()[0]},</p>
    <p>We received a request to reset the password for your account.
       Click the button below to choose a new password.</p>
    <a href="{reset_link}" class="btn">Reset Password</a>
    <p class="note">
      This link expires in <strong>15 minutes</strong>.
      If you did not request a password reset, you can safely ignore this email.
    </p>
    <div class="footer">
      <p>Autonex AI &mdash; {os.getenv("MAIL_FROM", "")}</p>
    </div>
  </div>
</body>
</html>"""
    _send(
        to_email=to_email,
        to_name=to_name,
        subject="Reset your Autonex AI password",
        html_body=html,
    )


def try_send_password_reset_email(*, to_email: str, to_name: str, reset_link: str) -> bool:
    """Returns True on success, False on failure (logs the error)."""
    try:
        send_password_reset_email(to_email=to_email, to_name=to_name, reset_link=reset_link)
        return True
    except Exception as exc:
        logger.warning("[email] Password reset email failed for %s: %s", to_email, exc)
        return False
