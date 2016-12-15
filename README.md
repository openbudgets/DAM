# How to install DAM for Indigo on Ubuntu


* Step 0: Install some tools, database, e.g. git, redis-server
```
$ make step0
```

* Step 1: Clone the GitHub repository: `$ git clone https://github.com/openbudgets/DAM` and `$ git checkout staging_indigo`

* Step 2: go to the DAM directory
```
$ cd DAM
$ make venv
$ source env/bin/activate

```
* Step 3: install DAM 
```
$ make dam 

```
# How to start DAM for Indigo backend
* Step 0: 
```
$ python3 manage.py runserver
```
* Step 1: open a new terminal 
```
$ redis-server
```
* Step 2: open the third terminal
```
$ python3 worker.py
```



