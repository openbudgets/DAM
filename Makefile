step0:
	sudo apt-get install idle3
	sudo apt-get install git 
	sudo apt-get install -y redis-server
	sudo apt-get install python3-dev build-essential python-psycopg2 libpq-dev
	sudo apt-get install libblas-dev liblapack-dev
	sudo apt-get install postgresql postgresql-contrib
	sudo apt-get install python3-pip
	sudo pip3 install virtualenv 
venv:
	virtualenv env
	sudo pip3 install autoenv
	echo "source `which activate.sh`">> ~/.bashrc 
dam:
	pip3 install -r requirements.txt
	git clone https://github.com/openbudgets/preprocessing_dm.git
	pip3 install preprocessing_dm/.
	git clone https://github.com/openbudgets/uep_dm.git
	pip3 install uep_dm/.
	git clone https://github.com/openbudgets/okfgr_dm.git
	pip3 install okfgr_dm/.
	 
clean:
	pip3 uninstall preprocessing_dm
	pip3 uninstall okfgr_dm
	pip3 uninstall uep_dm
	pip3 uninstall outlier_dm  
