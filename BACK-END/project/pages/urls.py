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
    path('checkout/', views.checkout, name='checkout'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path("remove_from_cart/<str:product_id>/", remove_from_cart, name="remove_from_cart"),
    path("update-cart/", update_cart, name="update_cart"),
    path("logout/", views.logout_view, name="logout"),
    path("account/", views.account, name="account"),
    path("add_product/", views.add_product, name="add_product"),
    path('products/', ProductManagement, name='product-management'),
    path('products/<int:id>/', UpdateProduct.as_view(), name='update-product'),
    path('products/<int:id>/delete/', DeleteProduct.as_view(), name='delete-product'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('delivery-orders/', views.delivery_order_view, name='delivery_orders'),
    path('place_order/', views.place_order, name='place_order'),
    path('order_success/', views.order_success, name='order_success'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('orders/<int:order_id>/', views.order_details, name='order_detail'),
    path('rate/<int:product_id>/', views.rate_product, name='rate_product'),




]