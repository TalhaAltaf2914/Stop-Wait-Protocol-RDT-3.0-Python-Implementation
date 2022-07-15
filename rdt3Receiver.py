import socket
import threading
import struct
import time

global src_host, src_port, dst_host, dst_port, seqNum, sSock, rs
src_host = 0
src_port = dst_host = dst_port = seqNum = 0
  
# define the start_timer func.
def start_timer(t):
    
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1



def handle():
    global rs, sSock
    while True:
        sSock, addr = rs.accept()
        return 0


def initializeReceiver(
                src_host,
                src_port,
                dst_host,
                dst_port,
                seqNum,
                ):
    global rs, sSock
    
    src_host = src_host
    src_port = src_port
    dst_host = dst_host
    dst_port = dst_port
    seqNum = seqNum

    print("RDT 3.0 Receiver has been successfully initialized!")
    print("SOURCE IP ADDRESS: " + src_host)
    print("SOURCE PORT: " + str(src_port))
    print("DESTINATION IP ADDRESS: " + dst_host)
    print("DESTINATION PORT: " + str(dst_port))
    print("\n\n")
    rs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    rs.bind((src_host, src_port))
    


def make_pkt(data):# -> bytes:
    global seqNum, src_host, src_port, dst_host, dst_port
    
    chk_sum = 0
    
    type_id = 11#ack identifier
    
    strct = 'BBHH' + str(len(data)) + 's'
    message_format = struct.Struct(strct)
    payload_len = len(data)
    packet = message_format.pack(type_id, seqNum, chk_sum, payload_len, data)
    chk_sum = IntChksum(packet)#45137
    
    #updated chksum
    packet = message_format.pack(type_id, seqNum, chk_sum, payload_len, data)
    print("\nSent checksum: " + str(chk_sum))
    print("ACK PACKET SENT: " + str(packet))
    return packet
    
def udt_send(sndPkt):
    global rs

    rs.sendto(sndPkt, (dst_host, dst_port))

def IntChksum(byte_msg):
    # print("BYTE MESSAGE: " + str(byte_msg))
    total = 0
    length = len(byte_msg)	#length of the byte message object
    i = 0
    while length > 1:
        total += ((byte_msg[i+1] << 8) & 0xFF00) + ((byte_msg[i]) & 0xFF)
        i += 2
        length -= 2

    if length > 0:
        total += (byte_msg[i] & 0xFF)

    while (total >> 16) > 0:
        total = (total & 0xFFFF) + (total >> 16)

    total = ~total
    
    return total & 0xFFFF

def checkArrivedPkt():
    global rs
    global seqNum
    
    bufferSize = 13
    (rcvd_data, peer) = rs.recvfrom(bufferSize)
    msg_size = (len(rcvd_data) - 6)
    form = 'BBHH'+str(msg_size)+'s'
    
    message_format2 = struct.Struct(form)
    
    #unpacking the packet
    (type_id,sq_num,chk_sum,payload_len, rcvd_data) = message_format2.unpack(rcvd_data)
    strct = 'BBHH' + str(len(rcvd_data)) + 's'
    message_format = struct.Struct(strct)
    payload_len = len(rcvd_data)
    
    packet = message_format.pack(type_id, seqNum, 0, payload_len, rcvd_data)
    
    
    calculatedChkSum = IntChksum(packet)#45137
    print("\nCHECK SUM RECEIVED: " + str(chk_sum))
    # print("SEQ NUM: " + str(seqNum))
    calculatedChkSum = IntChksum(packet)
    print("CALCULATED CHECKSUM: " + str(calculatedChkSum))
    if(calculatedChkSum == chk_sum):
        #if chksum same then add seqNum
        print("\nGOT CORRECT PACKET")
        print("GOT SEQNUM: " + str(sq_num))
        seqNum = sq_num + 1
        
        print("\nRECEIVER INCREMENTED SEQNUM: " + str(seqNum))
        udt_send(make_pkt(b'ACK'))#transmitting the ack
    else:
        #corrupted cuz checksum ain't the same
        #will send the packet's seqNum as ack
        print("\nGOT CORRUPTED PACKET")
        seqNum = sq_num
        print("Seq Num for corrupted pkt: " + str(seqNum))
        udt_send(make_pkt(b'ACK'))



def startReceiver():
    global seqNum, src_host, src_port, dst_host, dst_port
    global rs
    
    src_host = dst_host = '127.0.0.1'
    src_port = 4080
    dst_port = 3080#sender
    seqNum = 0
    thread = threading.Thread(target = initializeReceiver(src_host, src_port, dst_host, dst_port, seqNum))
    thread.start()
    thread.join()

    while(1):
        checkArrivedPkt()
    
    rs.close()

if __name__ == '__main__':
    startReceiver()