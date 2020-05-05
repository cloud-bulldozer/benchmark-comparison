import dateparser
from prometheus_api_client import PrometheusConnect

class Prometheus:
    def __init__(self, metric_name, start_time_list, end_time_list):
        self.metric_name = metric_name
        self.start_time_list = start_time_list
        self.end_time_list = end_time_list
        self.pc = PrometheusConnect()

    def compare_data(self):
        output = []
        for i in range(len(self.start_time_list)):
            aggregates = {}
            aggregates['metric'] = self.metric_name
            settings = {"DATE_ORDER": "YMD"}
            start_time = dateparser.parse(str(self.start_time_list[i]), settings=settings)
            end_time = dateparser.parse(str(self.end_time_list[i]), settings=settings)
            aggregates.update(
                self.get_aggregates(start_time, end_time))
            output.append(aggregates)
        return output

    def get_aggregates(self, start_time, end_time):
        params = {
            'start': start_time,
            'end': end_time
        }
        aggregation_operations = ['sum', 'max', 'min', 'variance', 'deviation', 'average',
                                  'percentile_95']
        return self.pc.get_metric_aggregation(self.metric_name, params, aggregation_operations)
