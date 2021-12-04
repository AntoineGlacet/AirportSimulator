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

dct_step = {}


def create_step(step_str, win):

    dct_step["{}_queue".format(step_str)] = Snake_queue(
        win,
        win.dct_tmx["queue_{}".format(step_str)].x / TILESIZE,
        win.dct_tmx["queue_{}".format(step_str)].y / TILESIZE,
        config={
            "N_fold": int(win.dct_tmx["queue_{}".format(step_str)].height / TILESIZE),
            "N_position_1fold": int(
                win.dct_tmx["queue_{}".format(step_str)].width / TILESIZE
            ),
            "x_exit": win.dct_tmx["queue_{}_exit".format(step_str)].x / TILESIZE,
            "y_exit": win.dct_tmx["queue_{}_exit".format(step_str)].y / TILESIZE,
        },
    )

    dct_step["{}_desk".format(step_str)] = Snake_queue(
        win,
        win.dct_tmx["desk_{}".format(step_str)].x / TILESIZE,
        win.dct_tmx["desk_{}".format(step_str)].y / TILESIZE,
        config={
            "N_fold": int(win.dct_tmx["desk_{}".format(step_str)].height / TILESIZE),
            "N_position_1fold": int(
                win.dct_tmx["desk_{}".format(step_str)].width / TILESIZE
            ),
            "x_exit": win.dct_tmx["desk_{}_exit".format(step_str)].x / TILESIZE,
            "y_exit": win.dct_tmx["desk_{}_exit".format(step_str)].y / TILESIZE,
        },
    )

    # create process
    dct_step["{}_process".format(step_str)] = Custom_resource(
        arrival_area,
        max_capacity=20 * N,
        startup_capacity=max(
            int(win.dct_tmx["desk_{}".format(step_str)].height / TILESIZE),
            int(win.dct_tmx["desk_{}".format(step_str)].width / TILESIZE),
        ),
        Pt=PT_CHECKIN_1step,  # make this variable by pax for 1/2 step
        change_snake_queue=False,
    )

    arrival_area.dct_process[step_str] = dct_step["{}_process".format(step_str)]

    # link process to GUI
    arrival_area.dct_process[step_str].link_queues(
        dct_step["{}_queue".format(step_str)], dct_step["{}_desk".format(step_str)]
    )


create_step("A", win)
create_step("B", win)


process_list = ["A", "B"]

arrival_area.env.process(Pax_generator(arrival_area, 5, 600 / 60, process_list))

# run!
win.run(steps_per_update=STEPS_PER_UPDATE)
