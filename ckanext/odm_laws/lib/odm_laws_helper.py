#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import os
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.base import render

DEBUG = True

log = logging.getLogger(__name__)

def get_dataset_type():
	'''Return the dataset type'''

	log.debug('get_dataset_type')

	return 'laws_record'

def get_related_documents(package_id, limit=5):
	'''Search for law records sharing at least one taxonomy topic with the
	given package, excluding the package itself.

	Returns a dict like package_search results:
	    {results: [...], count: N, topic: <first shared topic>}
	'''
	try:
		import ckan.logic as logic
		context = {'ignore_auth': True}
		pkg = logic.get_action('package_show')(context, {'id': package_id})
	except Exception:
		return {'results': [], 'count': 0, 'topic': None}

	topics = pkg.get('taxonomy') or []
	if isinstance(topics, str):
		raw = topics.strip()
		if raw.startswith('{') and raw.endswith('}'):
			raw = raw[1:-1]
		topics = [t.strip().strip('"') for t in raw.split(',')]
		topics = [t for t in topics if t]
	if not topics:
		return {'results': [], 'count': 0, 'topic': None}

	# Build fq: dataset_type + (topic OR topic ...) - current id
	or_clause = ' OR '.join('taxonomy:"{0}"'.format(t.replace('"', '\\"')) for t in topics)
	fq = '+dataset_type:laws_record +({0}) -id:{1}'.format(or_clause, pkg['id'])

	try:
		context = {'ignore_auth': True}
		result = toolkit.get_action('package_search')(context, {
			'fq': fq,
			'rows': limit,
			'sort': 'metadata_modified desc',
		})
		return {
			'results': result.get('results', []),
			'count': result.get('count', 0),
			'topic': topics[0],
		}
	except Exception as e:
		log.error('get_related_documents failed: %s', e)
		return {'results': [], 'count': 0, 'topic': None}

def create_default_issue_laws_record(pkg_info, context=None):
	''' Uses CKAN API to add a default Issue as part of the vetting workflow for library records'''
	try:
		if not context:
			context = {}
		extra_vars = {}

		issue_message = render('messages/default_issue_laws_record.txt',extra_vars=extra_vars)

		params = {'title':'User Laws record Upload Checklist','description':issue_message,'dataset_id':pkg_info['id']}
		toolkit.get_action('issue_create')(context, params)

	except KeyError:

		log.error("Action 'issue_create' not found. Please make sure that ckanext-issues plugin is installed.")

def validate_fields(package):
	'''Checks that the package has all required fields'''

	if DEBUG:
		log.info('validate_fields: %s', package)

	missing = {"package" :[], "resources": [] }

	schema_path = os.path.abspath(os.path.join(__file__, '../../','odm_laws_schema.json'))
	with open(schema_path) as f:
		try:
			schema_json = json.loads(f.read())

			for field in schema_json['dataset_fields']:
				if "validate" in field and field["validate"] == "true":
					if field["field_name"] not in package or not package[field["field_name"]]:
						missing["package"].append(field["field_name"])
					elif "multilingual" in field and field["multilingual"] == "true":
						json_field = package[field["field_name"]];
						if json_field and "en" not in json_field or json_field["en"] == "":
							missing["package"].append(field["field_name"])

			for resource_field in schema_json['resource_fields']:
				for resource in package["resources"]:
					if "validate" in resource_field and resource_field["validate"] == "true":
						if resource_field["field_name"] not in resource or not resource[resource_field["field_name"]]:
							missing["resources"].append(resource_field["field_name"])
						elif "multilingual" in resource_field and resource_field["multilingual"] == "true":
							json_resource_field = resource[resource_field["field_name"]];
							if json_resource_field and "en" not in json_resource_field or json_resource_field["en"] == "":
								missing["resources"].append(resource_field["field_name"])

		except ValueError as e:
			log.info('invalid json: %s' % e)

	return missing

session = {}


@toolkit.chained_helper
def humanize_entity_type(next, entity_type, object_type, purpose):
  if object_type == 'laws_record':
    object_type = 'law'
  return next(entity_type, object_type, purpose)
