from django.urls import path
from .views import RegisterView,LoginView,ThreadView,MessageListCreateView
urlpatterns=[
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('thread/',ThreadView.as_view(),name='create-thread'),
    path('thread/<int:thread_id>/messages/',MessageListCreateView.as_view(),name='messages'),


]