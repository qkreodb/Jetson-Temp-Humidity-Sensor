import logging
import time
from datetime import datetime  # 시간 데이터를 위한 라이브러리
from pymodbus.client import ModbusSerialClient  # 시리얼(USB) 통신용으로 변경

# 1. 로깅 설정 (시간 형식을 더 깔끔하게 조정)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# 젯슨의 USB 포트 정보 (보통 /dev/ttyUSB0)
# 윈도우에서 테스트 시 'COM3' 등으로 변경 필요
SERIAL_PORT = '/dev/ttyUSB0'


def run_sensor_node():
    # 2. 시리얼 클라이언트 생성 (Modbus RTU 방식)
    client = ModbusSerialClient(
        port=SERIAL_PORT,
        baudrate=9600,
        timeout=3
    )

    logger.info(f"🚀 젯슨 USB 데이터 수집 시작 (포트: {SERIAL_PORT})")

    try:
        while True:
            if client.connect():
                # 3. 데이터 읽기 (ID 1번 센서의 0번 주소부터 2개)
                # 온도가 나왔던 read_input_registers 방식 유지
                result = client.read_input_registers(address=0, count=2, device_id=1)

                if not result.isError():
                    # 4. 시간 스케일링 (포맷팅)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # 5. 데이터 스케일링 (/10.0)
                    temp = result.registers[0] / 10.0
                    humi = result.registers[1] / 10.0

                    # 최종 출력
                    logger.info(f"[{timestamp}] 🌡️ 온도: {temp}°C | 💧 습도: {humi}%")
                else:
                    logger.error(f"[{datetime.now().strftime('%H:%M:%S')}] 센서 응답 에러")
            else:
                logger.error("USB 컨버터 연결 실패. 포트와 권한을 확인하세요.")

            # 2초마다 반복
            time.sleep(2)

    except KeyboardInterrupt:
        logger.info("수집을 종료합니다.")
    finally:
        client.close()


if __name__ == "__main__":
    run_sensor_node()