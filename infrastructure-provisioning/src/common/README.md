Installation
=

**Installing Apache DLAB**

The first step is to install Apache DLAB.

First, checkout the latest version of Apache DLAB.

```
$ git clone https://github.com/mediapills/incubator-dlab.git
```

Apache DLAB is a python project, so it can be installed like any other python library. Several operating systems (Mac OS X, Major Versions of Linux/BSD) have Python pre-installed, so you should just have to run

```
$ easy_install dlabcli
```

  or

```
$ pip install dlabcli
```

Users are strongly recommended to install Apache DLAB in a virtualenv. Instructions to setup an virtual environment will be explained below.

> Note& When the package is installed via easy_install or pip this function will be bound to the dlab executable in the Python installation’s bin directory (on Windows - the Scripts directory).


Installing Apache DLAB in an Virtual Environment
=

virtualenv is a tool to create isolated Python environments. virtualenv creates a folder which contains all the necessary executables to use the packages that the Apache DLAB project would need.

Install virtualenv via pip:

```
  $ sudo env/bin/pip install virtualenv
```

Start by changing directory into the root of Apache DLAB’s project directory, and then use the virtualenv command-line tool to create a new environment:

```
  $ mkdir .env
  $ virtualenv .env
```

Activate environment:

```
  $ source env/bin/activate
```

Install Apache DLAB requirements:

```
  $ env/bin/pip -r requirements.txt
```

To build the source code and run all unit tests.

```
  $ env/bin/python setup.py develop test
```

Launch local Apache DLAB server, running on localhost:8090:

```
  $ env/bin/dev
```

Deactivate environment

```
  $ deactivate
```

Installing Documentation
=

To save yourself the trouble, all up to date documentation is available at ???.

However, if you want to manually build the documentation, the instructions are below.

First, install the documentation dependencies:

```
  $ env/bin/pip install -r doc_requirements.txt
```

To build Apache DLAB’s documentation, create a directory at the root level of /dlab called dlab-docs.

```
  $ mkdir dlab-docs & cd dlab-docs
```

Execute build command:

```
  # Inside top-level docs/ directory.
  $ make html
```

This should build the documentation in your shell, and output HTML. At then end, it should say something about documents being ready in dlab-docs/html. You can now open them in your browser by typing

```
  $ open dlab-docs/html/index.html
```
