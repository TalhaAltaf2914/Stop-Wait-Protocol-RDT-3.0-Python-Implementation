from socket import *
import rdt3Sender as r
import threading
# import time
# import datetime

if __name__ == '__main__':
    
    no_of_packets = int(input("Enter number of packets: "))
    c = -1
    #ss = socket(AF_INET, SOCK_STREAM)
    thread = threading.Thread(target = 
    r.initializeSender('127.0.0.1', 3080, '127.0.0.1', 4080))
    thread.start()
    thread.join()
    #ss.close()
    # print(r.initializeSender('localhost', 3000, 'localhost', 4000))
        
    ss = r.startSender(b'HOWWDWD', no_of_packets)
    if(ss == "ENDED PROGRAM"):
        print(ss)