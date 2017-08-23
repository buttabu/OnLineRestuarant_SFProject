"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from . import settings
from menu import views as menuViews

urlpatterns = [
    url(r'',include('users.urls', namespace='users')),
    url(r'^menu/', include('menu.urls', namespace='menu')),
    url(r'^admin/', admin.site.urls),
    url(r'^cart/', menuViews.cart, name='cart'),
    url(r'^checkout/', menuViews.checkout, name='checkout'),
    url(r'^process/', menuViews.renderMap, name='process'),
    url(r'^userrequest/(?P<param>\w*)', menuViews.handleRequest, name='handleRequest'),
    url(r'^profile/(?P<id>\d*)', menuViews.profile, name = 'profile'),
    url(r'^resolution/(?P<param>\w*)', menuViews.resolution, name = 'resolution'),
    url(r'^useraccounts/(?P<param>\w*)', menuViews.userAccounts, name = 'users'),
    url(r'^deliveryFeedback/(?P<param>\d*)', menuViews.deliveryFeedback, name = 'deliveryFeedback')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
