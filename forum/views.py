from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.db.models import Q
from .models import Forum, CommentForum
from .forms import ForumForm, CommentForm
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
import datetime
from django.core.paginator import Paginator
from django.contrib import messages
from socialnetwork.cryptage import decryptage,cryptage

class ForumListView(View):
    def get(self, request, *args,**kwargs):
        forums=Forum.objects.all().exclude(category="autres")
        forum_lists=Forum.objects.filter(category="autres").order_by('-create_on')[:8]
        context= {
            'form':ForumForm(),
            'forums':Paginator(forums,50).get_page(request.GET.get('page')),
            'forum_lists':forum_lists,
        }
        return render(request, 'forum/forum.html', context)

    def post(self, request, *args,**kwargs):
        form =ForumForm(request.POST)
        if form.is_valid():
            new_forum = form.save(commit=False)
            new_forum.user = request.user
            messages.success(request, "le forum a bien été enregitré!")
            new_forum.save()              
            return redirect('forum_detail',pk=new_forum.pk)      
        return           

class ForumDetailView(View):
    def get(self,request,pk, *args,**kwargs):
        forum= get_object_or_404(Forum,pk=pk)
        forums_connexe=Forum.objects.filter(category=forum.category)
        context = {
            'forum':forum,
            'forums_connexe':forums_connexe,
            'comments':CommentForum.objects.filter(forum=forum),
            'form':CommentForm(),
        }
        return render(request,'forum/forum_detail.html', context)

    def post(self,request,pk, *args,**kwargs):
        forum=Forum.objects.get(pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.user=request.user
            new_comment.forum=forum
            new_comment.save()
        
        return redirect('forum_detail',pk=pk)   

class ForumDeleteView(LoginRequiredMixin, UserPassesTestMixin,DeleteView):
    
    model=Forum
    template_name='delete.html'  
    success_url=reverse_lazy('forum_list')   
    def test_func(self):
        forum=self.get_object()
        return self.request.user == forum.user   
        
class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=CommentForum
    template_name='delete.html'    
    def get_success_url(self):
        return reverse_lazy('forum_detail', kwargs={'pk':self.kwargs['forum_pk']})
    def test_func(self):
         forum=self.get_object()
         return self.request.user == forum.user     
            
class CommentReplyView(LoginRequiredMixin, View):
    def post(self, request,forum_pk,pk, *args,**kwargs):
        forum=Forum.objects.get(pk=forum_pk)
        parent_comment=CommentForum.objects.get(pk=pk)
        form=CommentForm(request.POST)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.user=request.user
            new_comment.forum=forum
            new_comment.parent = parent_comment
            new_comment.save()
           
        return redirect('forum_detail',pk=forum_pk)    

