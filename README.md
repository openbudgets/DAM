# How to install DAM for Indigo on Ubuntu

* Step 0: Install git and make (if not yet)
```
$ sudo apt-get install git
$ sudo apt-get install build-essential
```

* Step 1: Clone the GitHub repository, and check out staging_indigo branch:
```
$ git clone https://github.com/openbudgets/DAM
$ git checkout staging_indigo
```

* Step 2: go to the DAM directory, and install necessary libraries
```
$ cd DAM
$ make pre
$ source env/bin/activate

```
* Step 3: install DAM 
```
$ make dam 

```
# How to start DAM for Indigo backend
* Step 0: 
```
$ python3 manage.py runserver --host 0.0.0.0
```
* Step 1: open a new terminal 
```
$ redis-server
```
* Step 2: open the third terminal
```
$ python3 worker.py
```

# How to update functional module
* to update pre-processing module
```
$ make update_pdm
```
* to update outlier_dm module
```
$ make update_outlier_dm
```


