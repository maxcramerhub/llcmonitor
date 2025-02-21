from django.shortcuts import render, redirect

from django.http import HttpResponse


def index(request):
    return render(request, 'monitor/index.html')

def success(request):
     return render(request, 'monitor/success.html')

def class_select(request):
    if request.method == 'POST':
        print("Student signed in!")
        return redirect('monitor:success')
    return render(request, 'monitor/class_select.html')
