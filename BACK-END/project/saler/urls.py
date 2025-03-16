from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path("saleaar/", views.add_product,name="saler.urls"),
]