import dateparser
from prometheus_api_client import PrometheusConnect


class Prometheus:
    def __init__(self, query_list, start_time_list, end_time_list,
                 url="http://127.0.0.1:9090", headers=None, disable_ssl=False):
        self.url = url
        self.headers = headers
        self.disable_ssl = disable_ssl
        self.query_list = query_list
        self.start_time_list = start_time_list
        self.end_time_list = end_time_list
        self.pc = PrometheusConnect(url=url, headers=headers, disable_ssl=disable_ssl)

    def compare_data(self):
        output = []
        len_times = 1 if self.start_time_list is None else len(self.start_time_list)
        for query in self.query_list:
            for i in range(len_times):
                aggregates = {'url': self.url, 'query': query}
                settings = {"DATE_ORDER": "YMD"}
                if self.start_time_list is not None:
                    aggregates['start_time'] = self.start_time_list[i]
                    start_time = dateparser.parse(str(self.start_time_list[i]),
                                                  settings=settings)
                else:
                    start_time = None
                if self.end_time_list is not None:
                    aggregates['end_time'] = self.end_time_list[i]
                    end_time = dateparser.parse(str(self.end_time_list[i]), settings=settings)
                else:
                    end_time = None
                aggregates.update(
                    self.get_aggregates(query, start_time, end_time))
                output.append(aggregates)
        return output

    def get_aggregates(self, query, start_time, end_time):
        aggregation_operations = ['sum', 'max', 'min', 'variance', 'deviation', 'average',
                                  'percentile_95']
        return self.pc.get_metric_aggregation(query=query, operations=aggregation_operations,
                                              start_time=start_time, end_time=end_time, step='15')
