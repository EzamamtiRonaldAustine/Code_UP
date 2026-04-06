# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This is a sample for a weather fulfillment webhook for an Dialogflow agent
This is meant to be used with the sample weather agent for Dialogflow, located at
https://console.dialogflow.com/api-client/#/agent//prebuiltAgents/Weather

This sample uses the WWO Weather Forecast API and requires an WWO API key
Get a WWO API key here: https://developer.worldweatheronline.com/api/
"""

import json
import logging

from flask import Flask, request, make_response, jsonify

from forecast import Forecast, ForecastError, validate_params

app = Flask(__name__)
# Ensure the Flask logger is configured consistently for a production-like environment.
app.logger.setLevel(logging.INFO)
log = app.logger


@app.route('/', methods=['POST'])
def webhook():
    """Handle Dialogflow webhook requests."""

    req = request.get_json(silent=True, force=True)
    if not isinstance(req, dict):
        log.error("Invalid JSON payload: %s", request.data)
        return make_response(
            jsonify({'fulfillmentText': "Sorry, I couldn't understand the request."})
        )

    query_result = req.get('queryResult') or {}
    action = query_result.get('action')
    if not action:
        log.error("Missing action in request: %s", req)
        return make_response(
            jsonify({'fulfillmentText': "Sorry, I couldn't determine the action."})
        )

    handlers = {
        'weather': weather,
        'weather.activity': weather_activity,
        'weather.condition': weather_condition,
        'weather.outfit': weather_outfit,
        'weather.temperature': weather_temperature,
    }

    handler = handlers.get(action)
    if not handler:
        log.error("Unexpected action: %s", action)
        return make_response(
            jsonify({'fulfillmentText': "Sorry, I don't know how to do that."})
        )

    try:
        res = handler(req)
    except ForecastError:
        log.exception("ForecastError while processing action: %s", action)
        res = "Sorry, I couldn't retrieve the weather right now. Please try again later."
    except Exception:
        log.exception("Unexpected error while processing action: %s", action)
        res = "Sorry, something went wrong. Please try again later."

    log.info("Action: %s; Response: %s", action, res)
    return make_response(jsonify({'fulfillmentText': res}))


def weather(req):
    """Return a text response that describes the weather.

    This is the handler for the "weather" action.
    """

    parameters = req.get('queryResult', {}).get('parameters', {})
    log.debug('Dialogflow parameters: %s', json.dumps(parameters, indent=2))

    # validate request parameters, return an error if there are issues
    error, forecast_params = validate_params(parameters)
    if error:
        log.warning('Validation error: %s; parameters: %s', error, parameters)
        return error

    # create a forecast object which retrieves the forecast from a external API
    try:
        forecast = Forecast(forecast_params)
    except ForecastError as error:
        log.exception('Failed to create Forecast object for params: %s', forecast_params)
        return 'Sorry, I could not retrieve the weather right now. Please try again later.'

    # If the user requests a datetime period (a date/time range), get the response
    if forecast.datetime_start and forecast.datetime_end:
        response = forecast.get_datetime_period_response()
    # If the user requests a specific datetime, get the response
    elif forecast.datetime_start:
        response = forecast.get_datetime_response()
    # If the user doesn't request a date in the request get current conditions
    else:
        response = forecast.get_current_response()

    return response


def weather_activity(req):
    """Returns a string containing text with a response to the user
    with a indication if the activity provided is appropriate for the
    current weather or a prompt for more information

    Takes a city, activity and (optional) dates
    uses the template responses found in weather_responses.py as templates
    and the activities listed in weather_entities.py
    """

    # validate request parameters, return an error if there are issues
    error, forecast_params = validate_params(req['queryResult']['parameters'])
    if error:
        return error

    # Check to make sure there is a activity, if not return an error
    if not forecast_params['activity']:
        return 'What activity were you thinking of doing?'

    # create a forecast object which retrieves the forecast from a external API
    try:
        forecast = Forecast(forecast_params)
    except ForecastError as error:
        log.exception('Failed to create Forecast object for activity query: %s', forecast_params)
        return 'Sorry, I could not retrieve the weather right now. Please try again later.'

    return forecast.get_activity_response()


def weather_condition(req):
    """Returns a string containing a human-readable response to the user
    with the probability of the provided weather condition occurring
    or a prompt for more information

    Takes a city, condition and (optional) dates
    uses the template responses found in weather_responses.py as templates
    and the conditions listed in weather_entities.py
    """

    # validate request parameters, return an error if there are issues
    error, forecast_params = validate_params(req['queryResult']['parameters'])
    if error:
        return error

    # Check to make sure there is a activity, if not return an error
    if not forecast_params['condition']:
        return 'What weather condition would you like to check?'

    # create a forecast object which retrieves the forecast from a external API
    try:
        forecast = Forecast(forecast_params)
    except ForecastError as error:
        log.exception('Failed to create Forecast object for condition query: %s', forecast_params)
        return 'Sorry, I could not retrieve the weather right now. Please try again later.'

    return forecast.get_condition_response()


def weather_outfit(req):
    """Returns a string containing text with a response to the user
    with a indication if the outfit provided is appropriate for the
    current weather or a prompt for more information

    Takes a city, outfit and (optional) dates
    uses the template responses found in weather_responses.py as templates
    and the outfits listed in weather_entities.py
    """

    # validate request parameters, return an error if there are issues
    error, forecast_params = validate_params(req['queryResult']['parameters'])
    if error:
        return error

    # Validate that there are the required parameters to retrieve a forecast
    if not forecast_params['outfit']:
        return 'What are you planning on wearing?'

    # create a forecast object which retrieves the forecast from a external API
    try:
        forecast = Forecast(forecast_params)
    except ForecastError as error:
        log.exception('Failed to create Forecast object for outfit query: %s', forecast_params)
        return 'Sorry, I could not retrieve the weather right now. Please try again later.'

    return forecast.get_outfit_response()


def weather_temperature(req):
    """Returns a string containing text with a response to the user
    with a indication if temperature provided is consisting with the
    current weather or a prompt for more information

    Takes a city, temperature and (optional) dates.  Temperature ranges for
    hot, cold, chilly and warm can be configured in config.py
    uses the template responses found in weather_responses.py as templates
    """

    parameters = req['queryResult']['parameters']

    # validate request parameters, return an error if there are issues
    error, forecast_params = validate_params(parameters)
    if error:
        return error

    # If the user didn't specify a temperature, get the weather for them
    if not forecast_params['temperature']:
        return weather(req)

    # create a forecast object which retrieves the forecast from a external API
    try:
        forecast = Forecast(forecast_params)
    except ForecastError as error:
        log.exception('Failed to create Forecast object for temperature query: %s', forecast_params)
        return 'Sorry, I could not retrieve the weather right now. Please try again later.'

    return forecast.get_temperature_response()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
