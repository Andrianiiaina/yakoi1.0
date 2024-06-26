"""socialnetwork URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Evenement.views import EventListView
from Profile import views

urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('admin/', admin.site.urls),
    path('accounts/',include('allauth.urls')),
    path('yakoi/',include('Evenement.urls')),
    path('',include('Profile.urls')),
    path('',include('Forum.urls')),
    path("yakoi/register", views.register_request, name="signup"),
    path("yakoi/login", views.login_request, name="login"),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


