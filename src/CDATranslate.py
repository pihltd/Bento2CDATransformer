# Python library of routines for translating using a translation yaml file
from python_graphql_client import GraphqlClient
import jsonschema
import yaml

def getGraphQLJSON(apiurl, query):
    # For use with a Bento GraphQL endpoint.  Returns query results as JSON
    client = GraphqlClient(endpoint=apiurl)
    jsondata = client.execute(query = query)
    return jsondata

def readTransformFile(yamlfile):
    #Reads a yaml mapping file, returns a JSON object of it
    with open(yamlfile, "r") as stream:
        transformdata = yaml.safe_load(stream)
    return transformdata

def getMappedKey(sourcefield, fullmappingjson):
    # Will return a list of CDA field name from the mapping json.
    mappingjson = fullmappingjson['field_mappings']
    mapping = mappingjson[sourcefield]
    for node, mappinglist in mapping.items():
        return mappinglist
    
def genericInfoParse(graphqlresults, mappingdata, graphqlindex):
    #First pass parse of data returned from graphql queries.  The graphqlindex is the field name after 'data' in graphql results
    finalarray = []
    tempjson = {}
    #mappings = mappingdata['field_mappings']
    for instance in graphqlresults['data'][graphqlindex]:
        for cdsfield,cdsvalue in instance.items():
            if isinstance(cdsvalue, dict):
                #Process dictionary
                for field, value in cdsvalue.items():
                    mappedlist = getMappedKey(field, mappingdata)
                    for newfield in mappedlist:
                        tempjson[newfield] = value
            elif isinstance(cdsvalue, list):
                #Process list
                for entry in cdsvalue:
                    if isinstance(entry,dict):
                        for field, value in entry.items():
                            mappedlist = getMappedKey(field, mappingdata)
                            for newfield in mappedlist:
                                tempjson[newfield] = value
                    #May need and if isinstance(entry, list), but no examples yet
                            
            else:
                #Not nested data, process
                mappedlist = getMappedKey(cdsfield, mappingdata)
                for newfield in mappedlist:
                    tempjson[newfield] = cdsvalue
        finalarray.append(tempjson)
    return finalarray

def testingParse(graphqlresults, mappingdata, graphqlindex):
    #Experimental version of genericInfoParse.  
    finalarray = {}
    tempjson = {}
    finallist = []
    for instance in graphqlresults['data'][graphqlindex]:
        for originalfield, originalvalue in instance.items():
            if isinstance(originalvalue, dict):
                #Process as dictionary
                print("Dictionary Parse")
            elif isinstance(originalvalue, list):
                #Process as list
                print("List Parse")
            else:
                #Not nested
                print("Normal Parse")
                cdafieldlist = testingGetMappedKeys(originalfield, mappingdata)
                for entry in cdafieldlist:
                    for cdadomain,cdafields in entry.items():
                        for cdafield in cdafields:
                            tempjson[cdafield]= originalvalue 
                            finalarray[cdadomain] = tempjson
                            finallist.append(finalarray)
                            tempjson = {}
                            finalarray = {}
    return finallist

def parseEntry(graphqlresults, mappingdata, entryjson, instancejson):
    #finaljson = {}
    for originalfield, originalvalue in graphqlresults.items():
        if isinstance(originalvalue, dict):
            #Process as dicitonary
            print("Dictionary Parse")
        elif isinstance(originalvalue, list):
            #process as a list
            print('List parse')
        else:
            #Not nested
            print("Normal parse")
            cdafieldlist = testingGetMappedKeys(originalfield, mappingdata)
            for entry in cdafieldlist:
                for cdadomain, cdafields in entry.items():
                    for cdafield in cdafields:
                        if cdafield in instancejson:
                            if isinstance(instancejson[cdafield], list):
                                instancejson[cdafield].append(originalvalue)
                            else:
                                instancejson[cdafield] = originalvalue
                        else:
                            #Has to be entryjson
                            if isinstance(entryjson[cdafield], list):
                                entryjson[cdafield].append(originalvalue)
                            else:
                                entryjson[cdafield] = originalvalue
    entryjson["identifiers"] = instancejson
    return entryjson

                

def testingGetMappedKeys(sourcefield, fullmappingjson):
    #Experimental version of getMappedKeys
    mappingjson = fullmappingjson['field_mappings']
    mapping = mappingjson[sourcefield]
    mappinglist = []
    # mapping should now be a list of dict
    for entry in mapping:
        #cdanode is the CDA domain, cdafield is a list of fields from that node
        for cdanode, cdafieldlist in entry.items():
            mappinglist.append({cdanode:cdafieldlist})
    return mappinglist
        

def validateJSON(schema, cdajson):
    sf =  open(schema, 'r')
    cdaschema = json.load(sf)
    try:
        jsonschema.validate(cdajson,cdaschema)
    except jsonschema.exceptions.ValidationError as e:
        print(e)
        return False
    return True

