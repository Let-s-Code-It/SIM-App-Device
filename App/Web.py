from threading import Thread

from flask import Flask, request, render_template, url_for, redirect, url_for, json, session, send_from_directory

import time

from datetime import datetime

from .SocketClient import SocketClient

from .Reader import GetReader

from .SQL import SQL

from .SocketClient import SocketClient

from .LaunchArguments import LaunchArguments

import os

import json

import serial.tools.list_ports

from .Device import Device

from .Utils.RestartProgram import RestartProgram

from .Utils.modification_date import modification_date

from .APN import apn_configured_check, apn_keys_list, get_apn_data

from ..Config import __APPLICATION_DATA__,  __APPLICATION_PATH__, __VERSION__, __PYPI_PACKAGE_NAME__, __AUTHOR_PAGE__, __HOW_TO_UPDATE_PAGE__

app = Flask(
    __name__, 
    template_folder=__APPLICATION_PATH__+'/Assets/Templates', 
    static_url_path='/static'
)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


from .Logger import logger

restart_required = False

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(__APPLICATION_PATH__+'/Assets/static',
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.context_processor
def inject_stage_and_region():
    return {
        'version': {'tag':__VERSION__},
        'endpoint': request.endpoint,
        'pypi_package_name': __PYPI_PACKAGE_NAME__,
        'author_page': __AUTHOR_PAGE__,
        'how_to_update_page': __HOW_TO_UPDATE_PAGE__,
        'restart_required': restart_required,
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

        SocketClient.Reload()

        return redirect(url_for('index'))
    else:
        return render_template('controller_configuration.html', 
        address=SQL.Get("socket_address"), 
        socket_logged = 'true' if SocketClient.Logged else 'false',
        socket_unique_auth_key=SQL.Get("socket_unique_auth_key") if SQL.Get("socket_unique_auth_key") else  SQL.Get("socket_unique_login_key"),
        )


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
        "apn_configured": apn_configured_check(),
        "connection_confirmed": GetReader().protocol.connection_confirmed if GetReader() != None else False,
        "sim_card_detected": GetReader().protocol.simCardDetected if GetReader() != None else False,
        "pin_code_required": GetReader().protocol.PinCodeRequired if GetReader() != None else False,
        "serial_ready": GetReader().protocol.Ready if GetReader() != None else False,
        "availablePinAttempts": GetReader().protocol.availablePinAttempts if GetReader() != None else False,


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

        for apn_key in apn_keys_list:
            if request.form[apn_key]:
                SQL.Set(apn_key, request.form[apn_key])

        global restart_required
        
        if GetReader() != None:
            restart_required = True
        
        return redirect(url_for('index'))
    else:
        apn_mms_templates = []
        try:
            apn_mms_templates = json.loads(open(__APPLICATION_PATH__ + "/Assets/apn_mms_templates.json", "r").read() if os.path.exists( __APPLICATION_PATH__ + "/Assets/apn_mms_templates.json") else "[]")
        except ValueError as e:
            pass

        return render_template('config.html', apn_mms_inputs=[
                {"title": "Friendly APN name", "name": "friendly_apn_mms_name"},
                {"title": "URL MMS Center", "name": "url_mms_center"},
                {"title": "IP MMS Proxy", "name": "ip_mms_proxy"},
                {"title": "PORT MMS Proxy", "name": "port_mms_proxy"},
                {"title": "APN Name", "name": "apn_name"},
            ], 
            apn_mms_templates=apn_mms_templates, 
            ports=serial.tools.list_ports.comports(), 
            target_port=SQL.Get("port_name"),
            apn_data=get_apn_data()
        )


@app.route('/debug_options', methods = ['GET'])
def debug_options():
    
    last_error_path = __APPLICATION_DATA__ + "/errors/last.txt"
    if os.path.exists(last_error_path):
        f = open(last_error_path)
        last_error = f.read()
        f.close()
    else:
        last_error = None

    return render_template('debug_options.html', last_error=last_error, last_error_crated_time=modification_date(last_error_path))

@app.route('/debug_options', methods = ['POST'])
def debug_options_post():
    if request.form['submit'] == 'shutdown':
        os._exit(0)
    elif request.form['submit'] == 'reboot':
        #RestartProgram()
        GetReader().kill()

    return redirect(url_for('index'))

@app.route('/debug/comands_in_queue', methods = ['GET', 'POSt'])
def commands_in_queue():
    added_command = ''
    if request.method == 'POST':
        added_command = request.form['new_command']
        GetReader().protocol.write(added_command)
    return render_template('commands_in_queue.html', added_command=added_command)
@app.route('/debug/comands_in_queue/json', methods = ['GET'])
def commands_in_queue_json():
    return list(map(lambda x: x.value, GetReader().protocol.queue))

def WebStart():
    try:
        time.sleep(1)
        logger.debug("launch arguments when web start:")
        logger.debug(LaunchArguments)
        app.secret_key = 'super secret key ' + ( datetime.today().strftime('%Y-%m-%d %H:%M:%S') if LaunchArguments.authorization > 1 else "" )
        app.run(debug=False, host='0.0.0.0', port=LaunchArguments.webport)
    except:
        logger.debug("WebServer start problem!")

@app.route('/pin', methods = ['GET','POST'])
def pin():
    ready = GetReader() != None
    if ready and request.method == 'POST':
        if request.form['pin_code']:
            GetReader().protocol.SavePinCode(request.form['pin_code'])
            return redirect(url_for('index'))

    return render_template('pin.html', ready=ready)


WebThread = Thread(target=WebStart)