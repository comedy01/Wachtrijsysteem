import pyfirmata2
import time
from LCD import LCD

board = pyfirmata2.Arduino('COM3')
board.samplingOn(300)

lcd = LCD(board)

detection_pin_add = board.get_pin('d:2:u')
detection_pin_min = board.get_pin('d:3:u')

attractie_verwerkingssnelheid = 10
counter = 0
max_personen = 160

rustig_bovengrens = max_personen * 0.7
druk_bovengrens   = max_personen * 0.9

start_time = time.time()
processed_whole_minutes = 0

def get_state(count):
    if count == 0:
        return "leeg"
    elif count <= rustig_bovengrens:
        return "rustig"
    elif count <= druk_bovengrens:
        return "druk"
    else:
        return "vol"

def add_callback(released):
    global counter
    if not released:
        if counter < max_personen:
            counter += 1
            check_count()

def min_callback(released):
    global counter
    if not released:
        if counter > 0:
            counter -= 1
            check_count()

def display_status(current_state):
    lcd.set_cursor(0, 0)
    lcd.print(f"Wachtrij {current_state:<5}")

def display_estimated_wait_time():
    wait_time = counter / float(attractie_verwerkingssnelheid)
    lcd.set_cursor(0, 1)
    lcd.print(f"Wachttijd:{wait_time:5.1f}m")

def check_count():
    current_state = get_state(counter)

    if current_state == "leeg":
        board.digital[13].write(0)
        board.digital[12].write(0)
        board.digital[11].write(1)
    elif current_state == "rustig":
        board.digital[13].write(0)
        board.digital[12].write(0)
        board.digital[11].write(1)
    elif current_state == "druk":
        board.digital[13].write(0)
        board.digital[12].write(1)
        board.digital[11].write(0)
    else:
        board.digital[13].write(1)
        board.digital[12].write(0)
        board.digital[11].write(0)

    lcd.clear()
    display_status(current_state)
    display_estimated_wait_time()

detection_pin_add.register_callback(add_callback)
detection_pin_min.register_callback(min_callback)

try:
    check_count()
    last_update_time = time.time()
    while True:
        time.sleep(0.5)
        if time.time() - last_update_time >= 3:
            check_count()
            last_update_time = time.time()

except KeyboardInterrupt:
    print("Exit")
finally:
    board.exit()
