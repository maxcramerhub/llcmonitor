from django.shortcuts import render, redirect

from django.http import HttpResponse
import requests
from django.http import JsonResponse
from django.conf import settings
from django.core.cache import cache
from monitor.models import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json

#Enter StuID or Name Sign In Page

def index(request):
    if request.method == 'POST':
        login = request.POST.get('login')

        if all(x.isnumeric() for x in login):

            student = Students.objects.filter(western_id = int(login)).first()
            #If we found a student
            if student:
                return redirect('class-check/')
            else:
                #TODO: Change to setup once created
                student = Students.objects.create(western_id = login)
                request.session['western_id'] = student.western_id
                return redirect('class-select/')

        elif all(x.isalpha() or x.isspace() for x in login):
            loginArr = login.split()
            print(loginArr)
            student = Students.objects.filter(fname = loginArr[0], lname = loginArr[1]).first()
            print(student)
            #Checks to see if student is in db, redirects to class select if in db, index otherwise
            if student is not None:
                return render(request, 'monitor/class_check.html')
            else:
                #TODO: Change to setup once created
                return render(request, 'monitor/class_select.html')
        else:
            return render(request, 'monitor/index.html')
    else:
        return render(request, 'monitor/index.html')

#Success Sign In

def success(request):
    return render(request, 'monitor/success.html')

#Pick Class you are there for

def class_check(request):
    student_id = request.session.get('western_id')

    try: 
        most_recent_checkin = Checkin.objects.filter(student_id=student_id).order_by('-checkin_time').first()
    except e:
        print("NONE FOUND")


    if request.method == 'POST':
        course = request.POST.get('selected_course')
        try:
            student = Students.objects.get(id=student_id)
            class_obj = Class.objects.get(class_id=selected_class_id)
            
            # Create the checkin record
            checkin = Checkin.objects.create(
                checkin_time=timezone.now(),
                student=student,
                class_field=class_obj
            )
            
            # Optionally redirect to a confirmation page
            return redirect('monitor:success')
        except (Students.DoesNotExist, Class.DoesNotExist) as e:
        
            print("Student signed in!")
            return redirect('/monitor/class-check/')


    student = Students.objects.get(western_id=student_id)

    student_classes = student.classes.all()
        # Now you have all the classes this student is associated with
    context = {
            'student': student,
            'classes': student_classes
    }
    # if not student_id:
    #     return redirect('index')
        


    return render(request, 'monitor/class_check.html', context)

    

#Class Setup Page

def class_select(request):
    #grab stored login
    student_id = request.session.get('western_id')

    student = Students.objects.filter(western_id = int(student_id)).first()
    # if not student_id:
    #     return redirect('index')  # Redirect if no student in session

    if request.method == 'POST':
        # This gets all selected course checkboxes as a list
        selected_courses = request.POST.getlist('selected_course')
        
        # Now selected_courses is a list containing all the checked values
        print(f"Selected courses: {selected_courses}")
        for course_id in selected_courses:
            try:
                # Get the class object
                class_obj = Class.objects.get(class_id=course_id)
                student.classes.add(class_obj)

            except Class.DoesNotExist:
                # Handle case where class doesn't exist
                print(f"Class with ID {course_id} does not exist")
                class_obj = Class.objects.create(class_id=course_id)
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


    context = {
        'student_name': 'Max',
        'courses': llcs,  # Full list of unique courses
        'yours': llcs[:5],  # First 5 unique courses
        'subjects': subjects
    }


    #admin info 

    #llcadmin
    #learnbetter

    return render(request, 'monitor/class_select.html', context)



    
