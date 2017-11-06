#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from gcodehelpers import free_print_move, travel, retract, resume, start_sequence, stop_sequence, fan_on
from gcodehelpers import infill, line_pattern, get_line_distance, dilate_erode, print_layer

if __name__ == "__main__":
    filename = "line_overlap_cubes.gcode"
    with open(filename, 'w') as f:
        f.write(start_sequence() + "\n")
        coords = [(95, 95), (105, 95), (105, 105), (95, 105), (95, 95)]
        e = 0.0
        h = 0.3
        f.write(travel((coords[0][0], coords[0][1], h)) + "\n")
        old_x, old_y = coords[0]
        for x, y in coords:
            e, command = free_print_move((old_x, old_y, h), (x, y, h), old_e=e)
            old_x, old_y = x, y
            f.write(command + "\n")
        d = get_line_distance(overlap_factor=0.5)
        infill_boundary, infill_holes = dilate_erode(coords, distance=-d/2)
        infill_lines = infill(infill_boundary, infill_holes, pattern_lines=line_pattern(d))
        e, commands = print_layer(infill_lines, h=h, start_point=(old_x, old_y))
        f.write(commands)
        f.write(stop_sequence())
    print("File {0} written.".format(filename))
