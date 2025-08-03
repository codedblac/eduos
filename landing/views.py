from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from datetime import datetime

def index(request):
    return render(request, 'landing/index.html', {'year': datetime.now().year})
