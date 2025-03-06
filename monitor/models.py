from django.db import models

class Checkin(models.Model):
    checkin_id = models.AutoField(primary_key=True, blank=True, null=False)
    checkin_time = models.DateTimeField(blank=True, null=True)
    checkout_time = models.DateTimeField(blank=True, null=True)
    student = models.ForeignKey('Students', models.DO_NOTHING)
    class_field = models.ForeignKey('Class', models.DO_NOTHING, db_column='class_id', to_field='class_id')  # Field renamed because it was a Python reserved word.

    class Meta:
        managed = False
        db_table = 'CheckIn'


class Class(models.Model):
    class_id = models.AutoField(db_column='class_ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    class_name = models.TextField()
    instructor = models.TextField()
    semseter = models.TextField()

    class Meta:
        managed = False
        db_table = 'Class'


class Faculty(models.Model):
    faculty_id = models.AutoField(primary_key=True, blank=True, null=False)
    fname = models.TextField()
    lname = models.TextField()
    password = models.TextField()
    username = models.TextField(unique=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'Faculty'


class Reviews(models.Model):
    review_id = models.AutoField(primary_key=True, blank=True, null=False)
    written_review = models.TextField()
    tutor = models.ForeignKey('Tutor', models.DO_NOTHING, to_field='tutor_id')
    fname = models.ForeignKey('Tutor', models.DO_NOTHING, db_column='fname', to_field='fname', related_name='reviews_fname_set')
    lname = models.ForeignKey('Tutor', models.DO_NOTHING, db_column='lname', to_field='lname', related_name='reviews_lname_set')

    class Meta:
        managed = False
        db_table = 'Reviews'


class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True, blank=True, null=False)
    day = models.TextField()
    week = models.TextField()
    month = models.TextField()
    year = models.IntegerField()
    semester = models.TextField()
    tutor = models.ForeignKey('Tutor', models.DO_NOTHING, to_field='tutor_id')

    class Meta:
        managed = False
        db_table = 'Schedule'


class StudentCheckin(models.Model):
    student = models.OneToOneField('Students', models.DO_NOTHING, primary_key=True)  # The composite primary key (student_id, class_id) found, that is not supported. The first column is selected.
    class_field = models.ForeignKey(Class, models.DO_NOTHING, db_column='class_id', to_field='class_id')  # Field renamed because it was a Python reserved word.
    checkin_time = models.DateTimeField(blank=True, null=True)
    checkout_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Student_CheckIN'


class Students(models.Model):
    student_id = models.AutoField(primary_key=True, blank=True, null=False)
    fname = models.TextField()
    lname = models.TextField()
    username = models.TextField(unique=True)
    password = models.TextField()
    western_id = models.IntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'Students'


class Tutor(models.Model):
    tutor_id = models.AutoField(db_column='tutor_ID', primary_key=True, blank=True, null=False)  # Field name made lowercase.
    fname = models.TextField(unique=True)
    lname = models.TextField(unique=True)
    western_id = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'Tutor'


class TutorReviews(models.Model):
    tutor = models.OneToOneField(Tutor, models.DO_NOTHING, primary_key=True)  # The composite primary key (tutor_id, review_id) found, that is not supported. The first column is selected.
    review = models.ForeignKey(Reviews, models.DO_NOTHING)
    date_of_reveiw = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Tutor_Reviews'


class TutorSchedule(models.Model):
    tutor = models.OneToOneField(Tutor, models.DO_NOTHING, primary_key=True)  # The composite primary key (tutor_id, schedule_id) found, that is not supported. The first column is selected.
    schedule = models.ForeignKey(Schedule, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Tutor_Schedule'

