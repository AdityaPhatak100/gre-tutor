from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='main'), 
    path('login/', views.login_user, name='login'), 
    path('signup/', views.register_user, name='signup'),
    path('logout/', views.logout_user, name='logout'),
    path('error/', views.show_error, name='error'),
    path('user_profile/<str:pk>', views.user_profile, name='user-profile'),
    path('quiz/<str:pk>', views.quiz_home, name='quiz-home'),
    path('user_profile/<str:pk>/progress/', views.progress, name='progress'),
    path('user_profile/<str:pk>/add_word', views.add_word, name='add-word'),
    path('user_profile/<str:pk>/add_category', views.add_category, name='add-category'),
    path('user_profile/<str:pk>/word_details/<str:word_id>', views.word_details, name='word-details'),
    path('user_profile/<str:pk>/word_details/<str:word_id>', views.word_details, name='word-details'),
    path('user_profile/<str:pk>/word_details/<str:word_id>/edit_word', views.edit_word, name='edit-word'),
    path('user_profile/<str:pk>/word_details/<str:word_id>/delete_word', views.delete_word, name='delete-word'),
    path('user_profile/<str:pk>/word_details/<str:cat_id>/delete_category', views.delete_cat, name='delete-cat'),
]
