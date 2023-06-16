import socket

UDP_IP_IN = "45.32.82.27"
UDP_PORT_IN = 12345

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
    #print("received message: %s" % data[12:], addr)
    print("received header: %s" % data[:12].hex())
    if (addr[0] == UDP_IP_GATEWAY):
        print("Sending to the cloud")
        sock.sendto(data, (UDP_IP_OUT, 1700))
        #AA555ADCDBA824BD
        data[10] = 0x24
        print("new header: %s" % data[:12].hex())
        sock.sendto(data, (UDP_IP_OUT, 1700))
    else:
        print("Sending back to the gateway")
        sock.sendto(data, (UDP_IP_GATEWAY, 12345))