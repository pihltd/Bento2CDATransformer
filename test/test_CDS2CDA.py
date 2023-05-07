import pytest
import CDS2CDA as cds2cda

def test_checkAPI():
    testquery = """
    {
        program{
            program_acronym
        }
    }
    """

    CDSAPI = "https://dataservice.datacommons.cancer.gov/v1/graphql/"
    result = cds2cda.getAPIJSON(CDSAPI, testquery)
    #result = checkAPI(testquery)
    assert len(result['data']['program']) >= 1

def test_SingleMappingTransform():
    mappingdata = {"md5sum" : {"file" : "checksum"}}
    maplist = cds2cda.getMappedKey('md5sum', mappingdata)
    assert maplist == "checksum"

def test_ManyToOneMappingTransform():
    mappingdata = {'file_id': {'file': ['id',
                                         'identifier.field_name',
                                         'identifier.value',
                                         'drs_uri']}}
    maplist = cds2cda.getMappedKey('file_id', mappingdata)
    assert maplist[0] == 'id'
    assert maplist[1] == 'identifier.field_name'
    assert maplist[2] == 'identifier.value'
    assert maplist[3] == 'drs_uri'

def test_EasyParse():
    data = {
  "data": {
    "file": [
      {
        "file_id": "CDS-FILE-865205",
        "file_name": "scientiae_et_patriae",
        "file_type": "TSV"
      }]}}
    
    mappingdata = {"field_mappings" :{'file_id': {'file': ['id',
                                         'identifer.field_name',
                                         'identifier.value',
                                         'drs_uri']},
                    'file_name': {'file': ['label']},
                    'file_size': {'file': ['byte_size']},
                    'file_type': {'file': ['file_format']}}}
    
    results = cds2cda.genericInfoParse(data, mappingdata, 'file')
    for result in results:
        assert result['id'] == "CDS-FILE-865205"
        assert result['label'] == "scientiae_et_patriae"
        assert result['file_format'] =="TSV"

def test_NestedDictParse():
    data = {
  "data": {
    "participant": [
      {
        "participant_id": "CDS-CASE-449906",
        "study": {
          "study_name": "salus_in_arduis"
        }
      }]}}
    
    mappingdata = {"field_mappings" :{"participant_id" :{'subject': ['id', 'identifier.value']},
                                      'study_name': {'file': ['associated_projects']}}}

    results = cds2cda.genericInfoParse(data, mappingdata, 'participant')
    for result in results:
        assert result['id'] == "CDS-CASE-449906"
        assert result['associated_projects'] =="salus_in_arduis"

def test_NestedListParse():

    data = {
  "data": {
    "participant": [
      {
        "participant_id": "CDS-CASE-449906",
        "gender": "Male",
        "race": "imperium_in_imperio",
        "ethnicity": "not reported",
        "study": {
          "organism_species": "scientiae_et_patriae",
          "study_acronym": "nascentes_morimur_finisque_ab_origine_pendet"
        },
        "diagnoses": [
          {
            "vital_status": "Alive"
          }
        ]
      }]}}
    
    mappingdata = {"field_mappings":{"participant_id" :{'subject': ['id', 'identifier.value']},
                                     'gender': {'subject': ['sex']},
                                      'race': {'subject': ['race']},
                                       'ethnicity': {'subject': ['ethnicity']},
                                        'organism_species': {'subject': ['species']},
                                         'study_acronym': {'file': ['associated_projects']},
                                        'vital_status': {'subject': ['vital_status']} }}
    
    results = cds2cda.genericInfoParse(data, mappingdata, 'participant')
    for result in results:
        assert result['id'] == "CDS-CASE-449906"
        assert result['species'] == "scientiae_et_patriae"
        assert result['vital_status']  == "Alive"

  
