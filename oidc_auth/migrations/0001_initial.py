# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Nonce'
        db.create_table(u'oidc_auth_nonce', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issuer_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('hash', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'oidc_auth', ['Nonce'])

        # Adding model 'OpenIDProvider'
        db.create_table(u'oidc_auth_openidprovider', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issuer', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('authorization_endpoint', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('token_endpoint', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('userinfo_endpoint', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('jwks_uri', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('client_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('client_secret', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'oidc_auth', ['OpenIDProvider'])


    def backwards(self, orm):
        # Deleting model 'Nonce'
        db.delete_table(u'oidc_auth_nonce')

        # Deleting model 'OpenIDProvider'
        db.delete_table(u'oidc_auth_openidprovider')


    models = {
        u'oidc_auth.nonce': {
            'Meta': {'object_name': 'Nonce'},
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer_url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'oidc_auth.openidprovider': {
            'Meta': {'object_name': 'OpenIDProvider'},
            'authorization_endpoint': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'client_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'client_secret': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'}),
            'jwks_uri': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'token_endpoint': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'userinfo_endpoint': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['oidc_auth']