from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('signup/', views.signup, name='signup'),
    path('play/', views.join_match,   name='play'),
    path('status/', views.match_status, name='match_status'),
    path('match/<int:match_id>/start/', views.start_round, name='start_round'),
    path('round/<int:round_id>/<str:user_phase>/play/', views.play_round, name='play_round'),
    path('round/<int:round_id>/<str:phase>/waiting/', views.waiting_phase, name='waiting_phase'),
    path('round/<int:round_id>/complete/', views.round_complete, name='round_complete'),
    path('match/<int:match_id>/complete/', views.match_complete, name='match_complete'),
]
