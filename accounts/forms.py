from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, PasswordChangeForm
from accounts.models import Profile, NewsletterSubscriber


#https://docs.djangoproject.com/en/3.0/topics/auth/default/
#https://docs.djangoproject.com/en/3.0/topics/forms/


class PwdChangeForm(PasswordChangeForm):

    old_password = forms.CharField(
        label='Old Password', widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'Old Password', 'id': 'form-oldpass'}))
    new_password1 = forms.CharField(
        label='New password', widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'New Password', 'id': 'form-newpass'}))
    new_password2 = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'New Password', 'id': 'form-new-pass2'}))



class PwdResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New password', widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'New Password', 'id': 'form-newpass'}))
    new_password2 = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'New Password', 'id': 'form-new-pass2'}))



class PwdResetForm(PasswordResetForm):

    email = forms.EmailField(max_length=250, widget=forms.TextInput(
        attrs={'class': 'form-control mb-3', 'placeholder': 'Email', 'id':'form-email'}
   ))
    def clean_email(self):
        email = self.cleaned_data['email']
        test = User.objects.filter(email=email)
        if not test:
            raise forms.ValidationError(
                'Unfortunatley we can not find that email address')
        return email



class UserLoginForm( AuthenticationForm):
    
    username = forms.CharField(widget = forms.TextInput(
        attrs={ 'class':'form-control  mb-4', 'placeholder': 'Username', 'id':'login-username'}))
    
    password = forms.CharField(widget = forms.PasswordInput(
        attrs={ 'class':'form-control', 'placeholder': 'Password', 'id':'login-password'}))
    
#la classe  d'enregistrement
    
class RegistrationForm(forms.ModelForm):

    username = forms.CharField(
        label='Enter Username', min_length=4, max_length=50, help_text='Required')
    email = forms.EmailField(max_length=100, help_text='Required', error_messages={
        'required': 'Sorry, you will need an email'})
    password = forms.CharField(label='Password', widget=forms.PasswordInput, min_length=8)
    password2 = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("Username already exists")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and (len(password) < 8 or not any(char.isdigit() for char in password)):
            raise forms.ValidationError('Le mot de passe doit contenir au moins 8 caractères et un chiffre.')
        return password

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords do not match.')
        return cd['password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control mb-3', 'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control mb-3', 'placeholder': 'E-mail', 'name': 'email', 'id': 'id_email'})
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Repeat Password'})
        
class UserEditForm(forms.ModelForm):

    first_name = forms.CharField(
        label='Firstname', min_length=4, max_length=50, widget=forms.TextInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'Firstname', 'id': 'form-firstname'}))

    last_name = forms.CharField(
        label='Lastname', min_length=4, max_length=50, widget=forms.TextInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'Lastname', 'id': 'form-lastname'}))

    email = forms.EmailField(
        max_length=200, widget=forms.TextInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'Old Password', 'id': 'form-email'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Please use another Email, that is already taken')
        return email
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['last_name'].required = False
        self.fields['email'].required = False


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio','avatar']

        widgets = {
            'bio': forms.Textarea(attrs={'class':'form-control', 'rows':'5'}),
        }



""" class NewsletterForm(forms.Form):
    email = forms.EmailField(
        max_length=200, widget=forms.TextInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'Adresse e-mail', 'id': 'form-newsletter'}))
    
    name = forms.CharField(
        max_length=200, widget=forms.TextInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'Nom', 'id': 'form-name'}))

    class Meta:
        model = User
        fields = ('email', 'name')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Please use another Email, that is already taken')
        return email """



class NewsletterForm(forms.Form):
    email = forms.EmailField(
        max_length=200, 
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Adresse e-mail', 'id': 'form-newsletter'})
    )
    
    name = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Nom', 'id': 'form-name'})
    )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists() or NewsletterSubscriber.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Cette adresse e-mail est déjà utilisée. Veuillez en choisir une autre.')
        return email