from django.conf.urls import patterns, url

from ladlindex import views

urlpatterns = patterns('',
    url(r'^$', views.index),
)
