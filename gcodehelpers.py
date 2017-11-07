#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from math import pi, sqrt, acos
from shapely.geometry import Polygon, MultiLineString
from shapely import affinity


def dist(start, destination):
    coord_sum = 0
    for i in range(len(start)):
        coord_sum += (start[i] - destination[i]) ** 2
    return sqrt(coord_sum)


def a_overlap(d, h=0.2):
    a_circle_part = (h/2)**2*acos(d/h)
    a_triangle = 0.125*d/2*sqrt(h*h-d*d)
    return 2*a_circle_part-2*a_triangle


def get_line_distance(w=0.42, h=0.2, overlap_factor=0.5):
    min_distance = h / 2
    for step in range(1, 32):
        a = a_overlap(min_distance, h)
        min_distance = min_distance - (2 * int(h * min_distance - pi * (h / 2)**2 + a < a) - 1) * h / 2 * 0.5**step
    max_overlap = a
    interval = h - min_distance
    d = h - interval / 2
    for step in range(2, 32):
        a = a_overlap(d, h)
        d = d + (2 * int(a > max_overlap * overlap_factor) - 1) * interval * 0.5 ** step
    return w + d


def set_h(point, h):
    return point[0], point[1], h


def offset_coords(coords, offset=(0, 0)):
    ocs = []
    for x, y in coords:
        ocs.append((x + offset[0], y + offset[1]))
    return ocs


def dilate_erode(boundary, holes=[], distance=0, resolution=4):
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


def infill(boundary, holes=[], pattern_lines=MultiLineString([])):
    fill_area = Polygon(boundary, holes)
    fill_lines = []
    for line in pattern_lines:
        intersection = line.intersection(fill_area)
        if intersection.type[:5] == 'Multi' or intersection.type == 'GeometryCollection':
            for segment in intersection.geoms:
                fill_lines.append(segment.coords)
        else:
            fill_lines.append(intersection.coords)
    return fill_lines


def line_pattern(distance, angle=45):
    coords = []
    for i in range(round(500/distance)):
        coords.append([(-150+distance*i, -150), (-150+distance*i, 350)])
    pattern = MultiLineString(coords)
    return list(affinity.rotate(pattern, angle, origin=(100, 100), use_radians=False).geoms)


def print_layer(lines, h, e=0, start_point=(0, 0),
                travel_speed=2500, print_speed=1800,
                filament_d=1.75, w=0.42, layer_height=0.2,
                beam_width=1):
    command_population = [{'commands': "",
                           'e': e,
                           'travel_distance': 0,
                           'remaining_lines': lines,
                           'last_position': start_point}]
    remaining = len(lines)
    while remaining > 0:
        new_population = []
        for candidate in command_population:
            for line in candidate['remaining_lines']:
                forward_candidate = {
                    'commands': candidate['commands'],
                    'e': candidate['e'],
                    'travel_distance': candidate['travel_distance'],
                    'remaining_lines': list(candidate['remaining_lines']),
                    'last_position': candidate['last_position']
                }
                forward_candidate['remaining_lines'].remove(line)
                if line[0][0] != forward_candidate['last_position'][0] or \
                   line[0][1] != forward_candidate['last_position'][1]:
                    forward_candidate['commands'] += travel(set_h(line[0], h), speed=travel_speed) + "\n"
                    forward_candidate['travel_distance'] += dist(forward_candidate['last_position'], line[0])
                    forward_candidate['last_position'] = line[0]
                for point in line:
                    forward_candidate['e'], cmd = print_move(
                        set_h(forward_candidate['last_position'], h), set_h(point, h),
                        old_e=forward_candidate['e'],
                        h=layer_height, speed=print_speed, w=w, filament_d=filament_d)
                    forward_candidate['commands'] += cmd + "\n"
                    forward_candidate['last_position'] = point
                new_population.append(forward_candidate)
                backward_candidate = {
                    'commands': candidate['commands'],
                    'e': candidate['e'],
                    'travel_distance': candidate['travel_distance'],
                    'remaining_lines': list(candidate['remaining_lines']),
                    'last_position': candidate['last_position']
                }
                backward_candidate['remaining_lines'].remove(line)
                if line[-1][0] != backward_candidate['last_position'][0] or \
                   line[-1][1] != backward_candidate['last_position'][1]:
                    backward_candidate['commands'] += travel(set_h(line[-1], h), speed=travel_speed) + "\n"
                    backward_candidate['travel_distance'] += dist(backward_candidate['last_position'], line[-1])
                    backward_candidate['last_position'] = line[-1]
                reversed_line = list(line)
                reversed_line.reverse()

                for point in reversed_line:
                    backward_candidate['e'], cmd = print_move(
                        set_h(backward_candidate['last_position'], h), set_h(point, h),
                        old_e=backward_candidate['e'],
                        h=layer_height, speed=print_speed, w=w, filament_d=filament_d)
                    backward_candidate['commands'] += cmd + "\n"
                    backward_candidate['last_position'] = point
                new_population.append(backward_candidate)
        remaining -= 1
        new_population.sort(key=lambda c: c['travel_distance'])
        command_population = new_population[:beam_width]
    return command_population[0]['e'], command_population[0]['commands']


def print_wall(boundary, holes, h, e=0, start_point=(0, 0), count=2, line_overlap_factor=0.5,
               w=0.42, layer_height=0.3, filament_d=1.75,
               travel_speed=2500, print_speed=2200):
    d = get_line_distance(w, layer_height, line_overlap_factor)
    wall_lines = []
    for i in range(count):
        boundary_line, hole_lines = dilate_erode(boundary, holes, distance=-d/2-i*d)
        wall_lines.append(boundary_line)
    return print_layer(wall_lines, h=h, e=e, start_point=start_point, layer_height=layer_height,
                       travel_speed=travel_speed, print_speed=print_speed, filament_d=filament_d, w=w)


def print_brim(boundary, e=0, line_count=10, line_overlap_factor=0.5, w=0.42, h=0.3, filament_d=1.75,
               travel_speed=2500, print_speed=1800):
    d = get_line_distance(w, h, line_overlap_factor)
    brim_lines = []
    for i in range(line_count):
        brim_lines.append(dilate_erode(boundary, holes=[], distance=d/2+i*d)[0])
    brim_lines.reverse()
    commands = ""
    for line in brim_lines:
        pos = line[0]
        commands += travel(set_h(pos, h), speed=travel_speed) + "\n"
        for point in line[1:]+[line[0]]:
            e, cmd = print_move(set_h(pos, h), set_h(point, h), old_e=e,
                                speed=print_speed, w=w, h=h, filament_d=filament_d)
            commands += cmd + "\n"
            pos = point
    return e, commands


def print_move(start, destination, old_e=0, speed=1800, w=0.42, h=0.2, filament_d=1.75):
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
        "M104 S0",
        "M117 Finished."
    ]
    return "\n".join(lines)


def fan_on():
    return "M106 S255"
