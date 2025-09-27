from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Root URL
    path('room/', views.room, name='room'),  # Room URL
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('dash/', views.dash, name='dash'),
    path('navigate/', views.navigate, name='navigate'),
    path('camera/', views.camera, name='camera'),
    path('generatecode/', views.generatecode, name='generatecode'),
    path('generate-aruco/', views.generate_aruco_codes, name='generate_aruco'),
    path('scan_aruco/', views.scan_aruco, name='scan_aruco'),
    path('video_feed/<int:camera_index>/', views.video_feed, name='video_feed'),  # ✅ added
]
