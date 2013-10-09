from django.conf.urls import patterns, include, url

from stats import views

urlpatterns = patterns('',
    url(r'^$', views.index),
)
