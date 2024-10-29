from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from django.db.models import Q
from django.http import HttpResponseRedirect
from .models import UserProfile,Gallery
from .forms import ProfileForm,  GalleryForm
from Evenement.models import Notification
from Evenement.forms import EventForm
from Evenement.models import Evenement
from django.views.generic.edit import UpdateView,DeleteView
from django.core.paginator import Paginator


def profile(request, username):
        user=User.objects.get(username=username)
        evenements= Evenement.objects.all().filter(user=user).order_by('-create_on')  
        context = {
            'form_evenement':EventForm(),
            'formgallery':GalleryForm(),
            'evenements':Paginator(evenements, 10).get_page(request.GET.get('page')),
            'is_following':request.user.followers.filter(user_id=user.id).exists(),
            'galleries':Gallery.objects.filter(user=user),
            'user':user,
        }
        return render(request, 'profile/profile.html', context)
class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model= UserProfile
    fields=["contact","bio","picture","localisation"]
    template_name = 'profile/profile_edit.html'
    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username':self.request.user.username})
    def test_func(self):
        profile=self.get_object()
        activities=self.request.POST.getlist('activities[]')
        profile.activities=','.join(map(str,activities))
        profile.save()
        return redirect('event_list')    
class ProfileForResponsableView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
        model= UserProfile
        fields=["picture","contact","bio","localisation","nif","stat","cin"]
        template_name = 'profile/profile_edit.html'
        def get_success_url(self):
            return reverse_lazy('profile', kwargs={'username':self.request.user.username})
        def test_func(self):
            profile=self.get_object()
            activities=self.request.POST.getlist('activities[]')
            profile.activities=','.join(map(str,activities))
            profile.save()
            return redirect('event_list')   

def follow_user(request, pk):
        profile = UserProfile.objects.get(pk=pk)       
        profile.followers.add(request.user)    
        notification=Notification.objects.create(notification_type=3, from_user=request.user, to_user=profile.user)
       
        return redirect('profile', username=request.user.username)

def unfollow_user(request, pk):
        profile = UserProfile.objects.get(pk=pk)       
        profile.followers.remove(request.user)    
        return redirect('profile', username=profile.user.username) 

def search_user(request):
        query=self.request.GET.get('query')
        profile_list = UserProfile.objects.filter(Q(user__username__icontains=query))
        return render(request, 'profile/search.html', {'profile_list':profile_list})


class AddNotification(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        evenement = Evenement.objects.get(pk=pk)   
        notification=Notification.objects.create(notification_type=5, to_user=request.user, evenement=evenement)
        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)          
