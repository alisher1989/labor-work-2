from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.urls import reverse
from main.settings import HOST_NAME
from django.views.generic import DetailView, UpdateView

from accounts.forms import SignUpForm, UserChangeForm, UserChangePasswordForm
from accounts.models import Token


def login_view(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('webapp:index')
        else:
            context['has_error'] = True
    return render(request, 'registration/login.html', context=context)


def logout_view(request):
    logout(request)
    return redirect('webapp:index')



def register_view(request):
    if request.method == 'GET':
        form = SignUpForm()
        return render(request, 'register.html', context={'form': form})
    elif request.method == 'POST':
        form = SignUpForm(data=request.POST)
        if form.is_valid():
            user = User(
                 username=form.cleaned_data.get('username'),
                 email=form.cleaned_data.get('email'),
                 is_active=False
            )
            user.set_password(form.cleaned_data.get('password'))
            user.save()

            token = Token.objects.create(user=user)

            activation_url = HOST_NAME + reverse('accounts:user_activate', kwargs={'token': token})
            try:
                user.email_user(
                    'Вы зарегистрировались на сайте localhost:8000.',
                    'Для активации перейдите по ссылке: ' + activation_url
                )
            except ConnectionRefusedError:
                print('Could not send email. Server error.')

            return redirect('webapp:index')
        else:
            return render(request, 'register.html', context={'form': form})


def user_activate_view(request, token):
    token = get_object_or_404(Token, token=token)
    user = token.user
    user.is_active = True
    user.save()
    login(request, user)
    return redirect('webapp:index')


class UserDetailView(DetailView):
    model = User
    template_name = 'user_detail.html'
    context_object_name = 'user_obj'


class UserChangeView(UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'user_update.html'
    context_object_name = 'user_obj'
    form_class = UserChangeForm

    def test_func(self):
        return self.get_object() == self.request.user

    def get_success_url(self):
        return reverse('accounts:user_detail', kwargs={'pk': self.object.pk})


class UserChangePasswordView(UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'user_change_password.html'
    form_class = UserChangePasswordForm
    context_object_name = 'user_obj'

    def test_func(self):
        return self.get_object() == self.request.user

    # def form_valid(self, form):
    #     user = form.save()
    #     login(self.request, user)
    #     return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('accounts:login')