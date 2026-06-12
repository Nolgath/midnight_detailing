"""Context processors for global template variables."""

from django.conf import settings


def site_info(request):
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Midnight Detailing'),
        'SITE_TAGLINE': getattr(settings, 'SITE_TAGLINE', ''),
        'SITE_URL': getattr(settings, 'SITE_URL', ''),
        'CONTACT_EMAIL': getattr(settings, 'CONTACT_EMAIL', ''),
        'WHATSAPP_NUMBER': getattr(settings, 'WHATSAPP_NUMBER', ''),
        'BUSINESS_PHONE': getattr(settings, 'BUSINESS_PHONE', ''),
        'BUSINESS_LOCALITY': getattr(settings, 'BUSINESS_LOCALITY', 'Alverca do Ribatejo'),
        'BUSINESS_REGION': getattr(settings, 'BUSINESS_REGION', 'Lisboa'),
        'BUSINESS_POSTAL_CODE': getattr(settings, 'BUSINESS_POSTAL_CODE', ''),
        'GOOGLE_BUSINESS_URL': getattr(settings, 'GOOGLE_BUSINESS_URL', ''),
        'INSTAGRAM_URL': getattr(settings, 'INSTAGRAM_URL', ''),
        'FACEBOOK_URL': getattr(settings, 'FACEBOOK_URL', ''),
        'TIKTOK_URL': getattr(settings, 'TIKTOK_URL', ''),
        'GOOGLE_REVIEW_COUNT': getattr(settings, 'GOOGLE_REVIEW_COUNT', ''),
    }
