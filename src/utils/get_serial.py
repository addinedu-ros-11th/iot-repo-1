import serial
import time

class SerialReader:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.connect()

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"Connected to {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"Error connecting to {self.port}: {e}")
            self.ser = None

    def read_line(self):
        """
        Reads a line from the serial port.
        Returns the decoded string or None if no data or error.
        """
        if self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    # Read line, decode to utf-8, and strip whitespace
                    line = self.ser.readline().decode('utf-8').strip()
                    return line
            except Exception as e:
                print(f"Error reading from serial: {e}")
        return None

    def write(self, data):
        """
        Writes data to the serial port.
        """
        if self.ser and self.ser.is_open:
            try:
                if isinstance(data, str):
                    data = data.encode('utf-8')
                self.ser.write(data)
                print(f"Sent: {data}")
            except Exception as e:
                print(f"Error writing to serial: {e}")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    # Example usage
    # Replace '/dev/ttyUSB0' with your actual Arduino port (e.g., 'COM3' on Windows)
    PORT = '/dev/ttyUSB0' 
    BAUDRATE = 9600
    
    reader = SerialReader(PORT, BAUDRATE)
    
    try:
        print("Starting serial read loop. Press Ctrl+C to exit.")
        while True:
            data = reader.read_line()
            if data:
                print(f"Received: {data}")
            time.sleep(0.01) # Small delay to prevent high CPU usage
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        reader.close()
