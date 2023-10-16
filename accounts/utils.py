from rest_framework import response, status

from log_app.serializers import LoggerSerializer


def log_to_logger(level, message):
    log_data = {'level': level, 'message': message}
    log_serializer = LoggerSerializer(data=log_data)
    if log_serializer.is_valid():
        log_serializer.save()
    else:
        return response.Response({'error': 'Failed to create user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    