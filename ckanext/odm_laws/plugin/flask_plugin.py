import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
log = logging.getLogger(__name__)


class OdmLawsMixinPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    '''OD Mekong laws plugin flask.'''

    plugins.implements(plugins.IBlueprint)
