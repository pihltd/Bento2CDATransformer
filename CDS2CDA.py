from tabnanny import verbose
import yaml
import json
import argparse
import pprint
from python_graphql_client import GraphqlClient
import cdsQueries as cdsq
#from jsonschema import validate
import jsonschema

# TODO: Handle lists of things better.  Most CDA fields accept lists, this scripts supplies only last value seen.


def getAPIJSON(apiurl, query):
    client = GraphqlClient(endpoint=apiurl)
    jsondata = client.execute(query = query)
    return jsondata

def readTransformFile(yamlfile):
    with open(yamlfile, "r") as stream:
        transformdata = yaml.safe_load(stream)
    return transformdata

def getMappedKey(sourcefield, mappingjson):
    # Will return a list of CDA field name from the mapping.
    finallist = []
    mapping = mappingjson[sourcefield]
    for node, mappinglist in mapping.items():
        return mappinglist

    
def unpack(nesteddict):
    flattened = {}
    for field, item in nesteddict.items():
        if isinstance(item,dict):
            unpack(flattened)
        else:
            flattened[field] = item
    return flattened

def addSample2File(filejson, filesampledata):
    #Adds sample information to the exiting filejson
    for fileinstance in filesampledata['data']['file']:
        fileid = fileinstance['file_id']
        samplelist = []
        for sample in fileinstance['samples']:
            samplelist.append(sample['sample_id'])
        for file in filejson:
            if file['id'] == fileid:
                file['specimens'] = samplelist
    return filejson

def addSubject2File(filejson, filesubjectdata):
    for fileinstance in filesubjectdata['data']['file']:
        fileid = fileinstance['file_id']
        subjectlist = []
        for sample in fileinstance['samples']:
            subjectlist.append(sample['participant']['participant_id'])
        for file in filejson:
            if file['id'] == fileid:
                file['subjects'] = subjectlist
                file['research_subjects'] = subjectlist
    return filejson
        
def genericInfoParse(graphqlresults, mappingdata, graphqlindex):
    #First pass parse of data returned from graphql queries.  The graphqlindex is the field name after 'data' in graphql results
    finalarray = []
    tempjson = {}
    mappings = mappingdata['field_mappings']
    for instance in graphqlresults['data'][graphqlindex]:
        for cdsfield,cdsvalue in instance.items():
            if isinstance(cdsvalue, dict):
                #Process dictionary
                for field, value in cdsvalue.items():
                    mappedlist = getMappedKey(field, mappings)
                    for newfield in mappedlist:
                        tempjson[newfield] = value
            elif isinstance(cdsvalue, list):
                #Process list
                for entry in cdsvalue:
                    if isinstance(entry,dict):
                        for field, value in entry.items():
                            mappedlist = getMappedKey(field, mappings)
                            for newfield in mappedlist:
                                tempjson[newfield] = value
                    #May need and if isinstance(entry, list), but no examples yet
                            
            else:
                #Not nested data, process
                mappedlist = getMappedKey(cdsfield, mappings)
                for newfield in mappedlist:
                    tempjson[newfield] = cdsvalue
        finalarray.append(tempjson)
    return finalarray


def validateJSON(schema, cdajson):
    sf =  open(schema, 'r')
    cdaschema = json.load(sf)
    try:
        jsonschema.validate(cdajson,cdaschema)
    except jsonschema.exceptions.ValidationError as e:
        pprint.pprint(e)
        return False
    return True



def main(args):
    CDSAPI = "https://dataservice.datacommons.cancer.gov/v1/graphql/"
    cdsq.init()
    cdajson = {}

    transformfile = args.transformfile
    mappingdata = readTransformFile(transformfile)
    if args.verbose:
        pprint.pprint(mappingdata)

    #File
    filedata = getAPIJSON(CDSAPI,cdsq.file_info)
    filejson = genericInfoParse(filedata, mappingdata, 'file')
    #Get sample data to add to files
    filesampledata = getAPIJSON(CDSAPI, cdsq.file_samples)
    filejson = addSample2File(filejson, filesampledata)
    #Get subject data to add to files
    filesubjectdata = getAPIJSON(CDSAPI, cdsq.file_participants)
    filejson = addSubject2File(filejson,filesubjectdata)
    cdajson['file'] = filejson

    #Diagnosis
    #Need to fine tune the identifiers
    diagdata = getAPIJSON(CDSAPI, cdsq.diagnosis_info)
    diagjson = genericInfoParse(diagdata, mappingdata, 'diagnosis')
    cdajson['diagnosis'] = diagjson

    #Treatment
    treatmentdata = getAPIJSON(CDSAPI, cdsq.treatment_info)
    treatmentjson = genericInfoParse(treatmentdata, mappingdata, 'treatment')
    cdajson['treatment'] = treatmentjson

    #Specimen
    sampledata = getAPIJSON(CDSAPI, cdsq.sample_info)
    samplejson = genericInfoParse(sampledata, mappingdata, 'sample')
    cdajson['specimen'] = samplejson

    #Subject
    #subjectdata = getAPIJSON(CDSAPI, cdsq.basic_subject_info)
    subjectdata = getAPIJSON(CDSAPI, cdsq.test_subject_info)
    subjectjson = genericInfoParse(subjectdata, mappingdata, 'participant')
    cdajson['subject'] = subjectjson

    #ResearchSubject
    #This is going to be a bit different in that it needs to count the number of projects per subject.  Not sure CDS allows that
    

    if args.output is not None:
        cdaoutput = json.dumps(cdajson, indent=4)
        f = open(args.output, "w")
        f.write(cdaoutput)
        f.close()
    if args.verbose:
        pprint.pprint(cdajson)

    if args.check_validation:
        validateJSON(args.schema, cdajson)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",help="Enable verbose feedback" )
    parser.add_argument("-t", "--transformfile", required=True, help="Name of the transform yaml file")
    parser.add_argument("-s", "--schema", required=True, help="JSON Schemafile")
    parser.add_argument("-o", "--output", help="Output file name")
    parser.add_argument("-c", "--check_validation", action="store_true", help="Run validation against the schema supplied with -s")

    args = parser.parse_args()
    main(args)