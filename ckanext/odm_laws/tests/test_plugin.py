import pytest
from ckanext.odm_laws import plugin
from ckanext.odm_laws.tests import helpers as test_h
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from ckan import model
import ckan.tests.helpers as helpers
from ckan.tests import factories
from ckan.logic import _actions
import mock


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestOdmLawsPlugin:

    def setup(self):
        self.instance = plugin.OdmLawsPlugin()

    def test_plugin_setup(self):
        assert len(self.instance.get_helpers()) > 0

    def test_after_create(self, monkeypatch):

        def issue_create(context, data_dict):
            # Patch the issue create and see if the module is called
            assert "title" in data_dict and data_dict.get('title', '') == "User Laws record Upload Checklist"
            assert "description" in data_dict
            assert "dataset_id" in data_dict
            return True

        monkeypatch.setitem(_actions, 'issue_create', issue_create)

        pkg = test_h.OdmLawsDataset().create(
            type='laws_record'
        )
        assert toolkit.asbool(toolkit.config.get("ckanext.issues.review_system", False))
        self.instance.after_create({}, pkg)
