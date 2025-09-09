# PortForwardPi

Flask 기반의 간단한 포트 포워딩 및 접속 제어 서비스입니다. Raspberry Pi 4B 등에서 실행하여
웹 인터페이스로 iptables 규칙을 관리할 수 있습니다. 포트 포워딩뿐 아니라 IP 주소 또는
국가 코드(GeoIP)에 따라 접근을 허용/차단할 수 있습니다.

## 실행 방법

1. 필요한 패키지 설치
   ```bash
   pip install flask
   ```
2. 애플리케이션 실행 (root 권한 필요)
   ```bash
 sudo python -m portforwardpi.app
  ```
3. 브라우저에서 `http://<라즈베리파이 IP>:5000` 접속 후 규칙을 추가/삭제합니다.

포트 포워딩 규칙과 더불어 허용/차단할 IP 또는 국가 코드를 추가할 수 있으며, 모든 설정은
`config.json`에 저장되고 즉시 iptables에 적용됩니다.
