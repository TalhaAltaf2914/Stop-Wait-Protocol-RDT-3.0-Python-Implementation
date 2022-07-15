import random
import socket
import struct
import time
from multiprocessing import Process


global src_host, src_port, dst_host, dst_port, seqNum, sSock

src_host = 0
src_port = dest_host = dest_port = seqNum = sSock = 0
  
# define the start_timer func.
def start_timer(t):
    global stopTimer
    stopTimer = False
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1
        if(stopTimer == True):
            return "TIMER STOPPED!!!!"


def initializeSender(
                source_host,
                source_port,
                dest_host,
                dest_port,
                ):
    global sSock, seqNum, src_host, src_port, dst_host, dst_port
    
    src_host = source_host
    src_port = source_port
    dst_host = dest_host
    dst_port = dest_port
    seqNum = 0

    print("RDT 3.0 Sender has been successfully initialized!")
    print("SOURCE IP ADDRESS: " + src_host)
    print("SOURCE PORT: " + str(src_port))
    print("DESTINATION IP ADDRESS: " + str(dst_host))
    print("DESTINATION PORT: " + str(dst_port))

    sSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sSock.bind((src_host, src_port))
    
def IntChksum(byte_msg):
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

def make_pkt(data):# -> bytes:
    global seqNum, src_host, src_port, dst_host, dst_port, pkts
    
    #simulating packet loss
    #if random function returns 1 then corrupted packet will be sent
    #else correct packet will be sent
    simPktLoss = random.randint(0, 1)
    print("simPktLoss: " + str(simPktLoss))
    
    chk_sum = 0
    type_id = 12
    strct = 'BBHH' + str(len(data)) + 's'
    message_format = struct.Struct(strct)
    payload_len = len(data)
    packet = message_format.pack(type_id, seqNum, chk_sum, payload_len, data)
    chk_sum = IntChksum(packet)
    if(simPktLoss):
        #if random function returned 1
        #corrupting the packet
        chk_sum += 1
        pkts +=1
    
    packet = message_format.pack(type_id, seqNum, chk_sum, payload_len, data)
    print("\nSent SEQNUM: " + str(seqNum))
    print("Sent CHECKSUM: " + str(chk_sum))
    
    return packet

def rdt_send(data):
    global seqNum
    
    sndpkt = make_pkt(data)
    return sndpkt
    
def udt_send(data):
    global sSock, proc
    sndPkt = make_pkt(data)
    sSock.sendto(sndPkt, (dst_host, dst_port))
    #asynchronous threading for 10 sec timer
    proc = Process(target=start_timer, args=(10, ))
    proc.start()
    
    print("\nTIMER STARTED")
    # print("MSG LENGTH: " + str(sSock.sendto(sndPkt, (dst_host, dst_port))))


def checkArrivedPkt():
    global sSock
    global seqNum, stopTimer, proc
    
    bufferSize = 13
    (rcvd_data, peer) = sSock.recvfrom(bufferSize)
    msg_size = (len(rcvd_data) - 6)
    form = 'BBHH'+str(msg_size)+'s'
    # message_format2 = struct.Struct('BBHH')
    message_format2 = struct.Struct(form)
    
    (type_id,sq_num,chk_sum,payload_len, rcvd_data) = message_format2.unpack(rcvd_data)
    strct = 'BBHH' + str(len(rcvd_data)) + 's'
    message_format = struct.Struct(strct)
    packet = message_format.pack(type_id, seqNum, chk_sum, payload_len, rcvd_data)
    
    
    print("\nPACKET RECEIVED: " + str(packet))

    print("SEQNUM RECEIVED IN CHECK: " + str(sq_num))


    
    #seqNum for current seq num and sq_num is the ack number sent by receiver
    
    if(seqNum != sq_num):#if ack by receiver contains an increment of sequence number then stop timer thread
        
        print("\nTIMER STOPPED")
        proc.kill()#killing timer thread
        #adding seqNum to transmit the next packet since ack was received okay
        seqNum += 1
    #if ack contains the same sequence number then sender will have to retransmit the packet with the exact sequence number
    
    

def startSender(data, no_of_packets):
    global seqNum, src_host, src_port, dest_host, dest_port
    global sSock, stopTimer, pkts, proc
    pkts = no_of_packets
    seqNum = 0 #at the start
    c=0
    # the while loop causes the sender to retransmit the same packet 

    while (c < pkts):
        print("\nSending the packet-------")
        udt_send(data)# the while loop causes the sender to transmit the next packet or retransmit the same packet 

        checkArrivedPkt()
        c+=1
        
    proc.kill() 
    sSock.close()