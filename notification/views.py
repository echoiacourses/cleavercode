from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .models import UserObj, Notification

# Create your views here.

def seenNotification(request, pk):
    if request.user.is_authenticated:
        user_obj = UserObj.objects.get(user=request.user)
        notification_qs = Notification.objects.get(id=pk)
        notification_qs.userobj.remove(user_obj)
        
        if notification_qs.userobj.count() == 0:
            notification_qs.delete()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('login')