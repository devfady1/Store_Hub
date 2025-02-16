from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# تسجيل نموذج User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "User Profiles"
    
    

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = "Created At"
    readonly_fields = ('get_created_at',) 
    



class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,) 
    
    list_display = ('username', 'email', 'get_role', 'get_phone_number', 'get_created_at', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'userprofile__role')  
    search_fields = ('username', 'email', 'userprofile__phone_number')


    def get_role(self, obj):
        return obj.userprofile.role
    get_role.short_description = "Role"

    def get_phone_number(self, obj):
        return obj.userprofile.phone_number
    get_phone_number.short_description = "Phone Number"

    def get_created_at(self, obj):
        return obj.userprofile.created_at
    get_created_at.short_description = "Created At"

    actions = ['make_delivery_agent', 'make_saler']

    @admin.action(description="Mark selected users as Delivery Agent")
    def make_delivery_agent(self, request, queryset):
        for user in queryset:
            if hasattr(user, 'userprofile'):
                user.userprofile.role = 'delivery_agent'
                user.userprofile.save()
                user.save()

    @admin.action(description="Mark selected users as Saler")
    def make_saler(self, request, queryset):
        for user in queryset:
            if hasattr(user, 'userprofile'):
                user.userprofile.role = 'saler'
                user.userprofile.save()
                user.save()

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)



# تسجيل نموذج Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'color', 'rating', 'image', 'total_likes', 'category')  # الحقول المعروضة في القائمة
    search_fields = ('name', 'color')  # إمكانية البحث
    list_display_links = ['name']  # الروابط القابلة للنقر
    list_filter = ('rating', 'color')  # الفلاتر
    readonly_fields = ('total_likes',)  # حقل للقراءة فقط

    # دالة علشان نحسب عدد اللايكات
    def total_likes(self, obj):
        return obj.likes.count()
    total_likes.short_description = 'Total Likes'  # عنوان العمود في الـ Admin


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)



# تسجيل نموذج Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'Product', 'Customer', 'Quantity', 'Status', 'OrderDate')  # الحقول المعروضة في القائمة
    list_filter = ('Status', 'OrderDate')  
    search_fields = ('Product__name', 'Customer__username')
    list_display_links = ('Product',)
    readonly_fields = ('OrderDate',)  # حقل للقراءة فقط

    # Action لتغيير حالة الطلبات
    actions = ['mark_as_completed']

    @admin.action(description="Mark selected orders as Completed")
    def mark_as_completed(self, request, queryset):
        queryset.update(Status='Completed')

# تسجيل نموذج Report
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'ReportType', 'GeneratedBy', 'GeneratedDate')  # الحقول المعروضة في القائمة
    list_filter = ('ReportType', 'GeneratedDate')  # الفلاتر
    search_fields = ('ReportType', 'GeneratedBy__username')  # إمكانية البحث
    readonly_fields = ('GeneratedDate',)  # حقل للقراءة فقط

# تسجيل نموذج DeliveryAssignment
@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'Order', 'DeliveryAgent', 'Status', 'AssignedDate')  # الحقول المعروضة في القائمة
    list_filter = ('Status', 'AssignedDate')  # الفلاتر
    search_fields = ('Order__id', 'DeliveryAgent__username')  # إمكانية البحث
    readonly_fields = ('AssignedDate',)  # حقل للقراءة فقط

    # Action لتغيير حالة التعيين
    actions = ['mark_as_delivered']

    @admin.action(description="Mark selected assignments as Delivered")
    def mark_as_delivered(self, request, queryset):
        queryset.update(Status='Delivered')

@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'start_date', 'end_date', 'old_price', 'new_price', 'rating')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'phone', 'message')



# إعدادات عامة للـ Admin
admin.site.site_header = 'STOREHUB'
admin.site.site_title = "STOREHUB"
admin.site.index_title = "Welcome to STOREHUB Admin Panel"
