from django.shortcuts import render, redirect

from django.http import HttpResponse

from models import Students

def index(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        type = None
        if login.isnumeric():
            student = Students.objects.get(western_id = login).first()
            #Checks to see if student is in db, redirects to class select if in db, index otherwise
            if student:
                redirect(request, 'monitor/class_select.html')
            else:
                #TODO: Change to setup once created
                redirect(request, 'monitor/index.html')
        elif login.isalpha():
            type = 'name'
        else:
            return render(request, 'monitor/index.html')

    return render(request, 'monitor/index.html')

def success(request):
    return render(request, 'monitor/success.html')


def class_select(request):
    if request.method == 'POST':
        print("Student signed in!")
        return redirect('monitor:success')
    return render(request, 'monitor/class_select.html')
