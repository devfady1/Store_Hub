from django import forms
from .models import *
from django.contrib.auth.forms import *
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import Subscriber



class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']



class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone_number', 'role']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("رقم الهاتف يجب أن يحتوي على أرقام فقط.")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)  
        if commit:
            user.save()  # حفظ المستخدم أولًا

            # إنشاء UserProfile إذا لم يكن موجودًا
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "role": self.cleaned_data['role'],
                    "phone_number": self.cleaned_data['phone_number']
                }
            )

            # تأكيد تحديث القيم في حالة كان UserProfile موجودًا مسبقًا
            if not created:
                profile.role = self.cleaned_data['role']
                profile.phone_number = self.cleaned_data['phone_number']
                profile.save()

        return user
    



class CustomLoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ' '})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("اسم المستخدم أو كلمة المرور غير صحيحة.")
            if not user.is_active:
                raise forms.ValidationError("هذا الحساب غير مفعل.")

        return cleaned_data
    

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'color', 'category', 'price', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input-seller', 'placeholder':''}),
            'description': forms.Textarea(attrs={'class': 'form-input-seller', 'placeholder': ''}),
            'color': forms.Select(attrs={'class': 'form-input-seller'}),
            'category': forms.Select(attrs={'class': 'form-input-seller'}),
            'price': forms.NumberInput(attrs={'class': 'form-input-seller', 'placeholder': ''}),
            'image': forms.FileInput(attrs={'class': 'file-input'}),
        }


from django import forms
from .models import Subscriber

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
