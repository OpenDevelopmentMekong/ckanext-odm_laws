import datetime
import json
from pylons import config
import rdflib
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, XSD, SKOS, RDFS
from geomet import wkt, InvalidGeoJSONException
from ckan.plugins import toolkit
from ckanext.dcat.utils import resource_uri, publisher_uri_from_dataset_dict
from ckanext.dcat.profiles import RDFProfile
import logging

log = logging.getLogger(__name__)

AGLS = Namespace('http://www.agls.gov.au/agls/terms/')
BIBO = Namespace('http://bibliontology.com/bibo/bibo.php#')
BIBFRAME = Namespace('http://id.loc.gov/ontologies/bibframe.html#')
GC = Namespace('http://www.oegov.org/core/owl/gc#')
DBPEDIA = Namespace('http://dbpedia.org/ontology')
DCT = Namespace('http://purl.org/dc/terms/')
DCAT = Namespace('http://www.w3.org/ns/dcat#')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
MREL = Namespace('http://id.loc.gov/vocabulary/relators/')
SCHEMA = Namespace('http://schema.org/')
SPDX = Namespace('http://spdx.org/rdf/terms#')
CRO = Namespace('http://rhizomik.net/ontologies/copyrightonto.owl#')
DOAP = Namespace('http://usefulinc.com/ns/doap#')
EBUCORE = Namespace('https://www.ebu.ch/metadata/ontologies/ebucore/index.html#')
DQM = Namespace('http://semwebquality.org/dqm-vocabulary/v1/dqm#')
DQ = Namespace('http://def.seegrid.csiro.au/isotc211/iso19115/2003/dataquality#')
OMN = Namespace('https://raw.githubusercontent.com/open-multinet/playground-rspecs-ontology/master/omnlib/ontologies/omn.ttl#')
OPUS = Namespace('http://lsdis.cs.uga.edu/projects/semdis/opus#')
PPROC = Namespace('http://contsem.unizar.es/def/sector-publico/pproc.html#')
MD = Namespace('http://def.seegrid.csiro.au/isotc211/iso19115/2003/metadata#')
GN = Namespace('http://www.geonames.org/ontology#')
SKOS = Namespace('https://www.w3.org/2009/08/skos-reference/skos.html#')
SORON = Namespace('http://www.bib.uc3m.es/~fcalzada/soron/soron_content/soron#')

namespaces = {
    'agls': AGLS,
    'bibo': BIBO,
    'bibframe': BIBFRAME,
    'dbpedia': DBPEDIA,
    'gc': GC,
    'dct': DCT,
    'dcat': DCAT,
    'foaf': FOAF,
    'mrel': MREL,
    'schema': SCHEMA,
    'cro': CRO,
    'doap': DOAP,
    'ebucore': EBUCORE,
    'dqm': DQM,
    'dq': DQ,
    'omn': OMN,
    'opus': OPUS,
    'pproc': PPROC,
    'md': MD,
    'gn': GN,
    'skos': SKOS,
    'soron': SORON
}


class ODMDCATBasicProfileLaws(RDFProfile):
  '''
  An RDF profile exposing metadata using standard vocabularies

  More information and specification:

  https://joinup.ec.europa.eu/asset/dcat_application_profile

  '''

  def parse_dataset(self, dataset_dict, dataset_ref):

    # This method does not need to be implemented until Harvesters are needed
    return super(ODMDCATBasicProfileLaws, self).parse_dataset(dataset_dict, dataset_ref)

  def graph_from_dataset(self, dataset_dict, dataset_ref):

    log.debug("ODMDCATBasicProfileLaws graph_from_dataset")

    g = self.g

    for prefix, namespace in namespaces.iteritems():
      g.bind(prefix, namespace)

    g.add((dataset_ref, DCT.identifier, Literal(dataset_dict.get('id', None))))
    g.add((dataset_ref, DCT.type, Literal(dataset_dict.get('type', 'dataset'))))
    g.add((dataset_ref, DCAT.landingPage, Literal(dataset_dict.get('url', None))))

    # Basic fields
    items = [
        ('document_type', AGLS.documentType, None),
        ('odm_document_number', DBPEDIA.documentNumber, None),
        ('title_translated', DCT.title, None),
        ('odm_short_title', GC.shortTitle, None),
        ('notes_translated', DCT.description, None),
        ('license', DCT.license, None),
        ('copyright', CRO.copyright, None),
        ('owner_org', FOAF.organization, None),
        ('contact', EBUCORE.contact, None),
        ('odm_laws_previous_changes_notes', SKOS.changeNote, None),
        ('odm_laws_official_publication_reference', SORON.citedBy, None),
        ('odm_laws_notes', SKOS.note, None),
        ('odm_reference_document', PPROC.documentReference, None)
    ]
    self._add_triples_from_dict(dataset_dict, dataset_ref, items)


    #  Lists
    items = [
        ('odm_language', DCT.language, None),
        ('odm_spatial_range', GN.countrycode, None),
        ('taxonomy', FOAF.topic, None)
    ]
    self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

    # Dates
    items = [
        ('odm_promulgation_date',BIBFRAME.legalDate, None)
    ]
    self._add_date_triples_from_dict(dataset_dict, dataset_ref, items)

    # Resources
    for resource_dict in dataset_dict.get('resources', []):

      distribution = URIRef(resource_uri(resource_dict))
      g.add((dataset_ref, DCAT.distribution, distribution))
      g.add((distribution, RDF.type, DCAT.Distribution))

      items = [
          ('name', DCT.title, None),
          ('description', DCT.description, None)
      ]
      self._add_triples_from_dict(resource_dict, distribution, items)

      #  Lists
      items = [
          ('odm_language', DCT.language, None)
      ]
      self._add_list_triples_from_dict(resource_dict, distribution, items)

      # Format
      if '/' in resource_dict.get('format', ''):
        g.add((distribution, DCAT.mediaType,
               Literal(resource_dict['format'])))
      else:
        if resource_dict.get('format'):
          g.add((distribution, DCT['format'],
                 Literal(resource_dict['format'])))

        if resource_dict.get('mimetype'):
          g.add((distribution, DCAT.mediaType,
                 Literal(resource_dict['mimetype'])))

      # URL
      url = resource_dict.get('url')
      download_url = resource_dict.get('download_url')
      if download_url:
        g.add((distribution, DCAT.downloadURL, Literal(download_url)))
      if (url and not download_url) or (url and url != download_url):
        g.add((distribution, DCAT.accessURL, Literal(url)))

  def graph_from_catalog(self, catalog_dict, catalog_ref):

    log.debug("ODMDCATBasicProfileLaws graph_from_catalog")

    g = self.g

    for prefix, namespace in namespaces.iteritems():
      g.bind(prefix, namespace)

    g.add((catalog_ref, RDF.type, DCAT.Catalog))

    # Basic fields
    items = [
        ('title', DCT.title, config.get('ckan.site_title')),
        ('description', DCT.description, config.get('ckan.site_description')),
        ('homepage', FOAF.homepage, config.get('ckan.site_url')),
        ('language', DCT.language, config.get('ckan.locale_default', 'en')),
    ]
    for item in items:
      key, predicate, fallback = item
      if catalog_dict:
        value = catalog_dict.get(key, fallback)
      else:
        value = fallback
      if value:
        g.add((catalog_ref, predicate, Literal(value)))

    # Dates
    modified = self._last_catalog_modification()
    if modified:
      self._add_date_triple(catalog_ref, DCT.modified, modified)
