from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
#from readline import get_current_history_length
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .forms import *
from django.template.loader import render_to_string
from django.http import HttpResponse
from .token import account_activation_token
from django.utils.encoding import force_bytes
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import Profile
from .forms import NewsletterForm
from .models import NewsletterSubscriber

# Create your views here.

""" @login_required
def avatar(request):
    user = User.objects.get(username=request.user)
    avatar = Profile.objects.filter(user=user)
    context = {
        'avatar': avatar,
    }
    return context """

""" def avatar(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        avatar = Profile.objects.filter(user=user)
        context = {
            "avatar": avatar,
        }
        return context
    else:
        return {
            'NotLoggedIn': User.objects.none()
        }
 """
""" @login_required
def avatar(request):
    user = request.user
    avatar = Profile.objects.filter(user=user)
    context = {
        'avatar': avatar,
    }
    return render(request, 'template_name.html', context) """

def avatar(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        avatar = Profile.objects.filter(user=user)
        context = {
            "avatar": avatar,
        }
        return context
    else:
        return {
            'NotLoggedIn': User.objects.none()
        }


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'section':'profile'}
    ) 


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)

        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=request.user.profile)

        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

    return render(request,
                  'accounts/update.html',
                  {'user_form': user_form, 'profile_form': profile_form})

""" @login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
    return render(request,
                  'accounts/update.html',
                  {'user_form': user_form}) """

@login_required
def delete_user(request):

    if request.method == 'POST':
        user = User.objects.get(username=request.user)
        user.is_active = False
        user.save()
        return redirect('accounts:login')

    return render(request, 'accounts/delete.html')


def accounts_register(request):
    if request.method == 'POST':
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.email = registerForm.cleaned_data['email']
            user.set_password(registerForm.cleaned_data['password'])
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate your Account'
            message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message)
            return render(request, 'registration/register_success.html', {'user': user})
    else:
        registerForm = RegistrationForm()
    return render(request, 'registration/register.html', {'form': registerForm})

""" def accounts_register(request):
    if request.method == 'POST':
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.email = registerForm.cleaned_data['email']
            user.set_password(registerForm.cleaned_data['password'])
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate your Account'
            message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_b64encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message)
            return HttpResponse('please check your email for account activation')
    else:
        registerForm = RegistrationForm()
    return render(request, 'registration/register.html', {'form': registerForm}) """


def activate(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('login')
    else:
        return render(request, 'registration/activation_invalid.html')
    

""" def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
           form.save()
                # Traitez les données du formulaire ici, par exemple, enregistrer l'email dans votre base de données ou envoyer un email de confirmation.
                #email = form.cleaned_data['email']
                # Code pour enregistrer l'email dans la base de données ou envoyer un email de confirmation
                 # Rediriger l'utilisateur vers une page de confirmation
        return render(request, 'registration/subscribe.html')
    else:
        form = NewsletterForm()
    return render(request, 'registration/subscribe.html', {'form': form}) """

""" 
def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']  # Si vous avez ajouté un champ 'name' dans le formulaire

            # Enregistrement dans la base de données
            subscriber = NewsletterSubscriber(email=email, name=name)
            subscriber.save()

            # Redirection vers une page de confirmation ou autre
            return render(request, 'registration/subscribe_success.html')
    else:
        form = NewsletterForm()
        return render(request, 'registration/subscribe.html', {'form': form}) """



def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            name = form.cleaned_data.get('name', '').strip()
            NewsletterSubscriber.objects.get_or_create(email=email, defaults={'name': name})
            return render(request, 'registration/subscribe_success.html', {'message': 'Vous êtes bien inscrit à la newsletter.'})
    else:
        form = NewsletterForm()

    return render(request, 'registration/subscribe.html', {'form': form})
