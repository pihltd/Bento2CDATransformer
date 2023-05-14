import CDA_dataclass as cdc
import CDATranslate as cdt
import pprint
import argparse
from dataclasses import asdict, fields
import sys






def main(args):
    #tester = cdc.Cdaidentifier("A", "B")
    #pprint.pprint(asdict(tester))

    #bigtest = cdc.File("a")
    #pprint.pprint(asdict(bigtest))

    #bigtest2 = cdc.File()
    #pprint.pprint(asdict(bigtest2))
    #sys.exit()



    simplequery = """
    {
        file{
            file_id
            file_name
            file_type
            file_size
            md5sum
        }
    }
    """

    #Read the config file
    configs = cdt.readTransformFile(args.configfile)
    graphqlresult = cdt.getGraphQLJSON(configs["graphql_url"],simplequery)
    #pprint.pprint(graphqlresult)

    finallist = []
    for file in graphqlresult['data']['file']:
        fileinfo = cdc.File()
        extrainfo = cdc.Cdaidentifier()
        #for field in fields(fileinfo):
         #   print(field.name)

        extrainfo.field_name = "file.file_name"
        extrainfo.system = "CDS"
        extrainfo.value = file['file_name']
        fileinfo.id = file['file_id']
        fileinfo.byte_size = file['file_size']
        fileinfo.file_format = file['file_type']
        fileinfo.identifiers = extrainfo
        finallist.append(asdict(fileinfo))
    pprint.pprint(finallist)








if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True, help="Configuraion yaml file")
    parser.add_argument("-v", "--verbose", action="store_true",help="Enable verbose feedback" )
    parser.add_argument("-o", "--output", help="Output file name")

    args = parser.parse_args()
    main(args)