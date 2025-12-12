# Import necessary modules and functions
from django.http import JsonResponse
from rest_framework import status


# Middleware for handling JSON error responses
class JsonErrorResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the response from the view function
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # Process exceptions and return JSON error response
        error_message = str(exception)
        response_data = {"error": error_message}
        return JsonResponse(response_data, status=500)


# Middleware for handling custom 404 responses
class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the response from the view function
        response = self.get_response(request)
        
        # Check if path is admin or API (exclude from JSON 404 handling)
        is_admin = request.path.startswith('/admin/') or '/admin/' in request.path
        is_api = request.path.startswith('/api/')
        
        # Only handle 404 for non-API and non-admin requests
        if not is_api and not is_admin:
            if response.status_code == status.HTTP_404_NOT_FOUND:
                # If response status is 404, handle 404 error
                return self.handle_404(request)

        return response

    def handle_404(self, request):
        # Handle 404 error and return JSON response
        data = {"detail": "Not Found"}
        return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)

