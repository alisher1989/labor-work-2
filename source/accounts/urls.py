from django.urls import path
from accounts.views import register_view, user_activate_view, \
    UserDetailView, UserChangeView, UserChangePasswordView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register'),
    path('activate/<token>/', user_activate_view, name='user_activate'),
    path('profile/<pk>/', UserDetailView.as_view(), name='user_detail'),
    path('profile/<pk>/edit/', UserChangeView.as_view(), name='user_update'),
    path('profile/<pk>/change-password/', UserChangePasswordView.as_view(), name='user_change_password'),
]


app_name = 'registration'