from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),  # Root URL
    path('room/', views.room, name='room'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('dash/', views.dash, name='dash'),
    path('navigate/', views.navigate, name='navigate'),
    path('camera/', views.camera, name='camera'),

    # Updated: generatecode now points to generate_aruco_codes
    path('generatecode/', views.generate_aruco_codes, name='generatecode'),
    path('generate-aruco/', views.generate_aruco_codes, name='generate_aruco'),
    path('scan_aruco/', views.scan_aruco, name='scan_aruco'),
    
    # Video feed (optional for local/testing)
    # Remove in production if no camera is available
    # path('video_feed/<int:camera_index>/', views.video_feed, name='video_feed'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
