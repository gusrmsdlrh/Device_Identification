# Device_Identification


UDP/5353 서비스인 mDNS(Multicast DNS)는 DNS에 기반하여 유사하게 동작이 이루어지지만 mDNS 위에 DNS-SD(DNS Service Discovery)를 추가적으로 빌드할 시 기기의 서비스 정보을 요청하여 정보를 얻어올 수 있다.

http://dns-sd.org/ServiceTypes.html 에서 요청할 수 있는 서비스 목록을 볼 수 있다.


요청 순서는 아래와 같다.
1. IP 기반 Host Name을 요청한다
2. 응답 데이터에서 HostName 데이터만 파싱한다.
![image](https://user-images.githubusercontent.com/40857478/121495038-3c9cd580-ca14-11eb-87bb-692e0af5f3e9.png)

4. Services Query로 서비스 목록을 요청한다
5. 

  
