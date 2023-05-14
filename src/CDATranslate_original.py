# Python library of routines for translating using a translation yaml file
from python_graphql_client import GraphqlClient
import jsonschema
import yaml
import sys
import CDSJSON_model as model

def getGraphQLJSON(apiurl, query):
    # For use with a Bento GraphQL endpoint.  Returns query results as JSON
    client = GraphqlClient(endpoint=apiurl)
    jsondata = client.execute(query = query)
    return jsondata

def readTransformFile(yamlfile):
    #Rename to readYamlFile
    #Reads a yaml mapping file, returns a JSON object of it
    with open(yamlfile, "r") as stream:
        transformdata = yaml.safe_load(stream)
    return transformdata

def getMappedKey(sourcefield, fullmappingjson):
    # Will return a list of CDA field name from the mapping json.
    mappingjson = fullmappingjson['field_mappings']
    #print(sourcefield)
    if sourcefield in mappingjson:
        print(sourcefield)
        mapping = mappingjson[sourcefield]
        #mapping will be either a list of string, or a list of dict
        #if isinstance(mapping, list): #This is a list of dict
            #[{'subject': ['id', 'value']}, {'research_subject': ['id', 'value']}]
            #print(mapping)
        for entry in mapping:
            for field, mappinglist in entry.items():
                    return mappinglist
        else:
            for node, mappinglist in mapping.items():
                if isinstance(mappinglist, dict):
                    for newfield, newlist in mappinglist.items():
                        return newlist
                else:
                    return mappinglist
    else:
        print("pariticipant id sixth position")
        return None
    
def getMapping(sourcefield, fullmappingjson):
    #Instead of returning a list of mapped keys, this returns the full mapped entry, including the CDA domain
    #The idea is to use the domain to populate the right part of the CDA JSON where field names are duplicated
    mappingjson = fullmappingjson['field_mappings']
    cdafields = None
    if sourcefield in mappingjson:
        cdafields = mappingjson[sourcefield]
    return cdafields
    
def locationSort(cdafield, originalvalue, domainjson, instancejson):
    #Common sorting routine
    if cdafield in instancejson:
        if isinstance(instancejson[cdafield], list):
            #instancejson[cdafield].append(originalvalue)
            print("List in instancejson")
        else:
            instancejson[cdafield] = originalvalue
    if cdafield in domainjson:
        #Has to be in domainjson
        if isinstance(domainjson[cdafield], list):
            #domainjson[cdafield].append(originalvalue)
            print("List in domainjson")
        else:
            domainjson[cdafield] = originalvalue
    return domainjson, instancejson

def domainMap(originalvalue, mappingdata, domainjson, instancejson):
    #Orignial value should be a dictionary, and should only be mapped to list element
    #print("domainMap")
    for field, value in originalvalue.items():
        cdafields = getMappedKey(field, mappingdata)
        for cdafield in cdafields:
            if cdafield in instancejson:
                if isinstance(instancejson[cdafield], list):
                    instancejson[cdafield].append(value)
            if cdafield in domainjson:
                if isinstance(domainjson[cdafield],list):
                    domainjson[cdafield].append(value)
    return domainjson, instancejson


def parseEntry(graphqlresults, mappingdata, entryjson, instancejson, datacommons, identifier_field):
    for originalfield, originalvalue in graphqlresults.items():
        entryjson, instancejson = parseDecider(originalfield, originalvalue,entryjson, instancejson, mappingdata)

    instancejson['system'] = datacommons
    instancejson['field_name'] = identifier_field
    entryjson['identifiers'] = instancejson
    return entryjson

def altStringParse(originalfield, originalvalue, mappingdata, entryjson, instancejson):
    #print("altStringParse")
    if isinstance(originalvalue,dict):
        #Got a nested structure and originalfield will be a domain and need special handling
        entryjson, instancejson = domainMap(originalvalue, mappingdata, entryjson, instancejson)
    else:
        #Normal key-value, map as normal
        cdafields = getMappedKey(originalfield, mappingdata)
        #cdafields is going to be a list of CDA fields including the CDA domain
        if cdafields is not None:
            for cdafield in cdafields:
                entryjson, instancejson = locationSort(cdafield,originalvalue, entryjson,instancejson)
    return entryjson, instancejson

def altDictParse( originalvalue, mappingdata, entryjson, instancejson):
    #print("altDictParse")
    #print(originalvalue)
    # {'sample_id': 'CDS-BIOS-492358', 'participant': {'participant_id': 'CDS-CASE-383394'}}
    for field, value in originalvalue.items():
        #print(field)
       # print(value)
        if isinstance(value, dict):
            #This means field should be a domain which is NOT in the mapping.
            entryjson, instancejson = domainMap(value, mappingdata, entryjson, instancejson)
        elif isinstance(value, list):
            print("In altDictParse and got a list")
            sys.exit()
        else:
            #Gotta be a string
            entryjson, instancejson = altStringParse(field, value, mappingdata, entryjson, instancejson)
    return entryjson, instancejson

def altListParse(originalvalue, mappingdata, entryjson, instancejson):
    #print("altListParse")
    #print(originalvalue)
    #[{'sample_id': 'CDS-BIOS-267335', 'participant': {'participant_id': 'CDS-CASE-383394'}}]
    #List of dict, so item should be a dict
    for item in originalvalue:
        if isinstance(item, dict):
            entryjson, instancejson = altDictParse(item, mappingdata, entryjson, instancejson)
        elif isinstance(item, list):
            entryjson, instancejson = altListParse(item, mappingdata, entryjson, instancejson)
        else:
            entryjson, instancejson = altStringParse(item, mappingdata, entryjson, instancejson)
    return entryjson, instancejson

def stringParse(originalfield, originalvalue, mappingdata, entryjson, instancejson):
    cdafieldlist = getMappedKey(originalfield, mappingdata)
    for cdafield in cdafieldlist:
        entryjson, instancejson = locationSort(cdafield, originalvalue,entryjson, instancejson)
    return entryjson, instancejson

def dictParse(originalvalue,mappingdata, entryjson, instancejson ):
    for field, value in originalvalue.items():
        cdafieldlist = getMappedKey(field, mappingdata)
        if cdafieldlist is not None: #This is needed to week out 0 length returns from nested graphql queries
            for cdafield in cdafieldlist:
                entryjson, instancejson = locationSort(cdafield, value, entryjson, instancejson)
    return entryjson, instancejson

def listParse(originalvalue, mappingdata, entryjson, instancejson):
    for item in originalvalue:
        if isinstance(item, dict):
            entryjson, instancejson = dictParse(item, mappingdata, entryjson, instancejson)
        elif isinstance(item, list):
            #This is the recursivy bit
            entryjson, instancejson = listParse(item, mappingdata, entryjson, instancejson)
        else:
           # entryjson, instancejson = stringParse(item, mappingdata, entryjson, instancejson)
            entryjson, instancejson = altStringParse(item, mappingdata, entryjson, instancejson)

    return entryjson, instancejson

def parseDecider(originalfield, originalvalue, entryjson, instancejson, mappingdata):
    #All this does is figure out if the value is a dict, list, or string and call the appropriate routine
    #If originalvalue is anything other than a string, 
    if isinstance(originalvalue, list):
        #Call list processing routine
        #entryjson, instancejson = listParse(originalvalue, mappingdata, entryjson, instancejson)
        entryjson, instancejson = altListParse(originalvalue, mappingdata, entryjson, instancejson)

    elif isinstance(originalvalue, dict):
        #Call dict processing routine
        #entryjson, instancejson = dictParse(originalvalue, mappingdata, entryjson, instancejson)
        entryjson, instancejson = altDictParse(originalvalue, mappingdata, entryjson, instancejson)

    else:
        #Call string processing routine
        #entryjson, instancejson = stringParse(originalfield, originalvalue,mappingdata, entryjson, instancejson)
        entryjson, instancejson = altStringParse(originalfield, originalvalue,mappingdata, entryjson, instancejson)

    return entryjson, instancejson
        


#def getAndProcessData(graphqlendpint, graphqlquery, domain, mappingdata, sectionmodel, identifiersmodel, repository,identifier_field):
def getAndProcessData(graphqlendpint, graphqlquery, domain, mappingdata,repository,identifier_field):
    modelselections = { 'file': model.file, 'diagnosis':model.diagnosis, 'treatement':model.treatment, 'sample':model.specimen,
                        'participant':model.subject, }

    #BUG:  Sectionmodel and identifiermodel don't get "fresh" copies after every for entry loop, so lists keep getting longer
    querydata = getGraphQLJSON(graphqlendpint,graphqlquery)
    templist = []
    for entry in querydata['data'][domain]:
        #print(entry)
        #newJSON = parseEntry(entry, mappingdata, sectionmodel, identifiersmodel, repository, identifier_field)
        model.init()
        sectionmodel = model.file
        identifiermodel = model.identifiers
        newJSON = parseEntry(entry, mappingdata, sectionmodel, identifiermodel, repository, identifier_field)

        templist.append(newJSON)
    
    return templist
        

def validateJSON(schema, cdajson):
    sf =  open(schema, 'r')
    cdaschema = json.load(sf)
    try:
        jsonschema.validate(cdajson,cdaschema)
    except jsonschema.exceptions.ValidationError as e:
        print(e)
        return False
    return True

