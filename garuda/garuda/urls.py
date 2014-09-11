from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('garuda.views',
    # Examples:
    # url(r'^$', 'garuda.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^about/','about'),
    url(r'^testdb/','testdb'),
    url(r'^admin/', include(admin.site.urls)),
)
