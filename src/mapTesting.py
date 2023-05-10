#Testing various ideas on using the yaml mapping files
import yaml
import json
import argparse
import pprint
import cdsQueries as cdsq
import CDATranslate as cdt
import CDA_dataclass as dc
from dataclasses import  asdict
import CDSJSON_model as model
#import dataclasses

def main(args):
    #Empty final JSON doc
    cdafinal = {}

    CDSAPI = "https://dataservice.datacommons.cancer.gov/v1/graphql/"

    model.init()
    cdsq.init()
    mappingdata = cdt.readTransformFile(args.transformfile)

    #Files
    filedata = cdt.getGraphQLJSON(CDSAPI,cdsq.file_info)
    templist = []
    for file in filedata['data']['file']:
        newJSON = cdt.parseEntry(file, mappingdata, model.file, model.identifiers, "CDS")
        templist.append(newJSON)
    cdafinal['file'] = templist

    #Diagnosis
    diagdata = cdt.getGraphQLJSON(CDSAPI, cdsq.diagnosis_info)
    templist = []
    for entry in diagdata['data']['diagnosis']:
        newJSON = cdt.parseEntry(entry, mappingdata, model.diagnosis, model.identifiers, "CDS")
        templist.append(newJSON)
    cdafinal['diagnosis'] = templist
    pprint.pprint(cdafinal)




    #Bring in the yaml file and transform it
    #mappingdata = cdt.readTransformFile(args.transformfile)
    #if args.verbose:
    #    pprint.pprint(mappingdata)

    #Question 1 - For one to many mappings, can the node information be used?  For example, distinguishing between CDA's subject and research_subject fields.
    # A CDS study maps to file.associated_projects and to research_subject.member_of_research_project
    #studyQuery = """
    #{
    #    study{
    #        study_name
    #    }
    #}
    #"""
    #studydata = cdt.getGraphQLJSON(CDSAPI, studyQuery)
    #tempjson = cdt.testingParse(studydata, mappingdata,'study')
    #pprint.pprint(tempjson)

    #Question 2 - Can a dataclass work better than a custom json job

    #fileQuery = """
    #{
    #    file{
    #        file_id
    #    }
    #}
    #"""

    #filelist = dc.Files
    #model.init()
    #filelist = []
    #filedata = cdt.getGraphQLJSON(CDSAPI, fileQuery)
    #for file in filedata['data']['file']:
    #    t = model.file
    #    t['id'] = file['file_id']
    #    filelist.append(t)
    #pprint.pprint(filelist)
        #t = dc.File()
        #print(asdict(t))
        #t.id = file['file_id']
        #print(asdict(t))
        #print(dataclasses.asdict(t))
        #print(t.__dict__)
        #pprint.pprint(t.id)
        #r = t.to_dict(t)
        #pprint.pprint(r)


    

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",help="Enable verbose feedback" )
    parser.add_argument("-t", "--transformfile", required=True, help="Name of the transform yaml file")
    parser.add_argument("-s", "--schema", required=True, help="JSON Schemafile")
    parser.add_argument("-o", "--output", help="Output file name")
    parser.add_argument("-c", "--check_validation", action="store_true", help="Run validation against the schema supplied with -s")

    args = parser.parse_args()
    main(args)