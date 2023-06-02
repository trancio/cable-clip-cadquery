#!/usr/bin/env python3

import cadquery as cq

############
# Parameters
############

clip_type = 'custom'  # big, small, big-small, custome

# for type: big, small,big-small

big_diameter = 6.5
small_diameter = 3.5

# for type custom
custom_parameters = [{
    'diameter': 8.0,
    'mounting': False
}, {
    'diameter': 6.5,
    'mounting': True
}, {
    'diameter': 3.5,
    'mounting': False
}, {
    'diameter': 7.0,
    'mounting': True
}, {
    'diameter': 4,
    'mounting': False
}, {
    'diameter': 5.5,
    'mounting': True
}]

# general parameters

width = 10.0
wall = 1.5
base_height = 4.0  # for bolt

bolt_diameter = 3.5
bolt_head_diameter = 5.5
bolt_head_length = 2.0

rounding = 0.4

#######################
# Calculated parameters
#######################

aux = bolt_head_length + wall
base_height = base_height if base_height > aux else aux

#########
# Objects
#########


def base_clip(base_height, diameter, mounting_hole=False):
    length = diameter + 2 * wall
    height = diameter + base_height
    cable_position = [(0, base_height / 2)]
    cut_out_position = [(0, height / 2)]
    narrowing = diameter / 10

    clip = cq.Workplane('front')
    clip = clip.rect(length, height).extrude(width)
    clip = clip.faces('>Z').workplane()
    clip = clip.pushPoints(cable_position)
    clip = clip.hole(diameter)
    aux = cq.Workplane('front')
    aux = aux.pushPoints(cut_out_position)
    aux = aux.rect(diameter - narrowing, diameter).extrude(width)
    clip = clip.cut(aux)
    if mounting_hole:
        bolt_head = bolt_head_length + diameter
        bolt_position = [(0, -width / 2)]
        clip = clip.faces('>Y').workplane()
        clip = clip.pushPoints(bolt_position)
        clip = clip.cboreHole(bolt_diameter, bolt_head_diameter, bolt_head)
    return clip


def big_clip(mounting_hole=True):
    clip = base_clip(base_height, big_diameter, True)
    return clip


def small_clip(mounting_pad=True):
    clip = base_clip(wall, small_diameter, False)
    if mounting_pad:
        pad_length = bolt_diameter + 2 * wall
        pad_height = base_height
        y_shift = (wall + small_diameter - pad_height) / 2
        pad = cq.Workplane()
        pad = pad.rect(pad_length, pad_height).extrude(width)
        pad = pad.faces('>Y').workplane()
        pad = pad.pushPoints([(0, width / 2)])
        pad = pad.cboreHole(bolt_diameter, bolt_head_diameter,
                            bolt_head_length)
        pad = pad.translate(
            (small_diameter / 2 + wall + pad_length / 2, -y_shift, 0))
        clip = clip.union(pad)
    return clip


def big_small_clip():
    custom = [{
        'diameter': big_diameter,
        'mounting': True
    }, {
        'diameter': small_diameter,
        'mounting': False
    }]
    clip = custom_clip(custom)
    return clip


def custom_clip(custom):
    clip = cq.Workplane('front')
    x_shift = 0
    last_diameter = 0
    max_diameter = max(custom, key=lambda x: x["diameter"])["diameter"]
    for cable in custom:
        if cable['mounting'] and cable['diameter'] * 0.9 < bolt_head_diameter:
            print(
                f'The bolt head not fit behind the {cable["diameter"]} diameter cable.'
            )
            aux = base_clip(base_height, cable['diameter'], False)
        else:
            aux = base_clip(base_height, cable['diameter'], cable['mounting'])
        x_shift += cable['diameter'] / 2
        y_shift = (max_diameter - cable['diameter']) / 2
        aux = aux.translate((x_shift, -y_shift, 0))
        clip = clip.union(aux)
        last_diameter = cable['diameter']
        x_shift += last_diameter / 2 + 1.5 * wall
    return clip


def clip(c_type):
    if c_type == 'big':
        clip = big_clip()
    elif c_type == 'small':
        clip = small_clip()
    elif c_type == 'big_small':
        clip = big_small_clip()
    elif c_type == 'custom':
        clip = custom_clip(custom_parameters)
    clip = clip.edges('|Z').fillet(rounding)
    clip = clip.rotate((0, 0, 0), (0.0, 0.0, 1), 200)
    return clip


if __name__ == '__main__':
    for c_type in ['small', 'big', 'big_small', 'custom']:
        obj = clip(c_type)
        cq.exporters.export(obj, f'{c_type}.stl')
else:
    show_object(clip(clip_type), name=clip_type)
