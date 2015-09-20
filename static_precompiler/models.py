from __future__ import unicode_literals

from django.db import models


class Dependency(models.Model):

    source = models.CharField(max_length=255, db_index=True)
    depends_on = models.CharField(max_length=255, db_index=True)

    class Meta:
        unique_together = ("source", "depends_on")

    def __unicode__(self):
        return "{0} depends on {1}".format(self.source, self.depends_on)
