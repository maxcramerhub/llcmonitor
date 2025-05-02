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
from django.views.decorators.csrf import csrf_exempt
from datetime import time
from pytz import timezone
import dateutil.parser
from django.core.paginator import Paginator
import pytz

mountain_tz = timezone('America/Denver')
# ------------------------------------------------------------------------
# CSV Export
# ------------------------------------------------------------------------

import csv
from django.http import HttpResponse
from django.utils import timezone

def export_checkins(request):
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="checkins.csv"'

    writer = csv.writer(response)
    writer.writerow(['Check In Time', 'Check Out Time', 'Duration (mins)', 'Subject', 'Class'])

    # Get all check-ins
    checkins = Checkin.objects.select_related('class_field').all()
    
    # Get Mountain timezone
    mountain_tz = pytz.timezone('America/Denver')

    for checkin in checkins:
        # Convert times to Mountain timezone
        checkin_time = checkin.checkin_time.astimezone(mountain_tz) if checkin.checkin_time else None
        checkout_time = checkin.checkout_time.astimezone(mountain_tz) if checkin.checkout_time else None
        
        # Calculate duration in minutes
        duration = None
        if checkin_time and checkout_time:
            duration = int((checkout_time - checkin_time).total_seconds() / 60)

        writer.writerow([
            checkin_time.strftime('%Y-%m-%d %I:%M %p') if checkin_time else 'None',
            checkout_time.strftime('%Y-%m-%d %I:%M %p') if checkout_time else 'None',
            duration if duration is not None else 'None',
            checkin.class_field.subject,
            checkin.class_field.class_name
        ])

    return response

# ------------------------------------------------------------------------
# Visualization better comments
# ------------------------------------------------------------------------

from django.db.models import Count, F, Avg, ExpressionWrapper, DateTimeField
from django.db.models.functions import TruncDate, ExtractWeekDay, Concat, ExtractHour
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


# ------------------------------------------------------------------------
# Visualize Data in Admin side
# ------------------------------------------------------------------------    


def visualize(request):
    if is_admin_logged_in(request):
        # get completed check-ins only
        data = Checkin.objects.filter(checkout_time__isnull=False).all()
        
        # --- daily check-ins chart data ---
        daily_checkins = Checkin.objects.filter(checkout_time__isnull=False)\
            .annotate(weekday=ExtractWeekDay('checkin_time'))\
            .values('weekday')\
            .annotate(count=Count('checkin_id'))\
            .order_by('weekday')
        
        # prepare weekday labels and initialize data array
        weekdays = [ 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
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
            'tablist': ['Today', 'Weekly', 'Monthly', 'Semester'],
            'datelist': list(duration_dates)
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
        ).select_related('class_field').first()  # Use select_related to get the class info

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

    context = {
            'signed_in': signed_in,
            'student': student,
            'classes': student_classes,
            'student_name': request.session.get('student_name', ''),
            'checkout_status': checkout_status,
            'check_in': check_in if signed_in else None
    }

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

            # Get current semester dynamically
            current_semester = get_current_semester()

            payload = json.dumps({
            "query": {
                "filters": [
                {
                    "field": "Standard_Term",
                    "value": current_semester,
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

            courses = response.json()

        except requests.RequestException as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)

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
        cache.set(cached_key, llcs, 86400)  # Cache for 24 hours
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
#AJAX for filling admin data
#------------------------------------------------------------------------
@csrf_exempt
def fetch_checkins(request):
    import dateutil.parser

...

@csrf_exempt
def fetch_checkins(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            timeframe = body.get('timeframe')
            selected_date = body.get('selected_date')

            if not timeframe:
                return JsonResponse({'error': 'Missing timeframe'}, status=400)

            if not selected_date:
                selected_date = timezone.now().date()
            else:
                # 🌟 Safer parsing
                if isinstance(selected_date, str):
                    try:
                        parsed_date = dateutil.parser.parse(selected_date)
                        selected_date = parsed_date.date()
                    except Exception:
                        return JsonResponse({'error': 'Invalid selected_date format'}, status=400)

            checkins_query = Checkin.objects.filter(checkout_time__isnull=False)

            if timeframe == 'Today':
                start = datetime.combine(selected_date, time.min)
                end = datetime.combine(selected_date, time.max)
            elif timeframe in ['Weekly', 'Monthly', 'Semester']:
                if timeframe == 'Weekly':
                    start_date = selected_date - timedelta(days=6)
                elif timeframe == 'Monthly':
                    start_date = selected_date.replace(day=1)
                else:
                    if selected_date.month <= 6:
                        start_date = selected_date.replace(month=1, day=1)
                    else:
                        start_date = selected_date.replace(month=7, day=1)
                start = datetime.combine(start_date, time.min)
                end = datetime.combine(selected_date, time.max)
            else:
                return JsonResponse({'error': 'Invalid timeframe'}, status=400)

            # Localize times
            start = mountain_tz.localize(start)
            end = mountain_tz.localize(end)

            checkins_query = checkins_query.filter(checkin_time__range=(start, end))

            if timeframe == 'Today':
                breakdown = checkins_query.annotate(
                    local_checkin_time=ExpressionWrapper(
                        F('checkin_time') + timedelta(hours=-6),  # shift manually for MDT
                        output_field=DateTimeField()
                    )
                ).annotate(
                    hour=ExtractHour('local_checkin_time')
                ).values('hour')\
                .annotate(count=Count('checkin_id'))\
                .order_by('hour')

                labels = [f"{h}:00" for h in range(24)]
                data = [0] * 24
                for entry in breakdown:
                    data[entry['hour']] = entry['count']
            else:
                breakdown = checkins_query.annotate(date=TruncDate('checkin_time'))\
                    .values('date')\
                    .annotate(count=Count('checkin_id'))\
                    .order_by('date')

                labels = []
                data = []
                current = start.date()
                while current <= selected_date:
                    labels.append(current.strftime('%Y-%m-%d'))
                    data.append(0)
                    current += timedelta(days=1)

                label_index = {d: i for i, d in enumerate(labels)}
                for entry in breakdown:
                    idx = label_index[entry['date'].strftime('%Y-%m-%d')]
                    data[idx] = entry['count']

            # Table entries
            checkins_serialized = []
            for checkin in checkins_query.select_related('class_field'):
                checkins_serialized.append({
                    'checkin_time': checkin.checkin_time.isoformat() if checkin.checkin_time else '',
                    'checkout_time': checkin.checkout_time.isoformat() if checkin.checkout_time else '',
                    'class_subject': checkin.class_field.subject if checkin.class_field else '',
                    'class_name': checkin.class_field.class_name if checkin.class_field else ''
                })

            # Top Classes
            top_classes = checkins_query.values('class_field__class_name')\
                .annotate(count=Count('checkin_id'))\
                .order_by('-count')[:5]
            classLabels = [c['class_field__class_name'] for c in top_classes]
            classCounts = [c['count'] for c in top_classes]

            # Average durations
            avg_durations = checkins_query.annotate(duration=F('checkout_time') - F('checkin_time'))\
                .annotate(date=TruncDate('checkin_time'))\
                .values('date')\
                .annotate(avg_duration=Avg('duration'))\
                .order_by('date')

            durationLabels = []
            durationHours = []
            for entry in avg_durations:
                durationLabels.append(entry['date'].strftime('%Y-%m-%d'))
                durationHours.append(entry['avg_duration'].total_seconds() / 3600)

            return JsonResponse({
                'labels': labels,
                'data': data,
                'checkins': checkins_serialized,
                'classLabels': classLabels,
                'classCounts': classCounts,
                'durationLabels': durationLabels,
                'durationHours': durationHours,
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

#------------------------------------------------------------------------
#'Secure' Admin Login
#------------------------------------------------------------------------

def admin_login(request):
    if request.method == 'POST':
        requestUser = request.POST.get('username')
        requestPass = request.POST.get('password')
        user = Faculty.objects.filter(username=requestUser).first()
        
        if user and user.password == requestPass:
            # Store user info in session
            request.session['faculty_id'] = user.faculty_id
            request.session['faculty_name'] = f"{user.fname} {user.lname}"
            request.session['faculty_username'] = user.username
            messages.success(request, f'Welcome back, {user.fname}!')
            return redirect('monitor:visualize')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'monitor/admin_login.html')
    
    return render(request, 'monitor/admin_login.html')

def admin_logout(request):
    if request.method == 'POST':
        # Clear session data
        request.session.flush()
        messages.info(request, 'You have been logged out successfully')
        return redirect('monitor:admin_login')
    
    return redirect('monitor:admin_login')

# Helper function to check if user is logged in
def is_admin_logged_in(request):
    return 'faculty_id' in request.session


#------------------------------------------------------------------------
# Tutor Management / Admin Management 
#------------------------------------------------------------------------    

def tutor_management(request):
    if not is_admin_logged_in(request):
        return render(request, 'monitor/admin_login.html')
    
    tutors = Tutor.objects.all()
    return render(request, 'monitor/tutor_management.html', {'tutors': tutors})

def add_tutor(request):
    if not is_admin_logged_in(request):
        return render(request, 'monitor/admin_login.html')
    
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        western_id = request.POST.get('western_id')
        
        tutor = Tutor.objects.create(
            fname=fname,
            lname=lname,
            western_id=western_id
        )
        messages.success(request, f'Tutor {tutor.fname} {tutor.lname} added successfully!')
        return redirect('monitor:tutor_management')
    
    return render(request, 'monitor/tutor_form.html', {'action': 'Add'})

def edit_tutor(request, tutor_id):
    if not is_admin_logged_in(request):
        return render(request, 'monitor/admin_login.html')
    
    tutor = Tutor.objects.get(tutor_id=tutor_id)
    
    if request.method == 'POST':
        tutor.fname = request.POST.get('fname')
        tutor.lname = request.POST.get('lname')
        tutor.western_id = request.POST.get('western_id')
        tutor.save()
        
        messages.success(request, f'Tutor {tutor.fname} {tutor.lname} updated successfully!')
        return redirect('monitor:tutor_management')
    
    return render(request, 'monitor/tutor_form.html', {'tutor': tutor, 'action': 'Edit'})

def delete_tutor(request, tutor_id):
    if not is_admin_logged_in(request):
        return render(request, 'monitor/admin_login.html')
    
    tutor = Tutor.objects.get(tutor_id=tutor_id)
    tutor_name = f"{tutor.fname} {tutor.lname}"
    tutor.delete()
    
    messages.success(request, f'Tutor {tutor_name} deleted successfully!')
    return redirect('monitor:tutor_management')

def admin_management(request):
    if not is_admin_logged_in(request):
        return render(request, 'monitor/admin_login.html')
    
    admins = Faculty.objects.all()
    return render(request, 'monitor/admin_management.html', {'admins': admins})

def add_admin(request):
    if not is_admin_logged_in(request):
        return render(request, 'monitor/admin_login.html')
    
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if username already exists
        if Faculty.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose a different username.')
            return render(request, 'monitor/admin_form.html', {'action': 'Add'})
        
        admin = Faculty.objects.create(
            fname=fname,
            lname=lname,
            username=username,
            password=password
        )
        messages.success(request, f'Admin {admin.fname} {admin.lname} added successfully!')
        return redirect('monitor:admin_management')
    
    return render(request, 'monitor/admin_form.html', {'action': 'Add'})

def edit_admin(request, admin_id):
    if not is_admin_logged_in(request):
        return render(request, 'monitor/admin_login.html')
    
    admin = Faculty.objects.get(faculty_id=admin_id)
    
    if request.method == 'POST':
        # Check if username is being changed and if it already exists
        new_username = request.POST.get('username')
        if new_username != admin.username and Faculty.objects.filter(username=new_username).exists():
            messages.error(request, 'Username already exists. Please choose a different username.')
            return render(request, 'monitor/admin_form.html', {'admin': admin, 'action': 'Edit'})
        
        admin.fname = request.POST.get('fname')
        admin.lname = request.POST.get('lname')
        admin.username = new_username
        admin.password = request.POST.get('password')
        admin.save()
        
        messages.success(request, f'Admin {admin.fname} {admin.lname} updated successfully!')
        return redirect('monitor:admin_management')
    
    return render(request, 'monitor/admin_form.html', {'admin': admin, 'action': 'Edit'})

def delete_admin(request, admin_id):
    if not is_admin_logged_in(request):
        return render(request, 'monitor/admin_login.html')
    
    # Prevent deleting the currently logged-in admin
    if request.session.get('faculty_id') == admin_id:
        messages.error(request, 'You cannot delete your own account while logged in.')
        return redirect('monitor:admin_management')
    
    admin = Faculty.objects.get(faculty_id=admin_id)
    admin_name = f"{admin.fname} {admin.lname}"
    admin.delete()
    
    messages.success(request, f'Admin {admin_name} deleted successfully!')
    return redirect('monitor:admin_management')


#------------------------------------------------------------------------
# Get Current Semester Helper Function and Admin Reviews
#------------------------------------------------------------------------        

def get_current_semester():
    current_date = timezone.now()
    month = current_date.month
    year = current_date.year

    #Get current date via timezone, then calc month and year, then auto determine semester for API call
    
    if 1 <= month <= 5:  # Spring semester
        return f"Spring {year} Semester"
    elif 6 <= month <= 8:  # Summer semester
        return f"Summer {year} Semester"
    else:  # Fall semester
        return f"Fall {year} Semester"

def admin_reviews(request):
    if not is_admin_logged_in(request):
        return render(request, 'monitor/admin_login.html')

      #Reviews with pagination :)
    
    reviews_list = Reviews.objects.select_related('tutor').prefetch_related('tutor__classes').all().order_by('-tutorreviews__date_of_review')
    paginator = Paginator(reviews_list, 10)
    page = request.GET.get('page')
    reviews = paginator.get_page(page)
    
    return render(request, 'monitor/admin_reviews.html', {'reviews': reviews})