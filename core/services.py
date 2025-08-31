from core.models import Competition
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import resend
import logging

logger = logging.getLogger(__name__)


def send_email_with_resend(to_email, subject, html_content, text_content=None):
    """
    Send email using Resend API
    """
    try:
        if not settings.RESEND_API_KEY:
            logger.warning("Resend API key not configured, falling back to Django's email backend")
            return send_mail(
                subject=subject,
                message=text_content or html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_content,
                fail_silently=False,
            )
        

        
        resend.api_key = settings.RESEND_API_KEY
        
        params = {
            "from": f"{settings.RESEND_FROM_NAME} <{settings.RESEND_FROM_EMAIL}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        
        if text_content:
            params["text"] = text_content
        
        print(f"DEBUG: Sending email with params: {params}")
        
        response = resend.Emails.send(params)
        print(f"DEBUG: Resend response: {response}")
        logger.info(f"Email sent successfully to {to_email}. Email ID: {response.get('id', 'unknown')}")
        return True
        
    except Exception as e:
        print(f"DEBUG: Exception details: {type(e).__name__}: {str(e)}")
        logger.error(f"Error sending email to {to_email}: {str(e)}")
        return False

def send_template_email(to_email, template_name, context, subject):
    """
    Send email using a Django template
    """
    try:
        html_content = render_to_string(f'emails/{template_name}.html', context)
        text_content = render_to_string(f'emails/{template_name}.txt', context)
        
        return send_email_with_resend(to_email, subject, html_content, text_content)
        
    except Exception as e:
        logger.error(f"Error sending template email to {to_email}: {str(e)}")
        return False