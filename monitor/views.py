from django.shortcuts import render, redirect

from django.http import HttpResponse
import requests
from django.http import JsonResponse
from django.conf import settings
from monitor.models import Class
import json


def index(request):
    return render(request, 'monitor/index.html')

def success(request):
     return render(request, 'monitor/success.html')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def class_check(request):
    #we want to grab the classes associated with the student
    #then we show them as options
    #then we can submit a post with the selected class
    #create the checkin object with class, student, checkin time

    context = {
        'student_name': 'Max'

    }
    return render(request, 'monitor/class_check.html', context)

#use checkboxes to make super simple

def class_select(request):
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

        print(response.text)

        courses = response.json()

    except requests.RequestException as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


    if request.method == 'POST':
        print("Student signed in!")
        return redirect('monitor:success')

    # Subjects of interest
    subjects = ["Mathematics", "Physics", "Computer Science", "Engineering"]

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

    context = {
        'student_name': 'Max',
        'courses': llcs,  # Full list of unique courses
        'yours': llcs[:5],  # First 5 unique courses
        'subjects': subjects
    }

    Class.objects.create(class_name="TEST")

    return render(request, 'monitor/class_select.html', context)



    
