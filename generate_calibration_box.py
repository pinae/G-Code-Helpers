#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from gcodehelpers import print_move, travel, start_sequence, stop_sequence, fan_on

if __name__ == "__main__":
    filename = "calibration_box.gcode"
    with open(filename, 'w') as f:
        f.write(start_sequence() + "\n")
        e = 0.0
        h = 0.3
        f.write(travel((65, 65, h)) + "\n")
        points = [(65, 65),
                  (105, 65),
                  (105, 105),
                  (65, 105),
                  (65, 65),
                  (64.6, 64.6),
                  (105.4, 64.6),
                  (105.4, 105.4),
                  (64.6, 105.4),
                  (64.6, 64.6)]
        old_x, old_y = points[0]
        for x, y in points:
            e, command = print_move((old_x, old_y, h), (x, y, h), old_e=e)
            old_x, old_y = x, y
            f.write(command + "\n")
        f.write(travel((70, 70, h)) + "\n")
        points = [(70, 70),
                  (100, 70),
                  (100, 100),
                  (70, 100),
                  (70, 70)]
        for i in range(99):
            for x, y in points:
                e, command = print_move((old_x, old_y, h), (x, y, h), old_e=e)
                old_x, old_y = x, y
                f.write(command + "\n")
            h += 0.2
            if i == 0:
                f.write(fan_on() + "\n")
            f.write(travel((70, 70, h)) + "\n")
        f.write(stop_sequence())
    print("File {0} written.".format(filename))
