from django.conf import settings

def notifications_count(request):
    if request.user.is_authenticated:
        try:
            return {'unread_notifications_count': request.user.notifications.filter(is_read=False).count(),
                    'unread_messages_count': request.user.received_messages.filter(is_read=False).count()}
        except Exception:
            return {}
    return {}

def theme_preference(request):
    theme = 'light'
    if request.user.is_authenticated and getattr(request.user, 'theme_preference', None):
        theme = request.user.theme_preference
    theme = request.COOKIES.get('gflow_theme', theme)
    # Language
    lang = request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else settings.LANGUAGE_CODE
    return {
        'current_theme': theme,
        'current_language': lang,
        'available_languages': settings.LANGUAGES,
    }
