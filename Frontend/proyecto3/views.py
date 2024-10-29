from django.shortcuts import render

import requests

def index(request):
    return render(request, 'index.html')

def configurar(request):
    return render(request, 'configurar.html')

# Create your views here.
