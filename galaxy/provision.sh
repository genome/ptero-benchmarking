#!/usr/bin/env bash

set -e

echo 'set -o vi' >> /home/vagrant/.bashrc
echo 'set -o vi' >> /root/.bashrc

apt-get update
apt-get install -y nginx postgresql postgresql-client vim-nox

# Create galaxy user and database
sudo -u postgres psql < /vagrant/postgres-setup.sql


# Download galaxy software
cd /tmp
curl --silent --show-error -O https://bitbucket.org/galaxy/galaxy-dist/get/tip.tar.gz


# Install galaxy software
cd /home/vagrant
sudo -u vagrant tar xf /tmp/tip.tar.gz
sudo -u vagrant mv galaxy-galaxy-dist-* galaxy-dist


# Install galaxy dependencies
cd galaxy-dist
sudo -u vagrant bash scripts/common_startup.sh

# Install configuration
cp -R /vagrant/config/* /


rm /etc/nginx/sites-enabled/default

service galaxy start
service nginx restart


# Wait for galaxy to create its database tables, then create a user
sleep 300
sudo -u postgres psql < /vagrant/galaxy-db-setup.sql
