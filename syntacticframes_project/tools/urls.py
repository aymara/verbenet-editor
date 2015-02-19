from django.conf.urls import patterns, url

from tools import views

urlpatterns = patterns('',
    url(r'^errors/$', views.errors),
    url(r'^distributions/$', views.distributions),
    url(r'^emptytranslations/$', views.emptytranslations),
    url(r'^verbvalidationstatus/$', views.verbvalidationstatus),
)
