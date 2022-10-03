import os
import json
import pickle
import time
import logging
import socket
import configparser
from datetime import datetime
from application_factory import current_path
import pandas as pd
import numpy as np


# Returns the home path
def home_path():
    from pathlib import Path
    home = str(Path.home())
    return (home)


def create_config(config_file):
    from backend.config import Config
    logging.warning(
        "Config File not found. Getting default values and saving.")
    # Get the default config and save into config.ini
    default_file = Config.default_config_file

    default_config = configparser.ConfigParser()
    default_config.read(default_file)

    with open(config_file, 'w') as file:
        default_config.write(file)

    return (default_config)


# Function to load and save data into pickles
def pickle_it(action='load', filename=None, data=None):
    if filename is not None:
        filename = '.dmtnt/' + filename
        filename = os.path.join(home_path(), filename)
    else:
        filename = '.dmtnt/'
        filename = os.path.join(home_path(), filename)

    # list all pkl files at directory
    if action == 'list':
        files = os.listdir(filename)
        ret_list = [x for x in files if x.endswith('.pkl')]
        return (ret_list)

    if action == 'delete':
        try:
            os.remove(filename)
            return ('deleted')
        except Exception:
            return ('failed')

    if action == 'load':
        try:
            if os.path.getsize(filename) > 0:
                with open(filename, 'rb') as handle:
                    ld = pickle.load(handle)
                    return (ld)
            else:
                os.remove(filename)
                return ("file not found")

        except Exception:
            return ("file not found")
    else:
        # Make directory if doesn't exist
        try:
            directory = os.path.dirname(filename)
            os.stat(directory)
        except Exception:
            os.mkdir(directory)

        with open(filename, 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
            return ("saved")


# Function to load and save data into json
def json_it(action='load', filename=None, data=None):
    filename = '.dmtnt/' + filename
    filename = os.path.join(home_path(), filename)
    if action == 'delete':
        try:
            os.remove(filename)
            return ('deleted')
        except Exception:
            return ('failed')

    if action == 'load':
        try:
            if os.path.getsize(filename) > 0:
                with open(filename, 'r') as handle:
                    ld = json.load(handle)
                    return (ld)
            else:
                os.remove(filename)
                return ("file not found")
        except Exception:
            return ("file not found")
    else:
        # Serializing json
        json_object = json.dumps(data, indent=4)

        # Writing to sample.json
        with open(filename, "w") as handle:
            handle.write(json_object)
            return ("saved")


def fxsymbol(fx, output='symbol'):
    # Gets an FX 3 letter symbol and returns the HTML symbol
    # Sample outputs are:
    # "EUR": {
    # "symbol": "",
    # "name": "Euro",
    # "symbol_native": "",
    # "decimal_digits": 2,
    # "rounding": 0,
    # "code": "EUR",
    # "name_plural": "euros"
    filename = os.path.join(current_path, 'static/json_files/currency.json')
    with open(filename) as fx_json:
        fx_list = json.load(fx_json)
    try:
        out = fx_list[fx][output]
    except Exception:
        if output == 'all':
            return (fx_list[fx])
        out = fx
    return (out)


def determine_docker_host_ip_address():
    cmd = "ip route show"
    import subprocess
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return str(output).split(' ')[2]


def runningInDocker():
    try:
        with open('/proc/self/cgroup', 'r') as procfile:
            for line in procfile:
                fields = line.strip().split('/')
                if 'docker' in fields:
                    return True

        return False

    except Exception:
        return False


# Serialize only objects that are json compatible
# This will exclude classes and methods
def safe_serialize(obj):

    def default(o):
        return f"{type(o).__qualname__}"

    return json.dumps(obj, default=default)


#  Check if a port at localhost is in use
def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def safe_filename(s):
    return ("".join([
        c for c in s if c.isalpha() or c.isdigit() or c == '_' or c == '-'
    ]).rstrip())


def join_all(threads, timeout):
    """
    Args:
        threads: a list of thread objects to join
        timeout: the maximum time to wait for the threads to finish
    Raises:
        RuntimeError: is not all the threads have finished by the timeout
    """
    start = cur_time = time.time()
    while cur_time <= (start + timeout):
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=0)
        if all(not t.is_alive() for t in threads):
            break
        time.sleep(0.1)
        cur_time = time.time()
    else:
        still_running = [t for t in threads if t.is_alive()]
        num = len(still_running)
        names = [t.name for t in still_running]
        raise RuntimeError('Timeout on {0} threads: {1}'.format(num, names))


def jformat(n, places, divisor=1):
    if n is None:
        return "-"
    else:
        try:
            n = float(n)
            n = n / divisor
            if n == 0:
                return "-"
        except ValueError:
            return "-"
        except TypeError:
            return (n)
        try:
            form_string = "{0:,.{prec}f}".format(n, prec=places)
            return form_string
        except (ValueError, KeyError):
            return "-"


# Function to clean string fields - leave only digits and .
def cleanfloat(text):
    if not isinstance(text, str):
        return text
    if text is None:
        return (0)
    acceptable = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
    string = ""
    for char in (text):
        if char in acceptable:
            string = string + char
    try:
        string = float(string)
    except Exception:
        string = 0
    return (string)


def cleandate(text):  # Function to clean Date fields
    if text is None:
        return (None)
    text = str(text)
    acceptable = [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "/", "-", ":",
        " "
    ]
    str_parse = ""
    for char in text:
        if char in acceptable:
            char = '-' if (char == '.' or char == '/') else char
            str_parse = str_parse + char
    from dateutil import parser

    str_parse = parser.parse(str_parse, dayfirst=True)
    return (str_parse)


def file_created_today(filename):
    try:
        today = datetime.now().date()
        filetime = datetime.fromtimestamp(os.path.getctime(filename))
        if filetime.date() == today:
            return True
        else:
            return False
    except Exception:
        return False


def df_col_to_highcharts(df, cols):
    """
    receives columns in format ['col1'] or ['col1', 'col2',...]
    returns a dictionary that can later be used in highcharts
    names is a list of names for the columns
    colors is a list of colors for the columns
    """
    # copy only these columns
    data = df[cols].copy()
    # dates need to be in Epoch time for Highcharts
    data.index = (data.index - datetime(1970, 1, 1)).total_seconds()
    data.index = data.index * 1000
    data.index = data.index.astype(np.int64)
    # Make sure it is a dataframe
    if isinstance(data, pd.Series):
        data = data.to_frame()
    data = data.to_records(index=True).tolist()
    data = [list(elem) for elem in data]
    return data


def get_image(domain):
    """
    Returns the image for a given ticker
    """
    return "https://www.google.com/s2/favicons?domain=" + domain


# Returns the average datetime from a datetime list
def average_datetime(list_times):
    df = pd.DataFrame(list_times, columns=['dates'])
    avg = pd.to_datetime(df.dates.dropna().astype(np.int64).mean())
    return avg


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
    local_ip_address = s.getsockname()[0]
    pickle_it('save', 'local_ip_address.pkl', local_ip_address)
    return (local_ip_address)
