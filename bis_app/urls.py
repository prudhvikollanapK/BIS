
from django.urls import path
from .views import UserBlockedDomainView, StartContainerView, StopContainerView,ContainerLogsView

urlpatterns = [
    path('users/<int:user_id>/blocked-domains/', UserBlockedDomainView.as_view(), name='user-blocked-domains'),
    path('users/<int:user_id>/blocked-domains/<int:domain_id>/', UserBlockedDomainView.as_view(), name='delete-user-domain'),
    path('users/<int:user_id>/start-container/', StartContainerView.as_view(), name='start-container'),
    path('containers/<str:container_id>/stop/', StopContainerView.as_view(), name='stop-container'),
    path('containers/<str:container_id>/logs/', ContainerLogsView.as_view(), name='container-logs'),

]
