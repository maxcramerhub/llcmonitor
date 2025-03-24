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

    class Meta:
        managed = True
        db_table = 'Tutor'

    def __str__(self):
        return f"{self.fname} {self.lname}"

class Reviews(models.Model):
    review_id = models.AutoField(primary_key=True)
    written_review = models.TextField()
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='reviews')

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
    tutor = models.OneToOneField(Tutor, on_delete=models.CASCADE)
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