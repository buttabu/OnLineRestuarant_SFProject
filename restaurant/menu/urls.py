from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search.*', views.search, name='search'),
    url(r'^(?P<cuisine>\w+)/$',views.cuisine,name='cuisine'),
    url(r'^(?P<cuisine>\w+)/(?P<food>\w+)/$', views.food, name='food'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
