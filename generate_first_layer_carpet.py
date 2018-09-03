#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from gcodehelpers import print_move, travel, start_sequence, stop_sequence, get_line_distance

if __name__ == "__main__":
    filename = "first_layer_carpet.gcode"
    with open(filename, 'w') as f:
        f.write(start_sequence() + "\n")
        e = 0.0
        h = 0.3
        w = 0.42
        x_offset = 65
        y_offset = 65
        carpet_width = 40
        carpet_length = 60
        f.write(travel((x_offset, y_offset, h)) + "\n")
        y = y_offset
        while y <= y_offset + carpet_length - 2 * get_line_distance(w, h, 0.4):
            e, command = print_move((x_offset, y, h), (x_offset+carpet_width, y, h), old_e=e)
            f.write(command + "\n")
            y = y + get_line_distance(w, h, 0.4)
            f.write(travel((x_offset+carpet_width, y, h)) + "\n")
            e, command = print_move((x_offset+carpet_width, y, h), (x_offset, y, h), old_e=e)
            f.write(command + "\n")
            y = y + get_line_distance(w, h, 0.4)
            f.write(travel((x_offset, y, h)) + "\n")
        f.write(stop_sequence())
    print("File {0} written.".format(filename))
