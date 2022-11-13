
from django.urls import path
from .views import *


urlpatterns = [
    path('group/<str:group_name>', socket,name="group"),
    path('notification', notification,name="notification"),
    path('chat/<str:contact>',personal,name="chat"),
    path('groups', groups,name="groups"),
    path('contacts', contacts,name="contacts"),
    path('signup',signup,name="handlesignup"),
    path('login',handlelogin,name="login"),
    path('logout',handlelogout,name="handlelogout"),
    path('creategroup',create_group,name='creategroup'),
    path('',home),
    
] 
