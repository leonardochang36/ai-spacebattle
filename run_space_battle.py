#!/usr/bin/env python3
""" entry point module

This module implements intefaces for using the ai-spacebattle platform.

Modify it under your own responsability, for the competition purposes only
the original version will be used.
"""

import sys
import argparse
import importlib
import random
import logging
import json

import cv2 as cv
import gamecore
import guicore
import satellite

def main(args):
    """ Program start """
    # load the background image. It also defines the size of the board
    board = cv.imread('assets/bg5-scaled.png')
    # load image for the satellites
    sat_image = cv.imread('assets/satellite_s.png', cv.IMREAD_UNCHANGED)

    # initiallize game state
    state = {}
    state['delta_t'] = 1/30
    # Board shape is (width, height, channels)
    state['board_shape'] = board.shape
    state['goal_size'] = 0.45
    # Use standard measures
    state['puck_radius'] = int(round(state['board_shape'][0] * 3.25 / 51.25))
    state['ship_radius'] = int(round(state['board_shape'][0] * 3.25 / 51.25))
    x_offset = 0.25 if random.uniform(-1, 1) < 0 else 0.75
    state['puck_pos'] = {'x': board.shape[1] * x_offset,
                         'y': random.uniform(0 + state['puck_radius'],
                                             board.shape[0] - state['puck_radius'])}
    state['puck_speed'] = {'x': 0, 'y': 700}
    state['ship1_pos'] = {'x': board.shape[1] * state['goal_size'] / 2 + 1,
                          'y': board.shape[0] / 2}
    state['ship2_pos'] = {'x': board.shape[1] - board.shape[1] * state['goal_size'] / 2 - 1,
                          'y': board.shape[0] / 2}
    state['ship1_speed'] = {'x': 0, 'y': 0}
    state['ship2_speed'] = {'x': 0, 'y': 0}
    state['ship_max_speed'] = 150
    state['goals'] = {'left': 0, 'right': 0}
    state['is_goal_move'] = None
    epsilon = 1

    # dinamically import Player classes for both players
    player1_module = importlib.import_module(args.player1)
    player2_module = importlib.import_module(args.player2)

    # create player instances
    player1 = player1_module.Player(state['ship1_pos'], 'left')
    player2 = player2_module.Player(state['ship2_pos'], 'right')

    # Load the player images, including alpha channel
    # Also rotate them according to their side
    p1_ship = cv.rotate(cv.imread(player1.my_ship_image, cv.IMREAD_UNCHANGED),
                        cv.ROTATE_90_COUNTERCLOCKWISE)
    p2_ship = cv.rotate(cv.imread(player2.my_ship_image, cv.IMREAD_UNCHANGED),
                        cv.ROTATE_90_CLOCKWISE)

    p1_sats = make_satellites(4, 'left', board, state)
    p2_sats = make_satellites(4, 'right', board, state)

    gui_items = {'board': board,
                 'sat_image': sat_image,
                 'p1_ship': p1_ship,
                 'p2_ship': p2_ship,
                 'p1_sats': p1_sats,
                 'p2_sats': p2_sats,
                 #'p1_shots': [],
                 #'p2_shots': [],
                 }


    # initiallize gui core
    if 'video_file' in args:
        gui_core = guicore.GUICore(gui_items,
                                   args.show_window == 'True', True,
                                   args.video_file)
    else:
        gui_core = guicore.GUICore(gui_items)

    # create game with given players
    game_core = gamecore.GameCore(player1, player2, board, state, epsilon, gui_core)

    # run game
    result = game_core.begin_game()

    # prepare output
    # convert exception data types to string
    for k, v in result.items():
        if isinstance(v, Exception):
            result[k] = str(type(v).__name__) + ': ' + str(v)

    result['display_names'] = {'left': player1.my_display_name,
                               'right': player2.my_display_name}

    result = json.dumps(result, skipkeys=True)
    return result


def make_satellites(num_sats, goal_side, board, state):
    """ Create the satellite objects for one player

    Return a list of instances of Satellite """
    # Variables to adjust satellite behaviour
    min_speed = 2
    max_speed = 8
    min_motion = 2
    max_motion = 6
    sat_list = []
    y_distance = board.shape[0] / (num_sats + 1)
    for i in range(num_sats):
        # Define initial position
        if goal_side == 'left':
            pos_x = board.shape[1] * state['goal_size'] / 2 + 1
        else:
            pos_x = board.shape[1] - board.shape[1] * state['goal_size'] / 2 + 1
        pos_y = y_distance * (i + 1)
        sat_pos = {'x': pos_x, 'y': pos_y}
        # Add random variations
        speed = random.randint(min_speed, max_speed)
        motion = random.randint(min_motion, max_motion)
        sat_list.append(satellite.Satellite(sat_pos, goal_side, speed, motion))
    return sat_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=sys.argv[0])

    # Optional arguments
    parser.add_argument("-p1", "--player1", default='player_A',
                        help="Enter Player1 file url without .py extension")
    parser.add_argument("-p2", "--player2", default='player_B',
                        help="Enter Player2 file url without .py extension")
    parser.add_argument("-vf", "--video_file", default=argparse.SUPPRESS,
                        help="Enter video url to save game, use .avi extension")
    parser.add_argument("-sw", "--show_window", default=True,
                        help="Do you want real-time visual feed?")

    args_ = parser.parse_args()

    try:
        sys.exit(main(args_))
    except Exception as exc:
        logging.error(" Oops... something went wrong :(", exc_info=True)
        status = {'status': 'ERROR', 'info': str(exc), 'goals': None,
                  'winner': None,
                  'display_names': {'left': 'left', 'right': 'rigth'}}

        print(json.dumps(status, skipkeys=True))
        sys.exit(-1)
