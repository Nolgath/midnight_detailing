"""Context processors for global template variables."""

from django.conf import settings


def site_info(request):
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Midnight Detailing'),
        'SITE_TAGLINE': getattr(settings, 'SITE_TAGLINE', ''),
        'CONTACT_EMAIL': getattr(settings, 'CONTACT_EMAIL', ''),
    }
