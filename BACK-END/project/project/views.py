from django.shortcuts import render


def handel404(request,exception):
    return render(request, '400.html', status = 404)

def handel500(request,exception):
    return render(request, '500.html', status = 500)

def index(request):
    return render(request, '400.html', name = 'index')

