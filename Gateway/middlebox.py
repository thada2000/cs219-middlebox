import socket
import json
import time
import base64
from collections import defaultdict

def majority_voting(byte_array_list):
    buffer1 = byte_array_list[0]
    buffer2 = byte_array_list[1]
    buffer3 = byte_array_list[2]

    if len(buffer1) != len(buffer2) or len(buffer2) != len(buffer3):
        raise ValueError("All buffers must be the same length")

    result = bytearray(len(buffer1))

    for i in range(len(buffer1)):
        for bit in range(8):
            mask = 1 << bit

            count_ones = 0
            if buffer1[i] & mask != 0:
                count_ones += 1
            if buffer2[i] & mask != 0:
                count_ones += 1
            if buffer3[i] & mask != 0:
                count_ones += 1

            if count_ones >= 2:
                result[i] |= mask  # Majority of bits are 1, set bit to 1

    return result

UDP_IP_IN = "45.32.82.27"
UDP_PORT_IN = 12349

UDP_IP_OUT = "219proj.nam1.cloud.thethings.industries"
UDP_PORT_OUT = 1700

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP_IN, UDP_PORT_IN))

epoch_change = False
max_tmst = 0
current_time = int(time.time())

packet_buffer = defaultdict(list)

previous_time = int(time.time())

error_packet_count = dict() # euid: [error_count, total_count]

prev_time_dump = int(time.time())

name = "aa555adcdba827bd" # to be registered on the TTN

with open("gateways.json", "r") as f:
    gateways = json.load(f)

while True:
    data, addr = sock.recvfrom(1024 * 8) # buffer size is 1024 bytes
    prefix = data[0:4].hex()
    euid = data[4:12].hex()

    if euid not in gateways or gateways[euid]['active']=="false":
        continue

    if len(data) <= 12:
        sock.sendto(data, (UDP_PORT_OUT, UDP_IP_OUT))

    data = bytearray(data)
    
    #print("received message: %s" % data[12:], addr)
    # print("received raw data: %s" % data)
    

    payload = json.loads(data[12:])
    current_time = int(time.time())
    if euid not in error_packet_count:
        error_packet_count[euid] = [0, 0]
    error_packet_count[euid][1] += 1 # total count
    error = False

    for p in payload['rxpk']:
        if p['crc_match'] != 1:
            error = True
        packet_buffer[(p['tmst'], p['mid'])].append((p, current_time, prefix))
        max_tmst = max(max_tmst, p['tmst'])
    
    # count packet errors
    if error:
        error_packet_count[euid][0] += 1

    if current_time >= previous_time + 3:
        previous_time = current_time
        items = list(packet_buffer.items())
        for key, data in items:
            (tmst, mid) = key
            min_tmst = min(data, key=lambda x: x[1])[1]
            if (current_time - min_tmst < 3):
                continue

            correct_data = None
            for p, _, _ in data:
                #we need to print this as hello world 
                # print(p["data"])
                # print(base64.b64decode(p["data"]))
                print('RECEIVED DATA FROM GATEWAY', base64.b64decode(p["data"]))
                if p["crc_match"] == 1:
                    correct_data = p["data"]
                    print('FIXED BY CRC')
                    #break

            if correct_data is None:
                if len(data) > 2:
                    raw_payload = [bytearray(base64.b64decode(d[0]['data'])) for d in data]
                    # print('incorrected data', raw_payload)
                    correct_data = majority_voting(raw_payload)
                    correct_data = base64.b64encode(correct_data).decode('utf-8')
                    print('FIXED BY MAJORITY VOTING')
                else:
                    print("MAJORITY VOTING FAIL : The number of gateways is not enough")

            if correct_data is not None:
                print('CORRECTED DATA ', base64.b64decode(correct_data) )
                #print("Fixed RESULT:", correct_data)
                for p, _, prefix in data:
                    header = bytes.fromhex(prefix+name)
                    p["data"] = correct_data
                    json_str = json.dumps({"rxpk":[p]})
                    packet = header + bytearray(json_str, encoding='utf-8')
                    sock.sendto(packet, (UDP_IP_OUT, 1700))
                    # print('Corrected packet', packet)
                    break
            


            del packet_buffer[key]
            #sock.sendto(data, (UDP_PORT_OUT, UDP_IP_OUT))
    
    # dump to a json file every 10 seconds
    if current_time >= prev_time_dump + 10:
        prev_time_dump  = current_time

        with open("gateways.json", "r") as f:
            gateways = json.load(f)

        with open("error_metrics.json", "w") as file:
            json.dump(error_packet_count, file)
            
    