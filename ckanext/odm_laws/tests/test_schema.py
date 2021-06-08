import pytest
from ckanext.odm_laws.tests import helpers as test_h
import ckan.plugins.toolkit as toolkit
import ckan.tests.helpers as helpers
from ckan.tests import factories
from ckan import model


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestLawsActions:

    def setup(self):
        self._org = factories.Organization()
        self._sysadmin = factories.Sysadmin()
        self.context = {
            "user": self._sysadmin['name'],
            "model": model,
            "session": model.Session
        }

    def test_odm_laws_create(self):
        pkg = test_h.OdmLawsDataset().create(
            type='laws_record',
            odm_laws_source="test source",
            odm_laws_notes={"en": "test laws"},
            odm_laws_implementing_agencies=["royal_government_of_cambodia"],
            odm_laws_issuing_agency_parties=["office_of_the_prime_minister"],
            odm_laws_official_publication_reference="Royal Gazette Cambodia"

        )
        assert "type" in pkg
        assert pkg.get('type', '') == 'laws_record'
        assert "notes_translated" in pkg
        assert pkg.get('odm_laws_notes', {"en": ""})['en'] == "test laws"
        assert pkg.get('odm_laws_implementing_agencies', [""])[0] == "royal_government_of_cambodia"
        assert pkg.get('odm_laws_issuing_agency_parties', [""])[0] == "office_of_the_prime_minister"
        assert pkg.get('odm_laws_source', '') == "test source"
        assert pkg.get('odm_laws_official_publication_reference', '') == "Royal Gazette Cambodia"

    def test_laws_update(self):
        pkg = test_h.OdmLawsDataset().create(
            type='laws_record',
        )

        pkg_show = toolkit.get_action('package_show')(self.context, {"id": pkg['id']})

        assert pkg['id'] == pkg_show['id']
        assert pkg_show['type'] == 'laws_record'

        pkg_show['odm_laws_official_publication_reference'] = "test update"
        pkg_sh = toolkit.get_action('package_update')(self.context, pkg_show)

        assert "odm_laws_official_publication_reference" in pkg_sh and \
               pkg_sh['odm_laws_official_publication_reference'] == "test update"

    def test_laws_delete(self):
        pkg = test_h.OdmLawsDataset().create(
            type='laws_record'
        )
        toolkit.get_action('package_delete')(self.context, {"id": pkg['id']})
        pkg_show = toolkit.get_action('package_show')(self.context, {"id": pkg['id']})
        assert pkg_show['state'] == 'deleted'
