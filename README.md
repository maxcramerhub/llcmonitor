# llcmonitor

**Code Review:**

This is a webapp built with django to handle checking in, out, switching, classes.
A base django project has quite a bit in it but here are the main pieces

```/monitor/```
this is our  app

```monitor/views.py```
this contains all the logic behind our views

```monitor/models.py```
this contains the models for our db

```monitor/templates/monitor```
this contains all of our views

```monitor/llcsite```
this is the base project

```/templates/base.html```
this is included in all of our views

**Basic Info:**

An automatic sign in tool for the LLC

To get this up and running, ensure you have django installed
via ```pip3 install django```

to run the server 
```python manage.py runserver``` from the main directory

inside /monitor/templates/monitor you can add new views or update existing ones

```urls.py``` contains routing for views within monitor/urls.py
```views.py``` contains the functions to render views
```models.py``` will be where we can manipulate data from db eventually

checkout https://docs.djangoproject.com/en/5.1/intro/tutorial01/ for more

**Troubleshooting:**

You might need to run migrations
```python manage.py makemigrations```
```python manage.py migrate```
or create the cache table
```python manage.py createcachetable```
or install further packages using pip3
