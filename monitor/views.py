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
from django.contrib.auth import authenticate, login
from django.urls import reverse

# ------------------------------------------------------------------------
# CSV Export
# ------------------------------------------------------------------------

import csv
from django.http import HttpResponse
from django.utils import timezone

def export_checkins(request):
    # create response for csv download
    response = HttpResponse(content_type='text/csv')
    
    # set filename with timestamp
    current_time = timezone.now().strftime('%Y-%m-%d')
    response['Content-Disposition'] = f'attachment; filename="checkins_{current_time}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Check-in ID', 
        'Student Name', 
        'Class', 
        'Check-in Time', 
        'Check-out Time', 
        'Duration (hours)'
    ])
    
    # get completed check-ins
    checkins = Checkin.objects.filter(checkout_time__isnull=False).all()
    
    # write data rows
    for checkin in checkins:
        # calculate duration in hours
        if checkin.checkin_time and checkin.checkout_time:
            duration = (checkin.checkout_time - checkin.checkin_time).total_seconds() / 3600
        else:
            duration = 0
        
        # get class identifier (handle different model structures)
        try:
            # first try to get id directly
            class_identifier = f"{checkin.class_field.class_id}"
        except AttributeError:
            try:
                # try using pk if id doesn't exist
                class_identifier = f"Class #{checkin.class_field.pk}"
            except AttributeError:
                # fallback to using the class object string representation
                class_identifier = f"Class #{checkin.class_field}"
            
        # write row for each checkin
        writer.writerow([
            checkin.checkin_id,
            f"{checkin.student.fname} {checkin.student.lname}",
            class_identifier,
            checkin.checkin_time.astimezone('America/Denver'),
            checkin.checkout_time.astimezone('America/Denver'),
            f"{duration:.2f}"  # format to 2 decimal places
        ])
    
    return response

# ------------------------------------------------------------------------
# Visualization better comments
# ------------------------------------------------------------------------

from django.db.models import Count, F, Avg
from django.db.models.functions import TruncDate, ExtractWeekDay, Concat
from django.db.models.expressions import Value
from django.db.models.fields import CharField
from datetime import datetime, timedelta
from .forms import ReviewForm
from django.utils.timezone import now

def thank_you(request):
    return render(request, 'thank_you.html')

def leave_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save()
            print(f"Review saved: {review}")

            tutor_review = TutorReviews.objects.create(
                tutor= review.tutor,
                review=review,
                date_of_review=now()
            )

            print(f"TutorReview saved: {tutor_review}")
            print(f"Redirecting to: monitor:index")
            print(f"Form data: {form.cleaned_data}")

            # return redirect('monitor:index')

            print(f"Saved Review ID: {review.review_id}")
            print(f"Tutor FK: {review.tutor}")
            print(f"Rating: {review.rating}")




            return redirect('monitor:thank_you')  # or to a 'thank you' page
        
        else:
            print(f"Form errors: {form.errors}")
            print(f"Form is not valid.")

    else:
        form = ReviewForm()

    return render(request, 'monitor/review_form.html', {'form': form})


def submit_review(request):

    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            
            print(f"Review saved: {review}")
            
            # Add a success message
            # messages.success(request, 'Your review has been submitted successfully!')
            
            # return render(request, 'success.html', {'form': ReviewForm(), 'message': 'Review submitted successfully!'})
            
            return redirect('thank_you.html')
            
            # return redirect('review_success')  # Redirect to success page
    else:
        form = ReviewForm()

    return render(request, 'success.html', {'form': form})


def visualize(request):
    if loginUser:
        # get completed check-ins only
        data = Checkin.objects.filter(checkout_time__isnull=False).all()
        
        # --- daily check-ins chart data ---
        daily_checkins = Checkin.objects.filter(checkout_time__isnull=False)\
            .annotate(weekday=ExtractWeekDay('checkin_time'))\
            .values('weekday')\
            .annotate(count=Count('checkin_id'))\
            .order_by('weekday')
        
        # prepare weekday labels and initialize data array
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_data = [0] * 7  # zero placeholder for each day
        
        # map database results to correct weekday position
        for entry in daily_checkins:
            # convert django's 1-7 (Sun-Sat) to 0-6 (Mon-Sun)
            day_index = entry['weekday'] % 7 - 1
            if day_index == -1:  # handle sunday
                day_index = 6
            daily_data[day_index] = entry['count']
        
        # --- top classes chart data ---
        top_classes = Checkin.objects.filter(checkout_time__isnull=False)\
            .values('class_field__class_name')\
            .annotate(count=Count('checkin_id'))\
            .order_by('-count')[:5]
        
        # prepare class names and counts for charts
        class_names = [f"{c['class_field__class_name']}" for c in top_classes]
        class_counts = [c['count'] for c in top_classes]
        
        # --- top students chart data ---
        top_students = Checkin.objects.filter(checkout_time__isnull=False)\
            .annotate(full_name=Concat('student__fname', Value(' '), 'student__lname', 
                                    output_field=CharField()))\
            .values('full_name', 'student')\
            .annotate(count=Count('checkin_id'))\
            .order_by('-count')[:5]
        
        # prepare student names and counts for charts
        student_names = [s['full_name'] for s in top_students]
        student_counts = [s['count'] for s in top_students]
        
        # --- average duration chart data ---
        avg_durations = Checkin.objects.filter(checkout_time__isnull=False)\
            .annotate(date=TruncDate('checkin_time'),
                        duration=F('checkout_time') - F('checkin_time'))\
            .values('date')\
            .annotate(avg_duration=Avg('duration'))\
            .order_by('date')
        
        # prepare duration dates and hours for charts
        duration_dates = [entry['date'].strftime('%Y-%m-%d') for entry in avg_durations]
        duration_hours = [entry['avg_duration'].total_seconds() / 3600 for entry in avg_durations]
        
        # build context with all chart data
        context = {
            'data': data,
            'daily_data': json.dumps(daily_data),
            'weekdays': json.dumps(weekdays),
            'class_names': json.dumps(class_names),
            'class_counts': json.dumps(class_counts),
            'student_names': json.dumps(student_names),
            'student_counts': json.dumps(student_counts),
            'duration_dates': json.dumps(duration_dates),
            'duration_hours': json.dumps(duration_hours),
            'tablist': ['Today', 'Weekly', 'Monthly', 'Semester', 'Tools']
        }
        
        return render(request, 'monitor/visualize.html', context)
    else:
        return render(request, 'monitor/admin_login.html')
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
        # so this if all(x.isnumeric() for x in login and len(login) == 6):

        # if all(x.isnumeric() for x in login):
        if login[0] == ';':
            login = login[9:15]

        if login.isdigit() and len(login) == 6:  # 

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
            elif student and class_exist == 0:
                student = Students.objects.get(fname = loginArr[0], lname = loginArr[1], western_id=None)
                request.session['student_id'] = student.student_id
                request.session['student_name'] = loginArr[0]
                return redirect('class-select/', type)
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
        
        elif not login.isdigit() or len(login) != 6:  #check to make sure id is 6 numbers and all numbers
            messages.error(request, "Please re-enter ID - must be 6 numbers")
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

    checkout_status = False 

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
                if request.session.get("student_name") != None:
                    name = request.session.get("student_name")
                else:
                    name = "Student"

                messages.success(request, f'Thanks for checking in to {class_obj.class_name}, {name}!')
                messages.info(request, 'Please come back to check out when you are done!')
                return redirect('monitor:success')
            except (Students.DoesNotExist, Class.DoesNotExist) as e:
            
                print("Student signed in!")
                return redirect('/class-check/')
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

                checkout_status = True #adding flag so that we can only display leave a review on checkout page

                return redirect(reverse('monitor:review_success') + '?checkout_status=True')
            except (Students.DoesNotExist, Class.DoesNotExist) as e:
            
                print("Student signed in!")
                return redirect('/class-check/')
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
                return redirect('/class-select/')


    student = Students.objects.get(student_id=student_id)

    student_classes = student.classes.all()
        # Now you have all the classes this student is associated with
    context = {
            'signed_in': signed_in,
            'student': student,
            'classes': student_classes,
            'student_name': request.session.get('student_name', ''),
            'checkout_status':checkout_status
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
        for entry in selected_courses:
            course_name, course_number, subject = entry.split('||')
            try:
                # Get the class object
                class_obj = Class.objects.get(class_name=course_name)
                student.classes.add(class_obj)
                
            except Class.DoesNotExist:
                # Handle case where class doesn't exist
                print(f"Class with name {course_name} does not exist")
                class_obj = Class.objects.create(class_name=course_name, class_number = course_number, subject = subject)
                student.classes.add(class_obj)
        
        # Optionally, save the student to ensure changes are committed
        student.save()
        print("attempting to redirect")
        return redirect('/class-check/')
            
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
        name = "Student"


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



#------------------------------------------------------------------------
#'Secure' Admin Login
#------------------------------------------------------------------------

def admin_login(request):
    if request.method == 'POST':
        requestUser = request.POST.get('username')
        requestPass = request.POST.get('password')
        user = Faculty.objects.filter(username = requestUser).first()
        global loginUser
        if user.password == requestPass:
            loginUser = user
            print('login successful')
            return redirect('/visualize/')
        else:
            #redirect back to login with error
            print('Invalid login')
            return render(request, 'monitor/admin_login.html')
    
    return render(request, 'monitor/admin_login.html')

def admin_logout(request):
    if request.method == 'POST':
        global loginUser
        loginUser = None
        return render(request, 'monitor/admin_login.html')