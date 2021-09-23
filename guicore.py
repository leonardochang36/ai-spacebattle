""" GUICore module

This module implements all the visual feedback functionalities.
Including, real-time window-based feed and .avi(h264) video file export.
Be sure you have installed OpenCV, ffmpeg, x264.

"""

import copy
import cv2 as cv
import numpy as np

import utils


class GUICore:
    """ Class in charge of the display of the game """
    def __init__(self, board, p1_ship, p2_ship, show_window=True,
                 save_video=False, video_file=None):
        self.board = board
        self.p1_ship = p1_ship
        self.p2_ship = p2_ship
        # if not board:
        #     raise Exception('ERROR loading board')
        self.show_window = show_window
        self.save_video = save_video
        if show_window:
            cv.namedWindow('AIR HOCKEY')
        if save_video:
            self.out_vid = cv.VideoWriter(video_file, cv.VideoWriter_fourcc(*'H264'), 50,
                                          (self.board.shape[1], int(round(self.board.shape[0] * 1.25))))

    def show_current_state(self, frame, sleep=False):
        """ Display the frame on screen """
        cv.imshow('AIR HOCKEY', frame)
        # key = cv.waitKey()
        key = cv.waitKey(1000 if sleep else 5)
        if key == 27:  # Esc key to stop
            return -1
        return 0

    def write_current_state(self, frame, sleep=False):
        """ Save a video frame """
        ticks = 60 if sleep else 1
        for _ in range(ticks):
            self.out_vid.write(frame)
        return

    def draw_sprite(self, board, sprite, position):
        """ Overlay an image on top of another one. Using alpha channel

        Based on the examples at:
        https://stackoverflow.com/questions/14063070/overlay-a-smaller-image-on-a-larger-image-python-opencv
        """
        round_position = utils.round_point_as_tuple(position)
        x_start = round_position[0] - self.p1_ship.shape[0] // 2
        x_end = round_position[0] + self.p1_ship.shape[0] // 2
        y_start = round_position[1] - self.p1_ship.shape[1] // 2
        y_end = round_position[1] + self.p1_ship.shape[1] // 2

        # Get the alpha filters on both images (large and small)
        alpha_s = sprite[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s

        # Copy each channel independently
        for c in range(0, 3):
            board[y_start:y_end, x_start:x_end, c] = (alpha_s * sprite[:, :, c] + alpha_l * board[y_start:y_end, x_start:x_end, c])

    def resolve_gui(self, state, p1, p2):
        """ Prepare the image to be draw on screen """
        board_feedback = np.zeros((int(round(self.board.shape[0] * 1.25)),
                                   self.board.shape[1], self.board.shape[2]),
                                  dtype=self.board.dtype)
        # visual feedback
        board_feedback[:self.board.shape[0], :self.board.shape[1]] = copy.copy(self.board)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['puck_pos']),
                  state['puck_radius'], (200, 255, 50), -1)
        """
        # Air hockey paddles
        cv.circle(board_feedback, utils.round_point_as_tuple(state['ship1_pos']),
                  state['ship_radius'], (255, 0, 0), -1)
        cv.circle(board_feedback, utils.round_point_as_tuple(state['ship2_pos']),
                  state['ship_radius'], (0, 0, 255), -1)
        """
        # Ship sprites
        self.draw_sprite(board_feedback, self.p1_ship, state['ship1_pos'])
        self.draw_sprite(board_feedback, self.p2_ship, state['ship2_pos'])

        if state['is_goal_move'] is None:
            # write text scores
            ## player 1
            ### write team's name
            pos_xy = (20, int(round(self.board.shape[0] * 1.20)))
            text_size = self.draw_text(board_feedback, p1, pos_xy, (255, 0, 0),
                                       (255, 255, 255), 1, 3, 'left')

            ### write score
            pos_xy = (20, int(round(self.board.shape[0] * 1.20 - text_size[1] * 1.5)))
            self.draw_text(board_feedback, str(state['goals']['left']),
                           pos_xy, (255, 0, 0), (255, 255, 255), 2, 3, 'left')

            ## player 2
            ### write team's name
            pos_xy = (self.board.shape[1] - 20, int(round(self.board.shape[0] * 1.20)))
            text_size = self.draw_text(board_feedback, p2, pos_xy, (0, 0, 255),
                                       (255, 255, 255), 1, 3, 'right')

            ### write score
            pos_xy = (self.board.shape[1] - 20, int(round(self.board.shape[0] * 1.20-text_size[1]*1.5)))
            self.draw_text(board_feedback, str(state['goals']['right']), pos_xy, (0, 0, 255),
                           (255, 255, 255), 2, 3, 'right')
        else:
            # write GOAL sign
            pos_xy = (int(board_feedback.shape[1]/2), int(round(self.board.shape[0] * 1.20)))
            self.draw_text(board_feedback, 'GOALLL for ' + (p1 if state['is_goal_move'] == 'left' else p2),
                           pos_xy, (0, 165, 255), (255, 255, 255), 1.5, 3, 'center')

        if self.save_video:
            self.write_current_state(board_feedback, state['is_goal_move'] is not None)
        if self.show_window:
            if self.show_current_state(board_feedback, state['is_goal_move'] is not None) < 0:
                return -1
        return 0

    def release_all(self):
        """ Clean up resources """
        if self.show_window:
            cv.destroyAllWindows()
        if self.save_video:
            self.out_vid.release()
        return

    def draw_text(self, img, text, pos_xy, text_color, bg_color, fontscale,
                  thickness, alignment='left'):
        """ Show text on the game screen """
        fontface = cv.FONT_HERSHEY_SIMPLEX
        # compute text size in image
        textsize = cv.getTextSize(text, fontface, fontscale, thickness)

        # set text origin according to alignment
        if alignment == 'left':
            textorg = (pos_xy[0], pos_xy[1])
        elif alignment == 'right':
            textorg = (pos_xy[0] - textsize[0][0], pos_xy[1])
        else:
            textorg = (int(round(pos_xy[0] - textsize[0][0] / 2)), pos_xy[1])

        # then put the text itself with offset border
        cv.putText(img, text, textorg, fontface, fontscale, bg_color,
                   int(round(thickness * 3)), cv.LINE_AA)
        cv.putText(img, text, textorg, fontface, fontscale, text_color,
                   thickness, cv.LINE_AA)
        return textsize[0]
