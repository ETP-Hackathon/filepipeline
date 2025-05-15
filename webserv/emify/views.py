from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import UploadFileForm
import subprocess
def hello(request):
	return HttpResponse("Hello, world. You're at the polls index.")
"""
def nada(request):
	return HttpResponse("add /hello-world to the url")
"""
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'upload_success.html')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

def nada(request):
     return render(request, 'home.html')