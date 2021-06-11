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
코드에서 사용되는 모듈은 아래와 같으며 최대한 내장 모듈을 이용하여 작성하였다.

* import socket
* import sys
* import binascii

# 3. 과정
example) Python3 mdns_scan.py <IP>

* Python 코드를 실행할 때 IP를 인자로 하여 Host Name Query 패킷을 생성하여 요청한다
def host_query_pkt():
        ip_byte=[]
        reverse = (target.split('.'))
        for i, k in zip(reverse, range(4)):
                ip_byte.append(binascii.unhexlify('0' + str(len(i))))
                globals()['var_{}'.format(k)] = ip_byte[k]+reverse[k].encode()
        
        addr_arpa = var_3 + var_2 + var_1+ var_0 + b'\x07\x69\x6e\x2d\x61\x64\x64\x72\x04\x61\x72\x70\x61\x00\x00\x0c\x00\x01'

        host_pkt = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' + addr_arpa

        return host_pkt, addr_arpa
        
![image](https://user-images.githubusercontent.com/40857478/121495154-58a07700-ca14-11eb-89a0-fd03d04053a3.png)


2. 응답 데이터에서 Host Name 데이터를 파싱한다.

![image](https://user-images.githubusercontent.com/40857478/121495200-635b0c00-ca14-11eb-8471-cdcd31d87041.png)


3. 서비스 목록을 얻기 위해 services.dns-sd.udp.local Query 패킷을 작성하여 Request 한다

![image](https://user-images.githubusercontent.com/40857478/121495313-7d94ea00-ca14-11eb-8b21-53fb2426f25d.png)


4. Response 패킷의 Answers 필드에서 Service Name 데이터만 파싱한다

![image](https://user-images.githubusercontent.com/40857478/121495373-88e81580-ca14-11eb-9b0e-ab53a10649ac.png)


5. 파싱된 Service Name들을 각 Query 패킷으로 작성하여 Request 한다

![image](https://user-images.githubusercontent.com/40857478/121495546-aae19800-ca14-11eb-93af-5a7291b703b2.png)


6. Response 패킷의 Answers 필드에서 Type(PTR, TXT, SRV)에 알맞게 데이터들을 파싱한다

![image](https://user-images.githubusercontent.com/40857478/121495631-bf259500-ca14-11eb-8f87-e3a843c015c1.png)


7. PTR, SRV Type은 Data Length 필드의 값을 가져와 그 뒤의 데이터 길이만큼 가져와 출력한다.

![image](https://user-images.githubusercontent.com/40857478/121495785-dd8b9080-ca14-11eb-830a-31cebb9d011e.png)


8. TXT Type은 Total Length와 TXT Length가 존재하는데 Total Length와 비교하여 TXT Length의 각 데이터들을 파싱하여 출력한다.

![image](https://user-images.githubusercontent.com/40857478/121497348-4fb0a500-ca16-11eb-8738-e21ac36f5f0e.png)

# 4. 결론
mDNS 프로토콜을 사용중인 대상으로 수행할 경우 아래와 같이 데이터가 출력되며 mDNS 프로토콜 뿐만 아닌 SSDP, NBNS .. 등도 이와 같이 프로토콜을 분석하여 패킷을 전송한 후 데이터를 파싱하여 사용한다.

# 5. Reference
[mDNS RFC 6763](https://datatracker.ietf.org/doc/html/rfc6763)

[DNS-SD RFC 6762](https://datatracker.ietf.org/doc/html/rfc6762)

[DNS-SD Service Type List](http://dns-sd.org/ServiceTypes.html)
