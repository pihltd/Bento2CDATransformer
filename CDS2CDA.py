from tabnanny import verbose
import yaml
import json
import argparse
import pprint
from python_graphql_client import GraphqlClient
import cdsQueries as cdsq
from jsonschema import validate

CDSAPI = "https://dataservice.datacommons.cancer.gov/v1/graphql/"

def getAPIJSON(apiurl, query):
    client = GraphqlClient(endpoint=apiurl)
    jsondata = client.execute(query = query)
    return jsondata

def readTransformFile(yamlfile):
    with open(yamlfile, "r") as stream:
        transformdata = yaml.safe_load(stream)
    return transformdata
def fileInfoParse(graphqldata):
    for file in graphqldata['data']['file']:
        pprint.pprint(file)

def main(args):
    cdsq.init()
    cdajson = {}


    if args.verbose:
        transformfile = args.transformfile
        data = readTransformFile(transformfile)
        pprint.pprint(data)

    #data2 = getAPIJSON(CDSAPI, cdsq.testquery)
    #pprint.pprint(data2)

    #pprint.pprint(cdsq.file_info)
    data3 = getAPIJSON(CDSAPI,cdsq.file_info)
    #pprint.pprint(data3)
    fileInfoParse(data3)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",help="Enable verbose feedback" )
    parser.add_argument("-t", "--transformfile", required=True, help="Name of the transform yaml file")
    parser.add_argument("-s", "--schema", required=True, help="JSON Schemafile")

    args = parser.parse_args()
    main(args)