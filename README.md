# Touchstone

Framework to help data comparison between 2 similar datasets.
Touchstone is a framework written in python that provides you an apples to apples comparison
between 2 similar datasets.

Touchstone currently supports comparison of the following docs:

|    Benchmark   |     Database     |    Harness    |
|----------------|------------------|---------------|
|      Uperf     |  Elasticsearch   |    Ripsaw     |

## Usage

It is suggested to use a venv to install and run touchstone.

```
python -m venv /path/to/new/virtual/environment
source /path/to/new/virtual/environment/bin/activate
git clone https://github.com/cloud-bulldozer/touchstone
python setup.py develop
touchstone_compare -h
```

For example:

To compare 2 runs of uperf data indexed into elasticsearch server marquez.perf.lab.eng.rdu2.redhat.com ran through ripsaw,
which generated 2 uuids: [6c5d0257-57e4-54f0-9c98-e149af8b4a5c 70cbb0eb-8bb6-58e3-b92a-cb802a74bb52]

You'd be running it as follows:
```
touchstone_compare uperf elasticsearch ripsaw -url marquez.perf.lab.eng.rdu2.redhat.com marquez.perf.lab.eng.rdu2.redhat.com  -u 6c5d0257-57e4-54f0-9c98-e149af8b4a5c 70cbb0eb-8bb6-58e3-b92a-cb802a74bb52
```
