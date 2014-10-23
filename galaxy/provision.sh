#!/usr/bin/env bash

set -e

echo 'set -o vi' >> /home/vagrant/.bashrc
echo 'set -o vi' >> /root/.bashrc

apt-get update
apt-get install -y nginx postgresql postgresql-client vim-nox

echo `date`: Create galaxy user and database 1>&2
sudo -u postgres psql < /vagrant/postgres-setup.sql


echo `date`: Downloading galaxy software 1>&2
cd /tmp
curl --silent --show-error -O https://bitbucket.org/galaxy/galaxy-dist/get/tip.tar.gz


echo `date`: Install galaxy software 1>&2
cd /home/vagrant
sudo -u vagrant tar xf /tmp/tip.tar.gz
sudo -u vagrant mv galaxy-galaxy-dist-* galaxy-dist


echo `date`: Installing galaxy dependencies 1>&2
cd galaxy-dist
sudo -u vagrant bash scripts/common_startup.sh

echo `date`: Install configuration 1>&2
cp -R /vagrant/config/* /

echo `date`: Starting galaxy 1>&2
service galaxy start

echo `date`: Restarting nginx 1>&2
rm /etc/nginx/sites-enabled/default
service nginx restart


# Wait for galaxy to create its database tables, then create a user
sleep 300
echo `date`: Creating galaxy user 1>&2
sudo -u postgres psql -d galaxy < /vagrant/galaxy-db-setup.sql
