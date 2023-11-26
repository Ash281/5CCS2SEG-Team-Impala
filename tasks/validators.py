from django.core.exceptions import ValidationError
from django.utils import timezone

def validate_not_past_date(value):
    if value < timezone.now().date():
        raise ValidationError('Due date cannot be in the past')
