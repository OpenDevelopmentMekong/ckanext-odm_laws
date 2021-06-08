from ckan.tests import factories


class OdmLawsDataset:
    def __init__(self):
        pass

    def _add_mandatory_fields(self, data_dict):
        """
        Add additional dataset arguments
        :return:
        """
        _mandatory_fields = {
            "notes_translated": {"en": "test"},
            "odm_spatial_range": "km",
            "odm_laws_issuing_agency_parties": ["royal_palace"],
            "odm_document_type": "law",
            "odm_laws_official_publication_reference": "Royal Gazette",
            "odm_laws_status": "signed_and_in_effect"
        }
        for k, val in _mandatory_fields.items():
            data_dict[k] = data_dict.get(k, val)
        return data_dict

    def create(self, *args, **kwargs):
        kwargs = self._add_mandatory_fields(kwargs)
        return factories.Dataset(*args, **kwargs)