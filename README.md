# README

### Starting a VM for Development in VirtualBox using Ansible

Requirements:
* [VirtualBox installed](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant installed](https://www.vagrantup.com/downloads.html)
* [Ansible installed](http://docs.ansible.com/ansible/intro_installation.html#installation)

### Init and provision vagrant box

`vagrant up`

### Fill searchdatabase width SXSW schedule
`vagrant ssh`

`/vagrant/init_data.sh`

The data scraped from sxsw.com is stored in /vagrant/data. To refill the index without scraping:

`/vagrant/refill_elastic.sh`

### Use the application

Access the page: <http://192.168.33.20/sxsw/>

Raw access to the Elastic index: <http://192.168.33.20/elastic/>

Whether you go to an event or not is stored in both the Elastic index and a SQLite database. Upon refilling the index the data from SQLite is used to enrich the data.
