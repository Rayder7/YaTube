from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    return render(
        request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    return render(request, 'core/403.html', {}, HTTPStatus.FORBIDDEN)


def server_error(request):
    return render(
        request, 'core/500.html', {}, HTTPStatus.INTERNAL_SERVER_ERROR)
