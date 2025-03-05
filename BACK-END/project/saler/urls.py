from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path("saler/", views.add_product,name="saler.urls"),
]