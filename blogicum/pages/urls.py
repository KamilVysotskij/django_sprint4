from django.conf.urls import handler404, handler500, handler403, handler400
from django.urls import path

from pages import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutView.as_view(), name='about'),
    path('rules/', views.RulesView.as_view(), name='rules'),
]