
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.Home,name="Home"),
    path('signup',views.Signup,name="Signup"),
    path('signin',views.Signin,name="Signin"),
    path('signout',views.Signout,name="Signout"),
    path('activate/<uidb64>/<token>',views.activate,name="activate"),
]
