from django.conf.urls import patterns, url

from tools import views

urlpatterns = patterns('',
    url(r'^errors/$', views.errors),
)

