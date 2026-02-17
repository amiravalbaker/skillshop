from django.urls import path
from . import views # import views.py from the current directory

urlpatterns = [ 
    path('', views.home, name='home'), 
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("listing/create/", views.create_listing, name="create_listing"),  
    path("search/", views.search, name="search"),
    path("listing/<int:listing_id>/edit/", views.edit_listing, name="edit_listing"),
]