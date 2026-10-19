r"""
Show Datadog metrics, events and monitors.

Environment:
    The datadog Python APIClient expects
    DD_APP_KEY and DD_API_KEY in the environment
    Make sure to supply both:
    export DD_APP_KEY=""
    export DD_API_KEY=""

Configuration parameters:
    icon_metric: The icon to display for metrics
    icon_monitor: The icon to display for monitors
    name: The name of the metric or monitor
    data_type: The type of data to request, One of: metric, monitor
    query: The query for the metric or monitor
    dashboard_url: An URL to an associated dashboard to be opened with a browser on left-click
    browser: The browser to use when opening associated dashboard URLs
    format: The display format for this module (default 'datadog')
    show notification: Whether to show a notification or not

Format placeholders:
    {name} The name of the metric or monitor
    {icon} A module icon
    {composite} The received value of the Datadog metric or monitor
    {color} The color of the composite item

Color options:
    color: Default to color_good
    color_medium: COLOR_DEGRADED if num events_medium > 0
    color_critical: COLOR_BAD if num events_critical > 0

@author bbusse, Björn Busse
@license 3-clause-BSD

SAMPLE OUTPUT
{"full_text": "\ud83d\udca1 lounge 23 \u25cf #E05B22", \
"instance": "lounge 0", "name": "lounge", "color": "#E05B22"}
"""

from datetime import datetime
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
from datadog_api_client.v2.api.events_api import EventsApi
import os
import subprocess
import platform


class Py3status:
    """ """

    # Configuration parameters
    # The browser to use to open URLs
    browser = os.getenv("BROWSER") or "firefox"
    icon = ""
    # The monitor icon
    icon_monitor = "🚨"
    # The metric icon
    icon_metric = "🐕"
    name= ""
    # The type of datadog data
    data_type = "metric"
    # Our parsed data derived from the API response
    dd_data = ""
    # The list of events already shown
    # We want to show events exactly once
    event_ids_current = []
    event_ids_shown = []
    num_events_critical = 0
    num_events_medium = 0
    # The datadog query
    query = ""
    # The size of the time series window in s
    time_delta_secs = 200000
    # The number of events to capture
    num_events = 50
    # The datadog dashboard to open
    dashboard_url = ""
    format_critical = "{icon} {name} {num_critical}"
    format_medium = "{icon} {name} {num_medium}"
    urgent = False
    # Show os level notification
    show_notification = True
    # Play notification sound
    play_notification_sound = True
    notification_sound_file = "/System/Library/Sounds/Ping.aiff"

    def datadog(self):
        icon = self.icon
        icon_monitor = self.icon_monitor
        icon_metric = self.icon_metric
        name = self.name
        data_type = self.data_type
        self.num_events_critical = 0
        self.num_events_medium = 0
        self.color_critical = ""
        self.color_medium = ""

        query = "count:my.orderbird.errors{env:prd, service:my.orderbird.webapp.api, myob.endpoint:masterdata, http.method:post} by {http.status_code,service}.as_rate()"
        response = self._metrics_query_timeseries(query)

        if response.status == "ok":
            dd_data = response.series[0].length
        else:
            dd_data = "E"

        events = self._dd_events()
        event_ids_current = []

        for event in events['data']:
            if 'monitor' in event['attributes']['attributes']:
                event_id = str(event['attributes']['attributes']['evt']['id'])
                # Track all current monitor event IDs to keep dedupe state stable.
                event_ids_current.append(event_id)

                # Check if this is a new event
                if event_id not in self.event_ids_shown:
                    priority = event['attributes']['attributes'].get('priority')
                    title = event['attributes']['attributes'].get('title', '')
                    print(f"Priority: {priority}")
                    print(f"Event: {title}")
                    self.event_ids_shown.append(event_id)

                    is_critical = str(priority) == 'normal'

                    if is_critical:
                        self.num_events_critical += 1
                    elif str(priority) == 'low':
                        self.num_events_medium += 1

                    if is_critical and self.show_notification:
                        self._send_notification("Critical", title)

                    if is_critical and self.play_notification_sound:
                        self._play_notification_sound(self.notification_sound_file)

        # Keep track of events that already got shown and discard old ones
        self.event_ids_shown = self._intersection(event_ids_current, self.event_ids_shown)
        if len(event_ids_current) > 0:
            num_events_shown = len(self.event_ids_shown)
            print(f"Number of events in buffer: {num_events_shown}")
            print(self.event_ids_shown)

        icon = self.icon_monitor if data_type == "monitor" else self.icon_metric

        self.color_critical = self.py3.COLOR_BAD if self.num_events_critical > 0 else self.py3.COLOR_GOOD
        self.color_medium = self.py3.COLOR_DEGRADED if self.num_events_critical == 0 and self.num_events_medium > 0 else self.py3.COLOR_GOOD

        if self.num_events_critical > 0: self.urgent = True

        def extract_string(val):
            # If val is a Composite object, extract its string content
            if hasattr(val, 'get_content'):
                content = val.get_content()
                if isinstance(content, list) and content:
                    # Use first item's full_text if available
                    first = content[0]
                    return str(first.get('full_text', ''))
                return str(content)
            if val is None:
                return ""
            return str(val)

        full_text_critical = extract_string(self.py3.safe_format(
            self.format_critical, {'icon': icon, 'name': name, 'num_critical': self.num_events_critical, 'color': self.color_critical}
        ))
        full_text_medium = extract_string(self.py3.safe_format(
            self.format_medium, {'icon': icon, 'name': name, 'num_medium': self.num_events_medium, 'color': self.color_medium}
        ))
        if not full_text_critical:
            full_text_critical = ""
        if not full_text_medium:
            full_text_medium = ""
        return {
            'cached_until': self.py3.CACHE_FOREVER,
            'composite': [
                {
                    'index': '0',
                    'full_text': full_text_critical,
                    'color': self.color_critical,
                },
                {
                    'index': '1',
                    'full_text': full_text_medium,
                    'color': self.color_medium,
                }
            ]
        }

    def _dd_events(self):
        import time
        configuration = Configuration()
        def try_events(attempts=None):
            attempt = 0
            while attempts is None or attempt < attempts:
                try:
                    with ApiClient(configuration) as api_client:
                        api_instance = EventsApi(api_client)
                        response = api_instance.list_events()
                    return response
                except Exception as e:
                    attempt += 1
                    time.sleep(5)
            raise Exception("All attempts to fetch events failed.")
        return try_events()

    def _metrics_query_timeseries(self, query):
        import time
        configuration = Configuration()
        def try_metrics(attempts=None):
            attempt = 0
            while attempts is None or attempt < attempts:
                try:
                    with ApiClient(configuration) as api_client:
                        api_instance = MetricsApi(api_client)
                        t_from = int(datetime.now().timestamp()) - self.time_delta_secs
                        t_to = int(datetime.now().timestamp())
                        response = api_instance.query_metrics(query=query, _from=t_from, to=t_to)
                    return response
                except Exception as e:
                    attempt += 1
                    time.sleep(5)
            raise Exception("All attempts to fetch metrics failed.")
        return try_metrics()

    def _intersection(self, list_1, list_2):
        list_3 = [value for value in list_1 if value in list_2]
        return list_3

    def _send_notification(self, title, message):
        if platform.system() == "Darwin":
            osascript = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", osascript], capture_output=False, text=True)

    def _play_notification_sound(self, notification_sound_file):
        if platform.system() == "Darwin":
            subprocess.run(["afplay", notification_sound_file], capture_output=False, text=True)

    def _open_dashboard(self):
        self.py3.command_run(self.browser + " " + self.dashboard_url)

    def on_click(self, event):
        """
        Open dashboard in a browser on left-click
        """

        # Left mouse button: Open dashboard in a browser
        if event["button"] == 1:
            self._open_dashboard(self.url)


if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test

    module_test(Py3status)
