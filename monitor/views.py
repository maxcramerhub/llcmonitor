from django.shortcuts import render, redirect

from django.http import HttpResponse
import requests
from django.http import JsonResponse
from django.conf import settings
from django.core.cache import cache
from monitor.models import *
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json
from django.contrib import messages
from monitor.models import Students

#------------------------------------------------------------------------
#Enter StuID or Name Sign In Page
#------------------------------------------------------------------------

def index(request):
    name = request.session.pop('student_name', None)
    student_id = request.session.pop('student_id', None)
    if request.method == 'POST':
        login = request.POST.get('login')

        #************************
        # login is numeric
        #************************
        # so this if all(x.isnumeric() for x in login and len(login) == 7):

        # if all(x.isnumeric() for x in login):
        if login.isdigit() and len(login) == 7:  # 

            student = Students.objects.filter(western_id = int(login)).first()
            class_exist = student.classes.count() if student else 0
            #If we found a student
            if student and class_exist > 0:
                request.session['student_id'] = student.student_id
                return redirect('class-check/')
            elif student and class_exist == 0:
                student = Students.objects.get(western_id = login)
                request.session['student_id'] = student.student_id
                return redirect('class-select/')
            else:
                #TODO: Change to setup once created
                student = Students.objects.create(western_id = login)
                request.session['student_id'] = student.student_id
                return redirect('class-select/')
        

        
        # else:
        #     messages.error(request, "Please enter only numbers if entering an ID")
        #     return render(request, 'monitor/index.html')


        #************************
        # login is a name
        #************************
        elif all(x.isalpha() or x.isspace() for x in login):
            loginArr = login.split()

            if len(loginArr) < 2:
                messages.error(request, "Please enter a first and last name.")
                return render(request, 'monitor/index.html')
            
            # print(loginArr) , try to
            student = Students.objects.filter(fname = loginArr[0], lname = loginArr[1]).first()

            # student = Students.objects.filter(fname="John", lname="Doe", western_id=None)
            # print(student)

            class_exist = 0

            if not student:
                student = Students.objects.create(fname=loginArr[0], lname=loginArr[1], western_id=None)
            
            #check this, im thinking this is storing the naems so it will display across multiple 
            request.session['student_name'] = student.fname
            request.session['student_id'] = student.student_id
                
            class_exist = student.classes.count()

            #If we found a student
            # if student and class_exist > 0:
            if class_exist > 0: #student has classes
                request.session['student_name'] = loginArr[0]
                request.session['student_id'] = student.student_id
                return redirect('class-check/') 
            else: #student and class_exist == 0:
                #student = Students.objects.get(fname = loginArr[0], lname = loginArr[1], western_id=None)
                request.session['student_id'] = student.student_id
                request.session['student_name'] = loginArr[0]
                return redirect('class-select/')
           
            # else:
            #     #TODO: Change to setup once created
            #     student = Students.objects.create(fname = loginArr[0], lname = loginArr[1],western_id=None)
            #     request.session['student_id'] = student.student_id
            #     request.session['student_name'] = loginArr[0]
            #     return redirect('class-select/')


            if student:
                request.session['student_name'] = loginArr[0]
                request.session['student_id'] = student.student_id
                return redirect('class-select/')
            else:
                messages.error(request, "There was an issue creating your student record.")
                return render(request, 'monitor/index.html') #return to the login page
            
            #TODO finish this section, send error message 
        
        elif not login.isdigit() or len(login) != 7:  #check to make sure id is 7 numbers and all numbers
            messages.error(request, "Please re-enter ID - must be 7 numbers")
            return render(request, 'monitor/index.html')
        
        
    else:
        return render(request, 'monitor/index.html')

#------------------------------------------------------------------------
#Success Redirect
#------------------------------------------------------------------------

def success(request):
    name = request.session.pop('student_name', None)
    student_id = request.session.pop('student_id', None)
    return render(request, 'monitor/success.html')

#------------------------------------------------------------------------
#Select what class you are here for
#------------------------------------------------------------------------

def class_check(request):
    # student_name = request.session.get('student_name')
    student_id = request.session.get('student_id')
    print(str(student_id))
    student = Students.objects.get(student_id=student_id)

    #we want to grab the checkin object and see if it exists...
    signed_in = Checkin.objects.filter(
            student=student, 
            checkout_time__isnull=True
        ).exists()

    if signed_in:
        #if the checkin object exists, for what class?
        check_in = Checkin.objects.filter(
            student=student, 
            checkout_time__isnull=True
        ).first()

    if request.method == 'POST':
        course = request.POST.get('selected_course')
        print(course)
        print(student_id)
        action = request.POST.get('action')
        if action == 'checkin':
            try:
                student = Students.objects.get(student_id=student_id)
                class_obj = Class.objects.get(class_id=course)
                # Create the checkin record
                checkin = Checkin.objects.create(
                    checkin_time=timezone.now(),
                    student=student,
                    class_field=class_obj
                )

                messages.success(request, f'Thanks for checking in to {class_obj.class_name}, {request.session.get("student_name")}!')
                messages.info(request, 'Please come back to check out when you are done!')
                return redirect('monitor:success')
            except (Students.DoesNotExist, Class.DoesNotExist) as e:
            
                print("Student signed in!")
                return redirect('/monitor/class-check/')
        elif action == 'checkout':
            try:
                student = Students.objects.get(student_id=student_id)
                class_obj = Class.objects.get(class_id=course)

                print(str(student), str(class_obj))
                checkin = Checkin.objects.filter(student=student, checkout_time__isnull=True).first()
                checkin.checkout_time = timezone.now()
                checkin.save()

                messages.success(request, f'Thanks for checking out of {checkin.class_field.class_name}, {request.session.get("student_name")}!')
                messages.info(request, 'Leave a review of your experience?')
                return redirect('monitor:success')
            except (Students.DoesNotExist, Class.DoesNotExist) as e:
            
                print("Student signed in!")
                return redirect('/monitor/class-check/')
        elif action == 'switch':
            #this is where we want to just swap the class checked in with the new selected class.
                student = Students.objects.get(student_id=student_id)
                class_obj = Class.objects.get(class_id=course)

                print("trying to switch!!")
                #this is where we want to just swap the class checked in with the new selected class.
                checkin = Checkin.objects.filter(student=student, checkout_time__isnull=True).first()
                checkin.checkout_time = timezone.now()
                checkin.save()

                # Create the checkin record
                checkin = Checkin.objects.create(
                    checkin_time=timezone.now(),
                    student=student,
                    class_field=class_obj
                )
                
                messages.success(request, f'Thanks for checking in to {class_obj.class_name}, {request.session.get("student_name")}!')
                messages.info(request, 'Please come back to check out when you are done!')
                return redirect('monitor:success')
        elif action == 'addclass':
            #take back to setup
                return redirect('/monitor/class-select/')


    student = Students.objects.get(student_id=student_id)

    student_classes = student.classes.all()
        # Now you have all the classes this student is associated with
    context = {
            'signed_in': signed_in,
            'student': student,
            'classes': student_classes,
            'student_name': request.session.get('student_name', '')
    }
    # if not student_id:
    #     return redirect('index')
        


    return render(request, 'monitor/class_check.html', context)

    

#------------------------------------------------------------------------
#Initial Setup Class Page
#------------------------------------------------------------------------
def class_select(request):
    #grab stored login
    student_id = request.session.get('student_id')

    student = Students.objects.filter(student_id = int(student_id)).first()

    student_classes = student.classes.all()
    # if not student_id:
    #     return redirect('index')  # Redirect if no student in session

    if request.method == 'POST':
        # This gets all selected course checkboxes as a list
        selected_courses = request.POST.getlist('selected_course')
        
        # Now selected_courses is a list containing all the checked values
        print(f"Selected courses: {selected_courses}")
        for course_name in selected_courses:
            try:
                # Get the class object
                class_obj = Class.objects.get(class_name=course_name)
                student.classes.add(class_obj)
                
            except Class.DoesNotExist:
                # Handle case where class doesn't exist
                course_number = course_name[-3:]
                print(f"Class with name {course_name} does not exist")
                class_obj = Class.objects.create(class_name=course_name, class_number = course_number)
                student.classes.add(class_obj)
        
        # Optionally, save the student to ensure changes are committed
        student.save()
        print("attempting to redirect")
        return redirect('/monitor/class-check/')
            
        #for each selected course
            #create StudentClass joint thingy
        
        #redirect to class_check

    cached_key = 'western_course'
    cached_data = cache.get(cached_key)
    subjects = ["Mathematics", "Physics", "Computer Science", "Engineering"]

    if cached_data is None:
        try:
            url = "https://apps.western.edu/cs/undergrad_search"


            # need to introduce dynamism for filter value
            payload = json.dumps({
            "query": {
                "filters": [
                {
                    "field": "Standard_Term",
                    "value": "Spring 2025 Semester",
                    "include": "True"
                }
                ],
                "searches": [
                {
                    "field": "Course",
                    "value": ""
                },
                {
                    "field": "Prerequisite",
                    "value": ""
                },
                {
                    "field": "Course_Tags",
                    "value": ""
                },
                {
                    "field": "Subject",
                    "value": ""
                },
                {
                    "field": "Instructors",
                    "value": ""
                },
                {
                    "field": "Name",
                    "value": ""
                }
                ]
            }
            })
            headers = {
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            # print(response.text)

            courses = response.json()

        except requests.RequestException as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)

        # Subjects of interest

        # Use a dictionary to track unique courses
        unique_courses = {}

        for course in courses:
            subject = course.get('Subject', 'Other')
            course_number = course.get("Course_Number", 0)
            
            # Create a unique identifier for the course
            course_key = f"{subject}_{course_number}"
            
            # Only add the course if it hasn't been seen before
            if subject in subjects and course_key not in unique_courses:
                unique_courses[course_key] = course

        # Convert unique courses to a list
        llcs = list(unique_courses.values())
        cache.set(cached_key, llcs, 86400)
    else:
        llcs = cached_data

    name = request.session.get('student_name')
    if name == None:
        name = ""


    array = []
    for student_class in student_classes:
        array.append(student_class.class_name)

    print(array)
    context = {
        'student_name': name,
        'courses': llcs,  # Full list of unique courses
        'yours': llcs[:5],  # First 5 unique courses
        'subjects': subjects,
        'classes': array
    }

    return render(request, 'monitor/class_select.html', context)



    
