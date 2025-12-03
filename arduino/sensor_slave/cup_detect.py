def cup_detected(serial_port):

    try:
        # 명령 전송
        serial_port.write(b"CUP\n")

        # 응답 읽기
        response = serial_port.readline().decode().strip()

        return response == "1"

    except Exception:
        return False
