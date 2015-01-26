===============
Verb∋Net editor
===============

A web-based tool to ease the translation from VerbNet to the French Verb∋Net.

https://verbenet.inria.fr/

Installation
============

We're going to assume Ubuntu when showing instructions, but this
should work anywhere, even though it was only tested on GNU/Linux.

Code and dependencies
--------------------

Make sure all dependencies are installed. That means Python 3 and
development files, libxml2 and libxslt1 development files, PostgreSQL
contrib modules and development files, and Node.js:

    sudo apt-get install python3-dev libxslt1-dev libxml2-dev postgresql-contrib postgresql-server-dev-all libapache2-mod-wsgi-py3 npm

Install Node.js dependencies:

    npm install less yuglify

Then, get the code:

    git clone https://github.com/aymara/verbenet-editor.git

Create a virtualenv, activate it, then install the Python
requirements:

    pip install -r requirements/local.txt

Make sure the PostgreSQL database supports the UNACCENT function

    sudo -u postgres psql syntacticframes

    CREATE EXTENSION UNACCENT;
    CREATE TEXT SEARCH CONFIGURATION fr ( COPY = french );

Data
----

Run `./manage.py migrate` from `syntacticframes_projects`. This will
set up initial data, but you will still need to import VerbNet or
VerbeNet afterwards. This is not currently possible: for now, simply
ask a PostgreSQL dump.

Acknowledgements
================

    - Laurence Danlos and Takuya Nakamura for their feedback
    - Many thanks to the "Two Scoops of Django" book which got me
      started
    - Thanks to Django and its community: I never got blocked long

Contact
=======

Feel free to open a GitHub issue or to contact me
(email is in https://github.com/pquentin)
