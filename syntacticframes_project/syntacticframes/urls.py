from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from syntacticframes import views

urlpatterns = patterns('',
    # admin:
    url(r'^admin/', include(admin.site.urls)),

    # Main page, levin class, class
    url(r'^$', views.index, name='index'),
    url(r'^class/(?P<class_number>\d+)/$', views.classe),
    url(r'^vn_class/(?P<class_name>\w+-[\d\.]+)/$', views.vn_class),  # for AJAX

    # Stats
    url(r'^stats/', include('stats.urls')),

    # Auth
    url(r'^login/$', views.login),

    # JS API
    url(r'^update/$', views.update),
    url(r'^remove/$', views.remove),
    url(r'^add/$', views.add),
    url(r'^show/$', views.show),
    url(r'^validate/$', views.validate),
    url(r'^invalidate/$', views.invalidate),

    # Search
    url(r'^search/$', views.search),

)
