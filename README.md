Verb∋Net editor
===============

A web-based tool to ease the translation from VerbNet to the French Verb∋Net.

https://verbenet.inria.fr/

Installation
============

Code and dependencies
--------------------

Make sure all dependencies are installed. That means Python 3 and
development files, libxml2 and libxslt1 development files, PostgreSQL
contrib modules and development files, and Node.js.

For Ubuntu:

    sudo apt-get install python3-dev libxslt1-dev libxml2-dev \
        postgresql-contrib postgresql-server-dev-all \
        libapache2-mod-wsgi-py3 npm

For OS X:

    brew install libxslt libxml2 postgresql npm
    # Follow brew instructions for PostgreSQL

Install Node.js dependencies globally:

    sudo npm install -g less yuglify

Then, get the code:

    git clone --recursive https://github.com/aymara/verbenet-editor.git

Create a Python 3 virtualenv, activate it. It's important! Then,
install the other requirements:

    pip install -r requirements/local.txt

Data
----

Create the database:

    createdb syntacticframes

Run `./manage.py migrate` from `syntacticframes_projects`. This will
set up initial data, but you will still need to import VerbNet or
VerbeNet afterwards. This is not currently possible: for now, simply
ask a PostgreSQL dump.

The result is a database named `syntacticframes`. Make sure the
database supports the `UNACCENT` function:

    psql syntacticframes
    syntacticframes=# CREATE EXTENSION UNACCENT;
    syntacricframes=# CREATE TEXT SEARCH CONFIGURATION fr ( COPY = french );


Running tests
=============

`./manage.py test` should work, even though it will take some time to
create a database then remove it: the fixtures load the entire LVF
data! This takes about 30 seconds on my laptop. To speed things up at
the expense of possible bugs creeping in, you can create a database
specifically for testing:

    createdb _test_verbenet_db
    ./manage.py migrate --settings=syntacticframes.settings.migratedtestdb

Tests now run fast:

    ./manage.py test --settings=syntacticframes.settings.migratedtestdb


Exporting to XML
================

I try to regularly export data to https://github.com/aymara/verbenet.
This is done using `./manage.py export_verbnet`.

At least on OS X El Capitan and FreeBSD, the collation table for
French does not exist, which means "étendre" will be after "zozoter",
which is not what we want. To fix this, you can install pyicu which
will be picked up by the export code. If you're using homebrew, then
you can simply do:

    brew install icu4c
    CFLAGS=-I$(brew --prefix icu4c)/include LDFLAGS=-L$(brew --prefix icu4c)/lib pip install pyicu

and re-run the export code.

Acknowledgements
================

  - Laurence Danlos and Takuya Nakamura for their feedback
  - Many thanks to the "Two Scoops of Django" book which got me
    started
  - Thanks to Django and its community: I never got blocked long

Contact
=======

Feel free to open a GitHub issue or to contact me
(email is at https://github.com/pquentin)
