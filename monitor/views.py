from django.shortcuts import render, redirect

from django.http import HttpResponse
from monitor.models import Students

def index(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        exists = False
        if all(x.isnumeric() for x in login):
            student = Students.objects.filter(western_id = int(login)).first()
            print(student)
            #Checks to see if student is in db, redirects to class select if in db, index otherwise
            if student is not None:
                exists = True
            else:
                exists = False

        elif all(x.isalpha() or x.isspace() for x in login):
            loginArr = login.split()
            print(loginArr)
            student = Students.objects.filter(fname = loginArr[0], lname = loginArr[1]).first()
            print(student)
            #Checks to see if student is in db, redirects to class select if in db, index otherwise
            if student is not None:
                exists = True
            else:
                exists = False
        else:
            return render(request, 'monitor/index.html')
        
        if exists:
            return render(request, 'monitor/class_select.html')
        else:
            #TODO: Change redirect to setup
            return render(request, 'monitor/index.html')
    else:
        return render(request, 'monitor/index.html')
def success(request):
    return render(request, 'monitor/success.html')

def class_select(request):
    if request.method == 'POST':
        print("Student signed in!")
        return redirect('monitor:success')
    return render(request, 'monitor/class_select.html')
