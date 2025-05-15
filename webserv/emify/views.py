from django.urls import path
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .forms import UploadFileForm
import os
from .parsing import get_info
from .convert_docx_to_pdf import convert_docx_to_pdf
from .ai_lawyer_service import get_placeholder_values
import json
from django.views.decorators.csrf import csrf_exempt

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

@csrf_exempt
def placeholder_values(request):
    """
    API endpoint for generating placeholder values from a legal document.
    
    Accepts POST requests with JSON body containing:
    - file_text: The legal document text to analyze
    - template_text: Optional template with placeholders to fill
    - placeholder_regex: Optional regex pattern for identifying placeholders
    - mock: Optional boolean to use mock values instead of AI
    
    Returns JSON with:
    - placeholder_values: Array of generated values
    - original_text: The input document text
    - prompt: Details of the prompt sent to AI (when not using mock)
    """
    # Validate request method
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
        
    # Validate content type
    if request.content_type != 'application/json':
        return JsonResponse({'error': 'Request must be JSON'}, status=400)
    
    # Parse JSON data
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Validate required fields
    if 'file_text' not in data:
        return JsonResponse({'error': 'file_text is required'}, status=400)

    file_text = data.get('file_text', '')
    if not file_text:
        return JsonResponse({'error': 'file_text cannot be empty'}, status=400)
    
    # Extract optional parameters
    template_text = data.get('template_text', None)
    placeholder_regex = data.get('placeholder_regex', None)
    use_mock = data.get('mock', False)
    
    # Prepare input data
    file_data = {'text': file_text}
    template_data = {'text': template_text} if template_text else None
    
    # Add regex to file_data if provided
    if placeholder_regex:
        file_data['placeholder_regex'] = placeholder_regex
    
    # Get placeholder values using appropriate method
    if use_mock:
        # Use mock values if explicitly requested
        from .ai_lawyer_service import get_placeholder_mock_values
        filled_placeholder_array, ai_prompt = get_placeholder_mock_values(file_data, template_data)
    else:
        # Use OpenAI API for real values
        from .ai_lawyer_service import get_placeholder_values
        filled_placeholder_array, ai_prompt = get_placeholder_values(file_data, parsed_json_template_file=template_data)

    # Prepare response
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
