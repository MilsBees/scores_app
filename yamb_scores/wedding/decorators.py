from functools import wraps

from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse


SESSION_FLAG = 'wedding_authenticated'


def wedding_view(api=False):
    def decorate(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.session.get(SESSION_FLAG) is not True:
                if api:
                    response = JsonResponse({'error': 'Authentication required.'}, status=401)
                else:
                    response = redirect(reverse('wedding:login'))
            else:
                response = view(request, *args, **kwargs)
            response['X-Robots-Tag'] = 'noindex, nofollow'
            return response
        return wrapped
    return decorate


def noindex(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        response['X-Robots-Tag'] = 'noindex, nofollow'
        return response
    return wrapped
