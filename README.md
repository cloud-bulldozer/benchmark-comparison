# Touchstone

Touchstone is a framework written in python that provides you an apples to apples comparison between 2 similar datasets.

## Usage

It is suggested to use a venv to install and run touchstone.

```shell
python -m venv /virtual/environment
source /virtual/environment/bin/activate
git clone https://github.com/cloud-bulldozer/benchmark-comparison
cd benchmark-comparison
python setup.py develop
touchstone_compare -h
usage: touchstone_compare [-h] [--version] [--database {elasticsearch}] [--identifier-key IDENTIFIER] -u UUID [UUID ...] [-a ALIASES [ALIASES ...]] [-o {json,yaml,csv}] --config CONFIG [--output-file OUTPUT_FILE]
                          [--tolerancy-rules TOLERANCY_RULES] [--rc RC] -url CONN_URL [CONN_URL ...] [-v] [-vv]
compare results from benchmarks

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --database {elasticsearch}
                        the type of database data is stored in
  --identifier-key IDENTIFIER
                        identifier key name(default: uuid)
  -u UUID [UUID ...], --uuid UUID [UUID ...]
                        identifier values to fetch results and compare
  -o {json,yaml,csv}, --output {json,yaml,csv}
                        How should touchstone output the result
  --config CONFIG       Touchstone configuration file
  --output-file OUTPUT_FILE
                        Redirect output of json/csv/yaml to file
  --tolerancy-rules TOLERANCY_RULES
                        Path to tolerancy rules configuration
  -url CONN_URL [CONN_URL ...], --connection-url CONN_URL [CONN_URL ...]
                        the database connection strings in the same order as the uuids
  -v, --verbose         set loglevel to INFO
  -vv, --very-verbose   set loglevel to DEBUG
```

Touchstone uses a `json` configuration to describe how to perform the comparisons. This file has the following shape:

```json
{"elasticsearch": {
   "ES-INDEX": [
      {
        "filter": {"foo": "bar"},
        "exclude": {"exclude": "me"},
        "buckets": [
          "list",
          "of",
          "buckets"
        ],
        "metric_aggregations": {
          "field_name": ["max", "avg", {"percentiles": {"percents": [90, 99]}}]
        }
      }
    ]
  }
}
```

Where:

- **ES-INDEX**: Points to the ElasticSearch index name to look documents from.
- **filter**: Contains a dictionary of valid ES term filter expression. e.g. `{"test_type.keyword": "stream"}`
- **exclude**: Contains a dictionary of valid ES exclude expressions. e.g. `{"message_size": 1024}`
- **buckets**: List of buckets to aggregate metrics into. `["test_type", "protocol", "message_size"]`. Find more info about bucket aggregation in the [official ES docs](https://www.elastic.co/guide/en/elasticsearch/reference/master/search-aggregations-bucket.html#search-aggregations-bucket)
- **aggregations**: List of metric aggregations to get from a certain field (`field_name` in the example above). e.g.`["avg", "min"]` Find more info about supported metric aggregations in ES in it's [official doc site](https://www.elastic.co/guide/en/elasticsearch/reference/master/search-aggregations-metrics.html#search-aggregations-metrics)


There're some configuration files in the [config directory](./config), these configuration files have been tested with metrics indexed using [benchmark-wrapper](https://github.com/cloud-bulldozer/benchmark-wrapper). However it's possible to build a custom configuration file able to get metrics from other indexers. To do so these documents just need to to have a `UUID` or other field to allow touchstone identify them.

### Comparing different UUIDs

`touchstone` is able to compare different UUIDs with similar datasets indexed in the same or different ES instances. You can use a line similar to the following:

```shell
# Comparing metrics indexed in the same ES instance
$ touchstone_compare -url <ES_INSTANCE-1> -u <UUID-1> <UUID-2> <UUID-n> --config config.json

# Comparing metrics indexed in different ES instance
$ touchstone_compare -url <ES_INSTANCE-1> <ES_INSTANCE-2> <ES_INSTANCE-n> -u <UUID-1> <UUID-2> <UUID-n> --config config.json
```

### Metadata comparison

In adition to fetch and/or compare metrics, `touchstone` is able to do the same with metadata extracted with [stockpile](https://github.com/cloud-bulldozer/stockpile/). This metadata comparison can be useful to have an improved context of the SUT.

Metadata comparison is configured through the `metadata` field in the touchstone configuration:

```json
{
    "elasticsearch": {
        "metadata": {
            "ES-INDEX": {
                "fields": ["field1", "nested.field"],
                "additional_fields": ["additional_field"]
            }
        }
    }
}
```

From above:

- **ES-INDEX**: should be a Valid ES index name  where metadata is indexed.
- **fields**: List of metadata fields to compare.
- **additional_fields**: List of additional fields to include in each metadata field.

The snippet below shows part of the output of executing a comparison using one of the [uperf configuration](config/uperf.json) files available in this repository.

```shell
$ touchstone_compare -url https://my-es-instance.com:9200 -u ec7f0cfb-0812-57ab-8905-fd6ddaacf593 975fa650-aeb2-5042-8517-fe277d7cb1f3  --config config/uperf.json
+------------------------------------------+--------------------+--------------------------------------+-----------------------------------------------+
|                 pod_name                 |      metadata      |                 uuid                 |                     value                     |
+------------------------------------------+--------------------+--------------------------------------+-----------------------------------------------+
| uperf-client-10.131.0.169-ec7f0cfb-k5gb4 |  value.Model name  | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 | Intel(R) Xeon(R) Platinum 8175M CPU @ 2.50GHz |
| uperf-client-10.131.0.169-ec7f0cfb-k5gb4 | value.Architecture | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 |                    x86_64                     |
| uperf-client-10.131.0.169-ec7f0cfb-k5gb4 |    value.CPU(s)    | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 |                       8                       |
| uperf-client-10.131.0.168-ec7f0cfb-txbq9 |  value.Model name  | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 | Intel(R) Xeon(R) Platinum 8175M CPU @ 2.50GHz |
| uperf-client-10.131.0.168-ec7f0cfb-txbq9 | value.Architecture | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 |                    x86_64                     |
| uperf-client-10.131.0.168-ec7f0cfb-txbq9 |    value.CPU(s)    | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 |                       8                       |
| uperf-client-10.131.0.167-ec7f0cfb-jl5hs |  value.Model name  | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 | Intel(R) Xeon(R) Platinum 8175M CPU @ 2.50GHz |
| uperf-client-10.131.0.167-ec7f0cfb-jl5hs | value.Architecture | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 |                    x86_64                     |
| uperf-client-10.131.0.167-ec7f0cfb-jl5hs |    value.CPU(s)    | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 |                       8                       |
| uperf-client-10.131.0.170-ec7f0cfb-58rrd |  value.Model name  | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 | Intel(R) Xeon(R) Platinum 8175M CPU @ 2.50GHz |
| uperf-client-10.131.0.170-ec7f0cfb-58rrd | value.Architecture | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 |                    x86_64                     |
| uperf-client-10.131.0.170-ec7f0cfb-58rrd |    value.CPU(s)    | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 |                       8                       |
| uperf-client-10.131.0.162-975fa650-tls42 |  value.Model name  | 975fa650-aeb2-5042-8517-fe277d7cb1f3 | Intel(R) Xeon(R) Platinum 8175M CPU @ 2.50GHz |
| uperf-client-10.131.0.162-975fa650-tls42 | value.Architecture | 975fa650-aeb2-5042-8517-fe277d7cb1f3 |                    x86_64                     |
| uperf-client-10.131.0.162-975fa650-tls42 |    value.CPU(s)    | 975fa650-aeb2-5042-8517-fe277d7cb1f3 |                       8                       |
| uperf-client-10.131.0.159-975fa650-lnq2k |  value.Model name  | 975fa650-aeb2-5042-8517-fe277d7cb1f3 | Intel(R) Xeon(R) Platinum 8175M CPU @ 2.50GHz |
| uperf-client-10.131.0.159-975fa650-lnq2k | value.Architecture | 975fa650-aeb2-5042-8517-fe277d7cb1f3 |                    x86_64                     |
| uperf-client-10.131.0.159-975fa650-lnq2k |    value.CPU(s)    | 975fa650-aeb2-5042-8517-fe277d7cb1f3 |                       8                       |
| uperf-client-10.131.0.161-975fa650-zj245 |  value.Model name  | 975fa650-aeb2-5042-8517-fe277d7cb1f3 | Intel(R) Xeon(R) Platinum 8175M CPU @ 2.50GHz |
| uperf-client-10.131.0.161-975fa650-zj245 | value.Architecture | 975fa650-aeb2-5042-8517-fe277d7cb1f3 |                    x86_64                     |
| uperf-client-10.131.0.161-975fa650-zj245 |    value.CPU(s)    | 975fa650-aeb2-5042-8517-fe277d7cb1f3 |                       8                       |
| uperf-client-10.131.0.160-975fa650-6pfhc |  value.Model name  | 975fa650-aeb2-5042-8517-fe277d7cb1f3 | Intel(R) Xeon(R) Platinum 8175M CPU @ 2.50GHz |
| uperf-client-10.131.0.160-975fa650-6pfhc | value.Architecture | 975fa650-aeb2-5042-8517-fe277d7cb1f3 |                    x86_64                     |
| uperf-client-10.131.0.160-975fa650-6pfhc |    value.CPU(s)    | 975fa650-aeb2-5042-8517-fe277d7cb1f3 |                       8                       |
+------------------------------------------+--------------------+--------------------------------------+-----------------------------------------------+
+------------------------------------------+----------------+--------------------------------------+-------------+
|                 pod_name                 |    metadata    |                 uuid                 |    value    |
+------------------------------------------+----------------+--------------------------------------+-------------+
| uperf-client-10.131.0.167-ec7f0cfb-jl5hs | value.MemTotal | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 | 32105908 kB |
| uperf-client-10.131.0.168-ec7f0cfb-txbq9 | value.MemTotal | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 | 32105908 kB |
| uperf-client-10.131.0.169-ec7f0cfb-k5gb4 | value.MemTotal | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 | 32105908 kB |
| uperf-client-10.131.0.170-ec7f0cfb-58rrd | value.MemTotal | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 | 32105908 kB |
| uperf-client-10.131.0.162-975fa650-tls42 | value.MemTotal | 975fa650-aeb2-5042-8517-fe277d7cb1f3 | 32105908 kB |
| uperf-client-10.131.0.161-975fa650-zj245 | value.MemTotal | 975fa650-aeb2-5042-8517-fe277d7cb1f3 | 32105908 kB |
| uperf-client-10.131.0.159-975fa650-lnq2k | value.MemTotal | 975fa650-aeb2-5042-8517-fe277d7cb1f3 | 32105908 kB |
| uperf-client-10.131.0.160-975fa650-6pfhc | value.MemTotal | 975fa650-aeb2-5042-8517-fe277d7cb1f3 | 32105908 kB |
+------------------------------------------+----------------+--------------------------------------+-------------+
+-----------+----------+--------------+-------------+----------------+--------------------+--------------------+
| test_type | protocol | message_size | num_threads |     metric     |    OpenShiftSDN    |        OVN         |
+-----------+----------+--------------+-------------+----------------+--------------------+--------------------+
|  stream   |   udp    |     1024     |      1      | max(norm_byte) |    196689920.0     |    196689920.0     |
|  stream   |   udp    |     1024     |      1      | avg(norm_byte) | 178356565.33333334 | 178356565.33333334 |
|  stream   |   udp    |      64      |      1      | max(norm_byte) |     12478464.0     |     12478464.0     |
|  stream   |   udp    |      64      |      1      | avg(norm_byte) | 11226859.705146037 | 11226859.705146037 |
|  stream   |   udp    |    16384     |      1      | max(norm_byte) |    1274544128.0    |    1274544128.0    |
|  stream   |   udp    |    16384     |      1      | avg(norm_byte) | 1128798626.714882  | 1128798626.714882  |
|  stream   |   tcp    |      64      |      1      | max(norm_byte) |     75060224.0     |     75060224.0     |
|  stream   |   tcp    |      64      |      1      | avg(norm_byte) | 69679493.68888889  | 69679493.68888889  |
|  stream   |   tcp    |    16384     |      1      | max(norm_byte) |    617873408.0     |    617873408.0     |
|  stream   |   tcp    |    16384     |      1      | avg(norm_byte) | 316504790.22531295 | 316504790.22531295 |
|  stream   |   tcp    |     1024     |      1      | max(norm_byte) |    619380736.0     |    619380736.0     |
|  stream   |   tcp    |     1024     |      1      | avg(norm_byte) | 315166389.10167134 | 315166389.10167134 |
+-----------+----------+--------------+-------------+----------------+--------------------+--------------------+
+-----------+----------+--------------+-------------+----------------------------+--------------------+--------------------+
| test_type | protocol | message_size | num_threads |           metric           |    OpenShiftSDN    |        OVN         |
+-----------+----------+--------------+-------------+----------------------------+--------------------+--------------------+
|    rr     |   tcp    |      64      |      1      |       max(norm_ops)        |       3764.0       |       3764.0       |
|    rr     |   tcp    |      64      |      1      |       avg(norm_ops)        | 3589.5194444444446 | 3589.5194444444446 |
|    rr     |   tcp    |      64      |      1      | 99.0percentiles(norm_ltcy) | 346.40508117675773 | 346.40508117675773 |
|    rr     |   tcp    |      64      |      1      |       avg(norm_ltcy)       | 280.28243395487465 | 280.28243395487465 |
|    rr     |   tcp    |     1024     |      1      |       max(norm_ops)        |       3708.0       |       3708.0       |
|    rr     |   tcp    |     1024     |      1      |       avg(norm_ops)        | 3529.961111111111  | 3529.961111111111  |
|    rr     |   tcp    |     1024     |      1      | 99.0percentiles(norm_ltcy) | 351.03181762695306 | 351.03181762695306 |
|    rr     |   tcp    |     1024     |      1      |       avg(norm_ltcy)       | 285.12439528571235 | 285.12439528571235 |
|    rr     |   tcp    |    16384     |      1      |       max(norm_ops)        |       3318.0       |       3318.0       |
|    rr     |   tcp    |    16384     |      1      |       avg(norm_ops)        | 3168.488888888889  | 3168.488888888889  |
|    rr     |   tcp    |    16384     |      1      | 99.0percentiles(norm_ltcy) | 392.5337493896483  | 392.5337493896483  |
|    rr     |   tcp    |    16384     |      1      |       avg(norm_ltcy)       | 317.63111754523385 | 317.63111754523385 |
|    rr     |   udp    |      64      |      1      |       max(norm_ops)        |       3788.0       |       3788.0       |
|    rr     |   udp    |      64      |      1      |       avg(norm_ops)        | 3579.760778859527  | 3579.760778859527  |
|    rr     |   udp    |      64      |      1      | 99.0percentiles(norm_ltcy) | 361.8567254638668  | 361.8567254638668  |
|    rr     |   udp    |      64      |      1      |       avg(norm_ltcy)       | 281.3683704275415  | 281.3683704275415  |
|    rr     |   udp    |     1024     |      1      |       max(norm_ops)        |       3772.0       |       3772.0       |
|    rr     |   udp    |     1024     |      1      |       avg(norm_ops)        | 3629.2670375521557 | 3629.2670375521557 |
|    rr     |   udp    |     1024     |      1      | 99.0percentiles(norm_ltcy) | 331.14006347656243 | 331.14006347656243 |
|    rr     |   udp    |     1024     |      1      |       avg(norm_ltcy)       | 277.26350731776716 | 277.26350731776716 |
|    rr     |   udp    |    16384     |      1      |       max(norm_ops)        |       3256.0       |       3256.0       |
|    rr     |   udp    |    16384     |      1      |       avg(norm_ops)        | 3147.229485396384  | 3147.229485396384  |
|    rr     |   udp    |    16384     |      1      | 99.0percentiles(norm_ltcy) | 392.8086782836913  | 392.8086782836913  |
|    rr     |   udp    |    16384     |      1      |       avg(norm_ltcy)       | 319.65084329533477 | 319.65084329533477 |
+-----------+----------+--------------+-------------+----------------------------+--------------------+--------------------+
```

### Comparing on a specific identifier

You can also now compare against identifiers other than the `uuid` key, so for example if you'd like to compare using the key `cluster_name` you can do so by using the `--identifier-key` argument and run as follows:

```shell
$ touchstone_compare --url https://es.instance:443 -u cnvcluster minikube --identifier-key cluster_name
```

Note: If the identifier is same for 2 or more uuids, then all of the results will be taken into consideration while computing aggregations, so please use with caution.

### Using tolerations

`touchstone` ships a metric toleration evaluation mechanism. This functionallity allows touchstone to detect regressions in metrics.
This feature can be enabled with the flag `--tolerancy-rules` which points to a tolerancy configuration file that looks like:

```yaml
- json_path: ["test_type", "stream", "protocol", "*", "message_size", "*", "num_threads", "*", "avg(norm_byte)"]
  tolerancy: -15
  max_failures: 25
- json_path: ["test_type", "rr", "protocol", "*", "message_size", "*", "num_threads", "*", "99.0percentiles(norm_ltcy)"]
  tolerancy: 15
  max_failures: 25
```

This YAML file contains a list of dictionaries, where the `json_path` key is a list that indicates the path that will allow `touchstone` to find the metric values from a comparison.
Wildcards can be used to match several keys at a certain level, and `tolerancy` defines the accepted tolerance percentage by the metrics matched by `json_path`.  i.e a 10 would mean any metric 10% higher than the baseline metric will be considered an error, and -10 would mean the opposite, any metric at least 10% below the baseline value will be considered an error. The optional parameter `max_failures` indicates the allowed percentage of failures permitted to consider a benchmark comparison as passed, by default is 0, meaning that only one fail will make set the comparison as failed.

By default `touchstone` takes the first UUID passed as baseline. When `touchstone` finds a metric not meeting a configured tolerancy thresholds it returns 1.

When tolerancy evaluation is enabled, touchstone will output the results of the evaluation after the results:

```shell
$ touchstone_compare -url https://my-es.instance.com -u 975fa650-aeb2-5042-8517-fe277d7cb1f3 ec7f0cfb-0812-57ab-8905-fd6ddaacf593 --config=config/mb.json --tolerancy-rules=tolerancy-configs/mb.yaml --alias OpenShiftSDN OVN --rc=1
 --tolerancy-rules tolerancy-configs/mb.yaml
 +-----------+--------+----------------------+-----------+--------------------------+--------+-----------+--------------+----------+
 | test_type | routes | conn_per_targetroute | keepalive |          metric          | result | deviation | OpenShiftSDN |   OVN    |
 +-----------+--------+----------------------+-----------+--------------------------+--------+-----------+--------------+----------+
 |   http    |  100   |          1           |     0     | avg(requests_per_second) |  Pass  |  -13.69%  |   59251.0    | 51141.5  |
 |   http    |  100   |          1           |     1     | avg(requests_per_second) |  Pass  |  -6.37%   |   21802.5    | 20414.5  |
 |   http    |  100   |          1           |    50     | avg(requests_per_second) |  Fail  |  -17.30%  |   56382.5    | 46628.5  |
 |   http    |  100   |          40          |     0     | avg(requests_per_second) |  Pass  |  25.19%   |   104666.5   | 131030.5 |
 |   http    |  100   |          40          |     1     | avg(requests_per_second) |  Fail  |  -27.99%  |   41068.5    | 29573.5  |
 |   http    |  100   |          40          |    50     | avg(requests_per_second) |  Pass  |  -10.76%  |   160984.5   | 143668.0 |
 |   http    |  100   |         200          |     0     | avg(requests_per_second) |  Pass  |  -9.86%   |   140269.0   | 126443.5 |
 |   http    |  100   |         200          |     1     | avg(requests_per_second) |  Pass  |  30.15%   |   38852.0    | 50565.5  |
 |   http    |  100   |         200          |    50     | avg(requests_per_second) |  Pass  |  -11.89%  |   147645.5   | 130094.5 |
 +-----------+--------+----------------------+-----------+--------------------------+--------+-----------+--------------+----------+
 +-----------+--------+----------------------+-----------+--------------------------+--------+-----------+--------------+---------+
 | test_type | routes | conn_per_targetroute | keepalive |          metric          | result | deviation | OpenShiftSDN |   OVN   |
 +-----------+--------+----------------------+-----------+--------------------------+--------+-----------+--------------+---------+
 |   edge    |  100   |          1           |     0     | avg(requests_per_second) |  Pass  |  -14.61%  |   64454.5    | 55034.5 |
 |   edge    |  100   |          1           |     1     | avg(requests_per_second) |  Fail  |  -59.37%  |   16390.0    | 6659.0  |
 |   edge    |  100   |          1           |    50     | avg(requests_per_second) |  Fail  |  -24.41%  |   60963.0    | 46082.5 |
 |   edge    |  100   |          40          |     0     | avg(requests_per_second) |  Pass  |  -11.03%  |   93206.5    | 82922.5 |
 |   edge    |  100   |          40          |     1     | avg(requests_per_second) |  Fail  |  -60.53%  |   22190.5    | 8759.5  |
 |   edge    |  100   |          40          |    50     | avg(requests_per_second) |  Fail  |  -20.08%  |   90001.5    | 71932.5 |
 |   edge    |  100   |         200          |     0     | avg(requests_per_second) |  Pass  |  -3.41%   |   72936.0    | 70450.0 |
 |   edge    |  100   |         200          |     1     | avg(requests_per_second) |  Fail  |  -56.28%  |   19330.5    | 8451.5  |
 |   edge    |  100   |         200          |    50     | avg(requests_per_second) |  Pass  |  -11.42%  |   70538.0    | 62480.5 |
 +-----------+--------+----------------------+-----------+--------------------------+--------+-----------+--------------+---------+
$ echo $?
1
# If for example max_failures is 50, the benchmark will fail too, because the second block, (test_type: http) has more than 50% of failures.
```

### Querying for raw data

Using the config file [ocm-requests.json](config/ocm-requests.json)

```shell
$ touchstone_compare -url https://my-es-instance.com:9200 -u 975fa650-aeb2-5042-8517-fe277d7cb1f3  --config config/ocm-results.json
[
    {
        "test_name": "self-terms-review",
        "uuid": "aeed6306-b7e1-11eb-b313-e86a640406b2",
        "timestamp": "2021-05-18T19:44:08.826868032Z",
        "code": 200,
        "method": "POST",
        "url": "/api/authorizations/v1/self_terms_review",
        "latency_ns": 5153765154,
        "bytes_out": 0,
        "bytes_in": 139,
        "has_error": false,
        "has_body": true
    },
    {
        "test_name": "self-terms-review",
        "uuid": "aeed6306-b7e1-11eb-b313-e86a640406b2",
        "timestamp": "2021-05-18T19:44:12.026910285Z",
        "code": 200,
        "method": "POST",
        "url": "/api/authorizations/v1/self_terms_review",
        "latency_ns": 3883379506,
        "bytes_out": 0,
        "bytes_in": 139,
        "has_error": false,
        "has_body": true
    },
    {
        "test_name": "self-terms-review",
        "uuid": "aeed6306-b7e1-11eb-b313-e86a640406b2",
        "timestamp": "2021-05-18T19:44:13.3269087Z",
        "code": 200,
        "method": "POST",
        "url": "/api/authorizations/v1/self_terms_review",
        "latency_ns": 3145732320,
        "bytes_out": 0,
        "bytes_in": 139,
        "has_error": false,
        "has_body": true
    },
...
...
...
    {
        "test_name": "self-terms-review",
        "uuid": "aeed6306-b7e1-11eb-b313-e86a640406b2",
        "timestamp": "2021-05-18T19:49:09.626913447Z",
        "code": 0,
        "method": "POST",
        "url": "/api/authorizations/v1/self_terms_review",
        "latency_ns": 15068360575,
        "bytes_out": 0,
        "bytes_in": 0,
        "has_error": true,
        "has_body": false
    }
]

```

### CodeStyling and Linting

Touchstone uses [pre-commit](https://pre-commit.com) framework to maintain the code linting and python code styling.
The CI would run the pre-commit check on each pull request.
We encourage our contributors to follow the same pattern, while contributing to the code.

The pre-commit configuration file is present in the repository `.pre-commit-config.yaml`
It contains the different code styling and linting guide which we use for the application.

Following command can be used to run the pre-commit:
`pre-commit run --all-files`

If pre-commit is not installed in your system, it can be install with : `pip install pre-commit`
