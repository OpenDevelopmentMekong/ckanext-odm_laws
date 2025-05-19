import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.odm_laws.lib import odm_laws_helper
from ckan.common import config

log = logging.getLogger(__name__)



class OdmLawsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
  '''OD Mekong laws plugin.'''

  plugins.implements(plugins.IConfigurer)
  plugins.implements(plugins.ITemplateHelpers)
  plugins.implements(plugins.IPackageController, inherit=True)
  plugins.implements(plugins.IResourceController, inherit=True)

  def update_config(self, config):
    '''Update plugin config'''
    toolkit.add_template_directory(config, 'templates')
    toolkit.add_public_directory(config, 'public')


  def get_helpers(self):
    '''Register the plugin's functions above as a template helper function.'''

    return {
      'odm_laws_get_dataset_type': odm_laws_helper.get_dataset_type,
      'odm_laws_validate_fields': odm_laws_helper.validate_fields,
      'humanize_entity_type': odm_laws_helper.humanize_entity_type,
    }

  def after_dataset_create(self, context, pkg_dict_or_resource):
    dataset_type = context['package'].type if 'package' in context else pkg_dict_or_resource['type']
    if dataset_type == 'laws_record':
      log.debug('after_create: %s', pkg_dict_or_resource['name'])

      review_system = toolkit.asbool(config.get("ckanext.issues.review_system", False))
      if review_system:
        if 'type' in pkg_dict_or_resource:
          odm_laws_helper.create_default_issue_laws_record(pkg_dict_or_resource)

  # It's unclear exactly what this is doing, so for now, just don't improve the situation
  after_resource_create = after_dataset_create
  after_create = after_dataset_create
