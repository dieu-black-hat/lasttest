from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('room/', views.room, name='room'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('dash/', views.dash, name='dash'),
    path('navigate/', views.navigate, name='navigate'),
    path('camera/', views.camera, name='camera'),

    # Render the page (HTML)
    path('generatecode/', views.generatecode, name='generatecode'),

    # API endpoints
    path('generate-aruco/', views.generate_aruco_codes, name='generate_aruco'),
    path('scan_aruco/', views.scan_aruco, name='scan_aruco'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
