from django.conf.urls.defaults import *

urlpatterns = patterns('myproject.crime.views',  # Common Prefix

    # MAIN PAGE
    url(r'^$', 'index'),
    # MAP PAGE
    url(r'^map/$', 'index', {'map': True}),
    # SEARCH PAGE
    url(r'^search/$', 'search_page'),
    # INCIDENT PAGE
    url(r'^(?P<Incident_id>\d+)/(?P<Incident_inc_slug>[-\w]+)/$', 'incident_page'),
    # VICTIMS PAGE
    url(r'^victims/$', 'victims_page'),
    # SUSPECTS PAGE
    url(r'^suspects/$', 'suspects_page'),
)
