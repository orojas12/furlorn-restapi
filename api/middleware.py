import logging
from rest_framework import status


class LoggingMiddleware:
    """This middleware logs every request and response."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        self.logger.debug(request)
        response = self.get_response(request)
        if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            self.logger.error(response)
        else:
            self.logger.debug(response)
        return response
