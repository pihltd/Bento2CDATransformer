#New and improved version of CDS2CDA
# Uses Nelson's mapping file
# flips parsing, loop through CDA data and try to load from CDS
import argparse
import pprint
import test_data as td
import CDSJSON_model as model
import CDATranslate as cdt
import cdsQueries as cdsq
import json

def printIt(cdafinal, filename):
    cdaoutput = json.dumps(cdafinal, indent=4)
    f = open(filename, "w")
    f.write(cdaoutput)
    f.close()


def main(args):
    configs = cdt.yaml2JSON(args.configfile)
    mappingjson = cdt.yaml2JSON(configs['field_mapping_file'])
    finaljson = {}

    if args.testmode:
          td.init()
          filequeryresults = td.file_res
    else:
         cdsq.init()
         filequeryresults = cdt.getGraphQLJSON(configs['graphql_url'], cdsq.file_info)

    # File
    finaljson['file'] = []
    for filegraphqldata in filequeryresults['data'][configs['file_keyword']]:
        flatpack = cdt.flatGraphQL(filegraphqldata)
        model.init() #Apparently need to init model every round otherwise lists keep accumluation over rounds
        processed = cdt.flatProcessMainJSON(model.file,flatpack, mappingjson['Props'][configs['file_keyword']], configs['data_source'])
        #NEED to make sure the identifiers routine returns a list, not just an instance
        identifiers = cdt.parseIdentifiers(model.identifiers, flatpack, configs['file_identifier'], configs['data_source'])
        processed['identifiers'].append(identifiers)
        finaljson['file'].append(processed)

    #Diagnosis
    diagnosisqueryresults = cdt.getGraphQLJSON(configs['graphql_url'], cdsq.diagnosis_info)
    finaljson['diagnosis'] = []
    for diagnosisgraphqldata in diagnosisqueryresults['data'][configs['diagnosis_keyword']]:
         flatpack = cdt.flatGraphQL(diagnosisgraphqldata)
         model.init()
         processed = cdt.flatProcessMainJSON(model.diagnosis,flatpack,mappingjson['Props'][configs['diagnosis_keyword']],configs['data_source'])
         identifiers = cdt.parseIdentifiers(model.identifiers, flatpack, configs['diagnosis_identifier'], configs['data_source'])
         processed['identifiers'].append(identifiers)
         finaljson['diagnosis'].append(processed)

    #Treatment
    #There's currently no treatment data in CDS, so load an empty list
    finaljson['treatment'] = []

    #Specimen
    specqueryresults = cdt.getGraphQLJSON(configs['graphql_url'], cdsq.sample_info)
    finaljson['specimen'] = []
    for specquerydata in specqueryresults['data'][configs['specimen_query_keyword']]:
         flatpack = cdt.flatGraphQL(specquerydata)
         model.init()
         processed = cdt.flatProcessMainJSON(model.specimen, flatpack, mappingjson['Props'][configs['specimen_map_keyword']], configs['data_source'])
         identifiers = cdt.parseIdentifiers(model.identifiers, flatpack, configs['specimen_identifier'], configs['data_source'])
         processed['identifiers'].append(identifiers)
         finaljson['specimen'].append(processed)

    cdt.validateJSON(finaljson)
    
    if args.output is not None:
         printIt(finaljson, args.output)
    
    if args.verbose:
        pprint.pprint(finaljson)
                      



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True, help="Configuraion yaml file")
    parser.add_argument("-v", "--verbose", action="store_true",help="Enable verbose feedback" )
    parser.add_argument("-o", "--output", help="Output file name")
    parser.add_argument("-t", "--testmode", action="store_true", help ="Run in test mode, limited data")

    args = parser.parse_args()
    main(args)