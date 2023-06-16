import socket
import argparse
import json
import random
import base64
import time

UDP_IP_IN = "45.32.82.27"
UDP_DST_PORT_MIDDLEBOX=12349
parser = argparse.ArgumentParser(description='argument parser')

parser.add_argument('--port_no', '-p', type=int)
parser.add_argument('--error_rate', '-e', type=float)
parser.add_argument('--packet_error_rate', '-pe', type=float)
parser.add_argument('--drop_rate', '-d', type=float)
args = parser.parse_args()

error_rate = args.error_rate
drop_rate = args.drop_rate
packet_error_rate = args.packet_error_rate

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP_IN, args.port_no))

def flip_bit(byte, index):
    mask = 1 << index
    return byte ^ mask

def weighted_sampler(error_rate): # or drop rate
    outcomes = [True] * int(error_rate * 100)  + [False] * int((1 - error_rate ) * 100)
    result = random.choice(outcomes)

    return result

while True:
    data, addr = sock.recvfrom(1024 * 8)
    current_time = int(time.time())
    msg_len = len(data)
    if msg_len == 12:
        print('Packet header: ', data)
        sock.sendto(data, (UDP_IP_IN, UDP_DST_PORT_MIDDLEBOX))
        continue
    
    header = bytearray(data)[:12]
    data = bytearray(data)[12:]

    # Decode the byte array into a string
    string_data = data.decode('utf-8')

    # Parse the string into a JSON object
    json_data = json.loads(string_data)

    # Access the JSON data
    # print(json_data)  # Output: value
    # print(json_data)
    if 'data' not in json_data['rxpk'][0]:
        sock.sendto(data, (UDP_IP_IN, UDP_DST_PORT_MIDDLEBOX))
        continue

    raw_payload = json_data['rxpk'][0]['data']
    # print("base64 before", raw_payload, len(raw_payload))
    raw_payload  = base64.b64decode(raw_payload)
    # print("byte array before", raw_payload, len(raw_payload))

    # introduce packet errors and (packet drops)
    if_packet_error = weighted_sampler(packet_error_rate)
    # if_packet_dropped = weighted_sampler(drop_rate)
    print("Error: ", if_packet_error)
    if if_packet_error:
        # apply byte errors
        error_indices = random.sample(range(len(raw_payload)), int(len(raw_payload) * error_rate))
        # print('changed_indices', error_indices)

        #just for test purposes we do not need to add this here for normal runs.
        #or packet_error_rate > 0:
        if len(error_indices) > 0 or packet_error_rate > 0:
            raw_payload_arr = bytearray(raw_payload)
            # flip a random bit in a byte sampled
            for idx in error_indices:
                flipped_byte = flip_bit(raw_payload_arr[idx], random.randint(0, 7))
                # print("flipped_byte ", str(flipped_byte))
                raw_payload_arr[idx] = flipped_byte

            # print("byte array after", raw_payload_arr, len(raw_payload))
            raw_payload = base64.b64encode(raw_payload_arr).decode('utf-8')
            json_data['rxpk'][0]['crc_match'] = 0
            json_data['rxpk'][0]['data'] = raw_payload 
            json_str = json.dumps(json_data)
            data = header + bytearray(json_str, encoding='utf-8')
            print('concatnated data: ', data)
            # print("base64 after", raw_payload, len(raw_payload))
            sock.sendto(data, (UDP_IP_IN, UDP_DST_PORT_MIDDLEBOX))

        else :
            # print('Bypass data: ', header+data)
            sock.sendto(header+data, (UDP_IP_IN, UDP_DST_PORT_MIDDLEBOX))
    else:
        sock.sendto(header+data, (UDP_IP_IN, UDP_DST_PORT_MIDDLEBOX))