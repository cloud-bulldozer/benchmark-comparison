# Touchstone

Touchstone is a framework written in python that provides you an apples to apples comparison between 2 similar datasets.

## Usage

It is suggested to use a venv to install and run touchstone.

```shell
python -m venv /virtual/environment
source /virtual/environment/bin/activate
git clone https://github.com/cloud-bulldozer/touchstone
cd touchstone
python setup.py develop
touchstone_compare -h
usage: touchstone_compare [-h] [--version] [--database {elasticsearch}] [--identifier-key IDENTIFIER] -u UUID [UUID ...] [-o {json,yaml,csv}] --config CONFIG [--output-file OUTPUT_FILE] [--tolerancy-rules TOLERANCY_RULES] -url CONN_URL
                          [CONN_URL ...] [-v] [-vv]

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
+-----------------------+--------------------------------------+-----------------------------------+
|       metadata        |                 uuid                 |               value               |
+-----------------------+--------------------------------------+-----------------------------------+
| value.cluster_version | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 | 4.7.0-0.nightly-2021-03-27-082615 |
| value.cluster_version | 975fa650-aeb2-5042-8517-fe277d7cb1f3 | 4.7.0-0.nightly-2021-03-27-082615 |
+-----------------------+--------------------------------------+-----------------------------------+

+-----------+----------+--------------+-------------+----------------------------+--------------------------------------+--------------------+
| test_type | protocol | message_size | num_threads |            key             |                 uuid                 |       value        |
+-----------+----------+--------------+-------------+----------------------------+--------------------------------------+--------------------+
|  stream   |   udp    |     1024     |      1      |       max(norm_byte)       | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 |    196689920.0     |
|  stream   |   udp    |     1024     |      1      |       max(norm_byte)       | 975fa650-aeb2-5042-8517-fe277d7cb1f3 |    193773568.0     |
|  stream   |   udp    |     1024     |      1      |       avg(norm_byte)       | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 | 178356565.33333334 |
|  stream   |   udp    |     1024     |      1      |       avg(norm_byte)       | 975fa650-aeb2-5042-8517-fe277d7cb1f3 | 178376094.44228095 |
|  stream   |   udp    |     1024     |      1      | 99.0percentiles(norm_byte) | ec7f0cfb-0812-57ab-8905-fd6ddaacf593 | 193717862.39999998 |
|  stream   |   udp    |     1024     |      1      | 99.0percentiles(norm_byte) | 975fa650-aeb2-5042-8517-fe277d7cb1f3 |    192008028.16    |
etc.
```

### Comparing on a specific identifier

You can also now compare against identifiers other than the `uuid` key, so for example if you'd like to compare using the key `cluster_name` you can do so by using the `--identifier-key` argument and run as follows:

```shell
$ touchstone_compare --url https://es.instance:443 -u cnvcluster minikube --identifier-key cluster_name
```

Note: If the identifier is same for 2 or more uuids, then all of the results will be taken into consideration while computing aggregations, so please use with caution.

### Using tolerations

`touchstone` brings a metric toleration evaluation mechanism. This functionallity allows to detect regressions in metrics.
This feature can be enabled with the flag `--tolerancy-rules` which points to a tolerancy configuration file that looks like:

```ỳaml
- json_path: "test_type/stream/protocol/*/message_size/*/num_threads/*/avg(norm_byte)"
  tolerancy: -10
- json_path: "test_type/rr/protocol/*/message_size/*/num_threads/*/99.0percentiles(norm_ltcy)"
  tolerancy: 15
```

This YAML file contains a list of dictionaries, where the `json_path` key indicates the path that will allow `touchstone` finding the metrics from a comparison.
Wildcards can be used to match several keys at a certain level, and `tolerancy` defines the accepted tolerance percentage by the metrics matched by `json_path`.  i.e a 10 would mean any metric 10% higher than the baseline metric will be considered an error, and -10 would mean the opposite, any metric at least 10% below the baseline value will be considered an error.

By default `touchstone` takes the first UUID passed as baseline. When `touchstone` finds a metric not meeting a configured tolerancy thresholds it returns 1.

When tolerancy evaluation is enabled, touchstone will output the results of the evaluation after the results:

```shell
$ touchstone_compare -url https://my-es.instance.com -u 975fa650-aeb2-5042-8517-fe277d7cb1f3 ec7f0cfb-0812-57ab-8905-fd6ddaacf593 --config config/uperf.json --tolerancy-rules tolerancy-configs/mb.yaml
<truncated output>
+-------------+--------+----------------------+-----------+--------------------------+--------------------------------------+----------+----------------+
|  test_type  | routes | conn_per_targetroute | keepalive |           key            |                 uuid                 |  value   |   tolerancy    |
+-------------+--------+----------------------+-----------+--------------------------+--------------------------------------+----------+----------------+
|    http     |  500   |          1           |     0     | avg(requests_per_second) | 6503a15d-ca27-4483-90d9-7116840aef87 | 191160.0 |    baseline    |
|    http     |  500   |          1           |     0     | avg(requests_per_second) | fb9d3fb0-1050-48b7-8e6d-8e7d6b0ba319 | 199434.0 |       ok       |
|    http     |  500   |          1           |     1     | avg(requests_per_second) | 6503a15d-ca27-4483-90d9-7116840aef87 | 12892.5  |    baseline    |
|    http     |  500   |          1           |     1     | avg(requests_per_second) | fb9d3fb0-1050-48b7-8e6d-8e7d6b0ba319 | 11559.0  |       ok       |
|    http     |  500   |          1           |    50     | avg(requests_per_second) | 6503a15d-ca27-4483-90d9-7116840aef87 | 170566.0 |    baseline    |
|    http     |  500   |          1           |    50     | avg(requests_per_second) | fb9d3fb0-1050-48b7-8e6d-8e7d6b0ba319 | 172050.5 |       ok       |
|    http     |  500   |          20          |     0     | avg(requests_per_second) | 6503a15d-ca27-4483-90d9-7116840aef87 | 66229.0  |    baseline    |
|    http     |  500   |          20          |     0     | avg(requests_per_second) | fb9d3fb0-1050-48b7-8e6d-8e7d6b0ba319 | 72479.0  |       ok       |
|    http     |  500   |          20          |     1     | avg(requests_per_second) | 6503a15d-ca27-4483-90d9-7116840aef87 | 12097.5  |    baseline    |
|    http     |  500   |          20          |     1     | avg(requests_per_second) | fb9d3fb0-1050-48b7-8e6d-8e7d6b0ba319 | 11075.0  |       ok       |
|    http     |  500   |          20          |    50     | avg(requests_per_second) | 6503a15d-ca27-4483-90d9-7116840aef87 | 75213.0  |    baseline    |
|    http     |  500   |          20          |    50     | avg(requests_per_second) | fb9d3fb0-1050-48b7-8e6d-8e7d6b0ba319 | 89248.0  |       ok       |
$ echo $?
1
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
