
from django.urls import re_path
from . import consumers  

websocket_urlpatterns = [
    re_path(r'ws/order_tracking/(?P<order_id>\d+)/$', consumers.TrackingConsumer.as_asgi()),
]
