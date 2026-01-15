import logging
import time
import os
import json
from datetime import datetime, timezone
from pymodbus.client import ModbusTcpClient

# 1. 로깅 설정
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

# 2. 설정 정보
SERVER_IP = '192.168.0.20'
SERVER_PORT = 8887
FIFO_PATH = "/tmp/th_fifo"  # C 프로그램과 약속된 통로 주소


def ensure_fifo(path: str):
    """FIFO 통로가 없으면 생성합니다."""
    if not os.path.exists(path):
        os.mkfifo(path)
        os.chmod(path, 0o666)


def open_fifo_writer_blocking(path: str):
    """C reader가 연결될 때까지 기다리며 통로를 엽니다."""
    logger.info(f"📌 FIFO 열기 대기 중: {path} (C reader를 먼저 실행하세요)")
    return open(path, "w", buffering=1)  # 줄 단위 버퍼링


def run_test():
    ensure_fifo(FIFO_PATH)
    client = ModbusTcpClient(SERVER_IP, port=SERVER_PORT)
    fifo = None

    try:
        # ✅ FIFO 연결 (C 프로그램이 실행 중이어야 여기서 안 막힙니다)
        fifo = open_fifo_writer_blocking(FIFO_PATH)
        logger.info("✅ FIFO 연결 완료 (Python -> C 버퍼 전송 시작)")

        while True:
            if client.connect():
                # 장치 ID 1번 센서에서 데이터 2개 읽기
                result = client.read_input_registers(0, count=2, slave=1)

                if not result.isError():
                    temp = result.registers[0] / 10.0
                    humi = result.registers[1] / 10.0

                    # 1. 터미널 및 로그 파일 출력
                    logger.info(f"🌡️ 온도: {temp}°C | 💧 습도: {humi}%")

                    # 2. ✅ FIFO로 JSON 전송 (C 버퍼 친구가 받을 데이터)
                    payload = {
                        "deviceId": "jetson_ds",
                        "ts": datetime.now(timezone.utc).isoformat(),  # 분석용 UTC 시간
                        "temperatureC": round(temp, 2),
                        "humidityPct": round(humi, 2)
                    }
                    fifo.write(json.dumps(payload) + "\n")

                else:
                    logger.error("센서 응답 오류")
            else:
                logger.error(f"{SERVER_IP} 서버 접근 오류 (네트워크 대역 확인)")

            time.sleep(5)  # 수집 주기 5초

    except BrokenPipeError:
        logger.error("❌ C 프로그램이 종료되어 FIFO 파이프가 끊겼습니다.")
    except KeyboardInterrupt:
        logger.info("수집을 종료합니다.")
    finally:
        if fifo:
            fifo.close()
        client.close()


if __name__ == "__main__":
    run_test()