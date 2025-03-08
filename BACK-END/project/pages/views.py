from django.shortcuts import render , redirect
from .models import *
from django.db.models import Count , Max 
from .forms import *
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
from .decorators import role_required

@role_required('saler')
def add_product(request):
    return render(request, 'add_product.html')




@login_required
def index(request):
    top_products = Product.objects.filter(name="banner").annotate(likes_count=Count('likes__id')).order_by('-likes_count')[:5]

    flash_sales = FlashSale.objects.all()

    max_time = flash_sales.aggregate(max_end_time=Max('end_date'))['max_end_time'] if flash_sales else None


    username = request.user.username 

    return render(request, 'pages/index.html', {
        'products': top_products,
        'flash_sales': flash_sales,
        'max_time': max_time,
        'username': username,  
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
    
    # إضافة أو إزالة اللايك
    if request.user in product.likes.all():
        product.likes.remove(request.user)  
        liked = False
    else:
        product.likes.add(request.user)  
        liked = True

    # تحديث التقييمات
    product.star_list = range(int(round(product.rating)))

    # حفظ التغييرات في قاعدة البيانات (مهم)
    product.save()

    # إرجاع الاستجابة بالعدد الجديد للايكات
    return JsonResponse({'liked': liked, 'likes_count': product.likes.count()})

def about(request):
    return render(request, 'pages/about.html')


def product(request, pk):
    product = Product.objects.get(id=pk)
    rating = getattr(product, 'rating', 0)
    full_stars = int(rating)
    empty_stars = 5 - full_stars  # عدد النجوم الفارغة

    # المنتجات المشابهة
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




def account(request):
    return render(request, 'pages/account/account.html')


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

    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'colors': colors,
        'products': page_obj.object_list,
        'page_obj': page_obj,
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



#لو حطيت .get(rating__gte=3) لا يعرض الا المنتجات التي تكون تقييمها 3 او اكبر
#.filter-price__exact=10 view all price10
#contains=10 view all contains 10
#price__range=(10,20) view all between 10-20
#price__in=(10,20) view all between 10-20
#price__in=[10,20] view all between 10-20
