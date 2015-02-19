from django.conf.urls import patterns, url

from indexes import views

urlpatterns = patterns('',
    url(r'^ladl/$', views.ladl),
    url(r'^members/$', views.members),
    url(r'^members/(?P<letter>\w)/$', views.members_letter),
    url(r'^hierarchy/$', views.hierarchy),
)
