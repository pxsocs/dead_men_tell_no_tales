import ntplib
import numbers
from statistics import mean
import logging
from datetime import datetime, timezone
from flask_mail import Mail, Message
from backend.utils import average_datetime


# This is important to make sure the computer time is always correct
# So a time is retrieved from a series of NTP servers and averaged out
# =====================
# TO BE DISCUSSED: Could this be an attack surface? I.E. the servers below
# keep a list of IP addresses pinging them? Low probability but needs to be
# discussed / disclosed. At a minimum this feature should be able to be disabled
# for users worried about this risk.
# =====================
def ntp_time():
    # List of servers being checked
    ntp_pool = [
        'us.pool.ntp.org', 'pool.ntp.org', 'time.nist.gov', 'time.google.com',
        'time.cloudflare.com', 'time.apple.com', 'time-a-g.nist.gov'
    ]

    def call_ntp(serverAddress):
        call = ntplib.NTPClient()
        return call.request(server, version=3)

    # Checks a few servers and finds the average response time
    response_list_delay = []
    response_list_times = []

    for server in ntp_pool:
        try:
            response = call_ntp(server)
            correction = response.delay / 2 - response.offset
            if isinstance(correction, numbers.Number):
                response_list_delay.append(correction)
                resp_time = datetime.fromtimestamp(
                    response.dest_time + response.offset, timezone.utc)
                response_list_times.append(resp_time)
        except Exception:
            pass

    return average_datetime(response_list_times)
