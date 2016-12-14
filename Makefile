install:
	pip3 install -r requirements.txt
	git clone https://github.com/openbudgets/preprocessing_dm.git
	pip3 install preprocessing_dm/.
	git clone https://github.com/openbudgets/uep_dm.git
	pip3 install uep_dm/.
	git clone https://github.com/openbudgets/okfgr_dm.git
	pip3 install okfgr_dm/.
	git clone https://github.com/openbudgets/outlier_dm
	pip3 install outlier_dm/.

clean:
	pip3 uninstall preprocessing_dm
	pip3 uninstall okfgr_dm
	pip3 uninstall uep_dm
	pip3 uninstall outlier_dm
	sudo rm -r outlier_dm
	sudo rm -r uep_dm
	sudo rm -r okfgr_dm
	sudo rm -r preprocessing_dm

test:
	nosetests tests
