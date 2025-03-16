from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="اسم المنتج", blank=True, null=True, default="منتج بدون اسم")
    description = models.TextField(verbose_name="الوصف", blank=True, null=True)
    color = models.CharField(max_length=50, verbose_name="اللون", blank=True, null=True)
    category = models.CharField(max_length=100,null=True, blank=True, verbose_name="التصنيف")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر", default=0.00)
    image = models.ImageField(upload_to='products/', default='default.jpg', verbose_name="صورة المنتج", blank=True, null=True)

    def __str__(self):
        return self.name
