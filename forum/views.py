from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from .models import Forum, CommentForum
from .forms import ForumForm, CommentForm
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
import datetime
from django.core.paginator import Paginator
from django.contrib import messages
from socialnetwork.cryptage import decryptage,cryptage
# Create your views here.
# Create your views here.

class ForumListView(View):
    def get(self, request, *args,**kwargs):
        forums=Forum.objects.all().exclude(category="autres")
        forum_lists=Forum.objects.filter(category="autres").order_by('-create_on')[:8]
        
        form=ForumForm()

        paginator = Paginator(forums,50)
        page_number = request.GET.get('page')
        forums_obj = paginator.get_page(page_number)
        context= {
            'form':form,
            'forums':forums_obj,
            'forum_lists':forum_lists,
        }
        return render(request, 'forum/forum.html', context)


    def post(self, request, *args,**kwargs):
        forums =Forum.objects.all().order_by('create_on')
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
        forum=Forum.objects.get(pk=pk)
        forums_connexe=Forum.objects.filter(category=forum.category)
        form = CommentForm()

        comments=CommentForum.objects.filter(forum=forum)
        context = {
            'forum':forum,
            'forums_connexe':forums_connexe,
            'comments':comments,
            'form':form,
        }
        return render(request,'forum/forum_detail.html', context)

    def post(self,request,pk, *args,**kwargs):
        pk=decryptage(url)
        forum=Forum.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.user=request.user
            new_comment.forum=forum
            new_comment.save()
        comments=CommentForum.objects.filter(forum=forum)
        
        context = {
            'forum':forum,
            'comments':comments,
            'form':form,
        }    
    
        return redirect('forum_detail',url=url)   

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
        pk=self.kwargs['forum_pk']

        return reverse_lazy('forum_detail', kwargs={'url':cryptage(pk)})
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
           
        return redirect('forum_detail',url=cryptage(forum_pk))    

