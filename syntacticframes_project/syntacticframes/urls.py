from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from syntacticframes import views

urlpatterns = patterns('',
    #url(r'^$', TemplateView.as_view(template_name='base.html')),
    url(r'^$', views.index, name='index'),
    url(r'^class/(?P<class_number>\d+)/$', views.classe, name='index'),
    url(r'^vn_class/(?P<class_name>\w+-[\d\.]+)/$', views.vn_class, name='index'),

    # JS API
    url(r'^update/$', views.update),
    url(r'^remove/$', views.remove),
    url(r'^add/$', views.add),

    # Examples:
    # url(r'^$', 'syntacticframes.views.home', name='home'),
    # url(r'^syntacticframes/', include('syntacticframes.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
