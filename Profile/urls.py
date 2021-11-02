from django.urls import path
from .views import GalleryDeleteView,AddNotification,GalleryView,ProfileRespoCreateView,ProfileEditView, ProfileView, ListFollowers, AddFollower, RemoveFollower,UserSearch
from socialnetwork.cryptage import cryptage

urlpatterns = [
    path('profile/notification/evenement/<int:pk>', AddNotification.as_view(), name="add_notification"),
    path('profile/<str:username>', ProfileView.as_view(), name="profile"),
    path('profile/edit/<int:pk>', ProfileEditView.as_view(), name="profile_edit"),
    
    path('gallery_image', GalleryView.as_view(), name="gallery"),
    path('gallery_image/delete/<int:pk>', GalleryDeleteView.as_view(), name="gallery_delete"),
  
    path('profile/responsable/create/<int:pk>', ProfileRespoCreateView.as_view(), name="profile_respo_create"),
    path('profile/<int:pk>/follower', ListFollowers.as_view(), name="list_followers"),
    path('profile/<int:pk>/follower/add', AddFollower.as_view(), name="add_follower"),
    path('profile/<int:pk>/follower/remove', RemoveFollower.as_view(), name="remove_follower"),
    path('search/', UserSearch.as_view(), name="profile_search"),
    

]    

