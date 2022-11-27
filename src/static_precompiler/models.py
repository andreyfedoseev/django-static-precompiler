from django.db import models


class Dependency(models.Model):

    source = models.CharField(max_length=255, db_index=True)
    depends_on = models.CharField(max_length=255, db_index=True)

    class Meta:
        unique_together = ("source", "depends_on")

    def __unicode__(self) -> str:
        return f"{self.source} depends on {self.depends_on}"
