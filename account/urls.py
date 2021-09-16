from typing import get_type_hints
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import CreateUserView, UserDetailView
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
    path('account/deleteOrgMember/<int:org_id>', views.delete_organizer_member, name='delete_member' ),
    path('account/addOrgMember/<int:org_id>', views.add_organizer_member, name='add_member' )
]