from sprites import Snake_queue, Mob_variable
from settings import *
from simulation import Custom_resource, kill_after_timeout

# IMPROVEMENTS POINTS
# make time continuous rather than checkin a discrete table
# for counter number...


class Airline(pg.sprite.Sprite):
    def __init__(self, win, airline_code, pos, counter_table):
        self.groups = win.airlines
        pg.sprite.Sprite.__init__(self, self.groups)
        self.win = win
        self.sim = win.sim
        self.env = self.sim.env
        self.code = airline_code
        self.pos = pos
        self.counter_table = counter_table
        self.str_process = "{}_checkin_desk".format(self.code)

        self.t_last_update = -5
        self.n_counter = 0
        self.alive = False

    def open_checkin(self):
        self.t_last_update = int(self.env.now)
        self.n_counter = self.counter_table[int(self.t_last_update)]

        # create queues
        self.snake_queue = Snake_queue(
            self.win,
            self.pos[0],
            self.pos[1],
            config={"N_fold": 4, "N_position_1fold": self.n_counter},
        )

        self.desk_queue = Snake_queue(
            self.win,
            self.pos[0],
            self.pos[1] + 5,  # to be determined depending on island side
            config={"N_fold": 1, "N_position_1fold": self.n_counter},
        )

        # create process
        self.process = Custom_resource(
            self.sim,
            max_capacity=20 * N,
            startup_capacity=self.n_counter,
            Pt=PT_CHECKIN_1step,  # make this variable by pax for 1/2 step
            change_snake_queue=True,
        )

        self.sim.dct_process[self.str_process] = self.process

        # link queues and process
        self.sim.dct_process[self.str_process].link_queues(
            self.snake_queue, self.desk_queue
        )

        self.alive = True

    def close_checkin(self):
        # delete process
        self.process.set_current_capacity(0, update_queues=False)
        del self.sim.dct_process[self.str_process]

        # deal with queueing Pax
        # self.snake_queue.empty_queue_to_wander()

        # kill and delete sprites
        self.snake_queue.kill()
        del self.snake_queue

        self.sim.env.process(
            kill_after_timeout(self.sim, self.desk_queue, PT_CHECKIN_1step)
        )

    def update(self):
        # check every minute for a change of counter number
        t_now = self.env.now
        if t_now - self.t_last_update > 1:
            time = self.env.now
            new_n_counter = self.counter_table[int(time)]
            # if number has changed, open, close or modify
            if new_n_counter != self.n_counter:
                if self.alive == False:
                    self.open_checkin()
                    self.alive = True
                else:
                    if new_n_counter == 0:
                        self.close_checkin()
                        self.n_counter = 0
                        self.alive = False
                    else:
                        self.sim.dct_process[self.str_process].set_current_capacity(
                            new_n_counter
                        )
                        self.n_counter = new_n_counter
