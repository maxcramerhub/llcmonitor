from django.db import models

class Students(models.Model):
    student_id = models.AutoField(primary_key=True)
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    western_id = models.IntegerField(null=True, blank=True, unique=True)

    classes = models.ManyToManyField('Class', related_name='students')

    class Meta:
        managed = True
        db_table = 'Students'

    def __str__(self):
        return f"{self.fname} {self.lname}"

class Class(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=200)
    instructor = models.CharField(max_length=200)
    semester = models.CharField(max_length=100)
    class_number = models.CharField(max_length = 3)
    subject = models.CharField(max_length = 16)

    class Meta:
        managed = True
        db_table = 'Class'

    def __str__(self):
        return self.class_name

class Faculty(models.Model):
    faculty_id = models.AutoField(primary_key=True)
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = True
        db_table = 'Faculty'

    def __str__(self):
        return f"{self.fname} {self.lname}"

class Checkin(models.Model):
    checkin_id = models.AutoField(primary_key=True)
    checkin_time = models.DateTimeField(blank=True, null=True)
    checkout_time = models.DateTimeField(blank=True, null=True)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    class_field = models.ForeignKey(Class, on_delete=models.CASCADE, db_column='class_id')

    class Meta:
        managed = True
        db_table = 'CheckIn'

class StudentCheckin(models.Model):
    student = models.OneToOneField(Students, on_delete=models.CASCADE)
    class_field = models.ForeignKey(Class, on_delete=models.CASCADE, db_column='class_id')
    checkin_time = models.DateTimeField(blank=True, null=True)
    checkout_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Student_CheckIN'

class Tutor(models.Model):
    tutor_id = models.AutoField(primary_key=True)
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    western_id = models.CharField(max_length=50, blank=True, null=True)
    classes = models.ManyToManyField(Class, related_name='tutors')

    class Meta:
        managed = True
        db_table = 'Tutor'

    def __str__(self):
        return f"{self.fname} {self.lname}"

class Reviews(models.Model):
    review_id = models.AutoField(primary_key=True)
    written_review = models.TextField()
    tutor = models.ForeignKey(Tutor, 
    on_delete=models.CASCADE, 
    related_name='reviews',
    null=True, #make it so we can allow null value for tutor 
    blank=True)
    rating = models.IntegerField(null=True, blank=True)
    class_reviewed = models.ForeignKey(Class, 
    on_delete=models.CASCADE, 
    related_name='reviews',
    null=True, 
    blank=True)
    subject_reviewed = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'Reviews'

class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    day = models.CharField(max_length=50)
    week = models.CharField(max_length=50)
    month = models.CharField(max_length=50)
    year = models.IntegerField()
    semester = models.CharField(max_length=100)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='schedules')

    class Meta:
        managed = True
        db_table = 'Schedule'

class TutorReviews(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    review = models.ForeignKey(Reviews, on_delete=models.CASCADE)
    date_of_review = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Tutor_Reviews'

class TutorSchedule(models.Model):
    tutor = models.OneToOneField(Tutor, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'Tutor_Schedule'

class EmailSettings(models.Model):
    # Email server settings
    email_host = models.CharField(max_length=100, default='smtp.office365.com')
    email_port = models.IntegerField(default=587)
    email_use_tls = models.BooleanField(default=True)
    email_host_user = models.EmailField(default='your-email@domain.com')
    email_host_password = models.CharField(max_length=255, help_text='App password for 2FA accounts')
    
    # Notification settings
    admin_email = models.EmailField(default='admin@domain.com')
    from_email = models.EmailField(default='noreply@domain.com')
    
    # Feature toggles
    enable_error_notifications = models.BooleanField(default=True)
    enable_csv_email_exports = models.BooleanField(default=True)
    enable_weekly_summaries = models.BooleanField(default=False)
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True)

    class Meta:
        managed = True
        db_table = 'EmailSettings'
        verbose_name = 'Email Settings'
        verbose_name_plural = 'Email Settings'

    def __str__(self):
        return f"Email Settings (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings record exists
        if not self.pk and EmailSettings.objects.exists():
            raise ValueError("Only one EmailSettings instance is allowed")
        super().save(*args, **kwargs)