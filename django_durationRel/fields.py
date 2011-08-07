from django.db import models

from datetime import datetime


class CurrentManager(models.Manager):
    def get_query_set(self):
        date = datetime.utcnow()
        return (super(CurrentManager, self).get_query_set()
                .filter(models.Q(startdate__lte=date) |
                        models.Q(startdate__isnull=True))
                .filter(models.Q(enddate__gt=date) |
                        models.Q(enddate__isnull=True)))


class DatedManager(models.Manager):
    def for_date(self, date):
        return (self.filter(models.Q(startdate__lte=date) |
                            models.Q(startdate__isnull=True))
                .filter(models.Q(enddate__gt=date) |
                        models.Q(enddate__isnull=True)))


class DurationRelField(models.ManyToManyField):
    def __init__(self, to, **kwargs):
        models.ManyToManyField.__init__(self, to, **kwargs)

    def contribute_to_class(self, cls, name):
         # name also set in set_attributes_from_name
         # hack needed by _get_m2m_db_table
        self.name = name
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
            'auto_created': False,
            'app_label': cls._meta.app_label,
            'unique_together': (from_, to, 'startdate', 'enddate'),
            'verbose_name': \
            '%(from)s-%(to)s relationship' % {'from': from_, 'to': to},
            'verbose_name_plural': \
            '%(from)s-%(to)s relationships' % {'from': from_, 'to': to},
        })
        # Construct and return the new class.
        relname_from = 'durationRel_%s' % name
        relname_to = 'durationRel_%s' % (self.rel.related_name or
                                         (cls._meta.object_name.lower() + "_set"))

        def _unicode(self):
            return u'%s \u2014 %s' % (getattr(self, from_).__unicode__(),
                                      getattr(self, to).__unicode__())

        _through = type(_name, (models.Model,), {
            'Meta': meta,
            '__module__': cls.__module__,
            from_: models.ForeignKey(cls, related_name=relname_from),
            to: models.ForeignKey(to_model, related_name=relname_to),
            'startdate': models.DateTimeField(default=datetime.utcnow,
                                              blank=True,
                                              null=True),
            'enddate': models.DateTimeField(blank=True,
                                            null=True),
            'objects': DatedManager(),
            'current': CurrentManager(),
            '__unicode__': _unicode
        })
        self.rel.through = _through
        super(DurationRelField, self).contribute_to_class(cls, name)

        def get_NAME_for(_self, date):
            filterargs = {from_: _self}
            q = (_through.objects
                 .for_date(date)
                 .filter(**filterargs))
            return (to_model.objects
                    .filter(id__in=list(q.values_list(to, flat=True))))
        cls.add_to_class('get_%s_for' % name, get_NAME_for)

        def get_current_NAME(_self):
            return get_NAME_for(_self, datetime.utcnow())
        cls.add_to_class('get_current_%s' % name, get_current_NAME)

        def get_latest_NAME(_self):
            filterargs = {from_: _self}
            q = (_through.objects
                 .filter(**filterargs)
                 .order_by('-startdate'))
            return (to_model.objects
                    .get(id=q.values_list(to, flat=True)[0]))
        cls.add_to_class('get_latest_%s' % name, get_latest_NAME)
