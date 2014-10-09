#!/usr/bin/env bash

apt-get update
apt-get install -y nginx postgresql postgresql-client vim-nox

sudo -u postgres psql < /vagrant/postgres-setup.sql

if [ ! -f /tmp/tip.tar.gz ]; then
    cd /tmp
    curl --silent --show-error -O https://bitbucket.org/galaxy/galaxy-dist/get/tip.tar.gz
fi

cd /home/vagrant
if [ ! -d galaxy-dist ]; then
    sudo -u vagrant tar xf /tmp/tip.tar.gz
    sudo -u vagrant mv galaxy-galaxy-dist-* galaxy-dist
fi

cp -R /vagrant/galaxy-configuration/* galaxy-dist/
