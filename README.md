GoProApp
================

Controls multiple GoPros from a web page.

This is a reusable Django app that provides a front end for the [GoProController](https://github.com/joshvillbrandt/GoProController) python class. The app itself is built off of [django-quick-start-app](http://github.com/joshvillbrandt/django-quick-start-app).

# Setup

To use this app, you must first set up a Django project. Try out [django-quick-start-project](http://github.com/joshvillbrandt/django-quick-start-project) for an easy start.

    django-admin startproject --template=https://github.com/joshvillbrandt/django-quick-start-project/archive/master.zip --extension=py,html GoProSite

Then add this app to the site.

    cd GoProSite
    git clone https://github.com/joshvillbrandt/GoProApp.git

Once you have added the app, add it to your INSTALLED_APPS list in your projects settings.py file. Then add a line to include the GoProApp urls.py file inyour projects urls.py file. Finally, run `python manage.py syncdb` to install the models.
