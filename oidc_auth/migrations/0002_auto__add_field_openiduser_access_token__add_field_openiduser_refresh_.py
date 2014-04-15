# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'OpenIDUser.access_token'
        db.add_column(u'oidc_auth_openiduser', 'access_token',
                      self.gf('django.db.models.fields.CharField')(default='dummytoken', max_length=255),
                      keep_default=False)

        # Adding field 'OpenIDUser.refresh_token'
        db.add_column(u'oidc_auth_openiduser', 'refresh_token',
                      self.gf('django.db.models.fields.CharField')(default='dummytoken', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'OpenIDUser.access_token'
        db.delete_column(u'oidc_auth_openiduser', 'access_token')

        # Deleting field 'OpenIDUser.refresh_token'
        db.delete_column(u'oidc_auth_openiduser', 'refresh_token')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'oidc_auth.nonce': {
            'Meta': {'object_name': 'Nonce'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'redirect_url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'state': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'oidc_auth.openidprovider': {
            'Meta': {'object_name': 'OpenIDProvider'},
            'authorization_endpoint': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'client_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'client_secret': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'}),
            'jwks_uri': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'signing_alg': ('django.db.models.fields.CharField', [], {'default': "'RS256'", 'max_length': '5'}),
            'token_endpoint': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'userinfo_endpoint': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'oidc_auth.openiduser': {
            'Meta': {'object_name': 'OpenIDUser'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['oidc_auth.OpenIDProvider']"}),
            'profile': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'refresh_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sub': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'oidc_account'", 'unique': 'True', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['oidc_auth']