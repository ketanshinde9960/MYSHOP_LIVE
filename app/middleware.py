# yourapp/middleware.py
# from django.contrib import messages
from django.urls import reverse
from .models import Auth
# from django.utils.safestring import mark_safe

class VerifyAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.verification_paths = [
            reverse('auth'), 
            # Add more paths as needed
        ]

    def __call__(self, request):
        # Exclude the login page from the middleware check
        if request.path_info == reverse('login'):  # Adjust 'login' based on your actual login URL or view name
            return self.get_response(request)

        # Check if the user is authenticated
        if request.user.is_authenticated:
            try:
                auth_instance = Auth.objects.get(user=request.user)
                if not auth_instance.is_verified and request.path_info not in self.verification_paths:
                    # Add an info message
                    verify_message = 'Please verify your email to access all features. <a href="/auth/" class="alert-link">Verify link</a>'
                    # messages.info(request, mark_safe(verify_message))
            except Auth.DoesNotExist:
                # Handle the situation if Auth object doesn't exist
                pass

        response = self.get_response(request)
        return response
