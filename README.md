# How to run DAM for Indigo


* Clone the GitHub repository: `git clone https://github.com/openbudgets/DAM` and `$ git checkout staging_indigo`

* Install and setup postgresql
```
# on osx, configures postgres without security measures from localhost and creates a user for your UID
brew install postgres

# on [debian/ubuntu] linux
apt-get install postgres

psql postgres
CREATE DATABASE openbudgets WITH OWNER=<username-is-usually-your-login-name>
```

* Install the Redis Server (http://redis.io/)

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

* Setup environment variables

```
export APP_SETTINGS=config.DevelopmentConfig # to tell the server to startup in development mode
export DATABASE_URL=localhost/openbudges # or whatever you used above as postgres DB
```

* Install all application requirements by executing
`pip install -r requirements.txt`


* Install data-preprocessing package for data-mining
```
DAM $ git clone https://github.com/openbudgets/preprocessing_dm.git
DAM $ cd preprocessing_dm
preprocessing_dm $ pip3 install .
```

* the source of data-preprocessing package can be deleted
```
preprocessing_dm $ cd ..
DAM $ sudo rm -r preprocessing_dm
```

* Install wrapper to access UEP data-mining server
```
DAM $ git clone https://github.com/openbudgets/uep_dm.git
DAM $ cd okfgr_dm
uep_dm $ pip3 install .
```

* the source of UEP data-mining server can be deleted
```
uep_dm $ cd ..
DAM $ sudo rm -r uep_dm
```

* Install wrapper to access OKFGR data-mining server
```
DAM $ git clone https://github.com/openbudgets/okfgr_dm.git
DAM $ cd okfgr_dm
okfgr_dm $ pip3 install .
```

* the source of OKFGR data-mining server can be deleted
```
okfgr_dm $ cd ..
DAM $ sudo rm -r okfgr_dm
```

* Start your application by executing
`python manage.py runserver`

  in a new terminal, run `redis-server`

  in a new terminal, run `python3 worker.py`
 
* Go to <http://localhost:5000>

# How to use Redis in a docker container

 go to the directory where you want to install

 clone the Redis image by typing `git clone https://github.com/mlukasch/dam_env`

 then, `cd dam_env && chmod +x startContainers.sh && ./startContainers.sh`

 in the `config.py` file, change `USE_DOCKER_REDIS = True`

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

* Solution 2 to Error 1

If you are using pyenv and pyenv virualenv you can simply install a python framework version:

```
env PYTHON_CONFIGURE_OPTS="--enable-framework CC=clang" pyenv virtualenv install <python_version>
# re-create the virtualenv
pyenv virtualenv [local] openbudgets
```

via: https://github.com/yyuu/pyenv-virtualenv/issues/140
