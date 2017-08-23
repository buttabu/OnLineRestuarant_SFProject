from django.conf.urls import url, include
from django.contrib import admin
from . import views
from menu.views import index as homeView
from django.urls import reverse
from menu.views import profile

urlpatterns = [
    url(r'^apply/$', views.register,{'src':'staff'}, name='register'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.signin, name="login"),
    url(r'^logout/$', views.signout, name = 'logout'),
    url(r'^$', homeView, name='homeView' )
]
