from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('garuda.views',
    # Examples:
    # url(r'^$', 'garuda.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^about/','about'),
    url(r'^test/','test'),
    url(r'^signup/','signup'),
    url(r'^signupuser/','signupuser'),
    url(r'^post_tweet/','post_tweet'),
    url(r'^login/','login_page'),
    url(r'^loginuser/','login_user'),
    url(r'^home/','home_page'),
    url(r'^logout/','logout'),
    url(r'^dbms/','dbms'), # For Project Purposes
    url(r'^admin/', include(admin.site.urls)),
)
