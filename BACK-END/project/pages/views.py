from django.shortcuts import render , redirect
from .models import *
from .models import WalletTransaction
import stripe
from django.db.models import Count , Max 
from .forms import *
from rest_framework.authtoken.models import Token
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
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
from .models import Subscriber
from .forms import SubscriberForm
from django.utils import timezone
import random, string
from .models import Subscriber, Coupon
from datetime import timedelta
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny









def is_seler(user):
    return user.userprofile.role == 'saler'

def is_delevry(user):
    return user.userprofile.role == 'delivery_agent'

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def custom_redirect_view(request):
    if not request.user.is_authenticated:
        return redirect('login')     
    try:
        user = request.user
        if user.userprofile.role == 'delivery_agent':
            return redirect('available_orders')
        elif user.userprofile.role == 'saler':
            return redirect('product-management')
        elif user.userprofile.role == 'admin':
            return redirect('/admin')
        else:
            messages.info(request, f"مرحباً بك {user.username}")
            return redirect('index')
    except AttributeError:
        if request.user.is_authenticated:
            return redirect('select_role')
        else:
            messages.error(request, "لم يتم العثور على الملف الشخصي للمستخدم")
            return redirect('login')



@login_required
def select_role(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['user', 'delivery_agent', 'saler']:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.role = role
            profile.save()
            return redirect('custom_redirect')
    return render(request, 'account/select_role.html')


def generate_coupon_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

from rest_framework.authtoken.models import Token

@login_required
def index(request):

    if request.user.is_authenticated:
        Token.objects.get_or_create(user=request.user)


    message = request.session.pop('message', None)
    message_type = request.session.pop('message_type', None)

    categories = Category.objects.all()
    top_products = Product.objects.filter(name="banner").annotate(likes_count=Count('likes__id')).order_by('-likes_count')[:5]
    flash_sales = FlashSale.objects.all()
    max_time = flash_sales.aggregate(max_end_time=Max('end_date'))['max_end_time'] if flash_sales else None
    all_products = list(Product.objects.all())
    random_products = random.sample(all_products, min(len(all_products), 8))  
    username = request.user.username 
    liked_products = request.user.product_likes.values_list('id', flat=True) if request.user.is_authenticated else []

    if request.method == "POST":
        form = SubscriberForm(request.POST)
        email = request.POST.get('email')

        if Subscriber.objects.filter(email=email).exists():
            request.session['message'] = "هذا البريد مستخدم من قبل."
            request.session['message_type'] = "error"
        else:
            if form.is_valid():
                subscriber = form.save(commit=False)
                code = generate_coupon_code()
                now = timezone.now()
                coupon = Coupon.objects.create(
                    code=code,
                    discount_percentage=10,
                    active_from=now,
                    notActve_until=now + timedelta(days=7),
                    is_active=True
                )
                subscriber.coupon = coupon
                subscriber.save()

                request.session['message'] = f"مبروك! حصلت على خصم 10٪ ✅. كودك: {code}"
                request.session['message_type'] = "success"
            else:
                request.session['message'] = "حدث خطأ أثناء الاشتراك."
                request.session['message_type'] = "error"

        return redirect('index')

    else:
        form = SubscriberForm()

    return render(request, 'pages/index.html', {
        'categories': categories,
        'products': top_products,
        'flash_sales': flash_sales,
        'max_time': max_time,
        'username': username,
        'random_products': random_products,
        'liked_products': liked_products,  
        'form': form,
        'message': message,
        'message_type': message_type,
    })




def logout_view(request):
    logout(request)
    return redirect("/login")
    



@login_required
def wishlist(request):
    liked_products = Product.objects.filter(likes=request.user).select_related("saler")
    random_products = Product.objects.exclude(likes=request.user).exclude(name="banner").order_by('?')[:4]

    for product in liked_products:
        product.old_price = Decimal(product.price) * Decimal(1.35)  

    for product in random_products:
        product.old_price = Decimal(product.price) * Decimal(1.35)

    for product in random_products:
        product.star_list = range(int(round(product.rating)))  
        
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

    # Get comments with user profiles in random order
    comments = product.comments.select_related('user').order_by('?').all()
    for comment in comments:
        try:
            profile = UserProfile.objects.get(user=comment.user)
            comment.profile_image_url = profile.profile_image.url if profile.profile_image else None
        except UserProfile.DoesNotExist:
            comment.profile_image_url = None

    # Split comments into pairs for 2x2 grid display
    comment_pairs = list(zip(comments[::2], comments[1::2])) if len(comments) > 1 else [(comments[0], None)] if comments else []

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
        'related_items': related_items,
        'comment_pairs': comment_pairs[:3],  # First 3 pairs (6 comments)
        'hidden_comment_pairs': comment_pairs[3:] if len(comment_pairs) > 3 else []  # Remaining pairs
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
                return redirect('custom_redirect')
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
    quantity = int(request.GET.get('quantity', 1))  # Get quantity from request, default to 1
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if product_id in cart:
        cart[product_id]['quantity'] += quantity  
    else:
        cart[product_id] = {
            'name': product.name,
            'price': float(product.price),
            'image': product.image.url,
            'quantity': quantity,  
        }

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({'status': 'success', 'cart': cart})

@login_required
@csrf_exempt
def update_cart(request):
    if request.method == "POST":
        try:
            cart = request.session.get("cart", {})
            data = json.loads(request.body)

            for product_id, new_quantity in data.items():
                if product_id in cart:
                    cart[product_id]["quantity"] = int(new_quantity)

            request.session["cart"] = cart
            request.session.modified = True

            return JsonResponse({"status": "success", "cart": cart})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@login_required
def cart(request):
    cart = request.session.get('cart', {})
    total = 0
    discount_percentage = request.session.get('discount_percentage', 0)

    for product_id, item in cart.items():
        item['subtotal'] = float(item['price']) * int(item['quantity'])
        total += item['subtotal']

    discount_amount = (discount_percentage / 100) * total
    final_price = total - discount_amount

    context = {
        'cart': cart,
        'total': total,
        'discount': discount_amount,
        'final_price': final_price,
        'discount_percentage': discount_percentage
    }

    return render(request, 'pages/payment/cart.html', context)


@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    total = 0

    for product_id, item in cart.items():
        item['subtotal'] = float(item['price']) * int(item['quantity'])
        total += item['subtotal']

    if request.method == 'POST':
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')

        # أنشئ الأوردر (ده مثال، غير حسب الموديل بتاعك)
        order = Order.objects.create(
            customer=request.user,
            client_lat=lat,
            client_lng=lng,
            status='pending'
        )
        # أضف بقية التفاصيل من السلة (cart) زي items وغيره
        return redirect('order_confirmation')  # غير الريدايركت حسب مشروعك

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
        return JsonResponse(products_list, safe=False)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
from rest_framework.authtoken.models import Token

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
        print(products_list)  
        
        
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



stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_checkout_session(request):
    cart = request.session.get('cart', {})
    line_items = []

    for item in cart.values():
        line_items.append({
            'price_data': {
                'currency': 'egp',
                'product_data': {
                    'name': item['name'],
                },
                'unit_amount': int(float(item['price']) * 100),  # بالسنت
            },
            'quantity': int(item['quantity']),
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://127.0.0.1:8000/order_success/',
        cancel_url='http://127.0.0.1:8000/cart/',
        metadata={'user_id': str(request.user.id)},
    )


    return redirect(session.url, code=303)

def payment_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('cart')

    try:
        session = stripe.checkout.Session.retrieve(session_id)

        # تأكد إن الدفع تم
        if session.payment_status == 'paid':
            return place_order(request)  

        else:
            return HttpResponse('الدفع لم يكتمل')
    except Exception as e:
        return HttpResponse(f'حدث خطأ: {str(e)}')





def order_success(request):
    return render(request, 'pages/payment/order_success.html')


@login_required
@csrf_exempt
def place_order(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        user = request.user

        if not cart:
            messages.error(request, "السلة فارغة.")
            return redirect('cart')

        payment_method = request.POST.get('payment_method')
        pay_with_wallet = payment_method == 'wallet'

        try:
            client_lat = float(request.POST.get('client_lat', 0.0))
            client_lng = float(request.POST.get('client_lng', 0.0))
        except ValueError:
            client_lat = 0.0
            client_lng = 0.0

        total_price = 0
        for item in cart.values():
            total_price += float(item['price']) * int(item['quantity'])

        if pay_with_wallet:
            credit = sum(t.amount for t in WalletTransaction.objects.filter(user=user) if t.is_credit())
            debit = sum(t.amount for t in WalletTransaction.objects.filter(user=user) if not t.is_credit())
            balance = credit - debit

            if total_price > balance:
                messages.error(request, "الرصيد غير كافي للدفع من المحفظة.")
                return redirect('cart')

        # إنشاء الطلب
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

        # لو الدفع بالمحفظة → خصم المبلغ من العميل
        if pay_with_wallet:
            WalletTransaction.objects.create(
                user=user,
                amount=total_price,
                transaction_type='purchase',
                description=f'شراء طلب رقم #{order.id}'
            )

        # توزيع الأرباح على البائعين
        seller_earnings = {}

        for item in order.items.all():
            product = item.product
            saler = product.saler
            quantity = item.quantity
            total = float(product.price) * quantity

            if saler not in seller_earnings:
                seller_earnings[saler] = 0
            seller_earnings[saler] += total

        for saler, total_sale in seller_earnings.items():
            commission = total_sale * 0.12
            earning = total_sale - commission

            # أرباح البائع
            WalletTransaction.objects.create(
                user=saler,
                amount=earning,
                transaction_type='earning',
                description=f'أرباح من طلب #{order.id}'
            )

            

        # تنظيف السلة
        request.session['cart'] = {}
        messages.success(request, "تم تنفيذ الطلب بنجاح.")
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

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Order, UserProfile
from geopy.distance import geodesic
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

@login_required
def assign_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, delivery_agent__isnull=True)
    user_profile = get_object_or_404(UserProfile, user=request.user, role='delivery_agent')

    order.delivery_agent = request.user
    order.delivery_agent_lat = user_profile.lat
    order.delivery_agent_lng = user_profile.lng
    order.status = 'in_progress'
    order.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"order_{order.id}",
        {
            'type': 'send_status',
            'message': json.dumps({'status': 'in_progress'})
        }
    )

    return redirect('order_detail', order_id=order.id)

@login_required
def available_order_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user, role='delivery_agent')
    driver_location = (user_profile.lat, user_profile.lng)

    available_orders = list(Order.objects.filter(
        status='pending',
        delivery_agent__isnull=True,
        client_lat__isnull=False,
        client_lng__isnull=False,
    ).prefetch_related('items', 'items__product', 'customer'))

    if request.method == 'POST':
        action = request.POST.get('action')
        order_id = int(request.POST.get('order_id'))
        order = get_object_or_404(Order, id=order_id)
        if action == 'accept':
            order.delivery_agent = request.user
            order.delivery_agent_lat = user_profile.lat
            order.delivery_agent_lng = user_profile.lng
            order.status = 'in_progress'
            order.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"order_{order.id}",
                {
                    'type': 'send_status',
                    'message': json.dumps({'status': 'in_progress'})
                }
            )
            request.session['rejected_order_ids'] = []
            return redirect('delivery_order_detail', order_id=order.id)
        elif action == 'decline':
            rejected_order_ids = request.session.get('rejected_order_ids', [])
            rejected_order_ids.append(order_id)
            request.session['rejected_order_ids'] = rejected_order_ids
            messages.info(request, 'Order declined.')
            return redirect('available_orders')

    rejected_order_ids = request.session.get('rejected_order_ids', [])
    available_orders = [o for o in available_orders if o.id not in rejected_order_ids]

    if not available_orders:
        return render(request, 'delivery agent/OrderTracking.html', {
            'orders_data': [],
            'driver_lat': user_profile.lat,
            'driver_lng': user_profile.lng,
        })

    def calculate_delivery_fee(distance_km):
        base_fee = 25
        extra_km_fee = 6
        if distance_km <= 5:
            return int(base_fee)
        else:
            return int(base_fee + ((distance_km - 5) * extra_km_fee))

    def order_distance(order):
        return geodesic(driver_location, (order.client_lat, order.client_lng)).km

    available_orders.sort(key=order_distance)
    closest_orders = available_orders[:2]

    orders_data = []
    for order in closest_orders:
        items = order.items.all()
        total_price = int(sum(item.product.price * item.quantity for item in items))
        product = items[0].product if items else None
        seller_lat = product.seller_lat if product else 0
        seller_lng = product.seller_lng if product else 0
        distance_km = order_distance(order)
        estimated_time_minutes = int((distance_km / 30) * 60)
        delivery_fee = calculate_delivery_fee(distance_km)

        orders_data.append({
            'order': order,
            'items': items,
            'total_price': total_price,
            'client_lat': order.client_lat,
            'client_lng': order.client_lng,
            'seller_lat': seller_lat,
            'seller_lng': seller_lng,
            'distance': round(distance_km, 1),
            'estimated_time': estimated_time_minutes,
            'delivery_fee': delivery_fee,
            'final_price': total_price + delivery_fee
        })

    context = {
        'orders_data': orders_data,
        'driver_lat': user_profile.lat,
        'driver_lng': user_profile.lng,
    }

    return render(request, 'delivery agent/OrderTracking.html', context)


@csrf_exempt
@login_required
def live_location_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'GET':
        customer_profile = UserProfile.objects.filter(user=order.customer).first()
        driver_profile = UserProfile.objects.filter(user=order.delivery_agent).first()

        items = order.items.all()
        product = items[0].product if items else None
        seller_profile = UserProfile.objects.filter(user=product.saler).first() if product and product.saler else None

        return JsonResponse({
            'customer': {
                'lat': customer_profile.lat if customer_profile else None,
                'lng': customer_profile.lng if customer_profile else None,
            },
            'driver': {
                'lat': driver_profile.lat if driver_profile else None,
                'lng': driver_profile.lng if driver_profile else None,
            },
            'seller': {
                'lat': seller_profile.lat if seller_profile else (product.seller_lat if product else None),
                'lng': seller_profile.lng if seller_profile else (product.seller_lng if product else None),
            },
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat = data.get('lat')
            lng = data.get('lng')

            if lat is None or lng is None:
                return JsonResponse({'status': 'error', 'message': 'Missing coordinates'}, status=400)

            user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
            user_profile.lat = lat
            user_profile.lng = lng
            user_profile.save()

            print(f"[Location Update] User: {request.user.username}, Role: {user_profile.role}, Lat: {lat}, Lng: {lng}")

            # تحديث مكان المنتج لو اليوزر بائع
            if user_profile.role == 'saler':
                items = order.items.all()
                for item in items:
                    if item.product.saler == request.user:
                        item.product.seller_lat = lat
                        item.product.seller_lng = lng
                        item.product.save()
                        print(f"[Product Update] Product ID: {item.product.id} - Updated with seller location")

            return JsonResponse({'status': 'success'})

        except Exception as e:
            print(f"[Error] {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method'}, status=405)
        
@login_required
@csrf_exempt
def update_order_status(request, order_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            order = get_object_or_404(Order, id=order_id)

            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save()
                return JsonResponse({'message': 'Status updated successfully.', 'new_status': order.get_status_display()})
            else:
                return JsonResponse({'error': 'Invalid status.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

 
@login_required
def delivery_order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if not request.user.userprofile.role == 'delivery_agent':
        return redirect('index')  # أو صفحة خطأ مخصصة
    items = order.items.all()
    total_price = sum(item.product.price * item.quantity for item in items)
    delivery_agent_profile = UserProfile.objects.filter(user=order.delivery_agent).first()
    filled_stars = int(round(delivery_agent_profile.rating)) if delivery_agent_profile and delivery_agent_profile.rating else 0
    empty_stars = 5 - filled_stars
    seller_lat = items[0].product.seller_lat if items else 0
    seller_lng = items[0].product.seller_lng if items else 0
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
    return render(request, 'delivery agent/delevry order.html', context)

def search_products(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )[:5]  # نقوم بتحديد عدد النتائج ب 5 فقط
        
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

def test_email(request):
    try:
        send_mail(
            'Test Email',
            'This is a test email from StoreHub.',
            settings.EMAIL_HOST_USER,
            ['fady555555555522@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse('Test email sent successfully! Check your console for the email content.')
    except Exception as e:
        return HttpResponse(f'Error sending email: {str(e)}') 
    


def role_required(roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            print("User:", request.user)
            print("User Role:", request.user.userprofile.role)
            if request.user.userprofile.role not in roles:
                print("Role not allowed!")
                return Response({'error': 'Unauthorized'}, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

#wallet
def get_user_wallet_balance(user):
    transactions = WalletTransaction.objects.filter(user=user)
    total_credit = sum(t.amount for t in transactions if t.is_credit())
    total_debit = sum(t.amount for t in transactions if not t.is_credit())
    return total_credit - total_debit



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import WalletTransaction
from .serializers import WalletTransactionSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_summary(request):
    user = request.user
    transactions = WalletTransaction.objects.filter(user=user).order_by('-created_at')

    credit = sum(t.amount for t in transactions if t.is_credit())
    debit = sum(t.amount for t in transactions if not t.is_credit())
    balance = credit - debit

    serializer = WalletTransactionSerializer(transactions, many=True)

    return Response({
        'balance': round(balance, 2),
        'transactions': serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_wallet_checkout_session(request):
    try:
        amount = float(request.data.get('amount'))
        amount_cents = int(amount * 100)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'egp',
                    'product_data': {'name': 'شحن رصيد المحفظة'},
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:8000/wallet/charge/success/?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://127.0.0.1:8000/',
            metadata={'user_id': str(request.user.id)},
        )

        return Response({'url': session.url})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def stripe_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return Response({'error': 'Session ID missing'}, status=400)

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        amount = session.amount_total / 100

        if session.payment_status == 'paid':
            user_id = session.metadata.get('user_id')
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)

            WalletTransaction.objects.create(
                user=user,
                amount=amount,
                transaction_type='charge',
                description='شحن رصيد عبر Stripe',
            )
            # إعادة التوجيه لصفحة النجاح في الواجهة
            return redirect('/wallet/success/')
        else:
            return Response({'error': 'الدفع لم يكتمل'}, status=400)

    except Exception as e:
        return Response({'error': str(e)}, status=500)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@role_required(['saler'])
def vendor_withdraw(request):
    amount = float(request.data.get('amount'))
    transactions = WalletTransaction.objects.filter(user=request.user)
    credit = sum(t.amount for t in transactions if t.is_credit())
    debit = sum(t.amount for t in transactions if not t.is_credit())
    balance = credit - debit

    if amount > balance:
        return Response({'error': 'الرصيد غير كافي للسحب'}, status=400)

    WalletTransaction.objects.create(
        user=request.user,
        amount=amount,
        transaction_type='withdrawal',
        description='سحب الأرباح إلى الفيزا'
    )

    return Response({'message': 'تم تسجيل طلب السحب بنجاح', 'amount': amount})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(['delivery_agent'])
def driver_earnings(request):
    driver = request.user

    assignments = Order.objects.filter(delivery_agent=driver ,status='completed')  # حسب حالتك
    total_earnings = sum(a.total_price for a in assignments)
    total_orders = Order.objects.filter(delivery_agent=driver).count()

    for a in assignments:
        distance = a.distance_km  
        if distance <= 5:
            total_earnings += 25
        else:
            total_earnings += distance * 6

    return Response({
        'driver': driver.username,
        'total_earnings': round(total_earnings, 2),
        'total_orders': total_orders,
    })


@login_required
def wallet_success_page(request):
    amount = request.GET.get("amount")
    tx_id = request.GET.get("tx") 
    return render(request, "pages/success.html")





@role_required(['delivery_agent'])
@login_required
def delivery_earnings_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    driver_location = (user_profile.lat, user_profile.lng)

    orders = Order.objects.filter(delivery_agent=request.user)

    orders_data = []
    total_earnings = 0

    for order in orders:
        items = order.items.all()
        total_price = sum(item.product.price * item.quantity for item in items)

        customer_location = (order.client_lat, order.client_lng)
        distance_km = geodesic(driver_location, customer_location).km
        distance_km = round(distance_km, 1)

        base_rate = 25 if distance_km <= 5 else 25 + (distance_km - 5) * 6
        base_rate = round(base_rate, 2)

        commission = base_rate * 0.15
        final_earning = base_rate - commission

        if order.status == "completed":
            total_earnings += final_earning

        orders_data.append({
            'id': order.id,
            'date': 'not found',
            'customer': order.customer.get_full_name() or order.customer.username,
            'status': order.status,
            'distance': f"{distance_km} km",
            'base_rate': f"${base_rate:.2f}",
            'commission': f"-${commission:.2f}",
            'total_earning': f"${final_earning:.2f}",
        })

    avg_earning = round(total_earnings / len(orders_data), 2) if orders_data else 0

    context = {
        'orders': orders_data,
        'total_earnings': f"${total_earnings:.2f}",
        'total_orders': len(orders_data),
        'avg_earning': f"${avg_earning:.2f}",
        'commission_rate': "15%",
    }
    return render(request, 'delivery agent/earnings.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@role_required(['delivery_agent'])
def driver_earnings_api(request):
    user_profile = UserProfile.objects.get(user=request.user)
    driver_location = (user_profile.lat, user_profile.lng)
    orders = Order.objects.filter(delivery_agent=request.user)
    orders_data = []
    total_earnings = 0
    for order in orders:
        items = order.items.all()
        total_price = sum(item.product.price * item.quantity for item in items)
        customer_location = (order.client_lat, order.client_lng)
        distance_km = geodesic(driver_location, customer_location).km
        distance_km = round(distance_km, 1)
        base_rate = 25 if distance_km <= 5 else 25 + (distance_km - 5) * 6
        base_rate = round(base_rate, 2)
        commission = base_rate * 0.15
        final_earning = base_rate - commission
        if order.status == "completed":
            total_earnings += final_earning
        orders_data.append({
            'id': order.id,
            'date': 'not found',
            'customer': order.customer.get_full_name() or order.customer.username,
            'status': order.status,
            'distance': f"{distance_km} km",
            'base_rate': f"${base_rate:.2f}",
            'commission': f"-${commission:.2f}",
            'total_earning': f"${final_earning:.2f}",
        })
    avg_earning = round(total_earnings / len(orders_data), 2) if orders_data else 0

    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 8))
    start = (page - 1) * page_size
    end = start + page_size
    paginated_orders = orders_data[start:end]
    total_pages = (len(orders_data) + page_size - 1) // page_size

    data = {
        'orders': paginated_orders,
        'total_earnings': f"${total_earnings:.2f}",
        'total_orders': len(orders_data),
        'avg_earning': f"${avg_earning:.2f}",
        'commission_rate': "15%",
        'page': page,
        'total_pages': total_pages,
    }
    return Response(data)
