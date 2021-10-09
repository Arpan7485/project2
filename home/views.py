from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from webapp import settings
from .tokens import generate_token
from django.core.mail import EmailMessage, send_mail


# Create your views here.
def Home(request):
    return render(request, "home/index.html")


def Signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        address = request.POST['address']

        if User.objects.filter(username=username):
            messages.error(request, "username already exists")
            return redirect('Home')
        if User.objects.filter(email=email):
            messages.error(request, "email already exists")
            return redirect('Home')
        if pass1 != pass2:
            messages.error(request, "passwords did't match")
            return redirect('Home')
        if username is None or email is None or pass1 is None or address is None:
            return redirect('Home')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.name = username
        myuser.email = email
        myuser.pass1 = pass1
        myuser.is_active = False
        myuser.save()
        messages.success(request,
                         "account created successfully. we've sent you a confirmation email, please confirm it to activate your account")

        subject = "Welcome!!"
        message = "hello" + myuser.username + "!!\n" + "please confirm your email address in order to activate your account\n please click the below link to activate your account\n"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        current_site = get_current_site(request)
        email_subject = "confirm your email @ the website!!"
        message2 = render_to_string('home/email_confirmation.html', {
            'name': myuser.username,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('Signin')

    return render(request, "home/signup.html")


def Signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)
        if user is not None:
            login(request, user)
            username = user.username
            return render(request, "home/welcome.html", {'username': username})
        else:
            messages.error(request, "bad credentials")
            return redirect('Home')
    return render(request, "home/signin.html")


def Signout(request):
    logout(request)
    messages.success(request, "logged out successfully")
    return redirect('Home')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExists):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('Home')
    else:
        return render(request, 'home/activation_failed.html')
