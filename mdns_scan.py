import sys
import socket
import binascii

def service_query():
        base = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'

	# _services._dns-sd._udp.local query
        service_list_req = b'\x09\x5f\x73\x65\x72\x76\x69\x63\x65\x73\x07\x5f\x64\x6e\x73\x2d\x73\x64\x04\x5f\x75\x64\x70\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01'

        sock = sock_create()
        print("\r\n[+] mDNS Service Query")
        sock.send(base + service_list_req )
        try:
                data=sock.recv(1024)
                service_raw=data.split(b'\xc0\x0c\x00\x0c') # Answers Field service name Split
                for i in range(1,len(service_raw)):
                        if b'\x5f\x74\x63\x70' in service_raw[i][8:-2] or b'\x5f\x75\x64\x70' in service_raw[i][8:-2]:
                                service_type(base, service_raw[i][8:-2]+b'\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01') #.local
                        elif b'\x5f\x74\x63\x70' not in service_raw[i][8:-2]:
                                service_type(base, service_raw[i][8:-2]+b'\x04\x5f\x74\x63\x70\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01') # _tcp.local
                        else:
                                service_type(base, service_raw[i][8:-2]+b'\x04\x5f\x75\x64\x70\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01') # _udp.local
        
        except socket.timeout as timeerror:
                print("Service Query : "+ str(timeerror))
        
        sock.close()

def service_type(base, service_req):
        print("\"" + service_req[1:-10].decode() + "\"")
        ptr_ = txt_ = srv_ = True
        sock = sock_create()
        try:
                sock.send(base + service_req)
                recv_data=sock.recv(1024)

                for i in range(len(recv_data.split(b'\x00\x01\x00\x00\x00\x0a'))): # type
                        if ptr_ and b"\x00\x0c\x00\x01\x00\x00\x00\x0a" in recv_data: # PTR (domain name PoinTeR)
                                ptr_data=recv_data.split(b'\x00\x0c\x00\x01\x00\x00\x00\x0a')[1]
                                data_len=int(binascii.hexlify(ptr_data[0:2]),16)
                                print("Type PTR : " + ptr_data[3:data_len].decode())
                                ptr_ = False

                        elif txt_ and b"\x00\x10\x00\x01\x00\x00\x00\x0a" in recv_data: # TXT (Text strings)
                                txt_data=recv_data.split(b'\x00\x10\x00\x01\x00\x00\x00\x0a')[1]
                                total_len=int(binascii.hexlify(txt_data[0:2]),16) # 
                                if total_len == 1: # total length
                                        print("Type TXT : NULL")
                                else:
                                        txt_len=txt_data[2] # first field length
                                        first_txt_data=txt_data[3:txt_len+3].decode()
                                        if ',' in first_txt_data:
                                                print("Type TXT : ", end='')
                                                comma_split=first_txt_data.split(',')
                                                for i in comma_split:
                                                        print(i)
                                        else:
                                                print("Type TXT : " + first_txt_data) # first field data
                                                while txt_len+1 != total_len:
                                                        txt_data_len = txt_data[txt_len+3] # next length
                                                        print(" "*11 + txt_data[txt_len+4 : txt_len+4+txt_data_len].decode())
                                                        txt_len += txt_data_len+1
                                txt_ = False

                        elif srv_ and b"\x00\x21\x00\x01\x00\x00\x00\x0a" in recv_data: # SRV (Server Selection)
                                srv_data=recv_data.split(b'\x00\x21\x00\x01\x00\x00\x00\x0a')[1]
                                print("Type srv : " + srv_data[9:ord(srv_data[1:2])].decode() + ", Port : " + str(int(binascii.hexlify(srv_data[6:8]),16)) +"\r\n")
                                srv_ = False
        except socket.timeout as timeerror:
                print("NULL Data")
                pass
        sock.close()

def host_query():
        sock = sock_create()
        sock.send(host_pkt)
        try:
                print("[+] mDNS HostName Query")
                host_data=sock.recv(1024).split(b'\x00\x01\x00\x00\x00\x0a')[1]
                data_len=int(binascii.hexlify(host_data[0:2]),16)
                print("\"HostName\" : " + host_data[3:data_len-4].decode())
                service_query()
        except socket.timeout as timeerror:
                print("HostName Query : "+ str(timeerror))
                service_query()

def sock_create():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(time)
        sock.connect((target, 5353))
        return sock

def host_query_pkt():
        ip_byte=[]
        reverse = (target.split('.'))
        for i, k in zip(reverse, range(4)):
                ip_byte.append(binascii.unhexlify('0' + str(len(i))))
                globals()['var_{}'.format(k)] = ip_byte[k]+reverse[k].encode()

        # 192.168.0.45 -> 45.0.168.192 -> '\x02\x34\x35 \x01\x30 \x03\x31\x36\x38 \x03\x31\x39\x32'
        addr_arpa = var_3 + var_2 + var_1+ var_0 + b'\x07\x69\x6e\x2d\x61\x64\x64\x72\x04\x61\x72\x70\x61\x00\x00\x0c\x00\x01'
        host_pkt = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' + addr_arpa
        return host_pkt, addr_arpa

if __name__=="__main__":
        time=1
        target = sys.argv[1]
        host_pkt,addr_arpa = host_query_pkt()
        host_query()
