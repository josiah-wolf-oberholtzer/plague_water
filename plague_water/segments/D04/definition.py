# -*- encoding: utf-8 -*-
from abjad import *
from plague_water import makers
from plague_water.segments import PaletteD

### BASE SEGMENT MAKER ###

base_segment_maker = PaletteD.segment_maker

### SEGMENT PARAMETERS ###

segment_id = 4
numerator = 7
denominator = 106
segment_name = 'Segment {} ({}:{})'.format(
    segment_id,
    numerator,
    denominator,
    )

target_segment_duration = makers.SegmentMaker.get_segment_target_duration(
    denominator=denominator,
    numerator=numerator,
    tempo=base_segment_maker.segment_tempo,
    total_duration_in_seconds=480,
    )

rebarrings = [
    (7, 8),   # 43: (7, 8)
    (7, 8),   # 44: (7, 8)
    (7, 8),   # 45: (7, 16)
    #         # 46: (7, 16)
    (4, 8),   # 47: (5, 16)
    #         # 48: (3, 16)
    (5, 8),   # 49: (7, 16)
    #         # 50: (3, 16)
    (7, 8),   # 51: (7, 8)
    (7, 8),   # 52: (7, 16)
    #         # 53: (7, 16)
    (7, 8),   # 54: (7, 8)
    (7, 8),   # 55: (7, 8)
    (3, 16),  # 56: (3, 16)
    (7, 8),   # 57: (7, 8)
    (9, 8),   # 58: (11, 16)
    #         # 59: (7, 16)
    (1, 8),   # 60: (5, 16)
    (3, 16),
    (7, 8),   # 61: (7, 8)
    (7, 8),   # 62: (7, 8)
    (5, 8),   # 63: (5, 8)
    (5, 8),   # 64: (7, 16)
    #         # 65: (3, 16)
    ]

### CONTEXT MAP ###

context_map = base_segment_maker.context_map.copy()
context_map['Plague Water Score']['pitch_agent'] = new(
    context_map['Plague Water Score']['pitch_agent'].rotate(6),
    )
context_map['Saxophone Voice']['register_agent'] = makers.RegisterAgent(
    global_inflections=NamedPitch('C2'),
    )
context_map['Guitar Voice']['register_agent'] = makers.RegisterAgent(
    global_inflections=NamedPitch('F#4'),
    )

### CURSOR TRANSFORM ###

cursor_transform = None

### GUITAR ###

guitar_context_maker = base_segment_maker['Guitar Voice']
guitar_context_maker = guitar_context_maker.transform_cursors(
    cursor_transform)
guitar_context_maker = new(guitar_context_maker)

### SAXOPHONE ###

saxophone_context_maker = base_segment_maker['Saxophone Voice']
saxophone_context_maker = saxophone_context_maker.transform_cursors(
    cursor_transform)
saxophone_context_maker = new(saxophone_context_maker)

### PIANO ###

piano_rh_context_maker = base_segment_maker['Piano RH Voice']
piano_rh_context_maker = piano_rh_context_maker.transform_cursors(
    cursor_transform)
piano_rh_context_maker = new(piano_rh_context_maker)

piano_lh_context_maker = base_segment_maker['Piano LH Voice']
piano_lh_context_maker = piano_lh_context_maker.transform_cursors(
    cursor_transform)

### PERCUSSION ###

percussion_shaker_context_maker = \
    base_segment_maker['Percussion Shaker Voice']
percussion_shaker_context_maker = \
    percussion_shaker_context_maker.transform_cursors(cursor_transform)
percussion_shaker_context_maker = new(percussion_shaker_context_maker)

percussion_woodblock_context_maker = \
    base_segment_maker['Percussion Woodblock Voice']
percussion_woodblock_context_maker = \
    percussion_woodblock_context_maker.transform_cursors(cursor_transform)
percussion_woodblock_context_maker = new(percussion_woodblock_context_maker)

percussion_drum_context_maker = base_segment_maker['Percussion Drum Voice']
percussion_drum_context_maker = \
    percussion_drum_context_maker.transform_cursors(cursor_transform)
percussion_drum_context_maker = new(percussion_drum_context_maker)

### DEPENDENT CONTEXT MAKERS ###

piano_pedals_context_maker = base_segment_maker['Piano Pedals']
piano_pedals_context_maker = new(piano_pedals_context_maker)

### SEGMENT DEFINITION ###

segment_maker = new(
    base_segment_maker,
    context_makers=(
        guitar_context_maker,
        percussion_drum_context_maker,
        percussion_shaker_context_maker,
        percussion_woodblock_context_maker,
        piano_lh_context_maker,
        piano_rh_context_maker,
        piano_pedals_context_maker,
        saxophone_context_maker,
        ),
    context_map=context_map,
    rebarrings=rebarrings,
    segment_id=segment_id,
    segment_name=segment_name,
    target_segment_duration=target_segment_duration,
    )

### MAIN ###

if __name__ == '__main__':
    segment_maker.build_and_persist(__file__)
