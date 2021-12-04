import simpy

from settings import *
from simulation import *
from sprites import *
from window import Window

from in_progress import Airline

# create a simulation environment
environ = simpy.Environment(initial_time=0)

# create an arrival area in this environment
arrival_area = arrival(environ)

# create the window and link both ways for convenience
# a priori, only one to one GUI to sim so it's alright
win = Window(arrival_area, CONFIG)
arrival_area.link_GUI(win)


counter_table = (
    [4 for i in range(5)]
    + [0 for i in range(5)]
    + [4 for i in range(10)]
    + [20 for i in range(2000)]
)
counter_table2 = (
    [2 for i in range(10)]
    + [4 for i in range(10)]
    + [60 for i in range(20)]
    + [20 for i in range(2000)]
)

airline_codes = ["AF", "VN"]

airline = Airline(
    win,
    airline_codes[0],
    vec(0, 0),
    counter_table,
)

airline = Airline(
    win,
    airline_codes[1],
    vec(0, 15),
    counter_table2,
)

process_list = [
    "{}_checkin_desk".format(airline_codes[0]),
    "{}_checkin_desk".format(airline_codes[1]),
]
arrival_area.env.process(Pax_generator(arrival_area, 5, 600 / 60, process_list))

# run!
win.run(steps_per_update=STEPS_PER_UPDATE)
