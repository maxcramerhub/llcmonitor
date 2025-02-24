from django.shortcuts import render, redirect

from django.http import HttpResponse



def index(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        type = None
        if login.isnumeric():
            type = 'sid'
        elif login.isalpha():
            type = 'name'
        else:
            type = 'other'
        print(type)
        if type == 'sid':
            #query for sid. If it's in db, go to class select. If false, go setup
            pass
        elif type == 'name':
            #query for sid. If it's in db, go to class select. If false, go to setup
            pass
        else:
            return render(request, 'monitor/index.html')
        
        return render(request, 'monitor/class_select.html')
    
    
    return render(request, 'monitor/index.html')

def success(request):
    return render(request, 'monitor/success.html')


def class_select(request):
    if request.method == 'POST':
        print("Student signed in!")
        return redirect('monitor:success')
    return render(request, 'monitor/class_select.html')
