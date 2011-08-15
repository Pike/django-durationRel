django-durationRel models a time-dependent relation between two django models.

Usage
=====
In your models.py:

::

  class MyModel(models.Model):
    pass
  class OtherModel(models.Model):
    mys = DurationField(MyModel)

See also ``tests/models.py`` and ``tests/tests.py``.

Tests
=====
You can run the tests from the parent dir with:

::

  django-admin.py test --settings=django_durationRel.tests.settings

They're using a sqlite3 in-memory database.

To run the tests with test coverage first make sure you have coverage_
installed:

::

  django-admin.py test --settings=django_durationRel.tests.coverage_settings

License
=======
django-durationRel is under BSD license.

.. _coverage: http://nedbatchelder.com/code/coverage/
