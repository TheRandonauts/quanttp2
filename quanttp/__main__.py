# Copyright (c) 2020 Andika Wasisto
# Modified by randogoth
# Modified by soliax
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import threading
import json
import socket
import requests
import base64

from flask import Flask, request, Response
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from quanttp.data.meterfeeder_wrapper import MeterFeederWrapper

app = Flask(__name__)
sockets = Sockets(app)

mf_wrapper = MeterFeederWrapper()

def main():
    # Commandline Arguments (servername, port)

    argNo = len(sys.argv) - 1

    if argNo < 2:
        print("--------------------------------------------")
        print("Please provide arguments: <servername> <port>")
        print("--------------------------------------------")
    else:
        servername = sys.argv[1]
        port = int(sys.argv[2])
        ip = requests.get('https://api.ipify.org').text
        id = str(mf_wrapper.deviceIds(False))
        print("----------------------------------------------------------------------------------------")
        print("Serving Entropy from TRNG ", id, " as pod \"", servername, "\" on http://", ip, ":", port, "/api/...", sep='')
        print("----------------------------------------------------------------------------------------")
        serve(servername, port, id)

def serve(servername, port, id):

    # Original API ----------------------------------------------

    @app.route('/api/devices')
    def devices():
        devices = str(mf_wrapper.deviceIds(False))
        return Response(devices, content_type='text/plain')

    @app.route('/api/randint32')
    def randint32():
        deviceId = request.args.get('deviceId')
        if len(deviceId) != 8:
            return Response('deviceId must be a valid 8 character serial number', status=400, content_type='text/plain')
        return Response(str(mf_wrapper.randint32(deviceId)), content_type='text/plain')

    @app.route('/api/randuniform')
    def randuniform():
        deviceId = request.args.get('deviceId')
        if len(deviceId) != 8:
            return Response('deviceId must be a valid 8 character serial number', status=400, content_type='text/plain')
        return Response(str(mf_wrapper.randuniform(deviceId)), content_type='text/plain')

    @app.route('/api/randnormal')
    def randnormal():
        deviceId = request.args.get('deviceId')
        if len(deviceId) != 8:
            return Response('deviceId must be a valid 8 character serial number', status=400, content_type='text/plain')
        return Response(str(mf_wrapper.randnormal(deviceId)), content_type='text/plain')

    @app.route('/api/randhex')
    def randhex():
        try:
            deviceId = request.args.get('deviceId')
            if len(deviceId) != 8:
                return Response('deviceId must be a valid 8 character serial number', status=400, content_type='text/plain')
            length = int(request.args.get('length'))
            if length < 1:
                return Response('length must be greater than 0', status=400, content_type='text/plain')
            return Response(mf_wrapper.randbytes(deviceId, length).hex(), content_type='text/plain')
        except (TypeError, ValueError) as e:
            return Response(str(e), status=400, content_type='text/plain')

    @app.route('/api/randbase64')
    def randbase64():
        try:
            deviceId = request.args.get('deviceId')
            if len(deviceId) != 8:
                return Response('deviceId must be a valid 8 character serial number', status=400, content_type='text/plain')
            length = int(request.args.get('length'))
            if length < 1:
                return Response('length must be greater than 0', status=400, content_type='text/plain')
            return Response(base64.b64encode(mf_wrapper.randbytes(deviceId, length)).decode('utf-8'), content_type='text/plain')
        except (TypeError, ValueError) as e:
            return Response(str(e), status=400, content_type='text/plain')


    @app.route('/api/randbytes')
    def randbytes():
        try:
            deviceId = request.args.get('deviceId')
            if len(deviceId) != 8:
                return Response('deviceId must be a valid 8 character serial number', status=400, content_type='text/plain')
            length = int(request.args.get('length'))
            if length < 1:
                return Response('length must be greater than 0', status=400, content_type='text/plain')
            return Response(mf_wrapper.randbytes(deviceId, length), content_type='application/octet-stream')
        except (TypeError, ValueError) as e:
            return Response(str(e), status=400, content_type='text/plain')

    @app.route('/api/clear')
    def clear():
        deviceId = request.args.get('deviceId')
        if len(deviceId) != 8:
            return Response('deviceId must be a valid 8 character serial number', status=400, content_type='text/plain')
        mf_wrapper.clear(deviceId)
        return Response(status=204)
        
    @app.route('/api/reset')
    def reset():
        mf_wrapper.reset()
        return Response(status=204)

    @app.route('/api/status')
    def status():
        status = "ONLINE" # TODO implement me
        return Response(json.dumps({"server" : servername, "devices": id, "status": status}), status=400, content_type='text/plain')

    # JSON API ----------------------------------------------

    @app.route('/api/json/devices')
    def devicesjson():
        devices = str(mf_wrapper.deviceIds(True))
        return Response('{"devices":'+devices+'}', content_type='application/json')

    @app.route('/api/json/randint32')
    def randjsonint32():
        try:
            deviceId = request.args.get('deviceId')
            if len(deviceId) != 8:
                return Response(json.dumps({"error": 'deviceId must be a valid 8 character serial number', "success":False}), status=400, content_type='application/json')
            status = str(mf_wrapper.status())
            length = int(request.args.get('length'))
            if length < 1:
                return Response(json.dumps({"error": 'length must be greater than 0', "success":False}), status=400, content_type='application/json')
            int32array = []
            for x in range(0, length):
                int32array.append(mf_wrapper.randint32(deviceId))
            return Response(json.dumps({"server" : servername, "device": id, "status": status, "type": "string", "format": "int32", "length":length, "data": int32array, "success":True}), content_type='application/json')
        except (TypeError, ValueError) as e:
            return Response(json.dumps({"error": str(e), "status": status, "success":False}), status=400, content_type='application/json')

    @app.route('/api/json/randuniform')
    def randjsonuniform():
        try:
            deviceId = request.args.get('deviceId')
            if len(deviceId) != 8:
                return Response(json.dumps({"error": 'deviceId must be a valid 8 character serial number', "success":False}), status=400, content_type='application/json')
            status = str(mf_wrapper.status())
            length = int(request.args.get('length'))
            if length < 1:
                return Response(json.dumps({"error": 'length must be greater than 0', "success":False}), status=400, content_type='application/json')
            uniformarray = []
            for x in range(0, length):
                uniformarray.append(mf_wrapper.randuniform(deviceId))
            return Response(json.dumps({"server" : servername, "device": id, "status": status, "type": "string", "format": "uniform", "length":length, "data": uniformarray, "success":True}), content_type='application/json')
        except (TypeError, ValueError) as e:
            return Response(json.dumps({"error": str(e), "device": id, "status": status, "success":False}), status=400, content_type='application/json')

    @app.route('/api/json/randnormal')
    def randjsonnormal():
        try:
            deviceId = request.args.get('deviceId')
            if len(deviceId) != 8:
                return Response(json.dumps({"error": 'deviceId must be a valid 8 character serial number', "success":False}), status=400, content_type='application/json')
            status = str(mf_wrapper.status())
            length = int(request.args.get('length'))
            if length < 1:
                return Response(json.dumps({"error": 'length must be greater than 0', "success":False}), status=400, content_type='application/json')
            normarray = []
            for x in range(0, length):
                normarray.append(mf_wrapper.randnormal(deviceId))
            return Response(json.dumps({"server" : servername, "device": id, "status": status, "type": "string", "format": "normal", "length":length, "data": normarray, "success":True}), content_type='application/json')
        except (TypeError, ValueError) as e:
            return Response(json.dumps({"error": str(e), "device": id, "status": status, "success":False}), status=400, content_type='application/json')

    @app.route('/api/json/randhex')
    def randjsonhex():
        try:
            deviceId = request.args.get('deviceId')
            if len(deviceId) != 8:
                return Response(json.dumps({"error": 'deviceId must be a valid 8 character serial number', "success":False}), status=400, content_type='application/json')
            status = str(mf_wrapper.status())
            length = int(request.args.get('length'))
            size = int(request.args.get('size'))
            if length < 1:
                return Response(json.dumps({"error": 'length must be greater than 0', "success":False}), status=400, content_type='application/json')
            if size < 1:
                return Response(json.dumps({"error": 'size must be greater than 0', "success":False}), status=400, content_type='application/json')
#            entropy = mf_wrapper.randbytes(size*length)
            hexarray = []
            for x in range(0, length):
                hexarray.append(mf_wrapper.randbytes(deviceId, size).hex())
#                hexarray.append(entropy[x*size:(x+1)*size].hex())
            return Response(json.dumps({"server" : servername, "device": id, "status": status, "type": "string", "format": "hex", "length":length, "size": size, "data": hexarray, "success":True}), content_type='application/json')
        except (TypeError, ValueError) as e:
            return Response(json.dumps({"error": str(e), "device": id, "status": status, "success":False}), status=400, content_type='application/json')
            
    @app.route('/api/json/randbase64')
    def randjsonbase64():
        try:
            deviceId = request.args.get('deviceId')
            if len(deviceId) != 8:
                return Response(json.dumps({"error": 'deviceId must be a valid 8 character serial number', "success":False}), status=400, content_type='application/json')
            status = str(mf_wrapper.status())
            length = int(request.args.get('length'))
            size = int(request.args.get('size'))
            if length < 1:
                return Response(json.dumps({"error": 'length must be greater than 0', "success":False}), status=400, content_type='application/json')
            if size < 1:
                return Response(json.dumps({"error": 'size must be greater than 0', "success":False}), status=400, content_type='application/json')
#            entropy = mf_wrapper.randbytes(size*length)
            basearray = []
            for x in range(0, length):
                basearray.append(base64.b64encode(mf_wrapper.randbytes(deviceId, size)).decode('utf-8'))
#                basearray.append(base64.b64encode(entropy[x*size:(x+1)*size]).decode('utf-8'))
            return Response(json.dumps({"server" : servername, "device": id, "status": status, "type": "string", "format": "base64", "length":length, "size": size, "data": basearray, "success":True}), content_type='application/json')
        except (TypeError, ValueError) as e:
            return Response(json.dumps({"error": str(e), "device": id, "status": status, "success":False}), status=400, content_type='application/json')
        

    # Websockets ----------------------------------------------

    @sockets.route('/ws')
    def ws(websocket):
        subscribed = [False]
        while not websocket.closed:
            threading.Thread(target=handle_ws_message, args=(websocket.receive(), websocket, subscribed)).start()

    def handle_ws_message(message, websocket, subscribed):
        try:
            split_message = message.strip().upper().split()
            if split_message[0] == 'DEVICES':
                websocket.send(str(mf_wrapper.deviceIds(False)))
            elif split_message[0] == 'RANDINT32':
                deviceId = split_message[1]
                if len(deviceId) != 8:
                    raise ValueError()
                websocket.send(str(mf_wrapper.randint32(deviceId)))
            elif split_message[0] == 'RANDUNIFORM':
                deviceId = split_message[1]
                if len(deviceId) != 8:
                    raise ValueError()
                websocket.send(str(mf_wrapper.randuniform(deviceId)))
            elif split_message[0] == 'RANDNORMAL':
                deviceId = split_message[1]
                if len(deviceId) != 8:
                    raise ValueError()
                websocket.send(str(mf_wrapper.randnormal(deviceId)))
            elif split_message[0] == 'RANDBYTES':
                deviceId = split_message[1]
                if len(deviceId) != 8:
                    raise ValueError()
                length = int(split_message[2])
                if length < 1:
                    raise ValueError()
                websocket.send(mf_wrapper.randbytes(deviceId, length))
            elif split_message[0] == 'SUBSCRIBEINT32':
                deviceId = split_message[1]
                if len(deviceId) != 8:
                    raise ValueError()
                if not subscribed[0]:
                    subscribed[0] = True
                    while subscribed[0] and not websocket.closed:
                        websocket.send(str(mf_wrapper.randint32(deviceId)))
            elif split_message[0] == 'SUBSCRIBEUNIFORM':
                deviceId = split_message[1]
                if len(deviceId) != 8:
                    raise ValueError()
                if not subscribed[0]:
                    subscribed[0] = True
                    while subscribed[0] and not websocket.closed:
                        websocket.send(str(mf_wrapper.randuniform(deviceId)))
            elif split_message[0] == 'SUBSCRIBENORMAL':
                deviceId = split_message[1]
                if len(deviceId) != 8:
                    raise ValueError()
                if not subscribed[0]:
                    subscribed[0] = True
                    while subscribed[0] and not websocket.closed:
                        websocket.send(str(mf_wrapper.randnormal(deviceId)))
            elif split_message[0] == 'SUBSCRIBEBYTES':
                deviceId = split_message[1]
                if len(deviceId) != 8:
                    raise ValueError()
                chunk = int(split_message[2])
                if chunk < 1:
                    raise ValueError()
                if not subscribed[0]:
                    subscribed[0] = True
                    while subscribed[0] and not websocket.closed:
                        websocket.send(mf_wrapper.randbytes(deviceId, chunk))
            elif split_message[0] == 'SUBSCRIBEHEX':
                deviceId = split_message[1]
                if len(deviceId) != 8:
                    raise ValueError()
                chunk = int(split_message[2])
                if chunk < 1:
                    raise ValueError()
                if not subscribed[0]:
                    subscribed[0] = True
                    while subscribed[0] and not websocket.closed:
                        websocket.send(mf_wrapper.randbytes(deviceId, chunk).hex())
            elif split_message[0] == 'UNSUBSCRIBE':
                subscribed[0] = False
                websocket.send('UNSUBSCRIBED')
            elif split_message[0] == 'CLEAR':
                deviceId = split_message[1]
                if len(deviceId) != 8:
                    raise ValueError()
                mf_wrapper.clear(deviceId)
        except (IndexError, ValueError, BlockingIOError):
            pass
        except Exception as e:
            websocket.close(code=1011, message=str(e))

    @app.errorhandler(Exception)
    def handle_exception(e):
        return Response(e.description, status=e.code, content_type='text/plain')

    server = pywsgi.WSGIServer(('0.0.0.0', port), application=app, handler_class=WebSocketHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()