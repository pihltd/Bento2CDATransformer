#New and improved version of CDS2CDA
# Uses Nelson's mapping file
# flips parsing, loop through CDA data and try to load from CDS
import argparse
import pprint
import test_data as td
import yaml
import CDSASON_model as model
import sys

def yaml2JSON(yamlfile):
    #Rename to readYamlFile
    #Reads a yaml mapping file, returns a JSON object of it
    with open(yamlfile, "r") as stream:
        transformdata = yaml.safe_load(stream)
    return transformdata

def parseList(bentovalue, flatpack):
    for entry in bentovalue:
        if isinstance(entry, dict):
            flatpack = parseDict(entry, flatpack)
        elif isinstance(entry,list):
            flatpack= parseList(entry, flatpack)
        else:
            for key, value in entry:
                flatpack[key] = value
    return flatpack

def parseDict(bentovalue, flatpack):
    for key, value in bentovalue.items():
        if isinstance(value, list):
            flatpack = parseList(value, flatpack)
        elif isinstance(value, dict):
            flatpack = parseDict(value, flatpack)
        else:
            flatpack[key] = value
    return flatpack
        

def flatGraphQL(graphqlresults):
    #WARNING assumes that all keys are unique
    flatpack = {}
    for bentofield, bentovalue in graphqlresults.items():
        if isinstance(bentovalue, dict):
            flatpack = parseDict(bentovalue, flatpack)
        elif isinstance(bentovalue, list):
            flatpack = parseList(bentovalue, flatpack)
        else:
            flatpack[bentofield] = bentovalue
    return flatpack

def parseGraphQLDict(graphqlresult, benotfield, cdafield, mainjson):

    return mainjson

def parseGraphQLList(graphqlresult, bentofield, cdafield, mainjson):
    # graphqlresult should be a fragment of a graphqlrespons
    # Example[{'sample_id': 'CDS-BIOS-523139', 'participant': {'participant_id': 'CDS-CASE-449906'}}]
    # bentofield should be the bentofiled associated with the cdafield
    # cdafield should be the field we're trying to fill with bento values
    # Mainjson is the json object we're populating
    print(("CDAFIELD:\t%s") % (cdafield))
    #print(("MAINJSON TYPE:\t %s") % (type(mainjson[cdafield])))
    for entry in graphqlresult:
        pprint.pprint(entry)
        #Assuming entry is a dictionary of some sort
        for bentokey, bentovalue in entry.items():
            if isinstance(bentovalue, dict):
                print(("Processing %s as a dict") % (bentovalue))
                mainjson = parseGraphQLDict(bentovalue, bentokey, cdafield, mainjson)
            elif isinstance(bentovalue, list):
                print(("processing %s as a list") % (bentovalue))
                mainjson = parseGraphQLList(bentovalue, bentokey, cdafield, mainjson)
            else:
                print(("Processing %s as normal") % (bentovalue))
                print(("Bentokey:\t%s\tBentofield:\t%s") % (bentokey, bentofield))
                if bentokey == bentofield:
                    if isinstance(mainjson[cdafield], list):
                        print(("Should be appending Value:\t%s\t to key:\t%s") %(bentovalue, cdafield))
                        mainjson[cdafield].append(bentovalue)
                    else:
                        mainjson[cdafield] = bentovalue
    return mainjson



def processMainJSON(mainjson, graphqldata, mappingsegment, datasource):
    # mapping segement should be mappingjson['Props][configs['file_keyword]]
    # graphqldata should just be a single stanza of a query result
    # mainjson is the CDA structure that will be loaded with data from graphqldata
    # Datasource is the Bento data repository such as CDS, ICDC, CTDC

    for cdafield in mainjson.keys():
        #Step One:  Only proceed with known mapped fields, ignore everything else
        searchfield = None
        if cdafield in mappingsegment:
            #Step Two: get the mapped Bento fields
            mappedbentolist = mappingsegment[cdafield][datasource]
            #Step Three: For CDA fields that are in the first level of Bento query results, get the data and move it
            for mappedbentoentry in mappedbentolist:
                for bentofield, value in mappedbentoentry.items():
                    if bentofield != 'Parents':
                        searchfield = bentofield
                        if bentofield in graphqldata:
                            if isinstance(mainjson[cdafield], list):
                                mainjson[cdafield].append(graphqldata[bentofield])
                            else:
                                mainjson[cdafield] = graphqldata[bentofield]
                #Step Four:  The CDA field has been mapped, but isn't in the first level, so it must be buried in the graphql results somewhere.
                #To pull this off, need the mapped value to cdafield
                for bentofield, bentovalue in graphqldata.items():
                    print(("Searchfield is:\t %s") % (searchfield))
                    if isinstance(bentovalue, list):
                        # Example[{'sample_id': 'CDS-BIOS-523139', 'participant': {'participant_id': 'CDS-CASE-449906'}}]
                        print("Do list things")
                        print(("BentoField:\t%s\tBentoValue:\t%s") % (bentofield, bentovalue))
                        mainjson = parseGraphQLList(bentovalue, searchfield, cdafield, mainjson)

                    #elif isinstance(bentovalue, dict):
                    #    print("Do dict things")
                    #    print(("BentoField:\t%s\tBentoValue:\t%s") % (bentofield, bentovalue))
                    
                    #else:
                    #    print("Houston, we have a problem")
                    #    print(("BentoField:\t%s\tBentoValue:\t%s") % (bentofield, bentovalue))
                    
    pprint.pprint(mainjson)
    return mainjson

def flatProcessMainJSON(mainjson, flatgraphqldata, mappingsegment, datasource):
    #Flatten the grpahqldata
    #flatgraphqldata = flatGraphQL(graphqldata)
    
    #Get a list of fields in the CDA JSON
    for cdafield in mainjson:
        #Ignore unmapped fields
        if cdafield in mappingsegment:
            #Get mapped Bento fields
            mappedbentollist = mappingsegment[cdafield][datasource]
            for mappedbentoentry in mappedbentollist:
                for bentofield in mappedbentoentry.keys():
                    if bentofield in flatgraphqldata:
                        if isinstance(mainjson[cdafield], list):
                            mainjson[cdafield].append(flatgraphqldata[bentofield])
                        else:
                            mainjson[cdafield] = flatgraphqldata[bentofield]
    return mainjson

def parseIdentifiers(idjson, flatpack, identifier, datasource):
    idjson['system'] = datasource
    idjson['field_name'] = identifier
    fieldid = identifier.split(".").pop()
    idjson['value'] = flatpack[fieldid]
    return idjson


def main(args):
    td.init()
    configs = yaml2JSON(args.configfile)
    mappingjson = yaml2JSON(configs['field_mapping_file'])
    finaljson = {}


    # A query woudl go here
    finaljson['file'] = []
    for filegraphqldata in td.file_res['data'][configs['file_keyword']]:
    #for filegraphqldata in td.mini_file['data'][configs['file_keyword']]:
        flatpack = flatGraphQL(filegraphqldata)
        model.init() #Apparently need to init model every round otherwise lists keep accumluation over rounds
        processed = flatProcessMainJSON(model.file,flatpack, mappingjson['Props'][configs['file_keyword']], configs['data_source'])
        identifiers = parseIdentifiers(model.identifiers, flatpack, configs['file_identifier'], configs['data_source'])
        processed['identifiers'] = identifiers
        finaljson['file'].append(processed)
    
    pprint.pprint(finaljson)
                      



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True, help="Configuraion yaml file")
    parser.add_argument("-v", "--verbose", action="store_true",help="Enable verbose feedback" )
    parser.add_argument("-o", "--output", help="Output file name")

    args = parser.parse_args()
    main(args)
