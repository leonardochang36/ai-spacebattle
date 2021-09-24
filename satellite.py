""" Satellite module

This class describes the behaviour of satellite objects.
Each player will have a set number of satellites to protect, while
attacking the oponent's satellites
"""

import random


class Satellite:
    """ Class to describe the behaviour of the satellites """
    def __init__(self, sat_pos, goal_side, speed, motion):
        self.sat_image = "assets/satellite_s.png"
        self.sat_side = goal_side
        self.sat_state = {}
        self.sat_pos = sat_pos
        self.current_pos = sat_pos
        self.move_direction = random.choice([1, -1])
        self.motion_range = motion
        self.speed = speed

    def next_move(self, state):
        """ Function that computes the next move of the satellite """
        # Detect when it is necesary to change direction
        if self.move_direction == 1 and self.current_pos['y'] > self.sat_pos['y'] + self.motion_range:
            self.move_direction = -1
        elif self.move_direction == -1 and self.current_pos['y'] < self.sat_pos['y'] - self.motion_range:
            self.move_direction = 1
        self.current_pos['y'] = self.current_pos['y'] + self.speed * state['delta_t']

    def on_hit(self):
        """ Detect what happens when hit by a laser """
        pass
