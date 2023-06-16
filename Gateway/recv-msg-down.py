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
    euid = data[4:12].hex()
    print(euid)
    if (euid == "aa555adcdba823bd"):
      sock.sendto(data, (UDP_IP_GATEWAY, UDP_PORT_IN))
