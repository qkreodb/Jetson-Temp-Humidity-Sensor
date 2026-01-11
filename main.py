import logging
import time
from pymodbus.client import ModbusSerialClient

# 로그 설정 (화면에 데이터 출력)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# 젯슨의 USB 포트 설정
client = ModbusSerialClient(
    port='/dev/ttyUSB0',  # 젯슨 포트 이름
    baudrate=9600,
    timeout=3
)


def run_on_jetson():
    print("🚀 센서 데이터 수집 시작 (오프라인 모드)")
    try:
        while True:
            if client.connect():
                # 0번 주소에서 2개의 데이터를 읽음 (Slave ID = 1)
                result = client.read_input_registers(0, count=2, device_id=1)

                if not result.isError():
                    temp = result.registers[0] / 10.0
                    humi = result.registers[1] / 10.0
                    print(f"🌡️ 온도: {temp}°C | 💧 습도: {humi}%")
                else:
                    print("❌ 데이터 읽기 실패 (배선 확인 요망)")
            else:
                print("❌ USB 컨버터 연결 실패")

            time.sleep(2)
    except KeyboardInterrupt:
        print("\n종료합니다.")
    finally:
        client.close()


if __name__ == "__main__":
    run_on_jetson()