import simpy
from pathlib import Path
import sys

module_path = Path(__file__).parent.parent / "src/airportSimulator"
sys.path.append(str(module_path) + "/")

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

dct_step = {}


def create_step(step_str, win, Pt=PT_CHECKIN_1step):

    for sub_step in ["queue", "desk"]:

        dct_step["{}_{}".format(step_str, sub_step)] = Snake_queue(
            win,
            x=win.dct_tmx["{}_{}".format(sub_step, step_str)].x,
            y=win.dct_tmx["{}_{}".format(sub_step, step_str)].y,
            config={
                "height": int(win.dct_tmx["{}_{}".format(sub_step, step_str)].height),
                "width": int(win.dct_tmx["{}_{}".format(sub_step, step_str)].width),
                "x_exit": win.dct_tmx["{}_{}_exit".format(sub_step, step_str)].x,
                "y_exit": win.dct_tmx["{}_{}_exit".format(sub_step, step_str)].y,
                "queue_dir_point": win.dct_tmx[
                    "{}_{}_direction".format(sub_step, step_str)
                ],
            },
        )

    # create process
    dct_step["{}_process".format(step_str)] = Custom_resource(
        arrival_area,
        max_capacity=50,
        startup_capacity=max(
            int(win.dct_tmx["desk_{}".format(step_str)].height / TILESIZE),
            int(win.dct_tmx["desk_{}".format(step_str)].width / TILESIZE),
        ),
        Pt=Pt,  # make this variable borne by the pax for different type of process eg.: 1step 2step bag drop ...
        change_snake_queue=False,
    )

    arrival_area.dct_process[step_str] = dct_step["{}_process".format(step_str)]

    # link process to GUI
    arrival_area.dct_process[step_str].link_queues(
        dct_step["{}_queue".format(step_str)], dct_step["{}_desk".format(step_str)]
    )


create_step("A", win)
create_step("B", win)
create_step("2", win, Pt=0)
create_step("7", win)

# add stairs to process list to prevent wandering of Pax
arrival_area.dct_process["take_stairs"] = "dummy"
process_list = ["2", "take_stairs", "A", "B", "7"]

arrival_area.env.process(Pax_generator(arrival_area, 5, 600 / 60, process_list))

# run!
win.run(steps_per_update=STEPS_PER_UPDATE)
