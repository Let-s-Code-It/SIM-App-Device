from threading import Thread

from flask import Flask, request, render_template, url_for, redirect, url_for, json, session

import time

from datetime import datetime

from App.SocketClient import SocketClient

from App.Reader import GetReader

from App.SQL import SQL

from App.SocketClient import SocketClient

from App.LaunchArguments import LaunchArguments

import os

import json

import serial.tools.list_ports

from App.Device import Device

app = Flask(__name__, template_folder='../Assets/Templates')

app.secret_key = 'super secret key ' + ( datetime.today().strftime('%Y-%m-%d %H:%M:%S') if LaunchArguments.authorization > 1 else "" )

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.context_processor
def inject_stage_and_region():
    return {
        'version': {'tag':'2.0'},
        'endpoint': request.endpoint
    }


@app.before_request
def check_session():
    if LaunchArguments.authorization > 0:
        if not session.get("legit"):
            if request.endpoint is 'json_data':
                d = {
                    "not_logged": True
                }
                return app.response_class(
                    response=json.dumps(d),
                    status=401,
                    mimetype='application/json'
                )
            elif request.endpoint is not 'login':
                return redirect(url_for('login'))


@app.route("/login", methods = ["GET", "POST"])
def login():

    if LaunchArguments.authorization == 0:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if request.form['password'] == LaunchArguments.password:
            session['legit'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Wrong password!")    
    else:
        return render_template('login.html')

@app.route("/", methods = ["GET"])
def index():
    return render_template('index.html')

@app.route("/controller_configuration", methods = ["GET", "POST"])
def controller_configuration():
    if request.method == 'POST':
        
        SocketClient.UpdateLoginKey(request.form["unique_login_key"])
        
        if "address" in request.form:
            SocketClient.UpdateAddress(request.form["address"])

        SocketClient.Reload() #TODO: ponownie połączyć socket

        return redirect(url_for('index'))
    else:
        return render_template('controller_configuration.html', address=SQL.Get("socket_address"))


@app.route('/send_sms', methods = ['GET', 'POST'])
def send_sms():

    if request.method == 'POST':
        
        if GetReader() != None:
            GetReader().protocol.send_sms(request.form['number'], request.form['text'])
        
        return redirect(url_for('index'))
    else:
        return render_template('send_sms.html')


@app.route('/sms_list', methods = ['GET'])
def sms_list():
    return render_template('sms_list.html')


@app.route('/json_data', methods = ['GET'])
def json_data():
    d = {
        "serial_connected": True if GetReader() != None else False,
        "socket_connected": SocketClient.IsConnected(),
        "socket_logged" : SocketClient.Logged,
        "device_adopted": Device.Adopted,



        "time_now" : datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
        "sms_list": SQL.select("SELECT * FROM sms ORDER by row_id DESC limit ?", [10])
    }
    return app.response_class(
        response=json.dumps(d),
        status=200,
        mimetype='application/json'
    )



@app.route('/config', methods = ['GET', 'POST'])
def config():

    if request.method == 'POST':
        
        for port in serial.tools.list_ports.comports():
            if port[0] == request.form['serial_port']:
                SQL.Set('port_name', port[0])
                SQL.Set('port_friendly_name', port[1])
                #TODO: Po zmianie portu zresetowac polaczenie serial.
        
        return redirect(url_for('index'))
    else:
        apn_mms_templates = []
        try:
            apn_mms_templates = json.loads(open("Assets/apn_mms_templates.json", "r").read() if os.path.exists("Assets/apn_mms_templates.json") else "[]")
        except ValueError as e:
            pass

        return render_template('config.html', apn_mms_inputs=[
                {"title": "Friendly APN name", "name": "friendly_apn_mms_name"},
                {"title": "URL MMS Center", "name": "url_mms_center"},
                {"title": "IP MMS Proxy", "name": "ip_mms_proxy"},
                {"title": "PORT MMS Proxy", "name": "port_mms_proxy"},
                {"title": "APN Name", "name": "apn_name"},
            ], apn_mms_templates=apn_mms_templates, ports=serial.tools.list_ports.comports(), target_port=SQL.Get("port_name"))






def WebStart():
    try:
        app.run(debug=False, host='0.0.0.0', port=LaunchArguments.webport)
    except:
        print("WebServer start problem!")


WebThread = Thread(target=WebStart)