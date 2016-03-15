# appengine-swapi


## Prerequisites

* [Python 2.7](https://www.python.org/downloads/)
  * Suggestion: if you're on OSX, use [Hombebrew](http://brew.sh/) to [install Python 2.7](http://docs.python-guide.org/en/latest/starting/install/osx/) and follow the brew prompt's directions to overwrite links
  * Suggestion: if you're on Linux, use your distribution's package manager to install Python 2.7
  * Do not use a Python install that's managed by your operating system (e.g., OSX comes with Python installed, but it's a custom installation for OSX and should not be used for Python development)
* [Google Cloud SDK](https://cloud.google.com/sdk/) (gcloud)
  * After installing, ensure the `~/google-cloud-sdk/` directory exists; this project's [test setup](https://github.com/py-in-the-sky/appengine-swapi/blob/master/graphql/app/fix_sys_path.py#L18) assumes it
* Google App Engine SDK for Python
  * With gcloud installed, this is easy; just run `gcloud components install app-engine-python` from the command line
* Run `pip --version` from the command line
  * If your system prints out pip's version number, and possibly other information, skip to the next step; you have pip installed already
  * Otherwise, [install it](https://pip.pypa.io/en/stable/installing/#installing-with-get-pip-py)
* [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/install.html#basic-installation)
  * After basic installation, follow the [Shell Startup File](https://virtualenvwrapper.readthedocs.org/en/latest/install.html#shell-startup-file) instructions for adding content to your `~/.bashrc`, `~/.bash_profile`, or other startup script


## Setup

* Git clone this repo and `cd` into it
* `mkvirtualenv appengine-swapi -a .`
* `pip install --upgrade pip setuptools`
* `add2virtualenv ./graphql/ ./graphql/lib/`
* `make install`
* Run tests: `py.test`
* Run app: `make run`
* Visit the Graphiql frontend to the app: [localhost:8080/graphiql](http://localhost:8080/graphiql)
