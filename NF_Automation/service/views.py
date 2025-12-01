import requests
from django.shortcuts import render



def fetch_api_data(request):
    response = requests.post('http://127.0.0.1:8000/nfserv/test_temp_create',json='payload')  # Your local API URL
    data = response.json()
    return render(request, 'template.html', {'api_data': data})





