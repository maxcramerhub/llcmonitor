import logging
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.utils import timezone
from io import StringIO
import csv
import traceback

logger = logging.getLogger(__name__)

def send_csv_export_email(recipient_email, data, filename, data_type="Check-ins"):
    """
    Send CSV data as email attachment
    
    Args:
        recipient_email: Email address to send to
        data: QuerySet or list of data to export
        filename: Name for the CSV file
        data_type: Type of data being exported (for email subject)
    """
    try:
        # Create CSV content
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        
        if data_type == "Check-ins":
            writer.writerow(['Check In Time', 'Check Out Time', 'Duration (mins)', 'Subject', 'Class'])
            
            from pytz import timezone as pytz_timezone
            mountain_tz = pytz_timezone('America/Denver')
            
            for checkin in data:
                checkin_time = checkin.checkin_time.astimezone(mountain_tz) if checkin.checkin_time else None
                checkout_time = checkin.checkout_time.astimezone(mountain_tz) if checkin.checkout_time else None
                
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
        
        # Create email
        subject = f'LLC {data_type} Export - {timezone.now().strftime("%Y-%m-%d")}'
        body = f"""
        Hello,
        
        Your {data_type.lower()} export has been generated and is attached to this email.
        
        Export Details:
        - Generated: {timezone.now().strftime("%Y-%m-%d %I:%M %p MST")}
        - Total Records: {len(data) if hasattr(data, '__len__') else data.count()}
        - File Format: CSV
        
        Best regards,
        Lambda Learning Center System
        """
        
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.FROM_EMAIL,
            to=[recipient_email],
        )
        
        # Attach CSV file
        email.attach(filename, csv_buffer.getvalue(), 'text/csv')
        
        # Send email
        email.send()
        
        logger.info(f"CSV export emailed successfully to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send CSV export email: {str(e)}")
        send_error_notification(f"CSV Export Email Failed", str(e))
        return False

def send_error_notification(error_type, error_message, request=None):
    """
    Send error notification to administrators
    
    Args:
        error_type: Type/category of error
        error_message: Detailed error message
        request: HTTP request object (optional)
    """
    try:
        subject = f'LLC System Error: {error_type}'
        
        # Gather system info
        system_info = f"""
        Error Type: {error_type}
        Time: {timezone.now().strftime("%Y-%m-%d %I:%M %p MST")}
        
        Error Details:
        {error_message}
        
        """
        
        # Add request info if available
        if request:
            system_info += f"""
        Request Information:
        - URL: {request.build_absolute_uri()}
        - Method: {request.method}
        - User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}
        - IP Address: {request.META.get('REMOTE_ADDR', 'Unknown')}
        
        """
        
        # Add stack trace if available
        system_info += f"""
        Stack Trace:
        {traceback.format_exc()}
        """
        
        # Send notification email
        send_mail(
            subject=subject,
            message=system_info,
            from_email=settings.FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        logger.info(f"Error notification sent for: {error_type}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send error notification: {str(e)}")
        return False

def send_weekly_summary_email():
    """
    Send weekly summary of system activity to administrators
    """
    try:
        from .models import Checkin, Reviews
        from django.db.models import Count
        from datetime import timedelta
        
        # Calculate date range for past week
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        
        # Get statistics
        checkins_count = Checkin.objects.filter(
            checkin_time__range=[start_date, end_date]
        ).count()
        
        reviews_count = Reviews.objects.filter(
            tutorreviews__date_of_review__range=[start_date, end_date]
        ).count()
        
        # Top classes this week
        top_classes = Checkin.objects.filter(
            checkin_time__range=[start_date, end_date]
        ).values('class_field__class_name', 'class_field__subject').annotate(
            count=Count('checkin_id')
        ).order_by('-count')[:5]
        
        subject = f'LLC Weekly Summary - {start_date.strftime("%m/%d")} to {end_date.strftime("%m/%d")}'
        
        body = f"""
        Lambda Learning Center Weekly Summary
        
        Period: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}
        
        📊 Activity Summary:
        - Total Check-ins: {checkins_count}
        - Total Reviews: {reviews_count}
        
        🔥 Top Classes This Week:
        """
        
        for i, cls in enumerate(top_classes, 1):
            body += f"\n{i}. {cls['class_field__subject']} - {cls['class_field__class_name']} ({cls['count']} check-ins)"
        
        body += f"""
        
        📈 System Health: All systems operational
        
        Generated automatically by LLC Monitor System
        {timezone.now().strftime("%Y-%m-%d %I:%M %p MST")}
        """
        
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        logger.info("Weekly summary email sent successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send weekly summary: {str(e)}")
        return False

def send_test_email(email_config):
    """
    Send a test email using the provided email configuration
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        import django.core.mail.backends.smtp
        
        # Temporarily override Django's email settings
        original_settings = {}
        email_settings = {
            'EMAIL_HOST': email_config.email_host,
            'EMAIL_PORT': email_config.email_port,
            'EMAIL_USE_TLS': email_config.email_use_tls,
            'EMAIL_HOST_USER': email_config.email_host_user,
            'EMAIL_HOST_PASSWORD': email_config.email_host_password,
        }
        
        # Save original settings
        for key, value in email_settings.items():
            if hasattr(settings, key):
                original_settings[key] = getattr(settings, key)
            setattr(settings, key, value)
        
        try:
            # Send test email
            send_mail(
                subject='LLC System - Email Configuration Test',
                message=f'''
This is a test email from your Lambda Learning Center monitoring system.

If you're receiving this email, your email configuration is working correctly!

Configuration Details:
- SMTP Server: {email_config.email_host}:{email_config.email_port}
- From Email: {email_config.from_email}
- TLS Enabled: {email_config.email_use_tls}

Generated at: {timezone.now().strftime("%Y-%m-%d %I:%M %p MST")}
                ''',
                from_email=email_config.from_email,
                recipient_list=[email_config.admin_email],
                fail_silently=False,
            )
            
            logger.info("Test email sent successfully")
            return True
            
        finally:
            # Restore original settings
            for key, value in original_settings.items():
                setattr(settings, key, value)
        
    except Exception as e:
        logger.error(f"Test email failed: {str(e)}")
        return False 