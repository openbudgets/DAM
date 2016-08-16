# DAM
OBEU Data Analysis and Mining repository

# Aim

This repository hosts implementation of the OBEU Data Analysis and Mining (The ten tasks defined in D2.3).
Currently, it has three branches: master, staging, and production.
OBEU Partners are encouraged to create their own branches for doing testing (Python, Java, etc.), better just use their personal name as the branch name. 


# Three main sub-tasks

* A OBEU lib for data analysis and mining

* Web page development for each task

* Communication with other modules/system (Visualization, Triple store, Openspending)

# Code and Architecture

To consistent with OpenSpending, we use Flask + Python at the backend, javascript(currently bootstrap) at the frontend.

# How to run

* install R
** using brew
    brew tap homebrew/science
    brew install r

* Clone the GitHub repository: `git clone https://github.com/openbudgets/DAM` and `$ git checkout tiansi`

* Install python 3.5 (see <https://www.python.org/downloads/>)

* Ensure that python 3 has been successfully installed and points to the correct interpreter, e.g.
```
$ python3 -V
$ Python 3.5.2
```

* In order to install the project dependencies you will need the following packages
`sudo apt-get install python3-dev build-essential python-psycopg2 libpng-devel postgresql-devel` (Mac os user skip this)

* Install autoenv
```
$ pip install autoenv
$ echo "source `which activate.sh`" >> ~/.bashrc
```

* Install virtualenv: `pip install virtualenv`

* Afterwards create a virtual environment for your project and go to the project's folder
```
$ virtualenv env
$ cd DAM
```

* Install all application requirements by executing
`pip install -r requirements.txt`


* Start your application by executing
`python manage.py runserver`

  in a new terminal, run `redis-server`

  in a new terminal, run `python3 worker.py`
 
* Go to <http://localhost:5000>

# Possible error and Solutions
* Error 1

> RuntimeError: Python is not installed as a framework. The Mac OS X backend will not be able to function correctly if Python is not installed as a framework.
> See the Python documentation for more information on installing Python as a framework on Mac OS X. Please either reinstall Python as a framework, or try
> one of the other backends. If you are Working with Matplotlib in a virtual enviroment see 'Working with Matplotlib in Virtual environments' in the Matplotlib FAQ

* Solution to Error 1

 touch `frameworkpython` file in the virtualenv bin directory with the following content:
```
#!/bin/bash

# what real Python executable to use
PYVER=3
PATHTOPYTHON=/usr/local/bin/
PYTHON=${PATHTOPYTHON}python${PYVER}

# find the root of the virtualenv, it should be the parent of the dir this script is in
ENV=`$PYTHON -c "import os; print(os.path.abspath(os.path.join(os.path.dirname(\"$0\"), '..')))"`

# now run Python with the virtualenv set as Python's HOME
export PYTHONHOME=$ENV
exec $PYTHON "$@"
```

 instead of running `python manage.py runserver`, run `frameworkpython manage.py runserver`




