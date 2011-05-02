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

License
=======
django-durationRel is under BSD license.
