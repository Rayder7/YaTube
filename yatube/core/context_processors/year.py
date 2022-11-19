from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    current_date = int(str(timezone.localtime(timezone.now()))[:4])
    return {
        'year': current_date
    }
