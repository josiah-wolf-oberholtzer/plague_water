# -*- encoding: utf-8 -*-
from abjad import *
from plague_water import makers
from plague_water.segments import PaletteA

### BASE SEGMENT MAKER ###

base_segment_maker = PaletteA.segment_maker

### SEGMENT PARAMETERS ###

segment_id = 11
numerator = 2
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

### CONTEXT MAP ###

context_map = base_segment_maker.context_map.copy()
context_map['Plague Water Score']['pitch_agent'] = new(
    context_map['Plague Water Score']['pitch_agent'].rotate(-2),
    )
context_map['Saxophone Voice']['register_agent'] = makers.RegisterAgent(
    global_inflections=NamedPitch('A2'),
    )
context_map['Guitar Voice']['register_agent'] = makers.RegisterAgent(
    global_inflections=NamedPitch('E2'),
    )
context_map['Piano RH Voice']['register_agent'] = makers.RegisterAgent(
    global_inflections=makers.RegisterCurve(
        ratio=(1,),
        registers=(
            NamedPitch('F#3'),
            NamedPitch('F#2'),
            ),
        ),
    )
context_map['Piano LH Voice']['register_agent'] = makers.RegisterAgent(
    global_inflections=makers.RegisterCurve(
        ratio=(1,),
        registers=(
            NamedPitch('C2'),
            NamedPitch('A0'),
            ),
        ),
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
music_maker = piano_rh_context_maker.music_makers[0]
piano_rh_context_maker = new(piano_rh_context_maker,
    music_makers=(
        new(music_maker, chord_agent=music_maker.chord_agent.rotate(2)),
        ),
    )

piano_lh_context_maker = base_segment_maker['Piano LH Voice']
piano_lh_context_maker = piano_lh_context_maker.transform_cursors(
    cursor_transform)
music_maker = piano_lh_context_maker.music_makers[0]
piano_lh_context_maker = new(piano_lh_context_maker,
    music_makers=(
        new(music_maker, chord_agent=music_maker.chord_agent.rotate(-2)),
        ),
    )

### PERCUSSION ###

percussion_shaker_context_maker = \
    base_segment_maker['Percussion Shaker Voice']
percussion_shaker_context_maker = \
    percussion_shaker_context_maker.transform_cursors(cursor_transform)
music_maker = percussion_shaker_context_maker.music_makers[0]
percussion_shaker_context_maker = new(percussion_shaker_context_maker,
    music_makers=(
        new(music_maker, pitch_agent=music_maker.pitch_agent.rotate(2)),
        ),
    )

percussion_woodblock_context_maker = \
    base_segment_maker['Percussion Woodblock Voice']

percussion_drum_context_maker = base_segment_maker['Percussion Drum Voice']
percussion_drum_context_maker = \
    percussion_drum_context_maker.transform_cursors(cursor_transform)
music_maker = percussion_drum_context_maker.music_makers[0]
percussion_drum_context_maker = new(percussion_drum_context_maker,
    music_makers=(
        new(music_maker, pitch_agent=music_maker.pitch_agent.rotate(3)),
        ),
    )

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
    segment_id=segment_id,
    segment_name=segment_name,
    target_segment_duration=target_segment_duration,
    )

### MAIN ###

if __name__ == '__main__':
    segment_maker.build_and_persist(__file__)
