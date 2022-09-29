from flask import (Blueprint, flash, request, current_app, jsonify, Response,
                   redirect, url_for)
from backend.connections import tor_request
from flask_login import login_required, current_user
from random import randrange
from backend.utils import pickle_it
from application_factory import current_path
from datetime import datetime
import logging
import json
import os
import pandas as pd

api = Blueprint('api', __name__)


@api.route("/satoshi_quotes_json", methods=['GET'])
@login_required
def satoshi_quotes_json():
    url = 'https://raw.githubusercontent.com/NakamotoInstitute/nakamotoinstitute.org/0bf08c48cd21655c76e8db06da39d16036a88594/data/quotes.json'
    try:
        quotes = tor_request(url).json()
    except Exception:
        return (json.dumps(' >> Error contacting server. Retrying... '))
    quote = quotes[randrange(len(quotes))]
    return (quote)


# Gets a local pickle file and dumps - does not work with pandas df
# Do not include extension pkl on argument
@api.route("/get_pickle", methods=['GET'])
@login_required
def get_pickle():
    filename = request.args.get("filename")
    serialize = request.args.get("serialize")
    if not serialize:
        serialize = True
    if not filename:
        return None
    filename += ".pkl"
    data_loader = pickle_it(action='load', filename=filename)
    if serialize is True:
        return (json.dumps(data_loader,
                           default=lambda o: '<not serializable>'))
    else:
        return (json.dumps(data_loader, default=str))


# Returns a JSON with Test Response on TOR
@api.route("/testtor", methods=["GET"])
@login_required
def testtor():
    from backend.connections import test_tor
    return json.dumps(test_tor())


# Latest Traceback message
@api.route("/traceback_error", methods=["GET"])
@login_required
def traceback_error():
    import traceback
    trace = traceback.format_exc()
    return json.dumps(trace, ignore_nan=True)
