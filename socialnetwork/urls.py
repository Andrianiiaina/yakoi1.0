from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Profile import views,auth_views
from Evenement.views import EventListView

urlpatterns = [
    path('yakoi/',include('forum.urls')),
    path('admin/', admin.site.urls),
    path('accounts/',include('allauth.urls')),
    path('yakoi/',include('Evenement.urls')),
    path('yakoi/',include('Profile.urls')),

    path("yakoi/register", auth_views.register_request, name="signup"),
    path("yakoi/login", auth_views.login_request, name="login"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


