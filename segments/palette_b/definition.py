# -*- encoding: utf-8 -*-
from abjad import new
from abjad.tools import datastructuretools
from abjad.tools import durationtools
from abjad.tools import indicatortools
from plague_water import makers
from plague_water import materials
from plague_water import score_templates

### SEGMENT PARAMETERS ###

measure_segmentation_talea = (1,)
permitted_time_signatures = materials.round_time_signatures
segment_tempo = indicatortools.Tempo(durationtools.Duration(1, 4), 72)

### CONTEXT MAP ###

score_template = score_templates.PlagueWaterScoreTemplate()
score = score_template()
context_map = datastructuretools.ContextMap(score_template)
context_map[score]['minimum_timespan_duration'] = durationtools.Duration(1, 8)

### MUSIC MAKERS ###

base_initial_music_maker = makers.MusicMaker(
    minimum_timespan_duration=durationtools.Duration(1, 8),
    playing_durations=materials.short_durations(),
    playing_groupings=materials.short_groupings(),
    )

base_music_maker = makers.MusicMaker(
    leading_rest_durations=materials.short_durations(),
    minimum_timespan_duration=durationtools.Duration(1, 8),
    playing_durations=materials.short_durations(),
    playing_groupings=materials.short_groupings(),
    )

### BRUSHES ###

guitar_brush = makers.Brush(
    initial_music_maker=new(
        base_initial_music_maker,
        playing_durations=materials.medium_durations(),
        playing_groupings=materials.short_groupings(),
        ),
    music_maker_indices=(),
    music_makers=[
        new(base_music_maker,
            leading_rest_durations=materials.very_short_durations(),
            playing_durations=materials.medium_durations(),
            playing_groupings=materials.medium_groupings(),
            ),
        ],
    )

saxophone_brush = makers.Brush(
    initial_music_maker=new(
        base_initial_music_maker,
        playing_durations=materials.medium_durations(),
        playing_groupings=materials.short_groupings(),
        ),
    music_maker_indices=(),
    music_makers=[
        new(base_music_maker,
            leading_rest_durations=materials.very_short_durations(),
            playing_durations=materials.medium_durations(),
            playing_groupings=materials.medium_groupings(),
            ),
        ],
    )

piano_rh_brush = makers.Brush(
    initial_music_maker=None,
    music_maker_indices=(),
    music_makers=[
        new(base_music_maker,
            ),
        ],
    )

piano_lh_brush = makers.Brush(
    initial_music_maker=None,
    music_maker_indices=(),
    music_makers=[
        new(base_music_maker,
            ),
        ],
    )

percussion_rh_brush = makers.Brush(
    initial_music_maker=None,
    music_maker_indices=(),
    music_makers=[
        new(base_music_maker,
            ),
        ],
    )

percussion_lh_brush = makers.Brush(
    initial_music_maker=None,
    music_maker_indices=(),
    music_makers=[
        new(base_music_maker,
            ),
        ],
    )

### SEGMENT DEFINITION ###

segment_maker = makers.SegmentMaker(
    context_map=context_map,
    guitar_brush=guitar_brush,
    is_final_segment=False,
    measure_segmentation_talea=measure_segmentation_talea,
    percussion_rh_brush=percussion_rh_brush,
    percussion_lh_brush=percussion_lh_brush,
    permitted_time_signatures=permitted_time_signatures,
    piano_lh_brush=piano_lh_brush,
    piano_rh_brush=piano_rh_brush,
    saxophone_brush=saxophone_brush,
    segment_tempo=segment_tempo,
    )
