Quanttp 2 Entropy Server
========================

_based on [quanttp](https://github.com/awasisto/quanttp) by [Andika Wasisto](https://www.wasisto.com/)_

An HTTP API that wraps [ComScire quantum random number generator API](https://comscire.com/downloads/qwqngdoc/).

Running
-------

1. Install ComScire driver from https://comscire.com/downloads/
2. Run the following commands
   ```
   pip3 install -r requirements.txt
   python3 -m quanttp <servername> <port>
   ```

Usage Example
-------------

### REST API

	http://localhost:<port>/api/devices
	< QWR4E002,QWR4E001

	http://localhost:<port>/api/randint32?deviceId=QWR4E001
	< -1741405968

	http://localhost:<port>/api/randuniform?deviceId=QWR4E001
	< 0.20340009994

	http://localhost:<port>/api/randnormal?deviceId=QWR4E001
	< 1.02206840644

	http://localhost:<port>/api/randbytes?length=16&deviceId=QWR4E001
	< ���E��s_�b����G�

### REST JSON API

	http://localhost:<port>/api/json/randint32?length=3&deviceId=QWR4E001
	< {"devices":['QWR4E002|MED100KX8 100 kHz', 'QWR4E001|MED100KX8 100 kHz']}

	http://localhost:<port>/api/json/randint32?length=3&deviceId=QWR4E001
	< {"server": "<servername>", "type": "string", "format": "int32", "length": 3, "data": [1524492492, -1194151004, 1365408501], "success": "true"}

	http://localhost:<port>/api/json/randuniform?length=2&deviceId=QWR4E001
	< {"server": "<servername>", "type": "string", "format": "uniform", "length": 2, "data": [0.07230273403292031, 0.733570206706375], "success": "true"}

	http://localhost:<port>/api/json/randnormal?length=1&deviceId=QWR4E001
	< {"server": "<servername>", "type": "string", "format": "normal", "length": 1, "data": [0.6430985466029758], "success": "true"}

	http://localhost:<port>/api/json/randhex?length=2&size=5&deviceId=QWR4E001
	< {"server": "<servername>", "type": "string", "format": "hex", "length": 2, "size": 5, "data": ["b90e1b01bc", "b59374fc0e"], "success": "true"}

### WebSocket API
	
	ws://localhost:<port>/ws
	> RANDINT32
	< 585865374

	> RANDUNIFORM
	< 0.70137183786

	> RANDNORMAL
	< -1.6120135370

	> RANDBYTES 32
	< �����9L).�!:���@Nh������d����_q�

	> SUBSCRIBEINT32
	< 1361330636
	< -604581511
	< 1510923919
	< ...
	> UNSUBSCRIBE
	< UNSUBSCRIBED

	> SUBSCRIBEUNIFORM
	< 0.54623951886
	< 0.67567578799
	< 0.09746421443
	< ...
	> UNSUBSCRIBE
	< UNSUBSCRIBED

	> SUBSCRIBENORMAL
	< -1.6120135370
	< 0.02943381135
	< -0.9883458007
	< ...
	> UNSUBSCRIBE
	< UNSUBSCRIBED

	> SUBSCRIBEBYTES 8
	< �K����{�
	< I]������
	< ���.�t�U
	< ...
	> UNSUBSCRIBE
	< UNSUBSCRIBED

License
-------

    Copyright (c) 2020 Andika Wasisto
	Modified by randogoth / Randonauts Co.
	Modified by soliax / fp2.dev

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
