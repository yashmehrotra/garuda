from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('garuda.views',
    # Examples:
    # url(r'^$', 'garuda.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^about/','about'),
    url(r'^$','login_page'),
    url(r'^test/','test'),
    url(r'^signup/','signup'),
    url(r'^signupuser/','signupuser'),
    url(r'^post_tweet/','post_tweet'),
    url(r'^add_follower/','add_follower'),
    url(r'^follow/','follow'),
    url(r'^all/','view_all_users'),
    url(r'^followers/','get_followers'),
    url(r'^following/','get_following'),
    url(r'^mytweets/','my_tweets'),
    url(r'^user/(?P<user_name>\w+)','user_page'),
    url(r'^search/(?P<search_term>\w+)','search'),
    url(r'^login/','login_page'),
    url(r'^loginuser/','login_user'),
    url(r'^home/','home_page'),
    url(r'^remove_following/','remove_following'),
    url(r'^delete_user/','delete_user'),
    url(r'^dosearch/','dosearch'),
    url(r'^logout/','logout'),
    url(r'^dbms/','dbms'), # For Project Purposes
    url(r'^admin/', include(admin.site.urls)),
)
