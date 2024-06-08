from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from blog import views

urlpatterns = [
    path(
        '',
        include('blog.urls', namespace='blog')
    ),
    path(
        'pages/',
        include('pages.urls', namespace='pages')
    ),
    path(
        'admin/',
        admin.site.urls
    ),
    path(
        'auth/',
        include('django.contrib.auth.urls')
    ),
    path(
        'auth/registration/',
        views.RegistrationView.as_view(),
        name='registration'
    ),
]

handler404 = 'pages.views.handler404'
handler403 = 'pages.views.handler403'
handler500 = 'pages.views.handler500'

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
