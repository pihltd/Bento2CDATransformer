# Python library of routines for translating using a translation yaml file
from python_graphql_client import GraphqlClient
import jsonschema
import yaml
import json

def getGraphQLJSON(apiurl, query):
    # For use with a Bento GraphQL endpoint.  Returns query results as JSON
    client = GraphqlClient(endpoint=apiurl)
    jsondata = client.execute(query = query)
    return jsondata
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

def parseIdentifiers(idjson, flatpack, identifier, sourceidentifier, datasource):
    idjson['system'] = datasource
    idjson['field_name'] = identifier
    #fieldid = identifier.split(".").pop()
    #fieldid = sourceidentifier
    idjson['value'] = flatpack[sourceidentifier]
    return idjson

def validateJSON(schema, cdajson):
    sf =  open(schema, 'r')
    cdaschema = json.load(sf)
    try:
        jsonschema.validate(cdajson,cdaschema)
    except jsonschema.exceptions.ValidationError as e:
        print(e)
        return False
    return True