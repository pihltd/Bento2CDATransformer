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
    if sourcefield in mappingjson:
        if sourcefield == 'participant_id':
            print("participant id first position")
        mapping = mappingjson[sourcefield]
        if isinstance(mapping, list):
            for entry in mapping:
                for field, mappinglist in entry.items():
                    if field == "participant_id":
                        print("participant_id at second position")
                    return mappinglist
        else:
            for node, mappinglist in mapping.items():
                if node == "participant_id":
                    print("Participant id third position")
                if isinstance(mappinglist, dict):
                    for newfield, newlist in mappinglist.items():
                        if newfield == "participant_id":
                            print("Participant id fourth position")
                        return newlist
                else:
                    return mappinglist
    else:
        return None
    
def locationSort(cdafield, originalvalue, domainjson, instancejson):
    #Common sorting routine
    if cdafield in instancejson:
        if isinstance(instancejson[cdafield], list):
            instancejson[cdafield].append(originalvalue)
        else:
            instancejson[cdafield] = originalvalue
    if cdafield in domainjson:
        #Has to be in domainjson
        if isinstance(domainjson[cdafield], list):
            domainjson[cdafield].append(originalvalue)
        else:
            domainjson[cdafield] = originalvalue
    return domainjson, instancejson


def parseEntry(graphqlresults, mappingdata, entryjson, instancejson, datacommons, identifier_field):
    for originalfield, originalvalue in graphqlresults.items():
        entryjson, instancejson = parseDecider(originalfield, originalvalue,entryjson, instancejson, mappingdata)

    instancejson['system'] = datacommons
    instancejson['field_name'] = identifier_field
    entryjson['identifiers'] = instancejson
    return entryjson

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
            entryjson, instancejson = stringParse(item, mappingdata, entryjson, instancejson)
    return entryjson, instancejson

def parseDecider(originalfield, originalvalue, entryjson, instancejson, mappingdata):
    #All this does is figure out if the value is a dict, list, or string and call the appropriate routine
    if isinstance(originalvalue, list):
        #Call list processing routine
        listParse(originalvalue, mappingdata, entryjson, instancejson)
    elif isinstance(originalvalue, dict):
        #Call dict processing routine
        entryjson, instancejson = dictParse(originalvalue, mappingdata, entryjson, instancejson)
    else:
        #Call string processing routine
        entryjson, instancejson = stringParse(originalfield, originalvalue,mappingdata, entryjson, instancejson)
    return entryjson, instancejson
        


#def getAndProcessData(graphqlendpint, graphqlquery, domain, mappingdata, sectionmodel, identifiersmodel, repository,identifier_field):
def getAndProcessData(graphqlendpint, graphqlquery, domain, mappingdata,repository,identifier_field):
    modelselections = { 'file': model.file, 'diagnosis':model.diagnosis, 'treatement':model.treatment, 'sample':model.specimen,
                        'participant':model.subject, }

    #BUG:  Sectionmodel and identifiermodel don't get "fresh" copies after every for entry loop, so lists keep getting longer
    querydata = getGraphQLJSON(graphqlendpint,graphqlquery)
    templist = []
    for entry in querydata['data'][domain]:
        print(entry)
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

