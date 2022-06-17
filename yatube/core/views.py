from django.shortcuts import render


def page_not_found(request, exception):
    context = {
        'path': request.path,
    }
    return render(request, 'core/404.html', context, status=404)


def permission_denied_view(request, reason=''):
    context = {
        'path': request.path,
    }
    return render(request, 'core/403.html', context, status=403)


def server_error(request):
    context = {
        'path': request.path,
    }
    return render(request, 'core/500.html', context, status=500)
