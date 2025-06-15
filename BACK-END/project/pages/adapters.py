from allauth.account.adapter import DefaultAccountAdapter
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import os

class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        msg = self.render_mail(template_prefix, email, context)
        msg.send()

    def render_mail(self, template_prefix, email, context):
        if template_prefix.startswith('account/email/'):
            template_prefix = template_prefix.replace('account/email/', '')

        subject_template = f"account/email/{template_prefix}_subject.txt"
        text_template = f"account/email/{template_prefix}_message.txt"
        html_template = f"account/email/{template_prefix}_message.html"

        subject = render_to_string(subject_template, context).strip()
        text_body = render_to_string(text_template, context)

        # تحقق إن قالب الـ HTML موجود فعلًا
        template_path = os.path.join(settings.TEMPLATES[0]['DIRS'][0], html_template)
        if os.path.exists(template_path):
            html_body = render_to_string(html_template, context)
        else:
            html_body = None

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )

        if html_body:
            msg.attach_alternative(html_body, "text/html")

        return msg
