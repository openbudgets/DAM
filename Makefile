SHELL := /bin/bash
pre:
	sudo apt-get install idle3
	sudo apt-get install -y redis-server
	sudo apt-get update
	sudo apt-get install python3-dev build-essential python-psycopg2 libpq-dev
	sudo apt-get install libblas-dev liblapack-dev
	sudo apt-get install wget postgresql postgresql-contrib
	sudo apt-get install libossp-uuid16
	sudo apt-get install libxslt1.1
	sudo apt-get install python3-pip
	sudo pip3 install virtualenv
	virtualenv env
	sudo pip3 install autoenv
	echo "source `which activate.sh`">> ~/.bashrc 
dam:
	source .env	
	pip3 install -r requirements.txt
	git clone https://github.com/openbudgets/preprocessing_dm.git
	pip3 install preprocessing_dm/.
	git clone https://github.com/openbudgets/uep_dm.git
	pip3 install uep_dm/.
	git clone https://github.com/openbudgets/okfgr_dm.git
	pip3 install okfgr_dm/.
	git clone https://github.com/openbudgets/outlier_dm.git
	pip3 install outlier_dm/.
update_pdm:
	pip3 uninstall preprocessing_dm	
	sudo rm -r preprocessing_dm
	git clone https://github.com/openbudgets/preprocessing_dm.git
	pip3 install preprocessing_dm/.
update_uep_dm:
	pip3 uninstall uep_dm
	sudo rm -r uep_dm
	git clone https://github.com/openbudgets/uep_dm.git
	pip3 install uep_dm/.
update_outlier_dm:
	pip3 uninstall outlier_dm
	sudo rm -r outlier_dm
	git clone https://github.com/openbudgets/outlier_dm.git
	pip3 install outlier_dm/.
	 
clean:
	pip3 uninstall preprocessing_dm
	pip3 uninstall okfgr_dm
	pip3 uninstall uep_dm
	pip3 uninstall outlier_dm  
