import logging
import time
from pymodbus.client import ModbusTcpClient

# 파일 저장은 나중에 지워도 됨, 현재 파일 저장이랑 출력 동시에 하도록 했음
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("sensor_data.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DS")

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
                    logger.info(f"온도: {temp} | 습도: {humi}")
                else:
                    logger.error("센서 응답 오류")
            else:
                logger.error("서버 접근 오류")
            # 주기는 추후에 조정
            time.sleep(5)
    # 해당 부분이 있어서 사용자가 Ctrl+C로 끌 수 있음
    except KeyboardInterrupt:
        logger.info("종료")
    finally:
        client.close()

if __name__ == "__main__":
    run_test()