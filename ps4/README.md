# Wireless Problem set 4: Part 2
The code in this directory relates to the second part of problem set 4.

The purpose of this code is to interact with a temperature sensor attached to
a LinkIt Smart 7688 Duo.  Climate information gets passed all the way up to the
server over the network.

## Running
To run this program.  You will first need to set up the LinkIt using the
Arduino IDE.  Information on how to do this is located at
https://labs.mediatek.com/fileMedia/download/4ef033b8-80ca-4cdb-9ad6-1c23836c63de.
When this is done, use the arduino IDE to upload `dht_sampler.ino` to the linkit.
The LinkIt should have a DHT11 sensor with the data pin attached to D12.  It should
also have an LED attached to D11.

Next generate a certificate and key for the SSL connection.  You can do this
using `openssl req -new -x509 -days 365 -nodes -out server.cert -keyout server.key`.
The certificate must be called server.cert and the key must be called server.key.
A sample certificate and key are included for convenience.

Next, start `temper_server.py` from the command line. The certificate and key
must be in the same directory as the server script.

Next, upload `temp_catcher.py` and the certificate to the LinkIt using SSH/SCP.
Using SSH, start `temp_catcher.py` using the IP of the server and the port
number, 1234. eg. `$ ./temp_catcher.py x.x.x.x 1234`

If everything works correctly, you should see temperature information appearing
in both the server and the catcher at roughly 2 second intervals.
