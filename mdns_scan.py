import sys
import socket
import binascii

def mdns_pkt():
        base = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
	# _services._dns-sd._udp.local query
        service_list_req = b'\x09\x5f\x73\x65\x72\x76\x69\x63\x65\x73\x07\x5f\x64\x6e\x73\x2d\x73\x64\x04\x5f\x75\x64\x70\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01'

        sock = sock_create()
        sock.send(host_pkt)
        print("[+] MDNS Request")
        host_data=sock.recv(1024).split(addr_arpa)[1]
        print("\r\n\"HostName\" : " + host_data[13:-6].decode())

        sock.send(base + service_list_req )

        data=sock.recv(1024).split(service_list_req) # Queries Field Split

        service_raw=data[1].split(b'\xc0\x0c\x00\x0c') # Answers Field service name Split
        for i in range(1,len(service_raw)):
                if b'\x5f\x74\x63\x70' in service_raw[i][8:-2] or b'\x5f\x75\x64\x70' in service_raw[i][8:-2]:
                        service_pkt(base, service_raw[i][8:-2]+b'\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01') #.local
                elif b'\x5f\x74\x63\x70' not in service_raw[i][8:-2]:
                        service_pkt(base, service_raw[i][8:-2]+b'\x04\x5f\x74\x63\x70\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01') # _tcp.local
                else:
                        service_pkt(base, service_raw[i][8:-2]+b'\x04\x5f\x75\x64\x70\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01') # _udp.local
        sock.close()

def service_pkt(base, service_req):
        print("\r\n\"" + service_req[1:-10].decode() + "\"")
        ptr_ = txt_ = srv_ = True
        sock = sock_create()
        try:
                sock.send(base + service_req)
                recv_data=sock.recv(1024)

                for i in range(len(recv_data.split(b'\x00\x01\x00\x00\x00\x0a'))): # type
                        if ptr_ and b"\x00\x0c\x00\x01\x00\x00\x00\x0a" in recv_data: # PTR (domain name PoinTeR)
                                ptr_data=recv_data.split(b'\x00\x0c\x00\x01\x00\x00\x00\x0a')[1]
                                print("[+] Type PTR : " + ptr_data[3:ord(ptr_data[1:2])].decode())
                                ptr_ = False

                        elif txt_ and b"\x00\x10\x00\x01\x00\x00\x00\x0a" in recv_data: # TXT (Text strings)
                                data2=recv_data.split(b'\x00\x10\x00\x01\x00\x00\x00\x0a')[1]
                                if ord(data2[1:2]) == 1: # total length
                                        print("[+] Type TXT : NULL")
                                else:
                                        txt_data=data2[2] # first field length
                                        if ',' in data2[3:txt_data+3].decode():
                                                print("[+] Type TXT : ", end='')
                                                comma_split=data2[3:txt_data+3].decode().split(',')
                                                for i in comma_split:
                                                        print(i)
                                        else:
                                                print("[+] Type TXT : " + data2[3:txt_data+3].decode()) # first field data
                                                while txt_data+1 != ord(data2[1:2]):
                                                        txt_data_len = data2[txt_data+3] # next length
                                                        print(" "*15 + data2[txt_data+4 : txt_data+4+txt_data_len].decode())
                                                        txt_data += txt_data_len+1
                                txt_ = False

                        elif srv_ and b"\x00\x21\x00\x01\x00\x00\x00\x0a" in recv_data: # SRV (Server Selection)
                                srv_data=recv_data.split(b'\x00\x21\x00\x01\x00\x00\x00\x0a')[1]
                                print("[+] Type srv : " + srv_data[9:ord(srv_data[1:2])].decode())
                                srv_ = False
        except socket.timeout as timeerror:
                print("NULL Data")
                pass
        sock.close()

def sock_create():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(time)
        sock.connect((target, 5353))
        return sock

def reverse_ip():
        ip_byte=[]
        reverse = (target.split('.'))
        for i, y in zip(reverse, range(4)):
                ip_byte.append(binascii.unhexlify('0' + str(len(i))))
                globals()['var_{}'.format(y)] = ip_byte[y]+reverse[y].encode()
        
        addr_arpa = var_3 + var_2 + var_1+ var_0 + b'\x07\x69\x6e\x2d\x61\x64\x64\x72\x04\x61\x72\x70\x61\x00\x00\x0c\x00\x01'

        host_pkt = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' + addr_arpa

        return host_pkt, addr_arpa

if __name__=="__main__":
        time=1
        target = sys.argv[1]
        host_pkt,addr_arpa = reverse_ip()
        mdns_pkt()
