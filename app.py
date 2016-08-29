#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from urllib.parse import urlencode
from urllib import request

from flask import Flask, render_template

__version__ = '0.9.0'

app = Flask(__name__)

STOCK_PRICE_URL = os.environ.get("STOCK_PRICE_URL", "http://127.0.0.1:5001/stock")
WEATHER_URL = os.environ.get("WEATHER_URL", "http://127.0.0.1:5002/weather")
PORT = int(os.environ.get("PORT", 5000))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


def get_request(url, values=None):
    headers = {"User-Agent": "Python urllib", "Content-Type": "application/json"}
    if values:
        data = urlencode(values)
        full_url = "{url}?{data}".format(url=url, data=data)
    else:
        full_url = url
    app.logger.debug("Full URL is: {full_url}".format(full_url=full_url))
    _request = request.Request(full_url, headers=headers)
    try:
        response = request.urlopen(_request)
        result = response.read()
        response.close()
        return result
    except Exception as error:
        app.logger.exception(error)


# The function to lookup weather for a particular city.
# Looks up the weather microservice and returns JSON doc
def lookup_weather(city):
    url = "{endpoint}/{city}".format(endpoint=WEATHER_URL, city=city)
    return get_request(url)


# The function to lookup stock price for a particular symbol.
# Looks up the 'stock-price' microservice and returns JSON doc
def lookup_stock(symbol):
    url = "{endpoint}/{symbol}".format(endpoint=STOCK_PRICE_URL, symbol=symbol)
    app.logger.debug(url)
    return get_request(url)


# The main web page.
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/healthz")
def health():
    app.logger.debug("health check")
    return "ok"


@app.route("/stock/<symbol>")
def stock(symbol):
    return lookup_stock(symbol)


@app.route("/weather/<city>")
def weather(city):
    return lookup_weather(city)


if __name__ == "__main__":
    formatter = logging.Formatter(
        "%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.getLevelName(LOG_LEVEL))
    app.run(host="0.0.0.0", port=PORT)
