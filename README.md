# GoProApp

An http API to control multiple GoPro cameras over wifi.

## Description

This program can be used to control multiple GoPro cameras via the [gopro](https://github.com/joshvillbrandt/gopro) Python library. When ran from a Linux machine with compatible wireless card, this program is capable of automatically negotiating between the different ad-hoc wireless networks that each cameras makes.

A user interface is available for this API as a standalone package. See [GoProControllerUI](https://github.com/joshvillbrandt/GoProControllerUI).

## How it works

The backbone of GoProApp is a program called `GoProProxy` that runs asynchronously to the server. This proxy periodically grabs the status of every camera in the database and sends commands to cameras when appropriate. The proxy uses [wifi](https://github.com/rockymeza/wifi) to jump between networks and [gopro](https://github.com/joshvillbrandt/gopro) to handle the communication to the cameras. A Django app is used to persist data from the proxy and serve API endpoints. 

## Setup

This app originally required one to first create a Django project, but the Django files are now integrated with the repo for easier deployment.

A bash script is also now included to perform the bulk of the required setup steps. This script is tested against Ubuntu 12.04. As a part of the setup procedure, an Apache config and Upstart config are installed into your system. If you do not want this, then take those steps out `setup.sh` before executing it.

First, download the code:

```bash
git clone https://github.com/joshvillbrandt/GoProController.git
```

If you are running Ubuntu 12.04, use the `setup.sh` script to automatically set up the application:

```bash
sudo GoProController/setup.sh
```

Upon completion of `setup.sh`, you should now be able to navigate to `http://localhost:80/` and see the API. In addition, the `GoProApp/proxy.py` file is also now running continuously to the local wifi adapter and communicate with the cameras.

## Development

To run GoProApp without Apache and Upstart, launch the site with the Django development server:

```bash
cd GoProController
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```

In another terminal window, launch the proxy to communicate with the cameras:

```bash
python GoProController/proxy.py
```

## Change History

This project uses [semantic versioning](http://semver.org/).

### v0.2.0 - 2014/11/??

* Renamed project from `GoProApp` to `GoProController`
* Added wireless control code for Linus systems
* Refactored user interface out of the project

### v0.1.1 - 2014/09/11

* Bug fixes

### v0.1.0 - 2013/10/31

* Initial release

# Todo

No new features are planned at this time.

## Contributions

Pull requests to the `develop` branch are welcomed!
