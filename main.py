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
druk_bovengrens = max_personen * 0.9


def add_callback(released):
    global counter
    if not released:
        if counter <= max_personen:
            counter += 1
            print(f"Personen in wachtrij: {counter}")
        else:
            print("Maximum aantal bereikt, niemand kan naar binnen.")


def min_callback(released):
    global counter
    if not released:
        if counter > 0:
            counter -= 1
            print(f"Personen in wachtrij: {counter}")
        else:
            print("Er zijn geen mensen om eruit te laten.")


def check_count():
    global counter
    if counter <= rustig_bovengrens:
        board.digital[13].write(0)
        board.digital[12].write(0)
        board.digital[11].write(1)
    elif rustig_bovengrens < counter <= druk_bovengrens:
        board.digital[13].write(0)
        board.digital[12].write(1)
        board.digital[11].write(0)
    elif counter > druk_bovengrens:
        board.digital[13].write(1)
        board.digital[12].write(0)
        board.digital[11].write(0)

detection_pin_add.register_callback(add_callback)
detection_pin_min.register_callback(min_callback)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('Exit')
finally:
    board.exit()