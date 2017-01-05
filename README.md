# How to install DAM for Indigo on Ubuntu

* Step 0: Install git (if not yet)
```
$ sudo apt-get install git
```

* Step 1: Clone the GitHub repository, and check out staging_indigo branch:
```
$ git clone https://github.com/openbudgets/DAM
$ git checkout staging_indigo
```

* Step 2: go to the DAM directory
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

# How to update functional module
* to update pre-processing module
```
$ make update_pdm
```


# Trouble shooting

* if the system is installed in VM, it can happen that the system is not accessible outside of the VM. Try the instruction at: https://2buntu.com/articles/1513/accessing-your-virtualbox-guest-from-your-host-os/ or https://coderwall.com/p/yx23qw/access-your-virtualbox-guest-localhost-from-your-host-os
