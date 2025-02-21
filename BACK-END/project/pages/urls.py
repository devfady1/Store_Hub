from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path('index/' ,views.index, name='index'),
    path('about/' ,views.about, name='about'),
    path('login/' ,views.user_login, name='login'),
    path('register/' ,views.register, name='register'),
    path('contact/' ,views.contact_view, name='contact'),
    path('allproducts/' ,views.allproducts, name='allproducts'),
    path('wishlist/' ,views.wishlist, name='wishlist'),
    path('toggle-like/<int:product_id>/', toggle_like, name='toggle_like'),
    path('product/<int:pk>/', views.product, name='product'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path("remove_from_cart/<str:product_id>/", remove_from_cart, name="remove_from_cart"),
    path("update-cart/", update_cart, name="update_cart"),
    path("logout/", views.logout_view, name="logout"),
]