# KIX_T1a_covid.py
# Where the simulation happens

import random
import simpy
from simpy.events import Timeout
from sprites import Mob_variable, Snake_queue
from settings import *


class Custom_resource(simpy.PriorityResource):
    """
    define a custom resource with extra functions
    for capacity and GUI
    """

    def __init__(self, arr, max_capacity, startup_capacity, Pt, change_snake_queue):
        super().__init__(arr.env, max_capacity)
        self.max_capacity = max_capacity
        self.current_capacity = max_capacity
        self.env = arr.env
        self.arr = arr
        self.Pt = Pt  # to be removed and defined by Pax
        self.change_snake_queue = change_snake_queue
        self.dummy_requests_list = []
        self.set_current_capacity(startup_capacity)
        self.current_capacity = startup_capacity
        self.alive = True

    def set_current_capacity(self, target_capacity, update_queues=True):
        # use dummy priority 0 request to manage capacity
        diff_capa = self.current_capacity - target_capacity
        for i in range(abs(diff_capa)):
            if diff_capa > 0:
                dummy_request = self.request(priority=0)
                self.dummy_requests_list.append(dummy_request)
            else:
                self.release(self.dummy_requests_list[i])
        self.current_capacity = target_capacity

        if self.current_capacity == 0:
            self.alive = False
            print("custom resource is not alive")

        # update shape for pygame
        if update_queues:
            if hasattr(self, "desk_queue"):
                self.desk_queue.change_config(
                    self.desk_queue.x, self.desk_queue.y, self.current_capacity, 1
                )
            if hasattr(self, "snake_queue") and self.change_snake_queue == True:
                self.snake_queue.change_config(
                    self.snake_queue.x,
                    self.snake_queue.y,
                    self.current_capacity,
                    self.snake_queue.N_fold,
                )

    def link_queues(self, snake_queue, desk_queue):
        self.snake_queue = snake_queue
        self.snake_queue.pax_list = []
        self.desk_queue = desk_queue
        self.desk_queue.pax_list = []

    def process(self):
        if RANDOM == True:
            Pt_rand = random.gauss(self.Pt, self.Pt * RANDOM_SIGMA)
            yield self.env.timeout(Pt_rand)
        else:
            yield self.env.timeout(self.Pt)


class arrival(object):
    """
    define an arrival area with one process called A
    """

    def __init__(
        self,
        env,
    ):
        self.env = env
        self.dct_process = {}

    def link_GUI(self, win):
        self.win = win

    def time_out(self, t):
        yield self.env.timeout(t)

    def queue_process(self, x0, y0, n, str_process):
        # description mob spawns, walks to queue, queue,
        # walks to desk, process at desk and disappear.
        process = self.dct_process[str_process]
        # spawn mob that goes to queue and disappear
        mob = Mob_variable(self.win, x0, y0, n, process.snake_queue)

        # wait for mob to arrive to queue
        while mob.arrived == False:
            yield self.env.process(self.time_out(1 / 60))

        with process.request(priority=2) as request:
            process.snake_queue.pax_list.append(str(n))
            yield request
            process.snake_queue.pax_list.remove(str(n))

            # spawn new mob to go to process
            x1, y1 = process.snake_queue.x_exit, process.snake_queue.y_exit
            # catch the case where we removed the process in between
            if str_process in self.dct_process:
                mob = Mob_variable(self.win, x1, y1, n, process.desk_queue)
                # dirty loop to be replaced
                while mob.arrived == False:
                    yield self.env.process(self.time_out(1 / 60))

                # do the process
                process.desk_queue.pax_list.append(str(n))
                yield self.env.process(process.process())
                process.desk_queue.pax_list.remove(str(n))

    def run(self, steps):
        self.env.run(until=self.env.now + steps)


def Pax(arr, n, process_list):
    """
    function that generate one Pax in an instanciated arrival area in a simulation env
    """
    # (x0, y0) = random.choice(SPAWN_POINTS)
    (x0, y0) = (
        arr.win.dct_tmx["spawn_point"].x / TILESIZE,
        arr.win.dct_tmx["spawn_point"].y / TILESIZE,
    )

    for index, str_process in enumerate(process_list):
        # if index != 0:
        #     previous_process = arr.dct_process[process_list[index-1]]
        #     (x0, y0) = (previous_process.desk_queue.x_exit, previous_process.desk_queue.y_exit)

        # wait for process opening if needed
        if process_list[index] not in arr.dct_process.keys():
            mob_wandering = Mob_variable(arr.win, x0, y0, n, None, wandering=True)

            while process_list[index] not in arr.dct_process.keys():
                yield arr.env.process(arr.time_out(10 / 60))

            (x0, y0) = mob_wandering.pos / TILESIZE
            mob_wandering.kill()

        process = arr.dct_process[process_list[index]]
        (x, y) = (process.desk_queue.x_exit, process.desk_queue.y_exit)
        yield arr.env.process(arr.queue_process(x0, y0, n, str_process))
        (x0, y0) = (x, y)


def Pax_generator(arr, N, H, process_list):
    """
    generate N pax per minute for H hours
    """
    t = 0
    n = 0
    while t < H * 60:
        yield arr.env.timeout(1 / N + 0.005)
        arr.env.process(Pax(arr, n, process_list))
        t = arr.env.now
        n += 1


def kill_after_timeout(arr, sprite, t):
    yield arr.env.timeout(t)
    sprite.kill()
    del sprite
