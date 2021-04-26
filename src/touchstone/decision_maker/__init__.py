# -*- coding: utf-8 -*-
import json
import yaml
import logging
import csv
from tabulate import tabulate
from ..utils.lib import flatten_and_discard

logger = logging.getLogger("touchstone")


class Compare:
    def __init__(self, baseline_uuid, json_data):
        self.json_data = json_data
        self.baseline_uuid = baseline_uuid
        self.tolerancy = 0
        self.compare_dict = {}
        self.rc = 0

    def _compare(self, input_dict, compare_dict):
        if self.baseline_uuid not in input_dict:
            logger.error(f"Missing UUID in input dict: {input_dict}")
            return
        # baseline value is the current value plus the tolerancy
        base_val = input_dict[self.baseline_uuid] + input_dict[self.baseline_uuid] * self.tolerancy / 100
        for u, v in input_dict.items():
            metric_percent = v * 100 / input_dict[self.baseline_uuid]
            # If percentage is greater than 100, sustract 100 from it else substract it from 100
            deviation = metric_percent - 100 if metric_percent > 100 else 100 - metric_percent
            deviation = -deviation if v < input_dict[self.baseline_uuid] else deviation
            compare_dict[self.baseline_uuid] = {input_dict[self.baseline_uuid]: "baseline"}
            if (self.tolerancy >= 0 and v > base_val) or (self.tolerancy < 0 and v < base_val):
                compare_dict[u] = {v: "failed: {:.2f}%".format(deviation)}
                self.rc = 1
            else:
                compare_dict[u] = {v: "ok: {:.2f}%".format(deviation)}

    def compare(self, json_path, tolerancy):
        """
        compare evaluates the tolerancy in the given json_path
        :param json_path JSON path to look for metrics
        :param tolerancy Tolerancy value
        """
        # Split json path
        self.json_path = json_path.split("/")
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
                        logger.error(
                            f"Key {json_path[0]} key not found in current dict level: {list(data.keys())}"
                        )
                        return
                    parent[json_path[0]] = {}
                    recurse(data[json_path[0]], json_path[1::], parent[json_path[0]])
            # Last level before tolerancy
            else:
                # Add metric names to the dict and call compare with the metric name
                parent[json_path[0]] = {}
                self._compare(data[json_path[0]], parent[json_path[0]])

        recurse(self.json_data, self.json_path, self.compare_dict)
        return self.rc


def run(baseline_uuid, results_data, rule_fd, output, compute_header, output_file):
    """
    run evaluates toleration thresholds against comparison data
    :param baseline_uuid UUID to use as baseline
    :param results_data comparison data
    :param rule_fd rule file descritor
    :param compute_header headers to use in CSV and tabulate outputs
    :param output_file Output file
    """
    rc = 0
    compute_header.append("tolerancy")
    try:
        json_paths = yaml.load(rule_fd, Loader=yaml.FullLoader)
    except Exception as err:
        logger.error(f"Error loading tolerations rules: {err}")
    c = Compare(baseline_uuid, results_data)
    for json_path in json_paths:
        r = c.compare(json_path["json_path"], json_path["tolerancy"])
        if r:
            rc = r
            if output == "yaml":
                print(yaml.dump({"tolerations": c.compare_dict}, indent=1), file=output_file)
            elif output == "json":
                print(json.dumps({"tolerations": c.compare_dict}, indent=4), file=output_file)
            elif output == "csv":
                row_list = [compute_header]
                flatten_and_discard(c.compare_dict, compute_header, row_list)
                writer = csv.writer(output_file, delimiter=",")
                list(map(writer.writerow, row_list))
            else:
                row_list = []
                flatten_and_discard(c.compare_dict, compute_header, row_list)
                print(tabulate(row_list, headers=compute_header, tablefmt="pretty"), file=output_file)
    return rc
