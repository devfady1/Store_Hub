from django.db import models
from django.contrib.auth.models import *


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('delivery_agent', 'Delivery Agent'),
        ('saler', 'Saler'),
        ('admin', 'Admin'), 
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # ارتباط كل مستخدم ببروفايل خاص بيه
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        إذا كان المستخدم أدمن، يتم جعله سوبر يوزر تلقائيًا.
        """
        print(f"Saving UserProfile: User={self.user.username}, Role={self.role}, Phone={self.phone_number}")

        if self.role == 'admin':
            self.user.is_superuser = True
            self.user.is_staff = True
        else:
            self.user.is_superuser = False
            self.user.is_staff = False

        self.user.save()  
        super().save(*args, **kwargs)  

    def __str__(self):
        return f"{self.user.username} - {self.role}"

#نموذج Product
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="التصنيف")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "تصنيفات"


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="اسم المنتج", blank=True, null=True, default="منتج بدون اسم")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر", default=0.00)
    description = models.TextField(verbose_name="الوصف", blank=True, null=True)
    quantity = models.PositiveIntegerField(verbose_name="الكمية", default=0)
    saler = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    image = models.ImageField(upload_to='products/', default='default.jpg', verbose_name="صورة المنتج", blank=True, null=True,max_length=255)
    color = models.CharField(max_length=50, verbose_name="اللون", blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='product_likes', blank=True, verbose_name="اللايكات")
    color = models.CharField(max_length=50, choices=[
        ('red', 'Red'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('blue', 'Blue'),
        ('orangered', 'OrangeRed'),
        ('black', 'Black')],
        default="black", verbose_name="اللون")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="التصنيف")
    rating = models.FloatField(default=0, verbose_name="التقييم")

    def __str__(self):
        return self.name

    def total_likes(self):
        return self.likes.count()

    def update_rating(self, new_rating):
        self.rating = new_rating
        self.save()

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "منتجات"


# نموذج Order
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    Product = models.ForeignKey(Product, verbose_name="المنتج", on_delete=models.CASCADE)
    Customer = models.ForeignKey( User,verbose_name="العميل" ,on_delete=models.CASCADE, related_name='orders')
    Quantity = models.IntegerField(verbose_name="كمية", default=1)
    OrderDate = models.DateTimeField(verbose_name="تاريخ الطلب" ,auto_now_add=True)
    Status = models.CharField( verbose_name="حالة الطلب" ,max_length=20, choices=STATUS_CHOICES, default='Pending')
    DeliveryAgent = models.ForeignKey(User, verbose_name="وكيل التوصيل", on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')

    def _str_(self):
        return f"Order {self.id} - {self.Status}"
    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "طلبات"

# نموذج Report
class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('Sales', 'Sales'),
        ('Inventory', 'Inventory'),
        ('Financial', 'Financial'),
    ]
    ReportType = models.CharField(max_length=20, verbose_name="نوع التقرير",choices=REPORT_TYPE_CHOICES)
    GeneratedBy = models.ForeignKey(User,verbose_name="المستخدم" ,on_delete=models.CASCADE, related_name='reports')
    GeneratedDate = models.DateTimeField(auto_now_add=True)
    ReportData = models.TextField(verbose_name="بيانات التقرير")

    def _str_(self):
        return f"Report {self.id} - {self.ReportType}"

    class Meta:
        verbose_name = "تقرير"
        verbose_name_plural = "تقارير"

# نموذج DeliveryAssignment
class DeliveryAssignment(models.Model):
    STATUS_CHOICES = [
        ('Assigned', 'Assigned'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    Order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='assignments')
    DeliveryAgent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    AssignedDate = models.DateTimeField(auto_now_add=True)
    Status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Assigned')

    def _str_(self):
        return f"Assignment {self.id} - {self.Status}"

    class Meta:
        verbose_name = "تعيين التوصيل"
        verbose_name_plural = "تعيينات التوصيل"


#نموذج لعمل FLASH SALES لاستخدامها في الصفحة الرئيسية
class FlashSale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = "فلاش سيل"
        verbose_name_plural = "فلاش سيلات"

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

    class Meta:
        verbose_name = "رسالة"
        verbose_name_plural = "رسائل"

