from django.db import models

from datetime import datetime

class DurationRelField(models.ManyToManyField):
    def __init__(self, to, **kwargs):
        models.ManyToManyField.__init__(self, to, **kwargs)
    def contribute_to_class(self, cls, name):
        self.name = name # also set in set_attributes_from_name, hack needed by _get_m2m_db_table
        if isinstance(self.rel.to, basestring):
            to_model = self.rel.to
            to = to_model.split('.')[-1]
        else:
            to_model = self.rel.to
            to = self.rel.to._meta.object_name
        _name = '%s_%s' % (cls._meta.object_name, name)
        from_ = cls._meta.object_name.lower()
        to = to.lower()
        meta = type('Meta', (object,), {
            'db_table': self._get_m2m_db_table(cls._meta),
            'managed': True,
            'auto_created': cls,
            'app_label': cls._meta.app_label,
            'unique_together': (from_, to, 'startdate', 'enddate'),
            'verbose_name': '%(from)s-%(to)s relationship' % {'from': from_, 'to': to},
            'verbose_name_plural': '%(from)s-%(to)s relationships' % {'from': from_, 'to': to},
        })
        # Construct and return the new class.
        relname_from = 'durationRel_%s' % name
        relname_to = 'durationRel_%s' % (self.rel.related_name or
                                         (cls._meta.object_name.lower() + "_set"))
        _through = type(_name, (models.Model,), {
            'Meta': meta,
            '__module__': cls.__module__,
            from_: models.ForeignKey(cls, related_name=relname_from),
            to: models.ForeignKey(to_model, related_name=relname_to),
            'startdate': models.DateTimeField(default=datetime.utcnow, blank=True, null=True),
            'enddate': models.DateTimeField(blank=True, null=True)
        })
        self.rel.through = _through
        super(DurationRelField, self).contribute_to_class(cls, name)
        def get_NAME_for(_self, date):
            filterargs = {from_: _self}
            q = _through.objects.filter(**filterargs)
            q = q.filter(models.Q(startdate__lte=date)|models.Q(startdate__isnull=True))
            _t = q.filter(models.Q(enddate__gt=date)|models.Q(enddate__isnull=True))
            return to_model.objects.filter(id__in=list(_t.values_list(to, flat=True)))
        cls.add_to_class('get_%s_for' % name, get_NAME_for)
        def get_current_NAME(_self):
            return get_NAME_for(_self, datetime.utcnow())
        cls.add_to_class('get_current_%s' % name, get_current_NAME)
