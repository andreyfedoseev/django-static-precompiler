# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Dependency'
        db.create_table(u'static_precompiler_dependency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('depends_on', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal(u'static_precompiler', ['Dependency'])

        # Adding unique constraint on 'Dependency', fields ['source', 'depends_on']
        db.create_unique(u'static_precompiler_dependency', ['source', 'depends_on'])


    def backwards(self, orm):
        # Removing unique constraint on 'Dependency', fields ['source', 'depends_on']
        db.delete_unique(u'static_precompiler_dependency', ['source', 'depends_on'])

        # Deleting model 'Dependency'
        db.delete_table(u'static_precompiler_dependency')


    models = {
        u'static_precompiler.dependency': {
            'Meta': {'unique_together': "(('source', 'depends_on'),)", 'object_name': 'Dependency'},
            'depends_on': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['static_precompiler']
