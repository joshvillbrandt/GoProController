#!/bin/bash

# should be in the same directory as requirements.txt
cd /home/GoProController

echo "Installing packages..."
apt-get update
apt-get install -y python python-dev python-pip
# apt-get install -y network-manager --no-install-recommends
pip install -r requirements.txt

echo "Configuring Django..."
key=$(tr -dc "[:alpha:]" < /dev/urandom | head -c 48)
sed "s/^SECRET_KEY =.*/SECRET_KEY = '$key'/g" GoProController/settings.py --quiet
python manage.py syncdb --noinput # remove --noinput to create a super user
chmod a+rw sqlite3.db # so apache can write to the db
chmod a+w ./ # so apache can write to the db
python manage.py collectstatic --noinput # for the Django REST framework

# remove the steps below if you don't want Apache and Upstart

echo "Configuring Apache..."
apt-get install -y apache2 libapache2-mod-wsgi
rm /etc/apache2/sites-enabled/000-default*
ln -s /home/GoProController/apache.conf /etc/apache2/sites-enabled/GoProController.conf
a2enmod wsgi
service apache2 restart
PYTHON_EGG_CACHE='/var/www/.python-eggs'
mkdir $PYTHON_EGG_CACHE
chmod 777 $PYTHON_EGG_CACHE

echo "Configuring Upstart..."
# upstart does not support symlinks
cp /home/GoProController/upstart.conf /etc/init/gopro-proxy.conf
start gopro-proxy

echo "Good to go!"
