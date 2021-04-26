import argparse
import sys
import json
import yaml
import elasticsearch
import uuid
import time

def _parse_data(inputdict, my_uuid):
    new_dict = {}
    total = 0
    for key in inputdict.keys():
        if type(inputdict[key]) == dict:
            new_dict[key] =  _parse_data(inputdict[key], my_uuid)
        else:
            total += inputdict[key]
    if total != 0:        
        new_dict = { my_uuid: total/len(inputdict.keys()) }
    return new_dict

def _upload_to_es(my_dict, my_uuid, es_server, es_port, index, es_ssl):
    _es_connection_string = str(es_server) + ':' + str(es_port)
    if es_ssl == "true":
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        es = elasticsearch.Elasticsearch([_es_connection_string], send_get_body_as='POST',
                                         ssl_context=ssl_ctx, use_ssl=True)
    else:
        es = elasticsearch.Elasticsearch([_es_connection_string], send_get_body_as='POST')

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    data = {"uuid": my_uuid, "timestamp": timestamp}
    data.update(my_dict)
    try:
        es.index(index=index, body=data)
    except Exception as err:
        print("Uploading to elasticsearch failed")
        print(err)
        exit(1)

def main():
    parser = argparse.ArgumentParser(description="Gen averages of data given and upload to ES",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-f', '--file',
        required=True,
        help='Imput json file to iterate over')
    parser.add_argument(
        '-u', '--uuid',
        help='UUID to use for uploading to ES')
    parser.add_argument(
        '-s', '--server',
        help='Provide elastic server information')
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=9200,
        help='Provide elastic port information')
    parser.add_argument(
        '--sslskipverify',
        help='If es is setup with ssl, but can disable tls cert verification',
        default=False)
    parser.add_argument(
        '-i', '--index',
        help='What index to upload to ES',
        default=False)
    parser.add_argument(
        '-o', '--output',
        choices=['yaml', 'json'],
        default='yaml',
        help='What format to print output to stdout')
    parser.add_argument(
        '--output-file',
        help='Where to print the output. Mutually exclusive with loading to elasticsearch.')
    
    args = parser.parse_args()
    
    my_uuid = args.uuid
    if my_uuid is None:
        my_uuid = str(uuid.uuid4())

    try:
        inputdict = json.load(open(args.file))
    except:
        print("Could not load input as json. Trying yaml.")
        try_yaml = True
    else:
        print("Input loaded from json.")
        try_yaml = False

    if try_yaml:
        try:
            inputdict = yaml.safe_load(open(args.file))
        except Exception as err:
            print("Could not open input file as json or yaml. Exiting.")
            print(err)
            exit(1)
        else:
            print("Input loaded from yaml.")

    print("Generating averages for UUID",my_uuid)
    new_dict = _parse_data(inputdict, my_uuid)

    # If not ES info is given dump the new dictionary to stdout or output-file if given
    if args.server is None or args.port is None or args.index is None:
        print("No elasticsearch information provided.")
        if args.output_file is None:
            print("No output file given. Printing to STDOUT.")
            if args.output == "json":
                print(new_dict)
            else:
                print(yaml.dump(new_dict))
        else:
            try:
                file_out = open(args.output_file, 'w')
            except Exception as err:
                print("Failed to open file for printing")
                exit(1)
            else:
                print("Printing to file",args.output_file)

            if args.output == "json":
                json.dump(new_dict,file_out)
            else:
                yaml.dump(new_dict,file_out)

            file_out.close()
    else:
        print("Attempting to upload to elasticsearch index",args.index)
        _upload_to_es(new_dict, my_uuid, args.server, args.port, args.index, args.sslskipverify)

if __name__ == '__main__':
    sys.exit(main())
