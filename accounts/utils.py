from log_app.serializers import LoggerSerializer

def log_to_logger(level, message):
    log_data = {'level': level, 'message': message}
    log_serializer = LoggerSerializer(data=log_data)
    log_serializer.save()
    