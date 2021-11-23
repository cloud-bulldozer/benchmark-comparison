# Benchmark-Comparison Configs

Sample benchmark-comparison configuration files to help users.

## Control Plane metric comparison
### kubeburner-control-plane.json
Configuration to compare kube-api and etcd CPU/Memory
```
$ touchstone_compare -url http://<creds>@<server>:80 -u 9a267887-8fc0-4df3-ae78-3fd7da9dd50b 360db898-d602-476e-a4fb-4391a172c303 --config config/kubeburner-control-plane.json
+-----------------------+--------------------------------------+------------------------------------+
|       metadata        |                 uuid                 |               value                |
+-----------------------+--------------------------------------+------------------------------------+
| value.cluster_version | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 4.10.0-0.nightly-2021-11-04-001635 |
| value.cluster_version | 360db898-d602-476e-a4fb-4391a172c303 | 4.10.0-0.nightly-2021-11-04-001635 |
+-----------------------+--------------------------------------+------------------------------------+
+--------------------------+----------------------+--------------------------+---------------------------------------------+------------+--------------------------------------+----------------------+
|     labels.namespace     |      metricName      |     labels.namespace     |              labels.container               |    key     |                 uuid                 |        value         |
+--------------------------+----------------------+--------------------------+---------------------------------------------+------------+--------------------------------------+----------------------+
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |               kube-apiserver                | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |  331.87200927734375  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |               kube-apiserver                | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |  230.3757781982422   |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |               kube-apiserver                | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |  81.11722889072017   |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |               kube-apiserver                | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 |  83.16142937191972   |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver | kube-apiserver-cert-regeneration-controller | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |  0.6711747050285339  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver | kube-apiserver-cert-regeneration-controller | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |  0.7165213823318481  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver | kube-apiserver-cert-regeneration-controller | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 0.07314285307177015  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver | kube-apiserver-cert-regeneration-controller | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 0.08084937240320116  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |         kube-apiserver-cert-syncer          | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |  0.3297658860683441  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |         kube-apiserver-cert-syncer          | max(value) | 360db898-d602-476e-a4fb-4391a172c303 | 0.27191007137298584  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |         kube-apiserver-cert-syncer          | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 0.10286365697781245  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |         kube-apiserver-cert-syncer          | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 0.10228757489355164  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |       kube-apiserver-check-endpoints        | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |  0.6163581609725952  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |       kube-apiserver-check-endpoints        | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |  0.6884093880653381  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |       kube-apiserver-check-endpoints        | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 0.32412490067317296  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |       kube-apiserver-check-endpoints        | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 0.32056543247791025  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |       kube-apiserver-insecure-readyz        | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 0.031776733696460724 |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |       kube-apiserver-insecure-readyz        | max(value) | 360db898-d602-476e-a4fb-4391a172c303 | 0.03195793554186821  |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |       kube-apiserver-insecure-readyz        | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 0.008451469454213796 |
| openshift-kube-apiserver | containerCPU-Masters | openshift-kube-apiserver |       kube-apiserver-insecure-readyz        | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 0.00833430613754506  |
+--------------------------+----------------------+--------------------------+---------------------------------------------+------------+--------------------------------------+----------------------+
+--------------------------+-------------------------+--------------------------+---------------------------------------------+------------+--------------------------------------+--------------------+
|     labels.namespace     |       metricName        |     labels.namespace     |              labels.container               |    key     |                 uuid                 |       value        |
+--------------------------+-------------------------+--------------------------+---------------------------------------------+------------+--------------------------------------+--------------------+
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |               kube-apiserver                | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |   10816573440.0    |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |               kube-apiserver                | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |   11261952000.0    |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |               kube-apiserver                | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 6299737680.842105  |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |               kube-apiserver                | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 6197453113.657658  |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver | kube-apiserver-cert-regeneration-controller | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |     58310656.0     |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver | kube-apiserver-cert-regeneration-controller | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |     56328192.0     |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver | kube-apiserver-cert-regeneration-controller | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 36576022.456140354 |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver | kube-apiserver-cert-regeneration-controller | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 37678891.81981982  |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |         kube-apiserver-cert-syncer          | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |     36110336.0     |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |         kube-apiserver-cert-syncer          | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |     39059456.0     |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |         kube-apiserver-cert-syncer          | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 34762051.368421055 |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |         kube-apiserver-cert-syncer          | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 34993354.95495495  |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |       kube-apiserver-check-endpoints        | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |     49041408.0     |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |       kube-apiserver-check-endpoints        | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |     46850048.0     |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |       kube-apiserver-check-endpoints        | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 47618335.438596494 |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |       kube-apiserver-check-endpoints        | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 |  45831204.9009009  |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |       kube-apiserver-insecure-readyz        | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |     29261824.0     |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |       kube-apiserver-insecure-readyz        | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |     28864512.0     |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |       kube-apiserver-insecure-readyz        | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |     27083776.0     |
| openshift-kube-apiserver | containerMemory-Masters | openshift-kube-apiserver |       kube-apiserver-insecure-readyz        | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 |     28303360.0     |
+--------------------------+-------------------------+--------------------------+---------------------------------------------+------------+--------------------------------------+--------------------+
+------------------+----------------------+------------------+---------------------+------------+--------------------------------------+---------------------+
| labels.namespace |      metricName      | labels.namespace |  labels.container   |    key     |                 uuid                 |        value        |
+------------------+----------------------+------------------+---------------------+------------+--------------------------------------+---------------------+
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  |        etcd         | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 119.02513885498047  |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  |        etcd         | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |  86.94966888427734  |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  |        etcd         | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |  34.27420365810394  |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  |        etcd         | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 |  34.45009884748373  |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  | etcd-health-monitor | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 3.0158426761627197  |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  | etcd-health-monitor | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |  3.03432559967041   |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  | etcd-health-monitor | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 1.8687284797952886  |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  | etcd-health-monitor | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 1.8538861666713748  |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  |    etcd-metrics     | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |  1.523898959159851  |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  |    etcd-metrics     | max(value) | 360db898-d602-476e-a4fb-4391a172c303 | 1.5008670091629028  |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  |    etcd-metrics     | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |  0.875722878465527  |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  |    etcd-metrics     | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 |  0.875589746948298  |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  |        guard        | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 0.6852850317955017  |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  |        guard        | max(value) | 360db898-d602-476e-a4fb-4391a172c303 | 0.6698623299598694  |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  |        guard        | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 0.42274315723855244 |
|  openshift-etcd  | containerCPU-Masters |  openshift-etcd  |        guard        | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 0.4248275798116181  |
+------------------+----------------------+------------------+---------------------+------------+--------------------------------------+---------------------+
+------------------+-------------------------+------------------+---------------------+------------+--------------------------------------+--------------------+
| labels.namespace |       metricName        | labels.namespace |  labels.container   |    key     |                 uuid                 |       value        |
+------------------+-------------------------+------------------+---------------------+------------+--------------------------------------+--------------------+
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |        etcd         | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |    2235195392.0    |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |        etcd         | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |    2170417152.0    |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |        etcd         | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 1110624022.4561403 |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |        etcd         | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 1105052017.0090091 |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  | etcd-health-monitor | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |     42729472.0     |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  | etcd-health-monitor | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |     41623552.0     |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  | etcd-health-monitor | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 40685738.666666664 |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  | etcd-health-monitor | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 40164047.567567565 |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |    etcd-metrics     | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |     26906624.0     |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |    etcd-metrics     | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |     28274688.0     |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |    etcd-metrics     | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 24359684.49122807  |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |    etcd-metrics     | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 24763124.46846847  |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |       etcdctl       | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |      442368.0      |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |       etcdctl       | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |      421888.0      |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |       etcdctl       | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 314026.6666666667  |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |       etcdctl       | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 404138.6666666667  |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |        guard        | max(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b |     3563520.0      |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |        guard        | max(value) | 360db898-d602-476e-a4fb-4391a172c303 |     3567616.0      |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |        guard        | avg(value) | 9a267887-8fc0-4df3-ae78-3fd7da9dd50b | 758507.1824175824  |
|  openshift-etcd  | containerMemory-Masters |  openshift-etcd  |        guard        | avg(value) | 360db898-d602-476e-a4fb-4391a172c303 | 761745.2972972973  |
+------------------+-------------------------+------------------+---------------------+------------+--------------------------------------+--------------------+
```
