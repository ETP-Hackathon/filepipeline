from django.urls import path
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .forms import UploadFileForm
import os
from .parsing import get_info
from .convert_docx_to_pdf import convert_docx_to_pdf
from .ai_lawyer_service import get_placeholder_values
from .ai_lawyer import get_placeholder_values2
import json
from django.views.decorators.csrf import csrf_exempt
import requests
from docx import Document

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
                #success.print()
                #return render(request, 'upload_success.html')
                #make post request to placeholder_values
                
            response = requests.post(
                'http://localhost:8000/placeholder_values/',
                json={"file_text": success.to_string()}
            )
            if response.status_code == 200:
                with open("output.json", "w", encoding="utf-8") as outfile:
                    json.dump(response.json(), outfile, ensure_ascii=False, indent=2)
                return render(request, 'upload_success.html')
            else:
                return HttpResponse("Error parsing file")
            
            return redirect('placeholder_values')
        except ImportError:
            return HttpResponse("Parser module not implemented yet")
@csrf_exempt
def placeholder_values(request):
    # Only accept POST requests
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
        
    # check if the request is JSON
    if request.content_type != 'application/json':
        return JsonResponse({'error': 'Request must be JSON'}, status=400)
    
    # Parse JSON data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # check if file_text is in the request
    if 'file_text' not in data:
        return JsonResponse({'error': 'file_text is required'}, status=400)

    # get the file text from the request json
    file_text = data['file_text']
    
    # Get template text if provided
    template_text = data.get('template_text', None)
    
    # Get placeholder regex if provided
    placeholder_regex = data.get('placeholder_regex', None)
    
    # check if file_text is null or empty
    if not file_text:
        return JsonResponse({'error': 'file_text cannot be empty'}, status=400)
    
    # Check if mock parameter is set to true
    use_mock = data.get('mock', False)
    
    # Prepare input data
    file_data = {'text': file_text}
    template_data = {'text': template_text} if template_text else None
    
    # Add regex to file_data if provided
    if placeholder_regex:
        file_data['placeholder_regex'] = placeholder_regex
    
    if use_mock:
        # Use mock values if explicitly requested
        from .ai_lawyer_service import get_placeholder_mock_values
        filled_placeholder_array = get_placeholder_mock_values(file_data, template_data)
        ai_prompt = None
    else:
        # Use OpenAI API for real values
        filled_placeholder_array, ai_prompt = get_placeholder_values(file_data, parsed_json_template_file=template_data)

    response = {
        'placeholder_values': filled_placeholder_array,
        'original_text': file_text
    }
    
    # Include AI prompt in response if available
    if ai_prompt:
        response['prompt'] = ai_prompt

    return JsonResponse(response)

def nada(request):
     return render(request, 'home.html')
