#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from gcodehelpers import print_move, travel, start_sequence, stop_sequence, fan_on

if __name__ == "__main__":
    filename = "jerk_test.gcode"
    with open(filename, 'w') as f:
        f.write(start_sequence() + "\n")
        e = 0.0
        h = 0.3
        filament_d = 1.75
        f.write(travel((65, 65, h)) + "\n")
        points = [(65, 65),
                  (105, 65),
                  (105, 105),
                  (65, 105),
                  (65, 65),
                  (64.6, 64.6),
                  (104.6, 64.6),
                  (104.6, 104.6),
                  (64.6, 104.6),
                  (64.6, 64.6)]
        old_x, old_y = points[0]
        for x, y in points:
            e, command = print_move((old_x, old_y, h), (x, y, h), old_e=e, filament_d=filament_d)
            old_x, old_y = x, y
            f.write(command + "\n")
        f.write("G0 X70 Y70 Z0.3\n")
        speed = 2000
        jerk = 0
        f.write("M205 X" + str(jerk) + " Y" + str(jerk) + "\n")
        points = [(70, 70),
                  (100, 70),
                  (100, 100),
                  (70, 100),
                  (70, 70)]
        for i in range(399):
            for x, y in points:
                e, command = print_move((old_x, old_y, h), (x, y, h), old_e=e, filament_d=filament_d, speed=speed)
                old_x, old_y = x, y
                f.write(command + "\n")
            h += 0.2
            if i % 10 == 9:
                jerk += 1
                f.write("M205 X" + str(jerk) + " Y" + str(jerk) + "\n")
            if i == 0:
                f.write(fan_on() + "\n")
        f.write(stop_sequence())
    print("File {0} written.".format(filename))
