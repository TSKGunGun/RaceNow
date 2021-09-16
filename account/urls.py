from typing import get_type_hints
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import CreateUserView, UserDetailView, CreateOrganizerView, OrganizerDetailView
from . import views

urlpatterns = [
    path('login/', LoginView.as_view(
        redirect_authenticated_user=True,
        template_name = 'account/login.html',
        ), 
    name='login' ),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('account/create', CreateUserView.as_view(), name='account_create'),
    path('account/<int:pk>/detail', UserDetailView.as_view() ,name='account_detail'),
    path('account/deleteOrgMember', views.delete_organizer_member, name='delete_org_member' ),
    path('account/addOrgMember', views.add_organizer_member, name='add_org_member' ),
    path('organizer/create', CreateOrganizerView.as_view(), name='organizer_create'),
    path('organizer/<int:pk>/detail', OrganizerDetailView.as_view(), name='organizer_detail' ),
]