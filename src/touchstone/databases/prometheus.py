import datetime
from prometheus_api_client import PrometheusConnect
import time


class Prometheus:
    def __init__(self, metrics, start_time_list, end_time_list,
                 url="http://127.0.0.1:9090", headers=None, test_info=None, disable_ssl=False):
        self.test_info = test_info
        self.url = url
        self.headers = headers
        self.disable_ssl = disable_ssl
        self.metrics = metrics
        self.start_time_list = start_time_list
        self.end_time_list = end_time_list
        self.pc = PrometheusConnect(url=url, headers=headers, disable_ssl=disable_ssl)

    def compare_data(self):
        output = []
        # when start_time and end_time are None, these queries are called for the duration of
        # current prometheus session.
        len_times = 1 if self.start_time_list is None else len(self.start_time_list)
        for metric in self.metrics:
            for i in range(len_times):
                aggregates = {'url': self.url, 'query': metric['query'],
                              'metricName': metric['metricName'], 'test_info': self.test_info,
                              'timestamp': time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())}
                if self.start_time_list is not None:
                    aggregates['start_time'] = self.start_time_list[i]
                    start_time = datetime.datetime.fromtimestamp(int(self.start_time_list[i]))
                else:
                    start_time = None
                if self.end_time_list is not None:
                    aggregates['end_time'] = self.end_time_list[i]
                    end_time = datetime.datetime.fromtimestamp(int(self.end_time_list[i]))
                else:
                    end_time = None
                aggregates.update(
                    self.get_aggregates(metric['query'], start_time, end_time))
                output.append(aggregates)
        return output

    def get_aggregates(self, query, start_time, end_time):
        aggregation_operations = ['sum', 'max', 'min', 'variance', 'deviation', 'average',
                                  'percentile_95']
        return self.pc.get_metric_aggregation(query=query, operations=aggregation_operations,
                                              start_time=start_time, end_time=end_time, step='30')
