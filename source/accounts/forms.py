from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label='Username')
    password = forms.CharField(max_length=100, required=True, label='Password',
                               widget=forms.PasswordInput)
    password_confirm = forms.CharField(max_length=100, required=True,
                                       label="Password confirm", widget=forms.PasswordInput)
    email = forms.EmailField(required=True, label='Email')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            User.objects.get(username=username)
            raise ValidationError('Username is already taken.', code='username_taken')
        except User.DoesNotExist:
            return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            User.objects.get(email=email)
            raise ValidationError('Email is already taken.', code='email_taken')
        except User.DoesNotExist:
            return email

    def clean(self):
        super().clean()
        password_1 = self.cleaned_data.get('password')
        password_2 = self.cleaned_data.get('password_confirm')
        if password_1 != password_2:
            raise ValidationError('Passwords do not match', code='passwords_do_not_match')
        return self.cleaned_data


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class UserChangePasswordForm(forms.ModelForm):
    password = forms.CharField(max_length=100, required=True, label='New Password',
                               widget=forms.PasswordInput)
    password_confirm = forms.CharField(max_length=100, required=True, label='New Password confirm',
                                       widget=forms.PasswordInput)
    old_password = forms.CharField(max_length=100, required=True, label='Old Password',
                                   widget=forms.PasswordInput)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        user = self.instance
        if not user.check_password(old_password):
            raise ValidationError('Invalid password.', code='invalid_password')
        return old_password

    def clean(self):
        super().clean()
        password_1 = self.cleaned_data.get('password')
        password_2 = self.cleaned_data.get('password_confirm')
        if password_1 != password_2:
            raise ValidationError('Passwords do not match.', code='passwords_do_not_match')
        return self.cleaned_data

    def save(self, commit=True):
        user = self.instance
        user.set_password(self.cleaned_data.get('password'))
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ['password', 'password_confirm', 'old_password']