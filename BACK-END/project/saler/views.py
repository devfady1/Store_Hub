from django.shortcuts import render, redirect  
from .forms import ProductForm 
from django.conf import settings
print(settings.TEMPLATES)


def add_product(request):
    if request.method == "POST":  
        form = ProductForm(request.POST, request.FILES)  
        if form.is_valid():  
            form.save()  
            return redirect("success") 
    else:
        form = ProductForm() 

    return render(request, "saler/seler.html", {"form": form}) 

def success_view(request):
    return render(request, "seller/success.html") 


