#!/bin/bash
# A space-separated list of UUIDs to query
UUIDS="88c4ac22-bc87-4557-bbab-5442ceed471d 491f27c8-f308-4bf3-a210-2e99f6ffc228 5a025027-0e4b-46c2-a88c-c32e93b120b1 75d91a2a-5208-4d49-8900-889a0a366497"
# Which elastic to query. If all UUIDs are not from the same source, then provide a space-separated list of URLs that map to the UUIDs in order.
ES_URL="https://search-perfscale-dev-chmf5l4sh66lvxbnadi4bznl3a.us-west-2.es.amazonaws.com:443"
OUTPUT_FILE="heavy.245ppn.v2-crun.csv"

CONFIG="config/kubeburner-node-density.json"
touchstone_compare --config $CONFIG -u $UUIDS -url $ES_URL -o csv > $OUTPUT_FILE

CONFIG="config/apirequestrate_verb.json"
touchstone_compare --config $CONFIG -u $UUIDS -url $ES_URL -o csv >> $OUTPUT_FILE

CONFIG="config/etcd_distribution.json"
touchstone_compare --config $CONFIG -u $UUIDS -url $ES_URL -o csv >> $OUTPUT_FILE

CONFIG="config/apiCalls_3-buckets.json"
touchstone_compare --config $CONFIG -u $UUIDS -url $ES_URL -o csv >> $OUTPUT_FILE

CONFIG="config/node-status.json"
touchstone_compare --config $CONFIG -u $UUIDS -url $ES_URL -o csv >> $OUTPUT_FILE

CONFIG="config/serviceSyncLatency.json"
touchstone_compare --config $CONFIG -u $UUIDS -url $ES_URL -o csv >> $OUTPUT_FILE

# This config generates 4 bucket columns when all others generate 3, so it should be handled separately where it can take common formatting with other 4 bucket queries, include:
# APIRequestRate,verb,resource
# mutatingAPICallsLatency,verb,scope
# readOnlyAPICallsLatency,verb,scope
# CONFIG="config/apiCalls_4-buckets.json"
# touchstone_compare --config $CONFIG -u $UUIDS -url $ES_URL -o csv >> $OUTPUT_FILE