# -*- coding: utf-8 -*-
import json
import yaml
import logging
import csv
from tabulate import tabulate
from ..utils.lib import flatten_and_discard

logger = logging.getLogger("touchstone")


class Compare:

    comparisons = 0
    fails = 0

    def __init__(self, baseline_uuid, json_data):
        self.json_data = json_data
        self.baseline_uuid = baseline_uuid
        self.passed = True
        self.tolerancy = 0
        self.compare_dict = {}

    def _compare(self, input_dict, compare_dict):
        self.comparisons += 1
        if self.baseline_uuid not in input_dict:
            logger.error(f"Missing UUID in input dict: {input_dict}")
            return
        # baseline value is the current value plus the tolerancy
        base_val = input_dict[self.baseline_uuid] + input_dict[self.baseline_uuid] * self.tolerancy / 100
        for u, v in input_dict.items():
            # skip input_dict values that are part of the baseline uuid (no comparison to self)
            if u == self.baseline_uuid:
                continue
            try:
                metric_percent = v * 100 / input_dict[self.baseline_uuid]
            except ZeroDivisionError:
                # both values are 0
                if (v == 0) and (input_dict[self.baseline_uuid] == 0):
                    metric_percent = 100
                # just baseline value is 0
                else:
                    metric_percent = 0
            finally:
                # If percentage is greater than 100, sustract 100 from it else substract it from 100
                deviation = metric_percent - 100 if metric_percent > 100 else 100 - metric_percent
                deviation = -deviation if v < input_dict[self.baseline_uuid] else deviation
                print(f"deviation is {deviation}")
                if (self.tolerancy >= 0 and v > base_val) or (self.tolerancy < 0 and v < base_val):
                    result = "Fail"
                    self.passed = False
                    self.fails += 1
                else:
                    result = "Pass"
            if result not in compare_dict:
                compare_dict[result] = {}
            compare_dict[result] = {
                "{:.2f}%".format(deviation): {self.baseline_uuid: input_dict[self.baseline_uuid], u: v}
            }

    def compare(self, json_path, tolerancy):
        """
        compare evaluates the tolerancy in the given json_path
        :param json_path JSON path to look for metrics
        :param tolerancy Tolerancy value
        """
        # Split json path
        self.json_path = json_path
        self.tolerancy = tolerancy
        self.compare_dict = {}

        # Data contains the dictionary
        # json_path contains the current json_path position
        # parent contains the output dictionary
        def recurse(data, json_path, parent):
            # If we haven't reached the first level
            if len(json_path) > 1:
                # In case of using a wildcard path iterate over each key and recurse using those
                if json_path[0] == "*":
                    for k in data:
                        parent[k] = {}
                        recurse(data[k], json_path[1::], parent[k])
                else:
                    if json_path[0] not in data:
                        self.passed = None
                        return
                    parent[json_path[0]] = {}
                    recurse(data[json_path[0]], json_path[1::], parent[json_path[0]])
            # Last level before tolerancy
            else:
                # Add metric names to the dict and call compare with the metric name
                parent[json_path[0]] = {}
                self._compare(data[json_path[0]], parent[json_path[0]])

        recurse(self.json_data, self.json_path, self.compare_dict)
        return self.passed


def run(baseline_uuid, results_data, compute_header, output_file, args):
    """
    run evaluates toleration thresholds against comparison data
    :param baseline_uuid UUID to use as baseline
    :param results_data comparison data
    :param compute_header headers to use in CSV and tabulate outputs
    :param args benchmark-comparison arguments
    """
    rc = 0
    passed = True
    try:
        args.tolerancy_rules.seek(0)
        json_paths = yaml.load(args.tolerancy_rules, Loader=yaml.FullLoader)
    except Exception as err:
        logger.error(f"Error loading tolerations rules: {err}")
    for json_path in json_paths:
        c = Compare(baseline_uuid, results_data)
        passed = c.compare(json_path["json_path"], json_path["tolerancy"])
        if passed is None:
            continue
        if args.output == "yaml":
            print(yaml.dump({"tolerations": c.compare_dict}, indent=1), file=output_file)
        elif args.output == "json":
            print(json.dumps({"tolerations": c.compare_dict}, indent=4), file=output_file)
        elif args.output == "csv":
            row_list = [compute_header]
            flatten_and_discard(c.compare_dict, compute_header, row_list)
            writer = csv.writer(output_file, delimiter=",")
            list(map(writer.writerow, row_list))
        else:
            row_list = []
            flatten_and_discard(c.compare_dict, compute_header, row_list)
            print(tabulate(row_list, headers=compute_header, tablefmt="pretty"), file=output_file)
        if not passed and c.fails * 100 / c.comparisons > json_path.get("max_failures", 0):
            rc = args.rc
    return rc
