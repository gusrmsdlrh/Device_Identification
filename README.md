# <center> mDNS UDP 프로토콜 Queries - Answers 데이터 파싱 코드</center>

# 1. 개요
UDP/5353 서비스인 mDNS(Multicast DNS)는 zeroconf 기술로 DHCP 환경이 없는 네트워크에서 프린터 등의 호스트(/etc/hosts)를 찾아 자동으로 연결해주는데 사용된다.<br>

기본적으로 DNS에 기반하여 동작이 이루어지지만 mDNS 위에 DNS-SD(DNS Service Discovery)를 빌드하여 사용할 경우 PTR Type으로 호스트네임, 서비스 목록을 Query하면 응답된 패킷의 Answers 필드에서 PTR/TXT/SRV/A 각 Type의 데이터들을 이용하여 정보를 얻어올수 있다.

**서비스 목록을 요청할 때는 service.dns-sd.udp.local 을 사용한다.**

* PTR : 서비스 도메인 이름
* TXT : 서비스에 대한 추가적인 정보
* SRV : PTR에서 ~~Priority, Weight,~~ Port를 추가적으로 제공
* ~~AAAA : IPv6~~
* ~~A : IPv4~~

# 2. Python3
**example) Python3 mdns_scan.py <IP>**
코드에서 사용되는 모듈은 아래와 같으며 최대한 내장 모듈을 이용하여 작성하였다.

* import socket
* import sys
* import binascii

# 3. 과정
* Python 코드를 실행할 때 인자로 받은 IP를 "." 기준으로 Split로 나누어 각 값의 길이를 ip_byte 리스트에 저장한다. ip_byte에 저장된 길이 값과 나누어진 IP 값 조합으로 데이터를 만드는데 데이터를 연결하는 과정에서 IP는 반대로 하여 Standard Query로 요청하게 된다. ex) 192.168.0.45 -> 45.0.168.192
```
def host_query_pkt():
        ip_byte=[]
        reverse = (target.split('.'))
        for i, k in zip(reverse, range(4)):
                ip_byte.append(binascii.unhexlify('0' + str(len(i))))
                globals()['var_{}'.format(k)] = ip_byte[k]+reverse[k].encode()
        # ex) '\x02\x34\x35 \x01\x30 \x03\x31\x36\x38 \x03\x31\x39\x32'
        addr_arpa = var_3 + var_2 + var_1+ var_0 + b'\x07\x69\x6e\x2d\x61\x64\x64\x72\x04\x61\x72\x70\x61\x00\x00\x0c\x00\x01'
        host_pkt = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' + addr_arpa
        return host_pkt, addr_arpa
```
![image](https://user-images.githubusercontent.com/40857478/121621321-eaf15b00-caa6-11eb-8807-758686f09de8.png)

*  Standard Query로 요청하여 응답된 패킷의 Answers 필드의 Data length 필드의 값을 가져와 다음 byte 값부터 Data length 값의 길이 만큼 데이터를 가져온다. 이때 HostName '.local' 접미사는 mDNS를 사용하는 Bonjour에서 기기를 식별하기 위해 확인하는 용도로 사용되어 데이터를 가져올 때 접미사를 제거하여 출력한다.
```
def host_query():
        sock = sock_create()
        sock.send(host_pkt)
        try:
                print("[+] mDNS HostName Query")
                host_data=sock.recv(1024).split(b'\x00\x01\x00\x00\x00\x0a')[1]
                data_len=int(binascii.hexlify(host_data[0:2]),16)
                print("\"HostName\" : " + host_data[3:data_len+1].decode())
                service_query()
        except socket.timeout as timeerror:
                print("HostName Query : "+ str(timeerror))
                service_query()
```

![image](https://user-images.githubusercontent.com/40857478/121622112-5c7dd900-caa8-11eb-990f-670ffcb14352.png)

* 서비스 목록을 요청하기 위한 services.dns-sd.udp.local Standard Query 패킷을 작성하여 Request 한다
```
def service_query():
        base = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'

	# _services._dns-sd._udp.local query
        service_list_req = b'\x09\x5f\x73\x65\x72\x76\x69\x63\x65\x73\x07\x5f\x64\x6e\x73\x2d\x73\x64\x04\x5f\x75\x64\x70\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01'

        sock = sock_create()
        print("\r\n[+] mDNS Service Query")
        sock.send(base + service_list_req )
```
![image](https://user-images.githubusercontent.com/40857478/121628791-e895fd80-cab4-11eb-9a53-b4a5d3c3e232.png)

4. Response 패킷의 Answers 필드에서 ServiceName 데이터만 파싱한다
```
data=sock.recv(1024).split(service_list_req) # Queries Field Split

                service_raw=data[1].split(b'\xc0\x0c\x00\x0c') # Answers Field service name Split
                for i in range(1,len(service_raw)):
                        if b'\x5f\x74\x63\x70' in service_raw[i][8:-2] or b'\x5f\x75\x64\x70' in service_raw[i][8:-2]:
                                service_type(base, service_raw[i][8:-2]+b'\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01') #.local
                        elif b'\x5f\x74\x63\x70' not in service_raw[i][8:-2]:
                                service_type(base, service_raw[i][8:-2]+b'\x04\x5f\x74\x63\x70\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01') # _tcp.local
                        else:
                                service_type(base, service_raw[i][8:-2]+b'\x04\x5f\x75\x64\x70\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01') # _udp.local
```
![image](https://user-images.githubusercontent.com/40857478/121628836-fc416400-cab4-11eb-8b21-b92edf2fdad0.png)

	
5. 파싱된 Service Name들을 각 Query 패킷으로 재 작성하여 Request 한다
```
def service_type(base, service_req):
        print("\"" + service_req[1:-10].decode() + "\"")
        ptr_ = txt_ = srv_ = True
        sock = sock_create()
        try:
                sock.send(base + service_req)
```

6. Response 패킷의 Answers 필드에서 Type(PTR, TXT, SRV)에 알맞게 데이터들을 파싱한다
```
recv_data=sock.recv(1024)

for i in range(len(recv_data.split(b'\x00\x01\x00\x00\x00\x0a'))): # type
	if ptr_ and b"\x00\x0c\x00\x01\x00\x00\x00\x0a" in recv_data: # PTR (domain name PoinTeR)
	elif txt_ and b"\x00\x10\x00\x01\x00\x00\x00\x0a" in recv_data: # TXT (Text strings)
	elif srv_ and b"\x00\x21\x00\x01\x00\x00\x00\x0a" in recv_data: # SRV (Server Selection)
```

7. PTR, SRV Type은 Data Length 필드의 값을 가져와 그 뒤의 데이터 길이만큼 가져와 출력한다.
```
if ptr_ and b"\x00\x0c\x00\x01\x00\x00\x00\x0a" in recv_data: # PTR (domain name PoinTeR)
	ptr_data=recv_data.split(b'\x00\x0c\x00\x01\x00\x00\x00\x0a')[1]
	data_len=int(binascii.hexlify(ptr_data[0:2]),16)
	print("Type PTR : " + ptr_data[3:data_len].decode())
	ptr_ = False
elif srv_ and b"\x00\x21\x00\x01\x00\x00\x00\x0a" in recv_data: # SRV (Server Selection)
	srv_data=recv_data.split(b'\x00\x21\x00\x01\x00\x00\x00\x0a')[1]
	print("Type srv : " + srv_data[9:ord(srv_data[1:2])].decode() + ", Port : " + str(int(binascii.hexlify(srv_data[6:8]),16)) +"\r\n")
	srv_ = False
```

8. TXT Type은 Total Length와 TXT Length가 존재하는데 Total Length와 비교하여 TXT Length의 각 데이터들을 파싱하여 출력한다.
```
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
```

# 4. 결론
mDNS 프로토콜을 사용중인 대상으로 수행할 경우 아래와 같이 데이터가 출력되며 mDNS 프로토콜 뿐만 아닌 SSDP, NBNS .. 등도 이와 같이 프로토콜을 분석하여 패킷을 전송한 후 데이터를 파싱하여 사용한다.
```python3 mdns_scan.py 192.168.0.45```
![image](https://user-images.githubusercontent.com/40857478/121629192-9f927900-cab5-11eb-9bc3-81b82f5441d9.png)
	
# 5. Reference
[mDNS RFC 6763](https://datatracker.ietf.org/doc/html/rfc6763)

[DNS-SD RFC 6762](https://datatracker.ietf.org/doc/html/rfc6762)

[DNS-SD Service Type List](http://dns-sd.org/ServiceTypes.html)
