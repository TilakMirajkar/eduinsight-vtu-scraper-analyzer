from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_detail = response.data
        if isinstance(error_detail, dict) and 'detail' in error_detail:
            error_detail = str(error_detail['detail'])
        response.data = {'error': error_detail}
        return response

    logger.exception('Unhandled exception in view', exc_info=exc)
    return Response(
        {'error': 'An unexpected server error occurred.'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )