from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_greater_than_zero(value):
    if value <= 0:
        raise ValidationError(
            _('Значение не может быть меньше или равно нулю'),
            params={'value': value},
        )
    return value
