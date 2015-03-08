# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    # noinspection PyUnusedLocal
    def forwards(self, orm):

        # Changing field 'Dependency.source'
        db.alter_column('static_precompiler_dependency', 'source',
                        self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Dependency.depends_on'
        db.alter_column('static_precompiler_dependency', 'depends_on',
                        self.gf('django.db.models.fields.CharField')(max_length=255))

    # noinspection PyUnusedLocal
    def backwards(self, orm):

        # Changing field 'Dependency.source'
        db.alter_column('static_precompiler_dependency', 'source',
                        self.gf('django.db.models.fields.CharField')(max_length=500))

        # Changing field 'Dependency.depends_on'
        db.alter_column('static_precompiler_dependency', 'depends_on',
                        self.gf('django.db.models.fields.CharField')(max_length=500))

    models = {
        'static_precompiler.dependency': {
            'Meta': {'unique_together': "(('source', 'depends_on'),)", 'object_name': 'Dependency'},
            'depends_on': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['static_precompiler']
