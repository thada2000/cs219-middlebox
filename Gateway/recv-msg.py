import socket
import json
import base64
import time

UDP_IP_IN = "45.32.82.27"
UDP_PORT_IN = 12345

UDP_PORT_GW1 = 12346
UDP_PORT_GW2 = 12347
UDP_PORT_GW3 = 12348

UDP_IP_GATEWAY = "131.179.85.144"
UDP_PORT_GATEWAY = 1700


UDP_IP_OUT = "219proj.nam1.cloud.thethings.industries"

UDP_IP_OUT_2 = "ec2-184-169-210-18.us-west-1.compute.amazonaws.com"
UDP_PORT_OUT = 1700

UDP_REAL_GW_SRC_PORT = 50279
UDP_REAL_GW_SRC_PORT2 = 50822

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP_IN, UDP_PORT_IN))

while True:
    data, addr = sock.recvfrom(1024 * 8) # buffer size is 1024 bytes
    data = bytearray(data)
    #print("received message: %s" % data[12:], addr)
    print("received raw data: %s" % data.hex())
    print("received hex data: %s" % data.hex())

    if (addr[0] == UDP_IP_GATEWAY):

        if len(data) > 12:
            payload = json.loads(data[12:])
            mismatch = False

            if 'rxpk' in payload:
                for item in payload['rxpk']:
                    if item['crc'] != item['crc_calc']:
                        mismatch = True
                if mismatch:
                    continue
                    
                print("Sending to the fake gateways")
                print(data[0:12])
                #AA555ADCDBA824BD
                data[10] = 0x24
                sock.sendto(data, (UDP_IP_IN, UDP_PORT_GW1))

                data[10] = 0x22
                sock.sendto(data, (UDP_IP_IN, UDP_PORT_GW2))

                data[10] = 0x25
                sock.sendto(data, (UDP_IP_IN, UDP_PORT_GW3))