import pyfirmata2
import time
from LCD import LCD

board = pyfirmata2.Arduino('COM3')
board.samplingOn(300)

lcd = LCD(board)

detection_pin_add = board.get_pin('d:2:u')
detection_pin_min = board.get_pin('d:3:u')

counter = 0
max_personen = 160

rustig_bovengrens = max_personen * 0.7
druk_bovengrens   = max_personen * 0.9


def get_state(count):
    if count <= rustig_bovengrens:
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
        else:
            print("Maximum aantal bereikt, niemand kan naar binnen.")

def min_callback(released):
    global counter
    if not released:
        if counter > 0:
            counter -= 1
            print(f"Personen in wachtrij: {counter}")
            check_count()
        else:
            print("Er zijn geen mensen om eruit te laten.")

def display_person_count():
    lcd.set_cursor(0, 1)
    lcd.print(f"Personen in wachtrij: {counter}")

def display_status(current_state):
    lcd.set_cursor(0, 0)
    lcd.print(f"Wachtrij is {current_state}, geschatte wachttijd: ")

def check_count():
    global counter

    current_state = get_state(counter)

    if current_state == "rustig":
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
    display_person_count()

detection_pin_add.register_callback(add_callback)
detection_pin_min.register_callback(min_callback)

try:
    check_count()
    while True:
        time.sleep(3)
        check_count()

except KeyboardInterrupt:
    print('Exit')
finally:
    board.exit()
