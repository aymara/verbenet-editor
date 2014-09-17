Install
=======

Install our slightly modified django-mptt (see
https://github.com/pquentin/django-mptt/commit/d7949d973fe7f41de5b038ff91e2da9691d2a603):

$ git clone https://github.com/pquentin/django-mptt.git
$ cd django-mptt
$ python setup.py install

Install verbenet-editor from GitHub:

$ git clone https://github.com/aymara/verbenet-editor.git
$ cd verbenet-editor
$ pip install -r requirements/local.txt

$ ./manage.py migrate

TODO: explain how to import initial VerbNet/VerbeNet data
