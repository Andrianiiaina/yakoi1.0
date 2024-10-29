from django.urls import path
from .views import AddNotification,ProfileForResponsableView,ProfileEditView
from . import views
from .gallery_views import GalleryDeleteView,GalleryView
urlpatterns = [
    path('profile/notification/evenement/<int:pk>', AddNotification.as_view(), name="add_notification"),
    path('profile/<str:username>', views.profile, name="profile"),
    path('profile/edit/<int:pk>', ProfileEditView.as_view(), name="profile_edit"),
    
    path('gallery_image', GalleryView.as_view(), name="gallery"),
    path('gallery_image/delete/<int:pk>', GalleryDeleteView.as_view(), name="gallery_delete"),
  
    path('profile/responsable/create/<int:pk>', ProfileForResponsableView.as_view(), name="profile_respo_create"),
    path('profile/<int:pk>/follower/add', views.follow_user, name="add_follower"),
    path('profile/<int:pk>/follower/remove', views.unfollow_user, name="remove_follower"),
    path('search/', views.search_user, name="profile_search"),
]    

