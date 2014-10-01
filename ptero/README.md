# All-In-One PTero Vagrant
This directory contains a Vagrantfile for spinning up a single virtual machine
with all of the PTero services running on it.


## Getting Started
Running the virtual machine requires [Vagrant](http://www.vagrantup.com/) 1.6
or newer and [VirtualBox](https://www.virtualbox.org/).  Once they are
installed, install the Vagrant/Librarian Puppet plugin:

    vagrant plugin install vagrant-librarian-puppet

Then you can start the VM using:

    vagrant up

which should take about 10 to 15 minutes.


## Using the VM
The services are running at the following urls:

| Service       | URL                       |
|:--------------|:--------------------------|
| Shell Command | http://192.168.10.10:2000 |
| Petri         | http://192.168.10.10:3000 |
| Workflow      | http://192.168.10.10:4000 |
