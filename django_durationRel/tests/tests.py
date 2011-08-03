"""
Test the DurationRelField class.
"""

from django import test
from models import One, Other


class OneOtherTest(test.TestCase):
    def setUp(self):
        self.one = One.objects.create(code="one")
        self.other = Other.objects.create(code="other")
        One.others.through.objects.create(one=self.one, other=self.other)

    def test_basic_relation(self):
        """
        Tests that there is exactly one other
        """
        self.assertEqual(self.one.others.count(), 1)
        self.assertEqual((self.one
                          .durationRel_others
                          .filter(enddate__isnull=False).count()),
                          0)
        self.assertEqual(self.one.others.all()[0].code, "other")

    def test_current(self):
        """
        Tests that get_current_others works.
        """
        self.assertEqual(list(self.one.get_current_others()), [self.other])

    def test_latest(self):
        """
        Tests that get_latest_others works.
        """
        self.assertEqual(self.one.get_latest_others(), self.other)

    def test_serialization(self):
        """
        Tests that we can serialize and deserialize.
        """
        from django.core import serializers
        from django.core.management.commands import dumpdata
        out = dumpdata.Command().handle("tests")
        objects = dict((o.object._meta.object_name, o.object)
                       for o in serializers.deserialize("json", out))
        self.assertEqual(self.one, objects['One'])
        self.assertEqual(self.other, objects['Other'])
        self.assertEqual(self.one, objects["One_others"].one)
        self.assertEqual(self.other, objects["One_others"].other)
