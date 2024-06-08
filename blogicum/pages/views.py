from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def handler404(request, exception):
    """Обработчик ошибок 404 (страница не найдена)."""
    return render(request, 'pages/404.html', status=404)

def handler500(request):
    """Обработчик ошибок 500 (внутренняя ошибка сервера)."""
    return render(request, 'pages/500.html', status=500)

def handler403(request, exception):
    """Обработчик ошибок 403 (запрет доступа)."""
    return render(request, 'pages/403csrf.html', status=403)