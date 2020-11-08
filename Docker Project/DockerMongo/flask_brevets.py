"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""
import os
import flask
from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY
client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
db = client.tododb

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    app.logger.debug("km={}".format(km))

    distance = request.args.get('distance',type=int)
    date = request.args.get('date',type=str)
    time = request.args.get('time',type=str)

    # FIXME: These probably aren't the right open and close times
    # and brevets may be longer than 200km
    timeFormat = date + ' ' + time + ':00'
    timeInput = arrow.get(timeFormat,'YYYY-MM-DD HH:mm:ss')
    timeInput = timeInput.replace(tzinfo='US/Pacific')
    timeInput = timeInput.isoformat()
    
    open_time = acp_times.open_time(km, distance, timeInput)
    close_time = acp_times.close_time(km, distance, timeInput)
    result = {"open": open_time, "close": close_time}

    return flask.jsonify(result=result)

@app.route('/todo', methods=['POST'])
def todo():
    _items = db.tododb.find()
    items = [item for item in _items]
    
    #if empty send error
    if items == []:
        return render_template('404.html')

    return render_template('todo.html', items=items)

@app.route('/new', methods=['POST'])
def new():

    #delete the previous 'display'                                                                               
    db.tododb.delete_many({})

    #get the lists and make another list to take the values
    kmT = request.form.getlist("km")
    openT = request.form.getlist("open")
    closeT = request.form.getlist("close")
    openL = []
    closeL = []
    kmL = []

    #we only need the non empty data from the list
    for i in openT:
        if i != '':
            openL.append(i)
    for i in closeT:
        if i != '':
            closeL.append(i)
    for i in kmT:
        if i != '':
            kmL.append(i)

    #will be bunch of items for the tofo.html to get
    #which will also help to seperate lines
    for i in range(len(openL)):
        item_doc = {
            'kming': kmL[i],
            'opening': openL[i],
            'closing': closeL[i]
            }
        db.tododb.insert_one(item_doc)

    #checks if nothing is submitted
    if kmL == []:
        return render_template('404.html')
    return redirect(url_for('index'))
#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
#    print("Opening for global access on port {}".format(CONFIG.PORT))
 #   app.run(port=CONFIG.PORT, host="0.0.0.0")
