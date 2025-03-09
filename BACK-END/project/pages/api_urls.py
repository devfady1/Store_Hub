from django.urls import path
from .views import *

urlpatterns = [
  

    # ✅ تعديل المنتج
    path('products/<int:id>/', UpdateProduct.as_view(), name='update-product'),

    # ✅ حذف المنتج
    path('products/<int:id>/delete/', DeleteProduct.as_view(), name='delete-product'),
]
