#Testing various ideas on using the yaml mapping files
import yaml
import json
import argparse
import pprint
import cdsQueries as cdsq
import CDATranslate as cdt
import CDSJSON_model as model
import importlib
import sys

def printIt(cdafinal, filename):
    cdaoutput = json.dumps(cdafinal, indent=4)
    f = open(filename, "w")
    f.write(cdaoutput)
    f.close()

def main(args):
    #Read the config file
    configs = cdt.readTransformFile(args.configfile)
    #pprint.pprint(configs)
    #sys.exit()

    #Import the query python module indicated in the config file
    #https://stackoverflow.com/questions/64916281/importing-modules-dynamically-in-python-3-x
    q = importlib.import_module(configs['query_module'])
    q.init()
   # pprint.pprint(q.file_info)
    #sys.exit()

    #Instatiate empty final JSON doc
    cdafinal = {}

    model.init()
    #cdsq.init()
    mappingdata = cdt.readTransformFile(configs['field_mapping_file'])
    #pprint.pprint(mappingdata)

    #Files
    #filelist = cdt.getAndProcessData(configs['graphql_url'],q.file_info, configs['file_keyword'], mappingdata,model.file, model.identifiers, configs['data_source'], configs['file_identifier'])
    filelist = cdt.getAndProcessData(configs['graphql_url'],q.nested_test_query, configs['file_keyword'],mappingdata, configs['data_source'], configs['file_identifier'])
    #filelist = cdt.getAndProcessData(configs['graphql_url'],q.file_info, configs['file_keyword'],mappingdata, configs['data_source'], configs['file_identifier'])


    cdafinal['file'] = filelist
    
    if args.output is not None:
        printIt(cdafinal, args.output)

    sys.exit()

    #Diagnosis
    diaglist = cdt.getAndProcessData(CDSAPI, cdsq.diagnosis_info,'diagnosis', mappingdata, model.diagnosis, model.identifiers, REPO)
    cdafinal['diagnosis'] = diaglist

    #Treatment
    treatlist = cdt.getAndProcessData(CDSAPI, cdsq.treatment_info, 'treatment', mappingdata, model.treatment, model.identifiers, REPO)
    cdafinal['treatment'] = treatlist

    #Specimen
    speclist = cdt.getAndProcessData(CDSAPI, cdsq.sample_info, 'sample', mappingdata, model.specimen, model.identifiers, REPO)
    cdafinal['specimen'] = speclist

    #Sujbect
    sublist = cdt.getAndProcessData(CDSAPI, cdsq.basic_subject_info, 'participant', mappingdata, model.subject, model.identifiers, REPO)
    cdafinal['subject'] = sublist

    #ResearchSubject
    rslist = cdt.getAndProcessData(CDSAPI, cdsq.research_subject_info, 'participant', mappingdata, model.research_subject, model.identifiers, REPO)
    cdafinal['research_subject'] = rslist

    if args.verbose:
        pprint.pprint(cdafinal)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True, help="Configuraion yaml file")
    parser.add_argument("-v", "--verbose", action="store_true",help="Enable verbose feedback" )
    #parser.add_argument("-t", "--transformfile", required=True, help="Name of the transform yaml file")
    #parser.add_argument("-s", "--schema", required=True, help="JSON Schemafile")
    parser.add_argument("-o", "--output", help="Output file name")
    #parser.add_argument("-c", "--check_validation", action="store_true", help="Run validation against the schema supplied with -s")

    args = parser.parse_args()
    main(args)