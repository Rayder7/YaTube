from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    current_date = timezone.now().year
    return {
        'year': current_date
    }
