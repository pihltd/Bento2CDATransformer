from tabnanny import verbose
import yaml
import json
import argparse
import pprint
from python_graphql_client import GraphqlClient

CDSAPI = "https://dataservice.datacommons.cancer.gov/v1/graphql/"

def getAPIJSON(apiurl, query):
    client = GraphqlClient(endpoint=apiurl)
    jsondata = client.execute(query = query)
    return jsondata

def readTransformFile(yamlfile):
    with open(yamlfile, "r") as stream:
        transformdata = yaml.safe_load(stream)
    return transformdata

def main(args):
    transformfile = args.transformfile
    data = readTransformFile(transformfile)
    pprint.pprint(data)

    testquery = """
    {
        program{
            program_acronym
        }
    }
    """
    data2 = getAPIJSON(CDSAPI, testquery)
    pprint.pprint(data2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",help="Enable verbose feedback" )
    parser.add_argument("-t", "--transformfile", required=True, help="Name of the transform yaml file")

    args = parser.parse_args()
    main(args)