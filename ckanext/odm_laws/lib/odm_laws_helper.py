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
