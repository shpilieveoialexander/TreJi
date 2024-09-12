# This file for delay tasks
# This file for delay tasks
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from service.core import settings
from service.core.celery_app import celery_app

from .utils import send_email


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"Test task return {word}"


@celery_app.task(acks_late=True)
def send_invite(email: str, tmp_token: str):
    url_link = f"https://{settings.SERVER_HOST}/developer-sign-up/?token={tmp_token}&email={email}"
    template_path = Path("service/templates/email_template.html")
    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(Path("service/templates/email_template.html").name)
    return send_email(email, "Account Verification", template.render(url=url_link))
