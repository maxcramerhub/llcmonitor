from django.shortcuts import render, redirect

from django.http import HttpResponse



def index(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        
        if login.isnumeric():
            print("Student ID Number")
        else:
            print(login.split())
        return render(request, 'monitor/class_select.html')
    
    return render(request, 'monitor/index.html')

def success(request):
    return render(request, 'monitor/success.html')


def class_select(request):
    if request.method == 'POST':
        print("Student signed in!")
        return redirect('monitor:success')
    return render(request, 'monitor/class_select.html')
