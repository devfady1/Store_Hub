from django.urls import re_path
from pages.consumers import TrackingConsumer  

websocket_urlpatterns = [
    re_path(r'ws/order_tracking/(?P<order_id>\d+)/$', TrackingConsumer.as_asgi()),
]
