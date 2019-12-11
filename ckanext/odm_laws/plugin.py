import ckan
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from beaker.middleware import SessionMiddleware
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import odm_laws_helper
from urlparse import urlparse
import json
from ckan.common import config
import collections
from routes.mapper import SubMapper
import ckan.lib.helpers as h
import requests
import tempfile

log = logging.getLogger(__name__)

def _create_or_update_pdf_thumbnail(context,pkg_dict_or_resource):
  pdf_url=pkg_dict_or_resource['url']
  filename, file_extension = os.path.splitext(pdf_url)

  if ".pdf" != file_extension.lower() or pkg_dict_or_resource['name'] == "PDF Thumbnail":
   return

  enabled_pdf_preview = False
  # enabled_pdf_preview = config.get("ckan.odm_nav_concept.generate_pdf_preview", False) == "true"
  if enabled_pdf_preview:

    try:
      from wand.image import Image

      pdf=Image(filename=pdf_url+"[0]")
      pdf.format='png'
      pdf.resize(135,201)
      temp_dir = os.path.abspath(tempfile.mkdtemp())
      temp_img=temp_dir+'/'+pkg_dict_or_resource['id']+'.png'
      pdf.save(filename=temp_img)
      params = {'package_id':pkg_dict_or_resource['package_id'],'upload':temp_img, 'url':'N/A','format':'PNG','mimetype_inner':'image/png','name':'PDF Thumbnail'}
      ckan_url = config.get("ckan.site_url", "")
      userobj = context['auth_user_obj']
      ckan_auth = userobj.apikey

      if context['resource'].name == "PDF Thumbnail":
        resource_id=context['resource'].id
        params['id']=resource_id
        requests.post(ckan_url + 'api/3/action/resource_update',verify=False,data=params,headers={"X-CKAN-API-Key": ckan_auth},files=[('upload', file(params["upload"]))])
      else:
        requests.post(ckan_url + 'api/3/action/resource_create',verify=False,data=params,headers={"X-CKAN-API-Key": ckan_auth},files=[('upload', file(params["upload"]))])

      if os.path.exists(temp_img):
        os.remove(temp_img)

    except Exception, e:
      log.error("Could not generate PDF thumbnail", e)


class OdmLawsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
  '''OD Mekong laws plugin.'''

  plugins.implements(plugins.IConfigurer)
  plugins.implements(plugins.ITemplateHelpers)
  plugins.implements(plugins.IRoutes, inherit=True)
  plugins.implements(plugins.IPackageController, inherit=True)
  plugins.implements(plugins.IResourceController, inherit=True)


  def before_map(self, m):

    m.connect('odm_laws_index','/laws_record',controller='package',type='laws_record',action='search')
    m.connect('odm_laws_new','/laws_record/new',controller='package',type='laws_record',action='new')
    m.connect('odm_laws_new_resource','/laws_record/new_resource/{id}',controller='package',type='laws_record',action='new_resource')
    m.connect('odm_laws_read', '/laws_record/{id}',controller='package',type='laws_record', action='read', ckan_icon='book')
    m.connect('odm_laws_edit', '/laws_record/edit/{id}',controller='package',type='laws_record', action='edit')
    m.connect('odm_laws_delete', '/laws_record/delete/{id}',controller='package',type='laws_record', action='delete')

    return m

  def update_config(self, config):
    '''Update plugin config'''

    toolkit.add_template_directory(config, 'templates')
    toolkit.add_public_directory(config, 'public')

  def get_helpers(self):
    '''Register the plugin's functions above as a template helper function.'''

    return {
      'odm_laws_get_dataset_type': odm_laws_helper.get_dataset_type,
      'odm_laws_validate_fields' : odm_laws_helper.validate_fields,
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

        if 'url_type' in pkg_dict_or_resource:
          _create_or_update_pdf_thumbnail(context,pkg_dict_or_resource)

  def after_update(self, context, pkg_dict_or_resource):
    log.debug('after_update: %s', pkg_dict_or_resource['name'])

    dataset_type = context['package'].type if 'package' in context else pkg_dict_or_resource['type']
    if dataset_type == 'laws_record':

      if 'url_type' in pkg_dict_or_resource:
        _create_or_update_pdf_thumbnail(context,pkg_dict_or_resource)
