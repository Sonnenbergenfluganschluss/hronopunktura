class CustomCSRFMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Устанавливаем флаг для HTTPS
        request.is_secure = lambda: True
        response = self.get_response(request)
        return response