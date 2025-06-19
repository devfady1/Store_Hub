from django.urls import path, include
from . import views
from .views import *





urlpatterns = [
    path('', views.custom_redirect_view, name='root'),
    path('custom-redirect/', views.custom_redirect_view, name='custom_redirect'),
    path('select-role/', select_role, name='select_role'),
    path('index/', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account, name='account'),
    path('allproducts/', views.allproducts, name='allproducts'),
    path('search-products/', views.search_products, name='search_products'),
    path('product/<int:pk>/', views.product, name='product'),
    path('rate/<int:product_id>/', views.rate_product, name='rate_product'),
    path('product/<int:product_id>/add_comment/', views.add_comment, name='add_comment'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('toggle-like/<int:product_id>/', toggle_like, name='toggle_like'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<str:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('update-cart/', update_cart, name='update_cart'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('add_product/', views.add_product, name='add_product'),
    path('products/', ProductManagement, name='product-management'),
    path('products/<int:id>/', UpdateProduct.as_view(), name='update-product'),
    path('products/<int:id>/delete/', DeleteProduct.as_view(), name='delete-product'),
    path('place_order/', views.place_order, name='place_order'),
    path('order_success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/', views.order_details, name='order_details'),
    path('delivery-orders/', views.delivery_order_view, name='delivery_orders'),
    path('delivery/orders/available/', views.available_order_view, name='available_orders'),
    path('delivery/orders/assign/<int:order_id>/', views.assign_order, name='assign_order'),
    path('live-location/<int:order_id>/', views.live_location_view, name='live_location'),
    path('orderss/<int:order_id>/', order_detail, name='accept_order'),
    path('orders/<int:order_id>/update-status/', update_order_status, name='update_order_status'),
    path('delivery/orders/<int:order_id>/details/', views.delivery_order_detail_view, name='delivery_order_detail'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('api/wallet/', views.wallet_summary, name='wallet_summary'),
    ]
