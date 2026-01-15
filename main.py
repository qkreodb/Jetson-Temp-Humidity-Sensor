from datetime import datetime
import time
from pymodbus.client import ModbusTcpClient

# BT-NB114 정보
# ebyte network configtool V5.5를 통해 설정해주었음
SERVER_IP = '192.168.0.20'
SERVER_PORT = 8887
# 클라이언트 생성
client = ModbusTcpClient(SERVER_IP, port=SERVER_PORT)

def run_test():
    try:
        while True:
            if client.connect():
                # 시작 주소는 0이고, 값을 두개 받아옴(0: 온도, 1: 습도)
                # 디바이스 아이디는 온·습도 센서의 8번 스위치를 켜서 1임
                result = client.read_input_registers(0, count = 2, device_id = 1)

                if not result.isError():
                    # 센서에서 값을 정수로 보내서 10.0을 나누어 스케일링 작업을 함
                    temp = result.registers[0] / 10.0
                    humi = result.registers[1] / 10.0
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{now}] 온도: {temp} | 습도: {humi}")
                else:
                    print("센서 응답 없음")
            else:
                print(f"{SERVER_IP} 접속 실패")

            # 주기는 추후에 조정
            time.sleep(2)
    # 해당 부분이 있어서 사용자가 Ctrl+C로 끌 수 있음
    except KeyboardInterrupt:
        print("\n종료")
    finally:
        client.close()

if __name__ == "__main__":
    run_test()