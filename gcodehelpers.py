#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from math import pi, sqrt
from shapely.geometry import Polygon


def dist(start, destination):
    coord_sum = 0
    for i in range(len(start)):
        coord_sum += (start[i] - destination[i]) ** 2
    return sqrt(coord_sum)


def dilate_erode(boundary, holes=[], distance=0, resolution=16):
    p = Polygon(boundary, holes)
    boundaries = p.buffer(distance, resolution=resolution).boundary
    holes = []
    if boundaries.type[:5] == 'Multi':
        boundary = boundaries[0]
        for hole_boundary in boundaries[1:]:
            holes.append(list(hole_boundary.coords))
    else:
        boundary = boundaries
    return list(boundary.coords), holes


def free_print_move(start, destination, old_e=0, speed=2200, w=0.42, h=0.2, filament_d=1.75):
    a = w * h + pi * (h / 2) ** 2
    new_e = old_e + a * dist(start, destination) / (pi * (filament_d / 2) ** 2)
    return new_e, "G1 X{x:f} Y{y:f} Z{z:f} E{e:f} F{f:d}".format(
        x=destination[0], y=destination[1], z=destination[2],
        e=new_e, f=speed)


def travel(destination, speed=2500):
    return "G0 X{x:f} Y{y:f} Z{z:f} F{f:d}".format(
        x=destination[0], y=destination[1], z=destination[2], f=speed)


def retract(old_e=0, retract_volume=5, retract_speed=1200, filament_d=1.75):
    retract_length = retract_volume / (pi * (filament_d / 2) ** 2)
    new_e = old_e - retract_length
    return new_e, "G1 E{e:f} F{f:d}".format(e=new_e, f=retract_speed)


def resume(old_e=0, retract_volume=5, retract_speed=1200, filament_d=1.75):
    resume_length = retract_volume / (pi * (filament_d / 2) ** 2)
    new_e = old_e + resume_length
    return new_e, "G1 E{e:f} F{f:d}".format(e=new_e, f=retract_speed)


def start_sequence():
    lines = [
        "M190 S100",
        "M140 S105",
        "M109 S220",
        "M104 S230",
        "G21 ;metric values",
        "G90 ;absolute positioning",
        "M82 ;set extruder to absolute mode",
        "M107 ;start with the fan off",
        "G28 X0 Y0 ;move X/Y to min endstops",
        "G28 Z0 ;move Z to min endstop",
        "G1 Z15.0 F9000 ;move Z to 15mm",
        "G92 E0 ;zero the extruded length",
        "G1 F200 E7 ;extrude 7mm of feed stock",
        "G92 E0 ;zero the extruded length again",
        "G0 F3000",
        ";Put printing message on LCD screen",
        "M117 Printing..."
    ]
    return "\n".join(lines)


def stop_sequence():
    lines = [
        "M205 X20 Y20",
        "M107",
        "M104 S0 ;extruder heater off",
        "M140 S0 ;heated bed heater off (if you have it)",
        "G91 ;relative positioning",
        "G1 E-1 F300  ;retract the filament a bit before lifting the nozzle, to release some of the pressure",
        "G1 Z+0.5 E-5 X-20 Y-20 F9000 ;move Z up a bit and retract filament even more",
        "G28 X0 Y0 ;move X/Y to min endstops, so the head is out of the way",
        "M84 ;steppers off",
        "G90 ;absolute positioning",
        "M104 S0"
    ]
    return "\n".join(lines)


def fan_on():
    return "M106 S255"
