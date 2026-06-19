class ActivityLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            from .models import ActivityLog
            if request.user.is_authenticated and not request.path.startswith('/static') and not request.path.startswith('/media'):
                ActivityLog.objects.create(
                    user=request.user,
                    action=f"{request.method} {request.path}",
                    path=request.path[:300],
                    method=request.method,
                    ip=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:300],
                )
        except Exception:
            pass
        return response
