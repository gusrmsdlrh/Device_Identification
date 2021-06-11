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
        
        addr_arpa = var_3 + var_2 + var_1+ var_0 + b'\x07\x69\x6e\x2d\x61\x64\x64\x72\x04\x61\x72\x70\x61\x00\x00\x0c\x00\x01'
        host_pkt = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' + addr_arpa
        return host_pkt, addr_arpa
```
![image](https://user-images.githubusercontent.com/40857478/121621321-eaf15b00-caa6-11eb-8807-758686f09de8.png)

*  Standard Query로 요청하여 응답된 패킷의 Answers 필드의 Data length 필드의 값을 가져와 다음 byte 값부터 Data length 값의 길이 만큼 데이터를 가져온다.


![image](https://user-images.githubusercontent.com/40857478/121622112-5c7dd900-caa8-11eb-990f-670ffcb14352.png)

3. 서비스 목록을 얻기 위해 services.dns-sd.udp.local Query 패킷을 작성하여 Request 한다



4. Response 패킷의 Answers 필드에서 Service Name 데이터만 파싱한다


5. 파싱된 Service Name들을 각 Query 패킷으로 작성하여 Request 한다


6. Response 패킷의 Answers 필드에서 Type(PTR, TXT, SRV)에 알맞게 데이터들을 파싱한다



7. PTR, SRV Type은 Data Length 필드의 값을 가져와 그 뒤의 데이터 길이만큼 가져와 출력한다.



8. TXT Type은 Total Length와 TXT Length가 존재하는데 Total Length와 비교하여 TXT Length의 각 데이터들을 파싱하여 출력한다.

# 4. 결론
mDNS 프로토콜을 사용중인 대상으로 수행할 경우 아래와 같이 데이터가 출력되며 mDNS 프로토콜 뿐만 아닌 SSDP, NBNS .. 등도 이와 같이 프로토콜을 분석하여 패킷을 전송한 후 데이터를 파싱하여 사용한다.

# 5. Reference
[mDNS RFC 6763](https://datatracker.ietf.org/doc/html/rfc6763)

[DNS-SD RFC 6762](https://datatracker.ietf.org/doc/html/rfc6762)

[DNS-SD Service Type List](http://dns-sd.org/ServiceTypes.html)
