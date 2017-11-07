#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from gcodehelpers import print_move, travel, retract, resume, start_sequence, stop_sequence, fan_on
from gcodehelpers import infill, line_pattern, get_line_distance, dilate_erode, offset_coords
from gcodehelpers import print_layer, print_brim, print_wall

if __name__ == "__main__":
    filename = "line_overlap_cubes.gcode"
    with open(filename, 'w') as f:
        f.write(start_sequence() + "\n")
        object_coords = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        e = 0.0
        h = 0.3
        e, cmd = retract(e, retract_volume=5, filament_d=1.75)
        f.write(cmd + "\n")
        while h <= 10:
            for overlap_index in range(11):
                d = get_line_distance(0.42, 0.3 if h < 0.31 else 0.2, overlap_index / 10)
                f.write(travel((30 + d/2 + (overlap_index % 4) * 30, 30 + d/2 + (overlap_index // 4) * 30, h)) + "\n")
                e, cmd = resume(e, retract_volume=5, filament_d=1.75)
                f.write(cmd + "\n")
                coords = offset_coords(object_coords, (30 + (overlap_index % 4) * 30, 30 + (overlap_index // 4) * 30))
                if h < 0.35:
                    e, commands = print_brim(coords, e, h=h, line_overlap_factor=overlap_index/10)
                    f.write(commands)
                    # print("e after Brim: {}".format(e))
                e, commands = print_wall(coords, [], h, e, start_point=(0, 0), line_overlap_factor=overlap_index/10)
                f.write(commands)
                # print("e after Wall: {}".format(e))
                infill_boundary, infill_holes = dilate_erode(coords, distance=-d/2-2*d)
                infill_lines = infill(infill_boundary, infill_holes,
                                      pattern_lines=line_pattern(d, angle=45 if h % 0.4 > 0.15 else -45))
                e, commands = print_layer(infill_lines, e=e, h=h, start_point=(0, 0),
                                          layer_height=0.3 if h < 0.31 else 0.2)
                f.write(commands)
                # print("e after Infill: {}".format(e))
                e, cmd = retract(e, retract_volume=5, filament_d=1.75)
                f.write(cmd + "\n")
            print("Height {} sliced.".format(h))
            h += 0.2
        f.write(stop_sequence())
    print("File {0} written.".format(filename))
