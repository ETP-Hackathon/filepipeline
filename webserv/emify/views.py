from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import UploadFileForm
import os
from .parsing import get_info
from .convert_docx_to_pdf import convert_docx_to_pdf

def hello(request):
	return HttpResponse("Hello, world. You're at the polls index.")

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('send_file')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

def send_file(request):
    if request.method == 'GET':
        upload_dir = 'media/uploads/'
        
        files = os.listdir(upload_dir)
        if not files:
            return HttpResponse("No files found in uploads folder")
            
        files.sort(key=lambda x: os.path.getmtime(os.path.join(upload_dir, x)))
        latest_file = os.path.join(upload_dir, files[-1])
        if latest_file.endswith('.docx'):
            pdf_file = latest_file.replace('.docx', '.pdf')
            if not os.path.exists(pdf_file):
                convert_docx_to_pdf(latest_file, pdf_file)
            latest_file = pdf_file
        if not os.path.exists(latest_file):
            return HttpResponse("File not found in uploads folder")
            
        output_file = 'output.pdf'
        
        try:
            
            success = get_info(latest_file)
            if success:
                success.print()
                return render(request, 'upload_success.html')
            else:
                return HttpResponse("Error parsing file")
        except ImportError:
            return HttpResponse("Parser module not implemented yet")

def nada(request):
     return render(request, 'home.html')
