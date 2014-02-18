# GoProApp

Controls multiple GoPros from a web page.

This is a webo app that provides a front end for the [GoProController](https://github.com/joshvillbrandt/GoProController) python class. The app itself is built off of [django-quick-start-app](http://github.com/joshvillbrandt/django-quick-start-app).

## Setup

This app originally required one to first create a Django, but the Django files are now integrated with the repo for easier deployment.

A bash script is also now included to perform the bulk of the required setup steps. This script is tested against Ubuntu 12.04. As a part of the setup procedure, an Apache config and Upstart config are installed into your system. If you do not want this, then take those steps out `setup.sh` before executing it.

```bash
sudo apt-get install git
cd ~/
git clone https://github.com/joshvillbrandt/GoProApp.git
cd ~/GoProApp
./setup.sh
```

Upon completion of `setup.sh`, You should now be able to navigate to `http://localhost:80/` and see the GoProApp. The `GoProApp/proxy.py` file is also now running which continuously polls the cameras for their statuses and sends commands to the cameras as they are queued up in the server.

## Development

To run GoProApp without Apache and Upstart, launch the site with the Django development server:

```bash
cd ~/GoProApp
python manage.py runserver 0.0.0.0:8000
```

In another terminal window, launch the proxy to communicate with the cameras:

```bash
python ~/GoProApp/GoProApp/proxy.py
```

# Todo

There are no planned developments at this time. Feel free to contribute with a pull request, however!

# Screenshots

![GoProApp Screenshot](screenshot.jpg)

![GoProApp Screenshot](screenshot2.jpg)
