from django.shortcuts import render


def custom_404(request, exception):
    template = 'core/404.html'
    return render(request, template, status=404)


def custom_403(request, exception):
    template = 'core/403.html'
    return render(request, template, status=403)


def custom_403csrf(request, reason=''):
    template = 'core/403csrf.html'
    return render(request, template, status=403)


def custom_500(request):
    template = 'core/500.html'
    return render(request, template, status=500)
