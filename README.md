# DAM
OBEU Data Analysis and Mining repository

# Aim

This repository hosts implementation of the OBEU Data Analysis and Mining (The ten tasks defined in D2.3).
Currently, it has three branches: master, staging, and production.
OBEU Partners are encouraged to create their own branches for doing testing (Python, Java, etc.), better just use their personal name as the branch name. 


# Three main sub-tasks

## A OBEU lib for data analysis and mining

## Web page developement for each task

## Communication with other modules/system (Visualization, Triple store, Openspending)

# Code and Architecture

To consistent with OpenSpending, we use Flask + Python at the backend, Angularjs at the frontend.

# How to run

* install R
** using brew
    brew tap homebrew/science
    brew install r

* Clone the GitHub repository: `git clone https://github.com/openbudgets/DAM`

* Install python 3.5 (see <https://www.python.org/downloads/>)

* Ensure that python 3 has been successfully installed and points to the correct interpreter, e.g.
```
$ python3 -V
$ Python 3.5.2
```

* In order to install the project dependencies you will need the following packages
`sudo apt-get install python3-dev build-essential python-psycopg2 libpng-devel postgresql-devel`

* Install autoenv
```
$ pip install autoenv
$ echo "source `which activate.sh`" >> ~/.bashrc
```

* Install virtualenv: `pip install virtualenv`

* Afterwards create a virtual environment for your project and go to the project's folder
```
$ virtualenv venv
$ cd DAM
```

* Install all application requirements by executing
`pip install -r requirements.txt`

* Install npm
`sudo apt-get install npm`

* Install node modules
`npm install`

* Start your application by executing
`python manage.py runserver`

* Go to <http://localhost:5000>


