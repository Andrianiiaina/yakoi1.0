from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View 
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .models import Image,Gallery
from .forms import GalleryForm 
from django.views.generic.edit import DeleteView

class GalleryView(LoginRequiredMixin, View):
    def post(self, request, *args,**kwargs):
        form=GalleryForm(request.POST)
        files = request.FILES.getlist('image')
        if form.is_valid():
            title = form.cleaned_data['title']
            new_gallery = form.save(commit=False)
            new_gallery.user = request.user
            new_gallery.save()
            for f in files:
                img=Image(image=f)
                img.save()
                new_gallery.image.add(img)
            new_gallery.save()
        return redirect('profile',username=new_gallery.user.username)   

class GalleryDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=Gallery
    template_name='delete.html'    
    success_url=reverse_lazy('event_list')   
    def test_func(self):
        gallery=self.get_object()
        return self.request.user == gallery.user 
