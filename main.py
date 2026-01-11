import logging
import time
from pymodbus.client import ModbusTcpClient

# 1. 로깅 설정 (실시간으로 통신 상태를 터미널에 출력)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# BT-NB114 정보
# ebyte network configtool V5.5를 통해 설정해주었음
SERVER_IP = '192.168.0.20'
SERVER_PORT = 8887


def run_test():
    # 2. 클라이언트 생성
    client = ModbusTcpClient(SERVER_IP, port=SERVER_PORT)

    logger.info(f"Connecting to {SERVER_IP}:{SERVER_PORT}...")

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
                    logger.info(f"현재 데이터 -> 온도: {temp}°C, 습도: {humi}%")
                else:
                    logger.error("센서로부터 데이터를 가져올 수 없습니다.")
            else:
                logger.error("BT-NB114 서버에 접속할 수 없습니다. 설정을 확인하세요.")

            # 주기는 추후에 조정
            time.sleep(2)

    # 해당 부분이 있어서 사용자가 Ctrl+C로 끌 수 있음
    except KeyboardInterrupt:
        logger.info("테스트를 종료합니다.")
    finally:
        client.close()

if __name__ == "__main__":
    run_test()