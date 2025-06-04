from django.shortcuts import render , redirect
from .models import *
from django.db.models import Count , Max 
from .forms import *
from .forms import ProductForm
from django.contrib.auth.decorators import user_passes_test 
from django.contrib import messages 
from django.contrib.auth import login, authenticate ,logout
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib.auth.decorators import *
from django.shortcuts import get_object_or_404
from decimal import Decimal
import json
from .models import Coupon
from .models import Order
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.parsers import MultiPartParser, FormParser                
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from random import sample
from .sentiment_utils import analyze_sentiment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from .models import Order, UserProfile
from geopy.distance import geodesic
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from geopy.distance import geodesic
from .models import Order, UserProfile 


def is_seler(user):
    return user.userprofile.role == 'saler'

def is_delevry(user):
    return user.userprofile.role == 'delivery_agent'



@login_required
def index(request):
    categories = Category.objects.all()
    top_products = Product.objects.filter(name="banner").annotate(likes_count=Count('likes__id')).order_by('-likes_count')[:5]
    flash_sales = FlashSale.objects.all()
    max_time = flash_sales.aggregate(max_end_time=Max('end_date'))['max_end_time'] if flash_sales else None
    all_products = list(Product.objects.all())
    random_products = sample(all_products, min(len(all_products), 8))  #
    username = request.user.username 
    liked_products = []
    if request.user.is_authenticated:
        liked_products = request.user.product_likes.values_list('id', flat=True)

    return render(request, 'pages/index.html', {
        'categories': categories,
        'products': top_products,
        'flash_sales': flash_sales,
        'max_time': max_time,
        'username': username,
        'random_products': random_products,
        'liked_products': liked_products,  
    })


def logout_view(request):
    logout(request)
    return redirect("/login")
    



@login_required
def wishlist(request):
    liked_products = Product.objects.filter(likes=request.user).select_related("saler")
    random_products = Product.objects.exclude(likes=request.user).exclude(name="banner").order_by('?')[:4]

    # حساب old_price لكل منتج في liked_products
    for product in liked_products:
        product.old_price = Decimal(product.price) * Decimal(1.35)  # تحويل السعر إلى Decimal

    # حساب old_price لكل منتج في random_products
    for product in random_products:
        product.old_price = Decimal(product.price) * Decimal(1.35)  # تحويل السعر إلى Decimal

    # إضافة قائمة النجوم لكل منتج في random_products
    for product in random_products:
        product.star_list = range(int(round(product.rating)))  # تخصيص النجوم المملوءة

    return render(request, 'pages/wishlist.html', {
        'liked_products': liked_products,
        'random_products': random_products
    })


@login_required
@csrf_exempt
def toggle_like(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user in product.likes.all():
        product.likes.remove(request.user)  
        liked = False
    else:
        product.likes.add(request.user)  
        liked = True


    product.star_list = range(int(round(product.rating)))

    product.save()

    return JsonResponse({'liked': liked, 'likes_count': product.likes.count()})

def about(request):
    return render(request, 'pages/about.html')


def product(request, pk):
    product = Product.objects.get(id=pk)
    rating = getattr(product, 'rating', 0)
    full_stars = int(rating)
    empty_stars = 5 - full_stars  


    related_items = Product.objects.filter(category=product.category).exclude(id=pk)[:4]

    # تجهيز بيانات النجوم للمنتجات المشابهة
    for item in related_items:
        item.star_list = range(int(item.rating))  # عدد النجوم الممتلئة
        item.empty_stars = range(5 - int(item.rating))  # عدد النجوم الفارغة

    return render(request, 'pages/onepro.html', {
        'product': product,
        'rating': rating,
        'star_list': range(full_stars),
        'empty_stars': range(empty_stars),
        'related_items': related_items
    })


@csrf_exempt
def user_login(request):
    if request.method == "POST":
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                messages.success(request, "تم تسجيل الدخول بنجاح!")
                return redirect('index')
            else:
                messages.error(request, "اسم المستخدم أو كلمة المرور غير صحيحة.")
        else:
            messages.error(request, "الرجاء تعبئة جميع الحقول بشكل صحيح.")
    else:
        form = CustomLoginForm()

    return render(request, 'pages/account/login.html', {'form': form})

@csrf_exempt
def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            phone_number = form.cleaned_data['phone_number']

            # التحقق من وجود اسم المستخدم
            if User.objects.filter(username=username).exists():
                messages.error(request, "اسم المستخدم هذا موجود بالفعل.")
                return redirect('register')

            # التحقق من وجود البريد الإلكتروني
            if User.objects.filter(email=email).exists():
                messages.error(request, "البريد الإلكتروني هذا مسجل بالفعل.")
                return redirect('register')

            # حفظ المستخدم وكلمة المرور
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()  # حفظ المستخدم في الداتابيز

            # إنشاء الـ UserProfile وربطه بالمستخدم
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.phone_number = phone_number
            profile.save()

            # تسجيل الدخول للمستخدم بعد إنشاء الحساب
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            # رسالة نجاح
            messages.success(request, "تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.")
            return redirect('index')  # إعادة التوجيه للصفحة الرئيسية بعد النجاح

        else:
            # في حالة وجود أخطاء في النموذج
            messages.error(request, "يرجى تصحيح الأخطاء المدخلة في النموذج.")
            print("Form Errors:", form.errors)

    else:
        form = SignUpForm()

    return render(request, 'pages/account/signUp.html', {'form': form})



@login_required
def account(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # التعامل مع رفع الصورة
        if 'profile_image' in request.FILES:
            profile_image = request.FILES.get('profile_image')
            if profile_image:
                profile.profile_image = profile_image
                profile.save()
                messages.success(request, "تم تحديث الصورة الشخصية بنجاح")
                return redirect('account')

        # التعامل مع تغيير كلمة المرور
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if current_password and new_password and confirm_password:
            if new_password != confirm_password:
                messages.error(request, "كلمة المرور الجديدة غير متطابقة")
            elif not user.check_password(current_password):
                messages.error(request, "كلمة المرور الحالية غير صحيحة")
            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, "تم تغيير كلمة المرور بنجاح")
                return redirect('account')

        # التعامل مع تحديث المعلومات الشخصية
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()

        # تحديث بيانات المستخدم مع التحقق من القيم الفارغة
        if first_name or last_name or email:
            user.first_name = first_name or user.first_name
            user.last_name = last_name or user.last_name
            user.email = email or user.email
            user.save()

        # تحديث بيانات البروفايل
        if address or phone:
            profile.address = address
            if phone:
                profile.phone_number = phone
            profile.save()

        messages.success(request, "تم تحديث البيانات بنجاح")
        return redirect('account')

    return render(request, 'pages/account/account.html', {
        'user': user,
        'profile': profile,
    })



def contact_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        
        return redirect('contact')

    return render(request, 'pages/contact.html')

@login_required
def allproducts(request):
    categories = Category.objects.all()
    colors = ['red', 'green', 'yellow', 'blue', 'orangered', 'black']


    products = Product.objects.all()
    selected_category = request.GET.get('category')
    selected_color = request.GET.get('color')

    filters = Q()
 
    if selected_category:
        
        filters &= Q(category__name=selected_category)

    if selected_color:
        filters &= Q(color=selected_color)

    if filters:
        products = products.filter(filters)

    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'colors': colors,
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'stars_range': range(5),
    }

    return render(request, 'pages/allproduct.html', context) 

    
@csrf_exempt
def remove_from_cart(request, product_id):
    if request.method == "POST":
        cart = request.session.get('cart', {})
        if product_id in cart:
            del cart[product_id]  
            request.session['cart'] = cart 
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "Product not found"})
    return JsonResponse({"success": False, "error": "Invalid request method"})



def add_to_cart(request):
    product_id = str(request.GET.get('product_id'))  
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if product_id in cart:
        cart[product_id]['quantity'] += 1
    else:
        cart[product_id] = {
            'name': product.name,
            'price': float(product.price),
            'image': product.image.url,
            'quantity': 1, 
        }

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({'status': 'success', 'cart': cart})

def update_cart(request):
    if request.method == "POST":
        try:
            cart = request.session.get("cart", {})
            data = json.loads(request.body)

            for product_id, new_quantity in data.items():
                if product_id in cart:
                    cart[product_id]["quantity"] = int(new_quantity)

            request.session["cart"] = cart  # تحديث الجلسة
            request.session.modified = True  # تأكيد حفظ التغييرات

            return JsonResponse({"status": "success", "cart": cart})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@login_required
def cart(request):
    cart = request.session.get('cart', {})
    total = 0

    for product_id, item in cart.items():
        item['subtotal'] = float(item['price']) * int(item['quantity'])  # حساب الـ subtotal
        total += item['subtotal']

    return render(request, 'pages/payment/cart.html', {'cart': cart, 'total': total})



def checkout(request):
    cart = request.session.get('cart', {})
    total = 0

    for product_id, item in cart.items():
        item['subtotal'] = float(item['price']) * int(item['quantity'])
        total += item['subtotal']

    return render(request, 'pages/payment/checkout.html', {'cart': cart, 'total': total})

@user_passes_test(is_seler)
def add_product(request):  
    if request.method == 'POST':  
        form = ProductForm(request.POST, request.FILES)  
        if form.is_valid():  
            product = form.save(commit=False)  
            product.saler = request.user  
            product.save()  
            return JsonResponse({'success': True})  
        else:  
            return JsonResponse({'success': False, 'errors': form.errors})  
    else:  
        form = ProductForm() 

    categories = Category.objects.all()  
    return render(request, 'pages/saler/saler.html', {'form': form, 'categories': categories})  



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from .models import Product
import json


from django.contrib.auth.decorators import login_required
def product_list(request):
    if request.user.is_authenticated:
        products = Product.objects.filter(saler=request.user)  # ✅ فلترة المنتجات على المستخدم الحالي
        products_list = [
            {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'color': product.color,
                'image': product.image.url if product.image else '',
            }
            for product in products
        ]
        return JsonResponse(products_list, safe=False)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

@login_required
def ProductManagement(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        products = Product.objects.filter(saler=request.user)
        products_list = [
            {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'color': product.color,
                'image': product.image.url if product.image else '',
            }
            for product in products
        ]
        print(products_list)  # ✅ تأكد إن الـ JSON صحيح
        return JsonResponse(products_list, safe=False)
    
    products = Product.objects.filter(saler=request.user)
    return render(request, 'pages/saler/ProductManagment.html', {'products': products})


class UpdateProduct(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]  

    def patch(self, request, id):
        product = get_object_or_404(Product, id=id)
        if product.saler != request.user:
            return Response({'error': 'You do not have permission to edit this product'}, status=403)
        try:

            product.name = request.data.get('name', product.name)
            product.price = request.data.get('price', product.price)
            product.color = request.data.get('color', product.color)

            if 'image' in request.FILES:
                product.image = request.FILES['image']

            product.save()
            return Response({'message': 'Product updated successfully!'})
        except Exception as e:
            print(f"Error updating product: {str(e)}")
            return Response({'error': f'Failed to update product: {str(e)}'}, status=400)

    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]  

    def patch(self, request, id):
        product = get_object_or_404(Product, id=id)
        if product.saler != request.user:
            return JsonResponse({'error': 'You do not have permission to edit this product'}, status=403)

        try:
            product.name = request.data.get('name', product.name)
            product.price = request.data.get('price', product.price)
            product.color = request.data.get('color', product.color)

            # ✅ تحديث الصورة (لو فيه صورة مرفوعة)
            if 'image' in request.FILES:
                product.image = request.FILES['image']

            product.save()

            # ✅ استجابة JSON منظمة
            return JsonResponse({
                'message': 'Product updated successfully!',
                'data': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'color': product.color,
                    'image': product.image.url if product.image else None,
                }
            })
        except Exception as e:
            print(f"❌ Error updating product: {str(e)}")  # سجل الخطأ
            return JsonResponse({'error': f'Failed to update product: {str(e)}'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteProduct(View):
    def delete(self, request, id):
        product = get_object_or_404(Product, id=id, saler=request.user)
        product.delete()
        return JsonResponse({'message': 'Product deleted successfully!'})



def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')  

        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            
            if coupon.valid_from <= timezone.now() <= coupon.valid_until:
                
                request.session['coupon_code'] = coupon_code
                request.session['discount_percentage'] = coupon.discount_percentage
                return redirect('cart')  
            else:
                return render(request, 'cart.html', {'error': 'الكوبون غير صالح !'})
        except Coupon.DoesNotExist:
            return render(request, 'cart.html', {'error': 'الكوبون غير موجود!'})
    return redirect('cart')

def cart_view(request):
    cart = get_cart_from_session(request) 
    coupon_code = request.session.get('coupon_code', None)
    discount_percentage = request.session.get('discount_percentage', 0)

    total_price = sum(item['subtotal'] for item in cart)  
    discount = (discount_percentage / 100) * total_price  
    final_price = total_price - discount  

    return render(request, 'cart.html', {
        'cart': cart,
        'total': total_price,
        'discount': discount,
        'final_price': final_price,
        'coupon_code': coupon_code
    })


def delivery_order_view(request):
    assignments = DeliveryAssignment.objects.filter(DeliveryAgent=request.user)
    context = {
        'assignments': assignments
    }
    return render(request, 'delivery agent/delivery_order.html', context)



def order_success(request):
    return render(request, 'pages/payment/order_success.html')



@login_required
def place_order(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        user = request.user

        if not cart:
            return redirect('cart')

        client_lat = request.POST.get('client_lat')
        client_lng = request.POST.get('client_lng')

        order = Order.objects.create(
            customer=user,
            status='pending',
            client_lat=client_lat,
            client_lng=client_lng
        )

        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity']
                )
            except Product.DoesNotExist:
                continue

        request.session['cart'] = {}
        return redirect('order_success')

    return redirect('cart')




def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    total_price = sum(item.product.price * item.quantity for item in items)

    delivery_agent_profile = None
    filled_stars = 0
    empty_stars = 5

    if order.delivery_agent:
        delivery_agent_profile = UserProfile.objects.filter(user=order.delivery_agent).first()
        if delivery_agent_profile and delivery_agent_profile.rating:
            filled_stars = int(round(delivery_agent_profile.rating))
            empty_stars = 5 - filled_stars

    seller_lat = None
    seller_lng = None
    if items:
        product = items[0].product
        seller_lat = product.seller_lat 
        seller_lng = product.seller_lng

    context = {
        'order': order,
        'items': items,
        'total_price': total_price,
        'delivery_agent_profile': delivery_agent_profile,
        'filled_stars': filled_stars,
        'empty_stars': empty_stars,
        'client_lat': order.client_lat,
        'client_lng': order.client_lng,
        'driver_lat': order.delivery_agent_lat,
        'driver_lng': order.delivery_agent_lng,
        'seller_lat': seller_lat,
        'seller_lng': seller_lng,
    }
    return render(request, 'delivery agent/Delivery Order Details.html', context)




def my_orders_view(request):
    user = request.user
    status_filter = request.GET.get('status')  

    orders = Order.objects.filter(customer=user).prefetch_related('items__product').order_by('-order_date')

    if status_filter and status_filter != 'all':
        orders = orders.filter(status=status_filter)

    for order in orders:
        total_price = sum(item.quantity * item.product.price for item in order.items.all())
        order.total_price = total_price

    context = {
        'orders': orders,
        'status_filter': status_filter or 'all',
    }
    return render(request, 'delivery agent/my_orders_view.html', context)



def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    return render(request, 'delivery agent/order_detail.html', {'order': order})


@login_required
def assign_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, delivery_agent__isnull=True)
    user_profile = get_object_or_404(UserProfile, user=request.user, role='delivery_agent')

    order.delivery_agent = request.user
    order.delivey_agent_lart = user_profile.lat
    order.delivery_agent_lng = user_profile.lng
    order.status = 'in_progress'
    order.save()

    return redirect('order_detail', order_id=order.id)

@login_required
def available_order_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user, role='delivery_agent')
    driver_location = (user_profile.lat, user_profile.lng)

    # Get all pending orders without a delivery agent
    available_orders = list(Order.objects.filter(
        status='pending',
        delivery_agent__isnull=True,
        client_lat__isnull=False,
        client_lng__isnull=False,
    ))

    if not available_orders:
        return render(request, 'delivery agent/no_orders.html')

    # Calculate distances and sort orders by proximity
    def order_distance(order):
        return geodesic(driver_location, (order.client_lat, order.client_lng)).km
    available_orders.sort(key=order_distance)

    # Filter out rejected orders
    rejected_order_ids = request.session.get('rejected_order_ids', [])
    available_orders = [o for o in available_orders if o.id not in rejected_order_ids]
    
    if not available_orders:
        return render(request, 'delivery agent/no_orders.html')
    
    # Get the closest orders
    closest_orders = available_orders[:2]

    if request.method == 'POST':
        action = request.POST.get('action')
        order_id = int(request.POST.get('order_id'))
        order = get_object_or_404(Order, id=order_id)

        if action == 'accept':
            order.delivery_agent = request.user
            order.delivery_agent_lat = user_profile.lat
            order.delivery_agent_lng = user_profile.lng
            order.status = 'accepted'
            order.save()
            request.session['rejected_order_ids'] = []
            return redirect('order_detail', order_id=order.id)

        elif action == 'decline':
            rejected_order_ids.append(order_id)
            request.session['rejected_order_ids'] = rejected_order_ids
            return redirect('available_orders')

    orders_data = []
    for order in closest_orders:
        items = order.items.all()
        total_price = sum(item.product.price * item.quantity for item in items)
        product = items[0].product if items else None
        seller_lat = product.seller_lat if product else None
        seller_lng = product.seller_lng if product else None

        orders_data.append({
            'order': order,
            'items': items,
            'total_price': total_price,
            'client_lat': order.client_lat,
            'client_lng': order.client_lng,
            'seller_lat': seller_lat,
            'seller_lng': seller_lng,
        })

    context = {
        'orders_data': orders_data,
        'driver_lat': user_profile.lat,
        'driver_lng': user_profile.lng,
    }

    return render(request, 'delivery agent/OrderTracking.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    total_price = sum(item.product.price * item.quantity for item in items)

    # Get delivery agent profile and rating
    delivery_agent_profile = None
    filled_stars = 0
    empty_stars = 5

    if order.delivery_agent:
        delivery_agent_profile = UserProfile.objects.filter(user=order.delivery_agent).first()
        if delivery_agent_profile and delivery_agent_profile.rating:
            filled_stars = int(round(delivery_agent_profile.rating))
            empty_stars = 5 - filled_stars

    # Get seller coordinates from first product
    seller_lat = None
    seller_lng = None
    if items:
        product = items[0].product
        seller_lat = product.seller_lat
        seller_lng = product.seller_lng

    context = {
        'order': order,
        'items': items,
        'total_price': total_price,
        'delivery_agent_profile': delivery_agent_profile,
        'filled_stars': filled_stars,
        'empty_stars': empty_stars,
        'client_lat': order.client_lat,
        'client_lng': order.client_lng,
        'driver_lat': order.delivery_agent_lat,
        'driver_lng': order.delivery_agent_lng,
        'seller_lat': seller_lat,
        'seller_lng': seller_lng,
    }
    return render(request, 'delivery agent/delivery_order.html', context)

@csrf_exempt
@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            order = get_object_or_404(Order, id=order_id)

            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save()
                return JsonResponse({
                    'message': 'Status updated successfully.',
                    'new_status': order.get_status_display()
                })
            else:
                return JsonResponse({'error': 'Invalid status.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
@login_required
def live_location_update(request, order_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat = data.get('lat')
            lng = data.get('lng')
            
            if lat is None or lng is None:
                return JsonResponse({'error': 'Missing coordinates'}, status=400)

            order = get_object_or_404(Order, id=order_id)
            order.delivery_agent_lat = lat
            order.delivery_agent_lng = lng
            order.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def rate_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        stars = int(request.POST.get('stars', 0))
        if 1 <= stars <= 5:
            rating, created = ProductRating.objects.update_or_create(
                user=request.user, product=product,
                defaults={'stars': stars}
            )
            product.update_rating()
            messages.success(request, 'تم حفظ تقييمك بنجاح.')
        else:
            messages.error(request, 'يرجى اختيار تقييم من 1 إلى 5 نجوم.')

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('product', pk=product.id)
    
def add_comment(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        comment_text = request.POST.get('comment')

        sentiment = analyze_sentiment(comment_text)  

        ProductComment.objects.create(
            product=product,
            user=request.user,
            comment_text=comment_text,
            sentiment=sentiment
        )

        print("Comment Text:", comment_text)
        print("Detected Sentiment:", sentiment) 

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('product', pk=product.id)
    
def search_products(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )[:5]  
        
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'name': product.name,
                'image': product.image.url if product.image else '',
                'price': str(product.price),
            })
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)
    