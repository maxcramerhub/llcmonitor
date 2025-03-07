# llcmonitor
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

Troubleshooting:

You might need to run migrations
```python manage.py makemigrations```
```python manage.py migrate```
or create the cache table
```python manage.py createcachetable```
or install further packages using pip3
