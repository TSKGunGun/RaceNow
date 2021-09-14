from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import CreateUserView

urlpatterns = [
    path('login/', LoginView.as_view(
        redirect_authenticated_user=True,
        template_name = 'account/login.html',
        ), 
    name='login' ),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('account/create', CreateUserView.as_view(), name='account_create')
]