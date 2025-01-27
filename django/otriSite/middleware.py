from django.utils.deprecation import MiddlewareMixin

class FixForwardedHostMiddleware(MiddlewareMixin):
    def process_request(self, request):
        forwarded_host = request.META.get('HTTP_X_FORWARDED_HOST')
        if forwarded_host:
            forwarded_host = forwarded_host.split(':')[0]
            request.META['HTTP_X_FORWARDED_HOST'] = forwarded_host 