# -*- encoding: utf-8 -*-
from abjad import *
from plague_water import makers
from plague_water.segments.segment_12_12_base import definition as base

### SEGMENT PARAMETERS ###

segment_id = '12b'
denominator = 106
numerator = 5
outer_numerator = 12
segment_name = 'Segment {} ({}:{}) ({}:{})'.format(
    segment_id,
    outer_numerator,
    denominator,
    numerator,
    outer_numerator,
    )

segment_target_duration = makers.SegmentMaker.get_segment_target_duration(
    denominator=denominator,
    numerator=numerator,
    tempo=base.segment_maker.segment_tempo,
    total_duration_in_seconds=480,
    )

### CONTEXT MAP ###

### BRUSHES ###

### SEGMENT DEFINITION ###

segment_maker = new(
    base.segment_maker,
    segment_id=segment_id,
    segment_name=segment_name,
    segment_target_duration=segment_target_duration,
    )

### MAIN ###

if __name__ == '__main__':
    segment_maker.build_and_persist(__file__)