from django.conf.urls import url

from core.views import UsersListView, UserCreateView, UserDetailView, UserDeleteView, UserUpdateView, UserExportView, \
    UserImportView

urlpatterns = [
    url(r'^$', UsersListView.as_view(), name='users_list'),
    url(r'^create/$', UserCreateView.as_view(), name='create_user'),
    url(r'^(?P<pk>\d+)/$', UserDetailView.as_view(), name='user_detail'),
    url(r'^(?P<pk>\d+)/update/$', UserUpdateView.as_view(), name='update_user'),
    url(r'^(?P<pk>\d+)/delete/$', UserDeleteView.as_view(), name='delete_user'),
    url(r'^export/$', UserExportView.as_view(), name='users_export'),
    url(r'^import/$', UserImportView.as_view(), name='users_import'),
]