from django.urls import path
from django.http import HttpResponse

def hello(request):
	return HttpResponse("Hello, world. You're at the polls index.")

def nada(request):
	return HttpResponse("add /hello-world to the url")