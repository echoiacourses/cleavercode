from django.urls import path
from . import views


urlpatterns = [
    path('is_read/<int:pk>', views.seenNotification, name='is_read'),
]

