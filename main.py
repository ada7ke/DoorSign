from machine import Pin
import time
import network
import socket

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
        # print(f"Read line: \"{line}\"")
        
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
        
        try:
            if len(path) == len(open_path) + 1:
                doornum = int(path[len(open_path):])
        except:
            print("Error parsing doornum.")

    return correct_path, doornum

def read_html_files():
    html = "index.html not present."
    
    with open("index.html") as f:
        html = f.read()
    # print(f"Read HTML file: {html}")
    
    redirect = "redirect.html not present."
    with open("redirect.html") as f:
        redirect = f.read()
    # print(f"Read Redirect file: {redirect}")

    return html, redirect

def main():
    setup_wifi()
    green, red, button = setup_pins()
    html, redirect = read_html_files()
    print("read html files")
    
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.settimeout(1)
    s.listen(1)
    print('listening on', addr)

    button_press_time = 0
    while True:
        connection = None
        try:
            connection, addr = s.accept()
            print('Client connected from', addr)
            connection.settimeout(3) # seconds
            correct_path, doornum = parse_request(connection)
            
            button_press_time = time.time()
            
            if correct_path:
                connection.sendall('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                
                if doornum is not None:
                    print("Sending redirect html")
                    connection.sendall(redirect)
                    print("Doornum: ", doornum)
                else:
                    print("Sending root html")
                    connection.sendall(html)
            else:
                print("Sending HTTP 400 bad request.")
                
                connection.sendall('HTTP/1.0 400 Bad Request\r\n')
        except Exception as e:
            print(f"Exception: {e}")
            # print("Caught socket timeout error.")
        finally:
            if connection is not None:
                print(f"Closing connection to: {addr}")
                connection.close()

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