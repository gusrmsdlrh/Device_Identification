# Device_Identification


UDP/5353 서비스인 mDNS(Multicast DNS)는 DNS에 기반하여 유사하게 동작이 이루어지지만 mDNS 위에 DNS-SD(DNS Service Discovery)를 추가적으로 빌드할 시 기기의 서비스 정보을 요청하여 정보를 얻어올 수 있다.

http://dns-sd.org/ServiceTypes.html 에서 요청할 수 있는 서비스 목록을 볼 수 있다.


요청 순서는 아래와 같다.
1. IP 기반 Domain Name을 요청한다
![image](https://user-images.githubusercontent.com/40857478/121495154-58a07700-ca14-11eb-89a0-fd03d04053a3.png)


2. 응답 데이터에서 Domain Name 데이터를 파싱한다.
![image](https://user-images.githubusercontent.com/40857478/121495200-635b0c00-ca14-11eb-8471-cdcd31d87041.png)


3. Services Query로 서비스 목록을 요청한다
![image](https://user-images.githubusercontent.com/40857478/121495313-7d94ea00-ca14-11eb-8b21-53fb2426f25d.png)

4. 응답 데이터에서 Service Name 데이터만 파싱한다.
![image](https://user-images.githubusercontent.com/40857478/121495373-88e81580-ca14-11eb-9b0e-ab53a10649ac.png)

5. 각 Service Name을 다시 Query로 요청하여 정보를 얻어온다.
![image](https://user-images.githubusercontent.com/40857478/121495546-aae19800-ca14-11eb-93af-5a7291b703b2.png)

6. 응답 데이터의 Type(PTR, TXT, SRV)에 맞게 데이터를 파싱한다
![image](https://user-images.githubusercontent.com/40857478/121495631-bf259500-ca14-11eb-8f87-e3a843c015c1.png)

7. PTR, SRV Type은 Data Length 필드의 값을 가져와 그 뒤의 데이터 길이만큼 가져온다.
![image](https://user-images.githubusercontent.com/40857478/121495785-dd8b9080-ca14-11eb-830a-31cebb9d011e.png)

8.

