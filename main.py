import logging
import time
from pymodbus.client import ModbusTcpClient

# 1. 로깅 설정 (실시간으로 통신 상태를 터미널에 출력)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# BT-NB114 정보
SERVER_IP = '192.168.0.20'  # 본인의 설정에 맞게 수정
SERVER_PORT = 8887


def run_test():
    # 2. 클라이언트 생성
    client = ModbusTcpClient(SERVER_IP, port=SERVER_PORT)

    logger.info(f"Connecting to {SERVER_IP}:{SERVER_PORT}...")

    try:
        while True:
            if client.connect():
                # 3. 데이터 읽기 (Bitbus 센서 매뉴얼의 주소를 넣으세요)
                # address=0, count=2는 보통 온도/습도 두 개를 읽겠다는 의미입니다.
                result = client.read_input_registers(0, count = 2, device_id = 1)
                print(f"Input Register 결과: {result.registers}")

                if not result.isError():
                    # 센서마다 변환 공식이 다를 수 있습니다 (보통 0.1을 곱함)
                    temp = result.registers[0] / 10.0
                    humi = result.registers[1] / 10.0
                    logger.info(f"현재 데이터 -> 온도: {temp}°C, 습도: {humi}%")
                else:
                    logger.error("센서로부터 데이터를 가져올 수 없습니다.")
            else:
                logger.error("BT-NB114 서버에 접속할 수 없습니다. 설정을 확인하세요.")

            time.sleep(2)  # 2초마다 반복

    except KeyboardInterrupt:
        logger.info("테스트를 종료합니다.")
    finally:
        client.close()


if __name__ == "__main__":
    run_test()