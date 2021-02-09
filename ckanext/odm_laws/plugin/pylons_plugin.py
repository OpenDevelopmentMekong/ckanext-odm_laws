import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
log = logging.getLogger(__name__)


class OdmLawsMixinPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    '''OD Mekong laws plugin pylons.'''
    plugins.implements(plugins.IRoutes, inherit=True)

    def update_config(self, config):
        '''Update plugin config'''

        toolkit.add_template_directory(config, '../templates')
        toolkit.add_public_directory(config, '../public')

    def before_map(self, m):
        m.connect('odm_laws_index', '/laws_record', controller='package', type='laws_record', action='search')
        m.connect('odm_laws_new', '/laws_record/new', controller='package', type='laws_record', action='new')
        m.connect('odm_laws_new_resource', '/laws_record/new_resource/{id}', controller='package', type='laws_record',
                  action='new_resource')
        m.connect('odm_laws_read', '/laws_record/{id}', controller='package', type='laws_record', action='read',
                  ckan_icon='book')
        m.connect('odm_laws_edit', '/laws_record/edit/{id}', controller='package', type='laws_record', action='edit')
        m.connect('odm_laws_delete', '/laws_record/delete/{id}', controller='package', type='laws_record',
                  action='delete')

        return m
