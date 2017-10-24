#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from gcodehelpers import free_print_move, travel, retract, resume, start_sequence, stop_sequence, fan_on

if __name__ == "__main__":
    filename = "retract_grid.gcode"
    with open(filename, 'w') as f:
        f.write(start_sequence() + "\n")
        e = 0.0
        h = 0.3
        f.write(travel((65, 65, h)) + "\n")
        points = [(65, 65),
                  (175, 65),
                  (175, 175),
                  (65, 175),
                  (65, 65),
                  (64.6, 64.6),
                  (174.6, 64.6),
                  (174.6, 174.6),
                  (64.6, 174.6),
                  (64.6, 64.6)]
        old_x, old_y = points[0]
        for x, y in points:
            e, command = free_print_move((old_x, old_y, h), (x, y, h), old_e=e)
            old_x, old_y = x, y
            f.write(command + "\n")
        f.write(travel((70, 70, h)) + "\n")
        for i in range(99):
            for j in range(10):
                e, command = free_print_move((70+j*10, 70, h), (70+j*10, 80, h), old_e=e)
                f.write(command + "\n")
                e, command = retract(old_e=e, retract_volume=j)
                f.write(command + "\n")
                f.write(travel((70+j*10, 90, h)) + "\n")
                e, command = resume(old_e=e, retract_volume=j)
                f.write(command + "\n")
                e, command = free_print_move((70+j*10, 90, h), (70+j*10, 100, h), old_e=e)
                f.write(command + "\n")
                e, command = free_print_move((70+j*10, 100, h), (75+j*10, 100, h), old_e=e)
                f.write(command + "\n")
                e, command = free_print_move((75+j*10, 100, h), (75+j*10, 90, h), old_e=e)
                f.write(command + "\n")
                e, command = retract(old_e=e, retract_volume=j+0.5)
                f.write(command + "\n")
                f.write(travel((75+j*10, 80, h)) + "\n")
                e, command = resume(old_e=e, retract_volume=j+0.5)
                f.write(command + "\n")
                e, command = free_print_move((75+j*10, 80, h), (75+j*10, 70, h), old_e=e)
                f.write(command + "\n")
                e, command = free_print_move((75+j*10, 70, h), (80+j*10, 70, h), old_e=e)
                f.write(command + "\n")
            e, command = free_print_move((80+90, 70, h), (80+90, 69.4, h), old_e=e)
            f.write(command + "\n")
            e, command = free_print_move((80+90, 69.4, h), (70, 69.4, h), old_e=e)
            f.write(command + "\n")
            e, command = free_print_move((70, 69.4, h), (70, 70, h+0.2), old_e=e)
            f.write(command + "\n")
            h += 0.2
            if i == 0:
                f.write(fan_on() + "\n")
        f.write(stop_sequence())
    print("File {0} written.".format(filename))
