from django.core.exceptions import ValidationError
from django.contrib.auth import validators


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            'Имя пользователя "me" не разрешено.'
        )
    return value
