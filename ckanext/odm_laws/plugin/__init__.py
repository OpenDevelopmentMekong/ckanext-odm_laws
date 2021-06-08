import ckan
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from beaker.middleware import SessionMiddleware
import sys
import os
from ckanext.odm_laws.lib import odm_laws_helper
from urlparse import urlparse
import json
from ckan.common import config
import collections
from routes.mapper import SubMapper
import ckan.lib.helpers as h
import requests
import tempfile

log = logging.getLogger(__name__)

if toolkit.check_ckan_version(min_version='2.9.0'):
  from ckanext.odm_laws.plugin.flask_plugin import OdmLawsMixinPlugin
else:
  from ckanext.odm_laws.plugin.pylons_plugin import OdmLawsMixinPlugin


class OdmLawsPlugin(OdmLawsMixinPlugin):
  '''OD Mekong laws plugin.'''

  plugins.implements(plugins.IConfigurer)
  plugins.implements(plugins.ITemplateHelpers)
  plugins.implements(plugins.IPackageController, inherit=True)
  plugins.implements(plugins.IResourceController, inherit=True)


  def get_helpers(self):
    '''Register the plugin's functions above as a template helper function.'''

    return {
      'odm_laws_get_dataset_type': odm_laws_helper.get_dataset_type,
      'odm_laws_validate_fields': odm_laws_helper.validate_fields,
    }

  def before_create(self, context, resource):

    dataset_type = context['package'].type if 'package' in context else ''
    if dataset_type == 'laws_record':
      log.info('after_update')

  def after_create(self, context, pkg_dict_or_resource):

    dataset_type = context['package'].type if 'package' in context else pkg_dict_or_resource['type']
    if dataset_type == 'laws_record':
      log.debug('after_create: %s', pkg_dict_or_resource['name'])

      review_system = toolkit.asbool(config.get("ckanext.issues.review_system", False))
      if review_system:
        if 'type' in pkg_dict_or_resource:
          odm_laws_helper.create_default_issue_laws_record(pkg_dict_or_resource)
