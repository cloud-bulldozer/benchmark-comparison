# Touchstone

Framework to help data comparison between 2 similar datasets.
Touchstone is a framework written in python that provides you an apples to apples comparison
between 2 similar datasets.

Touchstone currently supports comparison of the following docs:

|    Benchmark   |     Database     |    Harness    |
|----------------|------------------|---------------|
|      Uperf     |  Elasticsearch   |    Ripsaw     |
|      YCSB      |  Elasticsearch   |    Ripsaw     |
|      Pgbench   |  Elasticsearch   |    Ripsaw     |
|      Vegeta    |  Elasticsearch   |    Ripsaw     |
|        -       |  Prometheus      |       -       |

## Usage

It is suggested to use a venv to install and run touchstone.

```
python -m venv /path/to/new/virtual/environment
source /path/to/new/virtual/environment/bin/activate
git clone https://github.com/cloud-bulldozer/touchstone
python setup.py develop
touchstone_compare -h
```

#### For example:

##### To Compare benchmark database on Elasticsearch
To compare 2 runs of uperf data indexed into elasticsearch server marquez.perf.lab.eng.rdu2.redhat.com ran through ripsaw,
which generated 2 uuids: [6c5d0257-57e4-54f0-9c98-e149af8b4a5c 70cbb0eb-8bb6-58e3-b92a-cb802a74bb52]

You'd be running it as follows:
```
touchstone_compare -database elasticsearch -benchmark uperf -harness ripsaw -url marquez.perf.lab.eng.rdu2.redhat.com marquez.perf.lab.eng.rdu2.redhat.com  -u 6c5d0257-57e4-54f0-9c98-e149af8b4a5c 70cbb0eb-8bb6-58e3-b92a-cb802a74bb52
```

Regarding metadata collection, the indices from which metadata will be collected is listed in the file of the benchmark being run. However, these indices can be overrided by including the path to a metadata config file as a command line argument. The default location of this file is examples/metadata.json.

Running with this argument would be run as follows:
```
touchstone_compare -database elasticsearch -benchmark uperf -harness ripsaw -url marquez.perf.lab.eng.rdu2.redhat.com marquez.perf.lab.eng.rdu2.redhat.com  -u 6c5d0257-57e4-54f0-9c98-e149af8b4a5c -input-file examples/metadata.json 
```   

To compare the prometheus metric data aggreagations(sum, max, min, deviation, nth percentile) over a period of time
for prometheus running locally on url - http://localhost:9090 for the metric - 'node_disk_io_time_seconds_total' for a time interval
you need to create following config file - 

```
---
- url: http://localhost:9090
  query_list:
    - node_disk_io_time_seconds_total
  bearer_token:
  disable_ssl: True
  start_time_list:
    - 1594307762
  end_time_list:
    - 1594307777
```
You'd be running it as follows:
```
touchstone_compare -database prometheus -prom_config path/to/your/config_file.yaml 
``` 
### Comparing on a specific identifier

You can also now compare against identifiers other than the `uuid` key, so for
example if you'd like to compare using the key `cluster_name` you can do so by
using the `-id` argument and run as follows:

```
touchstone_compare uperf elasticsearch ripsaw -url marquez.perf.lab.eng.rdu2.redhat.com -u cnvcluster minikube -id cluster_name
```

Note: If the identifier is same for 2 or more uuids, then all of the results
will be taken into consideration while computing aggregations, so please use
with caution.


## Contributing

Touchstone uses factory pattern for the creating main objects - Benchmarks and Databases.

The logic of interacting with a specific database is in the databases directory, while
the knowledge and interaction of what the query and data should look like goes into a specific benchmark.

As a contributor, more often than not you'll be adding code to benchmarks dir.

### Benchmarks

To add a new benchmark, you'll create your the class and define three member function which will need to put together the following 5 types of keys:

1. Filter: To only take the particular entry into consideration if it passes filter
2. Bucket: To facilitate apple to apple comparison, touchstone will put records into buckets
3. Aggregation: Apply aggregation and the type on the keys
4. Compare: Compare the keys that help characterize the SUT/benchmark run
5. Collate: Collates the keys after applying filters, buckets and aggregations.
5. Exclude: Excludes entries which passes this filter.

The member functions are:

1. emit_compute_map(): This should emit a dictionary where key is the index and value is a list of various compute dictionaries, and each compute dictionary will have the following keys:

    a. 'filter': essentially only select docs/rows that match these conditions. one example for uperf is {'test_type.keyword': 'stream'}

    b. 'buckets': this is a list of all the various keys we'll need to look at while bucketing to ensure we do an apple to apple comparison. one example for uperf is ['protocol.keyword', 'message_size', 'num_threads']

    c. 'aggregations': aggregations is a dictionary of keys to do aggregations with value being a list of type of aggregations, note an aggregation can also be a dictionary. one example for uperf is {'norm_byte': ['max', 'avg', {'percentiles': {'percents': [50]}}]}


    d. 'exclude': excludes documents from the query that meet these conditions. For uperf we exclude documents with zero norm_ops metrics with {'norm_ops': 0}

2. emit_compare_map(): This should emit a dictionary where key is the index and the value is a list of keys to compare

3. emit_indices(): This should emit a list of indices to search against.

And you'll need to create the above for all the indices in the database choice, so for example in Uperf we look up in the dict and build which looks like:


```
{
      'elasticsearch': {
        'ripsaw': {
          'ripsaw-uperf-results': {
            'compare': ['uuid', 'user', 'cluster_name',
              'hostnetwork', 'service_ip'
            ],
            'compute': [{
              'filter': {
                'test_type.keyword': 'stream'
              },
              'exclude': {
                'norm_ops': 0
              },
              'buckets': ['protocol.keyword',
                'message_size', 'num_threads'
              ],
              'aggregations': {
                'norm_byte': ['max', 'avg',
                  {'percentiles': {
                    'percents': [50]
                  }}]
              }
            }, {
              'filter': {
                'test_type.keyword': 'rr'
              },
              'exclude': {
                'norm_ops': 0
              },
              'buckets': ['protocol.keyword',
                'message_size', 'num_threads'
              ],
              'aggregations': {
                'norm_ops': ['max', 'avg'],
                'norm_ltcy': [{
                  'percentiles': {
                    'percents': [90, 99]
                  }
                }, 'avg']
              },
            }]
          }
        }
      }
    }
```

The highest level is the database type, and then comes the harness, then the dictionary is of the indices ( in this case only one index )
This dictionary has 2 keys - compare and compute.


### Databases

If you're looking at adding databases please take a look at the elasticsearch class.

The main interfaces that will need to be added are as follows:
1. emit_compare_dict: This needs to be a dictionary where the keys are the keys in compare map for the benchmark,
while the value is another dictionary where the sub dictionary's key is the uuid and the value is the associated value.

So an example for uperf's compare is as follows:

```
{
    "uuid": {
        "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": "6c5d0257-57e4-54f0-9c98-e149af8b4a5c"
    },
    "user": {
        "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": "aakarsh"
    },
    "cluster_name": {
        "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": "cnvcluster"
    },
    "hostnetwork": {
        "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": "False"
    },
    "service_ip": {
        "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": "172.16.12.12"
    }
}
```

2. emit_compute_dict: This dictionary is going to be a nested dictionary with a depth of
2 * len(buckets) in the compute map, where first level key will be the first key in the list of bucket
and then the value is a dictionary with keys being the potential values for the bucket and then the value then being
a dictionary where the key will be the second level key and so on until we reach a depth of 2 * len(buckets) at which case
the value ends up being a dictionary with keys being the aggregations and the value being a dictionary similar to the compare dictionary
with key being uuid and the value being aggregation value.

So an example for uperf's compute map where buckets is ['protocol.keyword', 'message_size', 'num_threads']
and lets say protocol was only of 'tcp' while message_size could be either 512 or 1024 while num_threads takes the value of 1 or 2, then it
looks like following :

```
{
    "protocol": {
        "tcp": {
            "message_size": {
                "512": {
                    "num_threads": {
                        "1": {
                            "max(norm_ops)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": 1740.0
                            },
                            "avg(norm_ops)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": 1040.0
                            },
                            "90.0percentiles(norm_ltcy)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": null
                            },
                            "99.0percentiles(norm_ltcy)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": null
                            },
                            "avg(norm_ltcy)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": null
                            }
                        },
                        "2": {
                            "max(norm_ops)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": 4622.0
                            },
                            "avg(norm_ops)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": 2455.0833333333335
                            },
                            "90.0percentiles(norm_ltcy)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": null
                            },
                            "99.0percentiles(norm_ltcy)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": null
                            },
                            "avg(norm_ltcy)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": null
                            }
                        }
                    }
                },
                "1024": {
                    "num_threads": {
                        "1": {
                            "max(norm_ops)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": 2412.0
                            },
                            "avg(norm_ops)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": 1000.3333333333334
                            },
                            "90.0percentiles(norm_ltcy)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": null
                            },
                            "99.0percentiles(norm_ltcy)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": null
                            },
                            "avg(norm_ltcy)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": null
                            }
                        },
                        "2": {
                            "max(norm_ops)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": 3357.0
                            },
                            "avg(norm_ops)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": 1507.0833333333333
                            },
                            "90.0percentiles(norm_ltcy)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": null
                            },
                            "99.0percentiles(norm_ltcy)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": null
                            },
                            "avg(norm_ltcy)": {
                                "6c5d0257-57e4-54f0-9c98-e149af8b4a5c": null
                            }
                        }
                    }
                }
            }
        }
    }
}
```

### Prometheus metric agregation config file
For comparing the metric aggregations following keys are compulsory in the config file - 
```
url: string
query_list: string (this can accept multiple metrices)
bearer_token: string
disable_ssl: Boolean
start_time_list: int (this can accept multiple values)
end_time_list: int (this can accept multiple values)
```
An example config_file can be found [here](src/touchstone/databases/prom_config.yaml)
