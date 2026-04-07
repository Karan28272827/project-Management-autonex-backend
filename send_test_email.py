"""
send_test_email.py — Send a test email using the configured SMTP or Brevo credentials.

Usage:
    python send_test_email.py [recipient@example.com]

If no recipient is passed, defaults to the TO_EMAIL constant below.
Reads credentials from .env in the same directory.
"""

import os
import sys
import json
import smtplib
import urllib.request
import urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# ── Load .env.production then .env (production takes priority) ────────────────
for env_file in [".env.production", ".env"]:
    env_path = Path(__file__).parent / env_file
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip().strip('"'))

# ── Config ────────────────────────────────────────────────────────────────────
TO_EMAIL    = sys.argv[1] if len(sys.argv) > 1 else "paigudekaran2827@gmail.com"
TO_NAME     = "Test Recipient"
FROM_EMAIL  = os.getenv("MAIL_FROM", "")
FROM_NAME   = os.getenv("MAIL_FROM_NAME", "Autonex AI")
BREVO_KEY   = os.getenv("BREVO_API_KEY", "")
SMTP_HOST   = os.getenv("SMTP_HOST", "")
SMTP_PORT   = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER   = os.getenv("SMTP_USER", "")
SMTP_PASS   = os.getenv("SMTP_PASSWORD", "")

SUBJECT = "Autonex AI — Test Email"
HTML_BODY = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f7; margin: 0; padding: 0; }}
    .container {{ max-width: 560px; margin: 40px auto; background: #fff; border-radius: 8px;
                  padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    h2 {{ color: #1a1a2e; margin-top: 0; }}
    p  {{ color: #374151; line-height: 1.6; }}
    .badge {{ display: inline-block; background: #4f46e5; color: #fff; padding: 6px 16px;
              border-radius: 20px; font-size: 13px; margin-top: 8px; }}
    .footer {{ margin-top: 32px; font-size: 12px; color: #9ca3af;
               border-top: 1px solid #e5e7eb; padding-top: 16px; }}
  </style>
</head>
<body>
  <div class="container">
    <h2>Test Email from Autonex AI</h2>
    <p>Hi,</p>
    <p>This is a test email sent from the Autonex AI platform to verify that the email
       delivery system is working correctly.</p>
    <span class="badge">Email delivery OK</span>
    <p>From: <strong>{FROM_NAME}</strong> &lt;{FROM_EMAIL}&gt;<br>
       To:   <strong>{TO_NAME}</strong> &lt;{TO_EMAIL}&gt;</p>
    <div class="footer">
      <p>Autonex AI &mdash; {FROM_EMAIL}</p>
    </div>
  </div>
</body>
</html>"""


def send_via_brevo() -> None:
    payload = json.dumps({
        "sender":      {"name": FROM_NAME, "email": FROM_EMAIL},
        "to":          [{"email": TO_EMAIL, "name": TO_NAME}],
        "subject":     SUBJECT,
        "htmlContent": HTML_BODY,
        "trackClicks": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=payload,
        headers={
            "api-key":      BREVO_KEY,
            "Content-Type": "application/json",
            "Accept":       "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        print(f"[Brevo] Accepted: {resp.read().decode()}")


def send_via_smtp() -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = SUBJECT
    msg["From"]    = f"{FROM_NAME} <{SMTP_USER}>"
    msg["To"]      = TO_EMAIL
    msg.attach(MIMEText(HTML_BODY, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [TO_EMAIL], msg.as_string())
    print(f"[SMTP] Sent via {SMTP_HOST}:{SMTP_PORT}")


# ── Main ──────────────────────────────────────────────────────────────────────
print(f"Sending test email to {TO_EMAIL} ...")

if BREVO_KEY:
    print("Using: Brevo API")
    try:
        send_via_brevo()
    except urllib.error.HTTPError as exc:
        print(f"Brevo error {exc.code}: {exc.read().decode()}")
        sys.exit(1)
elif SMTP_HOST and SMTP_USER and SMTP_PASS:
    print(f"Using: SMTP ({SMTP_HOST})")
    try:
        send_via_smtp()
    except Exception as exc:
        print(f"SMTP error: {exc}")
        sys.exit(1)
else:
    print("ERROR: No email credentials found.")
    print("Set BREVO_API_KEY or SMTP_HOST + SMTP_USER + SMTP_PASSWORD in .env")
    sys.exit(1)

print(f"Done. Check {TO_EMAIL} inbox.")
