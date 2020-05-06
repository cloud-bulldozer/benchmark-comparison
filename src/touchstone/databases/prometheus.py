import dateparser
from prometheus_api_client import PrometheusConnect


class Prometheus:
    def __init__(self, metric_name_list, start_time_list, end_time_list,
                 url="http://127.0.0.1:9090", headers=None, disable_ssl=False):
        self.url = url
        self.headers = headers
        self.disable_ssl = disable_ssl
        self.metric_name_list = metric_name_list
        self.start_time_list = start_time_list
        self.end_time_list = end_time_list
        self.pc = PrometheusConnect(url=url, headers=headers, disable_ssl=disable_ssl)
        self.compare_data()

    def compare_data(self):
        output = []
        for metric_name in self.metric_name_list:
            for i in range(len(self.start_time_list)):
                aggregates = {'url': self.url, 'metric': metric_name,
                              'start_time': self.start_time_list[i], 'end_time': self.end_time_list[i]}
                settings = {"DATE_ORDER": "YMD"}
                start_time = dateparser.parse(str(self.start_time_list[i]), settings=settings)
                end_time = dateparser.parse(str(self.end_time_list[i]), settings=settings)
                aggregates.update(
                    self.get_aggregates(metric_name, start_time, end_time))
                output.append(aggregates)
        return output

    def get_aggregates(self, metric_name, start_time, end_time):
        params = {
            'start': start_time,
            'end': end_time
        }
        aggregation_operations = ['sum', 'max', 'min', 'variance', 'deviation', 'average',
                                  'percentile_95']
        return self.pc.get_metric_aggregation(metric_name, params, aggregation_operations)
