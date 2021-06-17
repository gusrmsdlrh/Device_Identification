# <center> mDNS 프로토콜 Queries - Answers 데이터 파싱</center>

# 1. 개요
[UDP-Based Active Scan for IoT Security (UAIS)](http://itiis.org/digital-library/24228) 논문에서 활용된 mDNS 프로토콜의 Python 활용 예제이다.<br>


UDP/5353 mDNS(Multicast DNS)는 zeroconf로 DHCP 환경이 없는 네트워크에서 프린터와 같은 호스트를 식별하고 자동으로 연결해주는 데 사용된다.<br>
기본적으로 DNS에 기반하여 동작이 이루어지지만 mDNS 위에 DNS-SD(DNS Service Discovery)를 빌드하여 사용할 경우 Discovery 프로토콜로 활용할 수 있으며 PTR Type으로 호스트 네임, 특정 서비스를 Query 하면 응답된 패킷의 Answers 필드에서 PTR/TXT/SRV/A 각 Type의 데이터들을 이용하여 정보를 얻어올 수 있다.

* PTR : 서비스 도메인 이름
* TXT : 서비스에 대한 추가적인 정보
* SRV : PTR에서 ~~Priority, Weight,~~ Port를 추가로 제공
* ~~AAAA : IPv6~~
* ~~A : IPv4~~

서비스 요청 목록은 [DNS-SD Service Type List](http://dns-sd.org/ServiceTypes.html)에서 확인할 수 있으며 운용중인 서비스를 요청해야 하지만 Bruteforce 식으로 하나씩 하기에는 리소스적으로 무리가 있기에 대상의 서비스 목록을 요청할 수 있는 **service.dns-sd.udp.local** 서비스 타입을 이용하면 된다.
<br>
# 2. Python3
**Usage) Python3 mdns_scan.py target**

코드에서 사용되는 모듈은 3가지이며 최대한 내장 모듈을 이용하여 프로그래밍 하였다.

* import socket
* import sys
* import binascii

# 3. 정 요약
* 실행할 때 인자로 받은 IP 주소를 "." 기준으로 나누어 저장하며 저장된 길이 값과 나누어진 IP 주소를 16진수 데이터로 만들고 주소 순서를 Reverse로 Standard Query를 요청한다. ex) 192.168.0.45 -> 45.0.168.192 -> '\x02\x34\x35 \x01\x30 \x03\x31\x36\x38 \x03\x31\x39\x32'
```
def host_query_pkt():
        ip_byte=[]
        reverse = (target.split('.'))
        for i, k in zip(reverse, range(4)):
                ip_byte.append(binascii.unhexlify('0' + str(len(i))))
                globals()['var_{}'.format(k)] = ip_byte[k]+reverse[k].encode()
	
        addr_arpa = var_3 + var_2 + var_1+ var_0 + b'\x07\x69\x6e\x2d\x61\x64\x64\x72\x04\x61\x72\x70\x61\x00\x00\x0c\x00\x01'
        host_pkt = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' + addr_arpa
        return host_pkt, addr_arpa
```
![image](https://user-images.githubusercontent.com/40857478/121621321-eaf15b00-caa6-11eb-8807-758686f09de8.png)
<br>

<br>

*  HostName을 요청하여 응답 패킷이 온다면 Answers 필드의 고정된 데이터를 기준으로 나누고 Data length의 값만큼 데이터를 읽어온다면 HostName을 얻을 수 있다. 이때 접미사 .local은 제거하고 출력한다.
```
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
```

![image](https://user-images.githubusercontent.com/40857478/121622112-5c7dd900-caa8-11eb-990f-670ffcb14352.png)
<br>

<br>

* HostName Query가 끝나고 Service List Query를 수행하는데 요청하기 위해선 [DNS-SD Service Type List](http://dns-sd.org/ServiceTypes.html) 목록에서 확인할 수 있는 services.dns-sd.udp.local 유형으로 Standard Query를 요청한다.
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
<br>

<br>

* Service List를 요청하여 응답 패킷이 온다면 Answers 필드에서 ServiceName 데이터들을 추출하기 위해 Answers 필드의 공통 데이터로 나누면 각 리스트 데이터의 일정한 offset에서 ServiceName을 얻어올 수 있다.<br>
* 그리고 ServiceName을 재요청하기 위해서는 도메인 데이터가 필요하기에 얻어온 Service Name에 도메인 데이터가 존재하지 않으면 추가하여 전달한다.
```
data=sock.recv(1024)
service_raw=data.split(b'\xc0\x0c\x00\x0c') # Answers Field service name Split
	for i in range(1,len(service_raw)):
		if b'\x5f\x74\x63\x70' in service_raw[i][8:-2] or b'\x5f\x75\x64\x70' in service_raw[i][8:-2]:
			service_type(base, service_raw[i][8:-2]+b'\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01') #.local
		elif b'\x5f\x74\x63\x70' not in service_raw[i][8:-2]:
			service_type(base, service_raw[i][8:-2]+b'\x04\x5f\x74\x63\x70\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01') # _tcp.local
		else:
			service_type(base, service_raw[i][8:-2]+b'\x04\x5f\x75\x64\x70\x05\x6c\x6f\x63\x61\x6c\x00\x00\x0c\x00\x01') # _udp.local
```
![image](https://user-images.githubusercontent.com/40857478/121628836-fc416400-cab4-11eb-8b21-b92edf2fdad0.png)
<br>

<br>

* 전달받은 ServiceName으로 Query 패킷을 재작성하여 요청한다.
```
def service_type(base, service_req):
        print("\"" + service_req[1:-10].decode() + "\"")
        ptr_ = txt_ = srv_ = True
        sock = sock_create()
        try:
                sock.send(base + service_req)
```
![image](https://user-images.githubusercontent.com/40857478/121630747-b5ee0400-cab8-11eb-9ac2-404edf6d4ec0.png)
![image](https://user-images.githubusercontent.com/40857478/121630762-bab2b800-cab8-11eb-81dd-5ed5a77ef79b.png)
![image](https://user-images.githubusercontent.com/40857478/121630771-beded580-cab8-11eb-8911-83fc2ba84785.png)
<br>

<br>

* 각 ServiceName 별로 응답 패킷이 존재한다면 Answers 필드에서 공통 데이터로 나누어진 값들에서 PTR/TXT/SRV Type 데이터가 존재하면 수행하게 된다.
```
recv_data=sock.recv(1024)
for i in range(len(recv_data.split(b'\x00\x01\x00\x00\x00\x0a'))): # type
	if ptr_ and b"\x00\x0c\x00\x01\x00\x00\x00\x0a" in recv_data: # PTR (domain name PoinTeR)
		[...]
	elif txt_ and b"\x00\x10\x00\x01\x00\x00\x00\x0a" in recv_data: # TXT (Text strings)
		[...]
	elif srv_ and b"\x00\x21\x00\x01\x00\x00\x00\x0a" in recv_data: # SRV (Server Selection)
		[...]
```
![image](https://user-images.githubusercontent.com/40857478/121630816-d1590f00-cab8-11eb-9c06-d2f4e82c38c0.png)
<br>

<br>

* PTR, SRV Type의 내부 로직은 Type 데이터로 나누어진 값에서 Data length의 값을 구하여 데이터를 출력한다.
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
![image](https://user-images.githubusercontent.com/40857478/121630892-f77eaf00-cab8-11eb-9d7b-797fb4e8fda1.png)
![image](https://user-images.githubusercontent.com/40857478/121630880-efbf0a80-cab8-11eb-9bf3-a49013c3d139.png)
<br>

<br>

* TXT Type은 Data length와 TXT Length 두 개가 존재하는데 Data length는 총 데이터의 길잇값이고 TXT Length는 해당 필드 데이터의 길잇값을 의미한다. <br>
* 먼저 Data length 값을 저장한 후 TXT Length 값만큼 데이터를 출력하는 반복문을 수행하는데 이때 TXT Length 값에 +1 씩 더하여 축적된 값과 Data length 값을 비교하여 같을 때까지 수행하면 모든 TXT 데이터를 얻어올 수 있게 된다.
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
![image](https://user-images.githubusercontent.com/40857478/121630911-06fdf800-cab9-11eb-8be8-e507d5449aa3.png)

# 4. 결과
mDNS 프로토콜을 사용 중인 대상으로 수행할 경우 기기의 정보들을 얻어올 수 있다.

<br><br>
![image](https://user-images.githubusercontent.com/40857478/121978411-19cb4200-cdc3-11eb-92d8-30524526409e.png)
![image](https://user-images.githubusercontent.com/40857478/121978223-b2ad8d80-cdc2-11eb-885a-f99449f83647.png)
![image](https://user-images.githubusercontent.com/40857478/121978176-9a3d7300-cdc2-11eb-9441-9370c3ecd5a7.png)
![image](https://user-images.githubusercontent.com/40857478/121978274-d53fa680-cdc2-11eb-9422-3aaf8d65fa21.png)
<br><br>

# 5. ETC
위 코드는 Unicast 통신 방식의 코드이며 기기간의 Multicast 방식을 위해서는 아래와 같이 사용하면 된다.
```
MCAST_GRP = '224.0.0.251'
MCAST_PORT = 5353
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', MCAST_PORT))
sock.sendto(mdns_pkt, (MCAST_GRP, MCAST_PORT))

mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

while 1:
	data, address = sock.recvfrom(1024)
	if target in address:
		[...]
```
