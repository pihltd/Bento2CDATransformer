#Testing various ideas on using the yaml mapping files
import yaml
import json
import argparse
import pprint
import cdsQueries as cdsq
import CDATranslate as cdt

def main(args):
    #Empty dictionaries for each of the CDA nodes
    cdafile = {}
    cdadiagnosis = {}
    cdatreatment = {}
    cdaspecimen = {}
    cdasubject = {}
    cdaresearchsubject = {}
    #Empty final JSON doc
    cdafinal = {}

    CDSAPI = "https://dataservice.datacommons.cancer.gov/v1/graphql/"


    #Bring in the yaml file and transform it
    mappingdata = cdt.readTransformFile(args.transformfile)
    if args.verbose:
        pprint.pprint(mappingdata)

    #Question 1 - For one to many mappings, can the node information be used?  For example, distinguishing between CDA's subject and research_subject fields.
    # A CDS study maps to file.associated_projects and to research_subject.member_of_research_project
    studyQuery = """
    {
        study{
            study_name
        }
    }
    """
    #studydata = cdt.getGraphQLJSON(CDSAPI, studyQuery)
    #tempjson = cdt.testingParse(studydata, mappingdata,'study')
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",help="Enable verbose feedback" )
    parser.add_argument("-t", "--transformfile", required=True, help="Name of the transform yaml file")
    parser.add_argument("-s", "--schema", required=True, help="JSON Schemafile")
    parser.add_argument("-o", "--output", help="Output file name")
    parser.add_argument("-c", "--check_validation", action="store_true", help="Run validation against the schema supplied with -s")

    args = parser.parse_args()
    main(args)