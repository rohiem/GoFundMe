from django.urls import path
from .views import*
from django.contrib.auth.views import LoginView,LogoutView

app_name = 'core'
urlpatterns = [
    path("signup/",SignUp,name="signup"),
    path("",home,name="home"),
    path("login/",LoginView.as_view(template_name="login.html"),name="login"),
    path("logout/",LogoutView.as_view(template_name="logout.html"),name="logout"),
    path("petitions/<int:pk>",petition_detail,name="petition_detail"),
    path("like/<int:pk>",follow,name="follow_petition"),
    path("create/",PetitionCreation.as_view(),name="create"),
    path("petitions/<int:pk>/update/",PetitionUpdate.as_view(),name="update"),
    path("donate/<int:pk>",petition_donation,name="donate"),
    path('charge/<int:pk>', charge, name="charge"),
    path('success/<str:args>/<int:pk>',successMsg, name="success"),
    path("profiles/<slug:slug>/update/",update_profile_view,name="update_profile"),
    path("profiles/<slug:slug>",profile_view,name="profile"),


]