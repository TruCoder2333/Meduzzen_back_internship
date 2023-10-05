from log_app.serializers import LoggerSerializer

def log_to_logger(user, action):
    log_data = {'user': user, 'action': action}
    log_serializer = LoggerSerializer(data=log_data)
    if log_serializer.is_valid():
        log_serializer.save()
    else:
        pass