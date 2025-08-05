from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('compose/', views.compose_message, name='compose'),
    path('message/<int:pk>/', views.message_detail, name='message_detail'),
]
