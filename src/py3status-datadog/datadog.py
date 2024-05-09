"""
Show Datadog metrics and monitors.

Configuration parameters:
    icon_metric: The icon to display for metrics
    icon_monitor: The icon to display for monitors
    name: The name of the metric
    data_type: The type of data to request, One of: metric, monitor
    query: The query for the metric or monitor
    dashboard_url: An URL to an associated dashboard to be opened with DD_BROWSER on left-click
    browser: The browser to use when opening associated dashboard URLs
    format: The display format for this module (default 'datadog')

Format placeholders:
    {name} The name of the metric or monitor
    {icon} A module icon
    {data} The received value of the Datadog metric or monitor

Color options:
    color: Default to color_good, active color otherwise

@author bbusse, Björn Busse

SAMPLE OUTPUT
{"full_text": "\ud83d\udca1 lounge 23 \u25cf #E05B22", \
"instance": "lounge 0", "name": "lounge", "color": "#E05B22"}
"""

from datetime import datetime
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
import os


class Py3status:
    """ """

    # Configuration parameters
    browser = "firefox"
    icon = ""
    icon_monitor = "🚨"
    icon_metric = "🐕"
    name = "dd"
    # The type of data to query and display:
    # metric versus monitor
    data_type = "metric"
    data = ""
    query = ""
    dashboard_url = ""
    format = "{icon} {name} {data}"

    def datadog(self):
        icon = self.icon
        icon_monitor = self.icon_monitor
        icon_metric = self.icon_metric
        name = self.name
        data_type = self.data_type
        data = self.data
        query = self.query
        dashboard_url = self.dashboard_url
        browser = self.browser

        response = self.metrics_query_timeseries(self.query)
        print(response)

        self.icon = self.icon_monitor if data_type == "monitor" else self.icon_metric

        return {
            "full_text": self.py3.safe_format(
                self.format, {"icon": icon}, {"name": name}, {"data": data}
            ),
            "icon": icon,
            "name": name,
            "data": data,
        }

    def metrics_query_timeseries(self, query):
        configuration = Configuration()

        with ApiClient(configuration) as api_client:
            api_instance = MetricsApi(api_client)
            t_from = int(datetime.now().timestamp()) - 20000
            t_to = int(datetime.now().timestamp())
            response = api_instance.query_metrics(query=query, _from=t_from, to=t_to)
            return response

    def open_dashboard(self):
        self.py3.command_run(self.browser + self.dashboard_url)

    def on_click(self, event):
        """
        Open dashboard in a browser on left-click
        """

        # Left mouse button: Turn on lights or switch color
        if event["button"] == 1:
            self.open_dashboard(self.url)


if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test

    module_test(Py3status)
