from machine import Pin
import time
import network

def setup_pins():
    green = Pin(16, Pin.OUT)
    green.value(1)
    red = Pin(5, Pin.OUT)
    red.value(0)
    button = Pin(13, Pin.IN)

    return green, red, button
    
def setup_wifi():
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect("Purple Lavenders", "need water")
    while not sta_if.isconnected():
        time.sleep(1)
        print("Not connected to Wifi")
        
    print("Connected to Wifi")
    print(sta_if.ifconfig())
    
def parse_request(connection):
    open_path = "/open_sesame/"

    doornum = None
    correct_path = False

    conn_file = connection.makefile('rb', 0)

    while True:
        line = conn_file.readline().decode('utf-8')
        print(f"Read line: \"{line}\"")
        
        if not line or line == '\r\n':
            print("End of connection input read")
            break
        
        if not line.startswith("GET "):
            continue
        
        segs = line.split(' ')
        if len(segs) != 3:
            continue
        
        path = segs[1]
        
        if not path.startswith(open_path):
            continue
        
        correct_path = True
        print("Correct path")

    return correct_path
    
def main():
    green, red, button = setup_pins()
    setup_wifi()    

    button_press_time = 0
    while True:
        if button.value() == True:
            button_press_time = time.time()
        now = time.time()
        if now - button_press_time < 5:
            green.value(0)
            red.value(1)
        else:
            green.value(1)
            red.value(0)


if __name__ == "__main__":
    main()