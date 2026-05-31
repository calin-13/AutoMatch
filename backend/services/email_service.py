import json
import logging
import urllib.request
import urllib.error

from config import RESEND_API_KEY, EMAIL_FROM

logger = logging.getLogger("automatch.email")


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    # In development logam mereu linkul ca sa putem testa fara inbox.
    print(f"[RESET LINK] {to_email} -> {reset_link}")
    logger.warning("Reset link pentru %s: %s", to_email, reset_link)

    if not RESEND_API_KEY:
        return

    payload = json.dumps({
        "from": EMAIL_FROM,
        "to": [to_email],
        "subject": "Resetare parola AutoMatch",
        "html": (
            "<p>Ai cerut resetarea parolei pentru contul tau AutoMatch.</p>"
            f'<p><a href="{reset_link}">Apasa aici pentru a seta o parola noua</a></p>'
            "<p>Linkul expira in 30 de minute. Daca nu tu ai cerut, ignora emailul.</p>"
        ),
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10):
            pass
    except urllib.error.HTTPError as e:
        logger.error("Resend HTTPError %s: %s", e.code, e.read().decode("utf-8", "ignore"))
    except Exception as e:
        logger.error("Eroare la trimiterea emailului: %s", e)
