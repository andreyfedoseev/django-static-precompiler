#!/bin/bash

############
# packages #
############

sudo aptitude update
sudo aptitude install -y virtualenvwrapper python-dev ruby-dev node npm sqlite3

sudo gem install sass -v 3.4.22
sudo gem install compass -v 1.0.1

# Fix path to nodejs executable
if [ ! -e /usr/local/bin/node ]; then
    sudo ln -s /usr/bin/nodejs /usr/local/bin/node
fi

sudo npm install -g coffee-script@1.7.1
sudo npm install -g livescript@1.4.0
sudo npm install -g less@1.7.4
sudo npm install -g babel-cli@6.2.0
sudo npm install -g handlebars@4.0.2
sudo npm install -g stylus@0.50.0


##############
# virtualenv #
##############

source /usr/share/virtualenvwrapper/virtualenvwrapper.sh

# Create virtualenv
if [ ! -e ~/.virtualenvs/staticprecompiler ]; then
    mkvirtualenv staticprecompiler
fi

echo "cd /vagrant; export DJANGO_SETTINGS_MODULE=static_precompiler.tests.django_settings" > ~/.virtualenvs/staticprecompiler/bin/postactivate

workon staticprecompiler

if [ ! -e ~/.pip ]; then
    mkdir ~/.pip
fi

echo -e "[global]\ndownload_cache = ~/.cache/pip" > ~/.pip/pip.conf

pip install django==1.7.4
pip install watchdog
pip install pytest-cov
pip install -e .
