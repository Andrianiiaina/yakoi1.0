from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from .models import Evenement, Comment, Notification, Image, Tag, Ville, Like
from Profile.models import UserProfile
from .forms import EventForm, CommentForm
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
import datetime

class EventListView(View):
    def get(self, request, *args,**kwargs):
        evenements=[]
        if request.user.is_authenticated:
            profile=UserProfile.objects.get(pk=request.user.pk)
            if profile.activities:
                evenements= Evenement.objects.filter(category__in=profile.activities.split(','))
                evenements=evenements.exclude(date__lte=datetime.date.today()+datetime.timedelta(days=-1))
        if(evenements is None):
            evenements=Evenement.objects.all().exclude(date__lte=datetime.date.today()+datetime.timedelta(days=-1)).order_by('-create_on')[:10]

        #recuperation des evenements chaque semaine
        today=datetime.date.today()
        start_week=today - datetime.timedelta(today.weekday())
        events_week=Evenement.objects.filter(date__range=[start_week, start_week + datetime.timedelta(7)])[:10]
        context= {
            'events_week':events_week,
            'evenements':evenements,
            'tags':Tag.objects.all().order_by('name'),
            'villes':Ville.objects.all().order_by('name'),
        }
        return render(request, 'evenements/event_list.html', context)

    def post(self, request, *args,**kwargs):
        form = EventForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            new_event = form.save(commit=False)
            new_event.user = request.user
            new_event.category = request.POST.get('category')
            start_date_str=request.POST.get('date') 
            end_date_str=request.POST.get('date_end')
            start=datetime.datetime.strptime(start_date_str,'%Y-%m-%d').date() 
            end=datetime.datetime.strptime(end_date_str,'%Y-%m-%d').date() 
            if end > start:     
                new_event.date=start
                new_event.end_date=end
                new_event.save()
                messages.success(request, "l'événement  a bien été ajouté!")
                new_event.create_tags()      
                #on met à jour le nom de ville disponible
                Ville.objects.get_or_create(name=new_event.location)
                new_event.save()  
                for image in request.FILES.getlist('image'):
                    img=Image(image=image, evenement=new_event)

                    img.save()
                new_event.save()  

                return redirect('event_detail',pk=new_event.pk)  
            return redirect('profile', username=request.user.username)   
 
        else: 
            messages.error(request, "la creation d'evenement a echouée, veuillez verifier vos données")
            return redirect('profile', username=request.user.username)   
class EventDetailView(View):
    def get(self,request,pk, *args,**kwargs):
        evenement= Evenement.objects.get(pk=pk)
        #recuperation des evenements connexes
        connexe_events=Evenement.objects.exclude(date__lte=datetime.date.today()+datetime.timedelta(days=-1)).filter(category = evenement.category)[:6]
        context = {
            'evenements':connexe_events,
            'evenement':evenement,
            'comments':Comment.objects.filter(event=evenement).order_by('-create_on'),
            'form':CommentForm(),
        }
        return render(request, 'evenements/event_detail.html', context)
         
class EventDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=Evenement
    template_name='delete.html'    
    success_url=reverse_lazy('event_list')   
    def test_func(self):
        event=self.get_object()
        return self.request.user == event.user 
class EventEditView(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    model= Evenement
    fields=["title","description","location","date","category"]
    template_name = 'edit.html'
   
    def get_success_url(self):
        pk=self.kwargs['pk']
        return reverse_lazy('event_detail',kwargs={'pk':pk})
    def test_func(self):
        event=self.get_object()
        return self.request.user == event.user  
class Explore(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        tag = Tag.objects.filter(name=query).first()
        evenements = Evenement.objects.filter(tags__in=[tag])
        return render(request, 'evenements/event_search.html', {'publications': evenements})
    #recherche à partir de plusieurs tag
    def post(self, request, *args,**kwargs):
        liste_tags=request.POST.getlist('rc[]') 
        tags=Tag.objects.filter(name__in=liste_tags)
        evenements=Evenement.objects.filter(tags__in=tags).distinct()
        return render(request, 'evenements/event_search.html', {'publications' : evenements })  