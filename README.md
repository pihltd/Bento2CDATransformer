# Bento2CDATransformer
Script to create a CDA JSON file from the Bento GraphQL API

# Pre-requisite libraries:
- argparse
- json
- jsonschema
- yaml


# Files:

## Bento2CDA.py
Man script to run.  Command line options:
  - __-v, --verbose__ : Verbose error messages.  Currently not in use
  - __-c, --configfile__ : Name of the configuration yaml file used to run Benot2CDA.  This exists to prevent an annoyingly huge number of command line options.  See __config.yaml__ for an example
  - __-o, --output__ : Filename for the final script output
  - __-t, ---testmode__ : eRun script using testing data
  - __-s, --schemavalidate__: Validate the final JSON against the schema listed in the confgiruation file
 -  __-h, --help__: Prints this list
  
## CDATranslate.py
Library of routines used by __Bento2CDA.py__

## Field mapping File
This YAML file contains a mapping between CDA fields and the fields from the Bento site.  While a full description of this format is beyond the scope of this document, the example shows the basic outline:

```yaml
Source: CDA
Models:
  - CDS
Props:
  file:
    id:
      CDS:
        - file_id:
          Parents: file
    label:
      CDS:
        - file_name:
          Parents: file
```
- __Source__: The model that all other models are mapped to.
- __Models__: A list of models that were mapped to the Source model.  Multiple model mappings are supported
- __Props__: A dictionary of all the property mappings.  Follows the format:
```yaml
Source domain/table:
  Source fieldname (example id):
    Model source (example CDS):
      - mapped model fieldname (example file_id)
        mapped model fieldname parent
```
This stanza is repeated for all model fields that are mapped to the source field
See __CDA-CDS_mapping.yaml__ for an example

## Query file 
This file should contatin the queries needed to populate the sections of the CDA JSON.  The expectation is for the following queries:
- file_info
- diganosis_info
- treatment_info
- sample_info
- subject_info
- research_subject_info

The information from these queries will be used for the respective sections of the CDA JSON listed in CDAJSON_model.py

See __cdsQueries.py__ for an example

## JSON Model file
This file contains JSON represented each of the major components of the final CDA JSON file.  They are broken out into file, diagnosis, treatment, specimen, subject, and research_subject.  Each instance would represent a single query result and multiple instances are put together in a list.
See __CDAJSON_model.py__ for an example

## Configuration file
This file contains a number of parameters that Bento2CDA needs to run.  This file should be valid Yaml.
### Configuration file fields:
- __data_source__: The CRDC data commons that will be the source of the data.  Valid values include CDS, ICDC, CTDC, etc.
- __graphql_url__: GraphQL endpoing URL that will be used to run queries
- __file_keyword__:  Bento GraphQL returns JSON that is itemized by two keywords  'data', and the keyword for the primary node.  This field provides the keyword used for the file primary node.
- __file_identifier__: This is a static value used to populate fields in the _identifiers_ section of the CDA standard JSON for file
- __diagnosis_keyword__: Same as file_keyword, but for diagnosis queries
- __diagnosis_identifier__: Same as file_identifier but for the diagnosis section
- __specimen_keyword__: Same as file_keyword, but for specimen queries
- __specimen_identifier__: Same as file_identifier but for the specimen section
- __treatment_keyword__: Same as file_keyword, but for treatment queries
- __treatment_identifier__: Same as file_identifier but for the treatment section
- __subject_keyword__:  Same as file_keyword, but for subject queries
- __subject_identifier__: Same as file_identifier but for the subject section
- __research_subject_keyword__: Same as file_keyword, but for research_subject queries (frequently the same as subject)
- __research_subject_identifier__: Same as file_identifier but for the research_subject section
- __query_module__: File that contains the GraphQL queries approprate for the data source
- __field_mapping_file__:  YAML file that contains the mappings between CDA and the Bento instance.  See __CDA-CDS_mapping.yaml__ for an example.
- __json_schema__: The CDA provided JSON schema file


  - 
