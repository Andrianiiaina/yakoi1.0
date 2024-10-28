from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.http import HttpResponseRedirect
from .models import Evenement, Comment, Notification, Image, Tag, Ville, Like
from .forms import EventForm, CommentForm
from django.views.generic.edit import  DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def comment_post(request,pk):  
    if request.method == 'POST':
        evenement=Evenement.objects.get(pk=pk)    
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.user=request.user
            new_comment.event=evenement
            new_comment.save()
        notification=Notification.objects.create(notification_type=2, from_user=request.user, to_user=evenement.user, evenement=evenement)
    return redirect('event_detail',pk=pk)  
def replay_comment_post(request,evenement_pk,pk):
    if request.method == 'POST':
        evenement=Evenement.objects.get(pk=evenement_pk)
        parent_comment=Comment.objects.get(pk=pk)
        form=CommentForm(request.POST)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.user=request.user
            new_comment.event=evenement
            new_comment.parent = parent_comment
            new_comment.save()
            if(new_comment.user != parent_comment.user):
                notification=Notification.objects.create(notification_type=2, from_user=request.user, to_user=parent_comment.user, comment=new_comment)
           
    return redirect('event_detail',pk=evenement.pk)    

class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=Comment
    template_name='delete.html' 

    def get_success_url(self):
        event_pk=self.kwargs['event_pk']
        pk=self.kwargs['pk']
        return reverse_lazy('event_detail', kwargs={'pk':event_pk})
    def test_func(self):
        event=self.get_object()
        return self.request.user == event.user
def like_event(request,pk):
    if request.method == 'POST':
        evenement=Evenement.objects.get(pk=pk)
        like, created= Like.objects.get_or_create(user_id=request.user.pk, event_id=pk)
        if created: 
            notification=Notification.objects.create(notification_type=1, from_user=request.user, to_user=evenement.user,evenement=evenement)
        else:
            like.delete() 
        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)   
def search_event(request):
    query=request.GET.get('query')
    if any(query in tup for tup in EventForm.TYPE_CHOICES):
        evenements=Evenement.objects.filter(category=query)
    else:     
        evenements=Evenement.objects.filter(Q(description__icontains=query)) 
    return render(request,'evenements/event_search.html',{'publications':evenements})
