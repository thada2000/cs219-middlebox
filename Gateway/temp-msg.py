import socket
import json

UDP_IP_IN = "45.32.82.27"
UDP_PORT_IN = 12345

UDP_PORT_GW1 = 12346
UDP_PORT_GW2 = 12347
UDP_PORT_GW3 = 12348

UDP_IP_GATEWAY = "131.179.85.144"
UDP_PORT_GATEWAY = 1700


UDP_IP_OUT = "219proj.nam1.cloud.thethings.industries"
UDP_PORT_OUT = 1700

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP_IN, UDP_PORT_IN))

while True:
    data, addr = sock.recvfrom(1024 * 8) # buffer size is 1024 bytes
    data = bytearray(data)
    if len(data) > 12:
        payload = json.loads(data[12:])
        if 'rxpk' in payload:
            payload['rxpk'][0]["crc_match"] = -1
            payload['rxpk'][0].pop('crc')
            payload['rxpk'][0].pop('crc_calc')
            payload['rxpk'][0].pop('crc_match')
            # payload['rxpk'][0]["crc"] = "0xFFF0"
            # payload['rxpk'][0]["crc_calc"] = "0xFFF"
        data_string = json.dumps(payload)
        data = data[:12] + bytearray(data_string, encoding='utf-8')
     #print("received message: %s" % data[12:], addr)
    print("received raw data: %s" % data)
    print("received hex data: %s" % data.hex())

    if (addr[0] == UDP_IP_GATEWAY):
        print("Sending to the fake gateways")
        #AA555ADCDBA824BD
        data[10] = 0x24
        sock.sendto(data, (UDP_IP_OUT, UDP_PORT_OUT))

        data[10] = 0x22
        sock.sendto(data, (UDP_IP_OUT, UDP_PORT_OUT))

        data[10] = 0x25
        sock.sendto(data, (UDP_IP_OUT, UDP_PORT_OUT))