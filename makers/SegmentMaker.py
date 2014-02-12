#-*- encoding: utf-8 -*-
import collections
import itertools
import os
import sys
from abjad import *
from plague_water import plague_water_configuration
from plague_water import score_templates
from plague_water.makers.PlagueWaterObject import PlagueWaterObject


class SegmentMaker(PlagueWaterObject):

    ### SLOTS ###

    __slots__ = (
        'cached_meters',
        'context_map',
        'is_final_segment',
        'lilypond_file',
        'measure_segmentation_talea',
        'meters',
        'permitted_time_signatures',
        'score',
        'segment_duration',
        'segment_name',
        'segment_id',
        'target_segment_duration',
        'segment_tempo',
        'time_signatures',
        'context_makers',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        context_map=None,
        is_final_segment=None,
        measure_segmentation_talea=None,
        permitted_time_signatures=None,
        segment_id=None,
        segment_name=None,
        target_segment_duration=None,
        segment_tempo=None,
        context_makers=None,
        ):
        self._prepare(
            allow_none_as_sentinel=True,
            context_map=context_map,
            is_final_segment=is_final_segment,
            measure_segmentation_talea=measure_segmentation_talea,
            permitted_time_signatures=permitted_time_signatures,
            segment_id=segment_id,
            segment_name=segment_name,
            target_segment_duration=target_segment_duration,
            segment_tempo=segment_tempo,
            context_makers=context_makers,
            )

    ### SPECIAL METHODS ###

    def __call__(self, current_file_path=None):
        ### VALIDATE AND SETUP ###
        self._prepare(
            allow_none_as_sentinel=False,
            context_map=self.context_map,
            is_final_segment=self.is_final_segment,
            measure_segmentation_talea=self.measure_segmentation_talea,
            permitted_time_signatures=self.permitted_time_signatures,
            segment_id=self.segment_id,
            segment_name=self.segment_name,
            segment_tempo=self.segment_tempo,
            target_segment_duration=self.target_segment_duration,
            context_makers=self.context_makers,
            )

        ### CREATE SCORE ###
        template = score_templates.PlagueWaterScoreTemplate()
        self.score = template()

        ### BUILD TIMESPAN STRUCTURES ###
        self.create_semantic_timespans()
        self.meters = self.find_meters()
        self.time_signatures = tuple(meter.implied_time_signature
            for meter in self.meters)
        self.segment_duration = sum(time_signature.duration
            for time_signature in self.time_signatures)
        self.cleanup_semantic_timespans()
        self.create_dependent_timespans()
        self.remove_empty_trailing_measures()
        self.create_silent_timespans()

        ### CREATE NOTATION ###
        self.populate_time_signature_context()
        self.populate_rhythms(rewrite_meter=True)
        self.apply_graces()
        self.apply_pitches()
        self.apply_registers()
        self.apply_chords()
        self.apply_piano_clefs_and_octavations()
        # self.apply_piano_staff_changes()
        self.color_piano_conflicts()
        self.apply_indicators()
        self.apply_dynamics()
        self.apply_spanners()
        self.apply_grace_slurs()

        ### APPLY LAYOUT ###
        self.configure_score()
        assert inspect_(self.score).is_well_formed()
        self.configure_lilypond_file()
        return self.lilypond_file

    def __getitem__(self, item):
        item = str(item)
        for context_maker in self.context_makers:
            if context_maker.context_name == item:
                return context_maker

    def __illustrate__(self):
        return self()

    def __makenew__(self, **kwargs):
        from abjad.tools import systemtools
        manager = systemtools.StorageFormatManager
        keyword_argument_dictionary = \
            manager.get_keyword_argument_dictionary(self)
        for key, value in kwargs.iteritems():
            if key in keyword_argument_dictionary:
                keyword_argument_dictionary[key] = value
            else:
                raise KeyError(key)
        result = type(self)(**keyword_argument_dictionary)
        return result

    ### PRIVATE METHODS ###

    def _prepare(
        self,
        allow_none_as_sentinel=False,
        context_map=None,
        is_final_segment=False,
        measure_segmentation_talea=None,
        permitted_time_signatures=None,
        segment_id=None,
        segment_name=None,
        segment_tempo=None,
        target_segment_duration=None,
        context_makers=None,
        ):
        from plague_water import makers
        ### TIMESPAN MAKERS ###
        if not allow_none_as_sentinel:
            prototype = (makers.ContextMaker, type(None))
            assert len(context_makers)
            assert all(isinstance(x, prototype) for x in context_makers)
            context_makers = sorted(
                context_makers,
                key=lambda x: x.context_name,
                )
            context_makers = tuple(context_makers)
            context_names = set([x.context_name for x in context_makers])
            assert len(context_names) == len(context_makers)
        ### OTHER ###
        assert isinstance(context_map, datastructuretools.ContextMap)
        permitted_time_signatures = indicatortools.TimeSignatureInventory(
            permitted_time_signatures)
        assert len(permitted_time_signatures)
        segment_tempo = Tempo(segment_tempo)
        if measure_segmentation_talea is not None:
            assert len(measure_segmentation_talea)
            assert mathtools.all_are_positive_integers(
                measure_segmentation_talea)
        if target_segment_duration is not None:
            target_segment_duration = Duration(target_segment_duration)
            assert 0 < target_segment_duration
        ### APPLY ###
        self.cached_meters = {}
        self.context_map = context_map
        self.is_final_segment = is_final_segment
        self.lilypond_file = None
        self.measure_segmentation_talea = measure_segmentation_talea
        self.meters = None
        self.permitted_time_signatures = permitted_time_signatures
        self.score = None
        self.segment_duration = None
        self.segment_id = str(segment_id)
        self.segment_name = segment_name
        self.segment_tempo = segment_tempo
        self.target_segment_duration = target_segment_duration
        self.time_signatures = None
        self.context_makers = context_makers

    ### PUBLIC METHODS ###

    def apply_chords(self):
        from plague_water import makers
        self.score._is_forbidden_to_update = True
        message = '\tapplying chords'
        with systemtools.ProgressIndicator(message) as progress_indicator:
            for leaf in iterate(self.score).by_timeline(Note):
                logical_tie = inspect_(leaf).get_logical_tie()
                if leaf is not logical_tie.head:
                    continue
                music_maker = inspect_(leaf).get_effective(makers.MusicMaker)
                chord_agent = music_maker.chord_agent
                if chord_agent is None:
                    continue
                chord_agent(
                    logical_tie=logical_tie,
                    segment_duration=self.segment_duration,
                    )
                progress_indicator.advance()
        self.score._is_forbidden_to_update = False

    def apply_dynamics(self):
        message = '\tapplying dynamics'
        music_maker_seeds = collections.Counter()
        with systemtools.ProgressIndicator(message) as progress_indicator:
            for music, music_maker in \
                self.iterate_containers_and_music_makers():
                seed = music_maker_seeds[music_maker]
                dynamic_agent = music_maker.dynamic_agent
                if dynamic_agent is None:
                    continue
                dynamic_agent(
                    music=music,
                    seed=seed,
                    segment_duration=self.segment_duration,
                    )
                music_maker_seeds[music_maker] += 1
                progress_indicator.advance()

    def apply_grace_slurs(self):
        message = '\tapplying grace slurs'
        with systemtools.ProgressIndicator(message) as progress_indicator:
            for leaf in iterate(self.score).by_class(scoretools.Leaf):
                grace_containers = inspect_(leaf).get_grace_containers('after')
                if not grace_containers:
                    continue
                assert len(grace_containers) == 1
                grace_container = grace_containers[0]
                next_leaf = inspect_(leaf).get_leaf(1)
                assert next_leaf is not None
                slur_notes = list(grace_container.select_leaves())
                assert len(slur_notes), (slur_notes, grace_container)
                slur_notes.append(next_leaf)
                phrasing_slur = spannertools.PhrasingSlur()
                phrasing_slur._contiguity_constraint = None
                attach(phrasing_slur, slur_notes)
                progress_indicator.advance()

    def apply_graces(self):
        from plague_water import makers
        message = '\tmaking graces'
        with systemtools.ProgressIndicator(message) as progress_indicator:
            for leaf in iterate(self.score).by_timeline(Note):
                logical_tie = inspect_(leaf).get_logical_tie()
                if leaf is not logical_tie.head:
                    continue
                music_maker = inspect_(leaf).get_effective(makers.MusicMaker)
                grace_maker = music_maker.grace_maker
                if grace_maker is None:
                    continue
                grace_maker(
                    logical_tie=logical_tie,
                    segment_duration=self.segment_duration,
                    )
                progress_indicator.advance()

    def apply_indicators(self):
        message = '\tapplying indicators'
        music_maker_seeds = collections.Counter()
        with systemtools.ProgressIndicator(message) as progress_indicator:
            for music, music_maker in \
                self.iterate_containers_and_music_makers():
                seed = music_maker_seeds[music_maker]
                indicator_agent = music_maker.indicator_agent
                if indicator_agent is None:
                    continue
                indicator_agent(
                    music=music,
                    seed=seed,
                    segment_duration=self.segment_duration,
                    )
                music_maker_seeds[music_maker] += 1
                progress_indicator.advance()

    def apply_piano_clefs_and_octavations(self):
        def cleanup(staff):
            leaves = list(iterate(staff).by_class(scoretools.Leaf))
            groups = list(iterate(leaves).by_run(
                (scoretools.Note, scoretools.Chord)))
            for group in groups:
                pitches = pitchtools.PitchSegment.from_selection(group)
                average = int(sum(float(x) for x in pitches) / len(pitches))
                average = pitchtools.NamedPitch(average)
                octavation = None
                if pitchtools.NamedPitch('C4') <= average:
                    clef = Clef('treble')
                    if NamedPitch('B5') < average:
                        octavation = 1
                else:
                    clef = Clef('bass')
                    if average < NamedPitch('D2'):
                        octavation = -1
                effective_clef = inspect_(group[0]).get_effective(Clef)
                if effective_clef != clef:
                    try:
                        attach(clef, group[0])
                    except ValueError:
                        pass
                if octavation is not None:
                    octavation_spanner = spannertools.OctavationSpanner(
                        start=octavation,
                        )
                    attach(octavation_spanner, group)
        message = '\tapplying piano clefs and octavations'
        print message
        upper_staff = self.score['Piano Upper Staff']
        lower_staff = self.score['Piano Lower Staff']
        if self.segment_id == '1':
            attach(Clef('treble'), upper_staff)
            attach(Clef('bass'), lower_staff)
        cleanup(upper_staff)
        cleanup(lower_staff)

    def apply_piano_staff_changes(self):
        message = '\tapplying piano staff changes'
        with systemtools.ProgressIndicator(message) as progress_indicator:
            piano_rh_voice = self.score['Piano RH Voice']
            piano_lh_voice = self.score['Piano LH Voice']
            piano_upper_staff = self.score['Piano Upper Staff']
            piano_lower_staff = self.score['Piano Lower Staff']
            old_piano_rh_staff = None
            rh_iterator = iterate(piano_rh_voice).by_logical_tie(pitched=True)
            for logical_tie in rh_iterator:
                if isinstance(logical_tie[0], scoretools.Note):
                    written_pitches = [logical_tie[0].written_pitch]
                else:
                    written_pitches = logical_tie[0].written_pitches
                pitch_numbers = [float(x) for x in written_pitches]
                pitch_center = sum(pitch_numbers) / len(pitch_numbers)
                if 0 < pitch_center:
                    new_piano_rh_staff = piano_upper_staff
                else:
                    new_piano_rh_staff = piano_lower_staff
                if new_piano_rh_staff != old_piano_rh_staff:
                    staff_change = indicatortools.StaffChange(
                        staff=new_piano_rh_staff,
                        )
                    attach(staff_change, logical_tie[0], scope=Voice)
                    old_piano_rh_staff = new_piano_rh_staff
                    progress_indicator.advance()
            old_piano_lh_staff = None
            lh_iterator = iterate(piano_lh_voice).by_logical_tie(pitched=True)
            for logical_tie in lh_iterator:
                if isinstance(logical_tie[0], scoretools.Note):
                    written_pitches = [logical_tie[0].written_pitch]
                else:
                    written_pitches = logical_tie[0].written_pitches
                pitch_numbers = [float(x) for x in written_pitches]
                pitch_center = sum(pitch_numbers) / len(pitch_numbers)
                if 0 < pitch_center:
                    new_piano_lh_staff = piano_upper_staff
                else:
                    new_piano_lh_staff = piano_lower_staff
                if new_piano_lh_staff != old_piano_lh_staff:
                    staff_change = indicatortools.StaffChange(
                        staff=new_piano_lh_staff,
                        )
                    attach(staff_change, logical_tie[0], scope=Voice)
                    old_piano_lh_staff = new_piano_lh_staff
                    progress_indicator.advance()

    def apply_pitches(self):
        from plague_water import makers
        message = '\tapplying pitch classes'
        with systemtools.ProgressIndicator(message) as progress_indicator:
            for leaf in iterate(self.score).by_timeline(Note):
                logical_tie = inspect_(leaf).get_logical_tie()
                if leaf is not logical_tie.head:
                    continue
                music_maker = inspect_(leaf).get_effective(makers.MusicMaker)
                pitch_agent = music_maker.pitch_agent
                if pitch_agent is None:
                    continue
                previous_pitch_set = None
                previous_leaf = inspect_(logical_tie.head).get_leaf(-1)
                if isinstance(previous_leaf, scoretools.Note):
                    previous_pitch_set = pitchtools.PitchSet(
                        [previous_leaf.written_pitch])
                elif isinstance(previous_leaf, scoretools.Chord):
                    previous_pitch_set = pitchtools.PitchSet(
                        previous_leaf.written_pitches)
                grace = ()
                if previous_leaf is not None:
                    inspector = inspect_(previous_leaf)
                    grace = inspector.get_grace_containers('after')
                inspector = inspect_(logical_tie.head)
                grace = grace or inspector.get_grace_containers('grace')
                logical_ties = []
                if grace:
                    iterator = iterate(grace[0]).by_logical_tie(pitched=True)
                    logical_ties.extend([x for x in iterator])
                logical_ties.append(logical_tie)
                for logical_tie in logical_ties:
                    previous_pitch_set = pitch_agent(
                        logical_tie=logical_tie,
                        previous_pitch_set=previous_pitch_set,
                        segment_duration=self.segment_duration,
                        )
                progress_indicator.advance()

    def apply_registers(self):
        message = '\tapplying registers'
        with systemtools.ProgressIndicator(message) as progress_indicator:
            for music, music_maker in \
                self.iterate_containers_and_music_makers():
                assert inspect_(music).get_duration(), music
                register_agent = music_maker.register_agent
                if register_agent is None:
                    continue
                register_agent(
                    music=music,
                    segment_duration=self.segment_duration,
                    )
                progress_indicator.advance()

    def apply_spanners(self):
        message = '\tapplying spanners'
        music_maker_seeds = collections.Counter()
        with systemtools.ProgressIndicator(message) as progress_indicator:
            for music, music_maker in \
                self.iterate_containers_and_music_makers():
                seed = music_maker_seeds[music_maker]
                spanner_agent = music_maker.spanner_agent
                if spanner_agent is None:
                    continue
                spanner_agent(
                    music=music,
                    seed=seed,
                    segment_duration=self.segment_duration,
                    )
                music_maker_seeds[music_maker] += 1
                progress_indicator.advance()

    def build_and_persist(self, current_file_path):
        print 'Building {}'.format(self.segment_name)
        with systemtools.Timer() as timer:
            current_directory_path = os.path.dirname(os.path.abspath(
                os.path.expanduser(current_file_path)))
            pdf_file_path = os.path.join(
                current_directory_path,
                'output.pdf',
                )
            lilypond_file = self()
            persist(lilypond_file).as_pdf(
                pdf_file_path=pdf_file_path,
                remove_ly=False,
                )
            print '\tfinished in {} seconds'.format(
                timer.elapsed_time)

    def color_piano_conflicts(self):
        message = '\tcoloring piano conflicts'
        with systemtools.ProgressIndicator(message) as progress_indicator:
            component = self.score['Piano Staff Group']
            for vertical_moment in iterate(component).by_vertical_moment():
                pitch_numbers = collections.Counter()
                notes_and_chords = vertical_moment.notes_and_chords
                for note_or_chord in notes_and_chords:
                    if isinstance(note_or_chord, scoretools.Note):
                        pitch_number = note_or_chord.written_pitch.pitch_number
                        pitch_number = float(pitch_number)
                        pitch_numbers[pitch_number] += 1
                    else:
                        for pitch in note_or_chord.written_pitches:
                            pitch_number = pitch.pitch_number
                            pitch_number = float(pitch_number)
                            pitch_numbers[pitch_number] += 1
                conflict_pitch_numbers = set()
                for pitch_number, count in pitch_numbers.iteritems():
                    if 1 < count:
                        conflict_pitch_numbers.add(pitch_number)
                if not conflict_pitch_numbers:
                    continue
                for note_or_chord in notes_and_chords:
                    if isinstance(note_or_chord, scoretools.Note):
                        pitch_number = note_or_chord.written_pitch.pitch_number
                        pitch_number = float(pitch_number)
                        if pitch_number in conflict_pitch_numbers:
                            note_or_chord.note_head.tweak.color = 'red'
                            progress_indicator.advance()
                    else:
                        for note_head in note_or_chord.note_heads:
                            pitch_number = note_head.written_pitch.pitch_number
                            pitch_number = float(pitch_number)
                            if pitch_number in conflict_pitch_numbers:
                                note_head.tweak.color = 'red'
                                progress_indicator.advance()

    def configure_lilypond_file(self):
        print '\tconfiguring lilypond file'
        lilypond_file = lilypondfiletools.LilyPondFile()
        lilypond_file.use_relative_includes = True
        score_block = lilypondfiletools.Block(name='score')
        score_block.items.append(self.score)
        lilypond_file.items.append(score_block)
        for file_path in plague_water_configuration.stylesheets_file_paths:
            file_name = os.path.split(file_path)[-1]
            relative_file_path = os.path.join(
                '..', '..', 'stylesheets',
                file_name,
                )
            lilypond_file.file_initial_user_includes.append(relative_file_path)
        lilypond_file.file_initial_system_comments[:] = []
        self.lilypond_file = lilypond_file

    def configure_score(self):
        print '\tconfiguring score'
        override(self.score).horizontal_bracket.color = 'red'
        rehearsal_mark_text = 'mark \\markup {{ ' \
            "\\override #'(box-padding . 0.5) " \
            '\\box {} }}'
        rehearsal_mark_text = rehearsal_mark_text.format(
            self.segment_id.upper(),
            )
        rehearsal_mark = indicatortools.LilyPondCommand(rehearsal_mark_text)
        attach(rehearsal_mark, self.score['TimeSignatureContext'][0],
            scope=scoretools.Context)
        attach(self.segment_tempo, self.score['TimeSignatureContext'][0])
        if self.is_final_segment:
            right_column = markuptools.MarkupCommand(
                'right-column', [
                    ' ',
                    ' ',
                    ' ',
                    'Jamaica Plain',
                    'December 2013 - February 2014',
                    ],
                )
            italic = markuptools.MarkupCommand(
                'italic',
                right_column,
                )
            final_markup = Markup(italic, 'down')
            self.score.add_final_markup(final_markup)
            self.score.add_final_bar_line()
        else:
            self.score.add_final_bar_line('||')

    def cleanup_semantic_timespans(self):
        print '\tcleaning up semantic timespans'
        split_offsets = []
        if self.measure_segmentation_talea:
            groups = sequencetools.partition_sequence_by_counts(
                self.time_signatures,
                self.measure_segmentation_talea,
                cyclic=True,
                overhang=True,
                )
            current_offset = Offset(0)
            for group in groups:
                current_offset += sum(x.duration for x in group)
                split_offsets.append(current_offset)
        for context_maker in self.context_makers:
            if context_maker.context_dependencies:
                continue
            context_maker.cleanup_timespans(
                split_offsets=split_offsets,
                )

    def create_dependent_timespans(self):
        print '\tcreating dependent timespans'
        from plague_water import makers
        ordered_context_makers = makers.ContextMaker.order_by_dependencies(
            self.context_makers)
        for context_maker in ordered_context_makers:
            if context_maker.context_dependencies:
                dependencies = [x for x in self.context_makers
                    if x.context_name in context_maker.context_dependencies
                    ]
                context_maker.create_timespans(
                    self.target_segment_duration,
                    context_map=self.context_map,
                    dependencies=dependencies,
                    )

    def create_semantic_timespans(self):
        print '\tcreating semantic timespans'
        from plague_water import makers
        ordered_context_makers = makers.ContextMaker.order_by_dependencies(
            self.context_makers)
        for context_maker in ordered_context_makers:
            if context_maker.context_dependencies:
                continue
            context_maker.create_timespans(
                self.target_segment_duration,
                context_map=self.context_map,
                )

    def create_silent_timespans(self):
        print '\tcreating silent timespans'
        for context_maker in self.context_makers:
            context_maker.create_silent_timespans(
                segment_duration=self.segment_duration,
                time_signatures=self.time_signatures,
                )

    def find_meters(self):
        print '\tfinding meters'
        offset_counter = datastructuretools.TypedCounter(
            item_class=Offset,
            )
        for context_maker in self.context_makers:
            for timespan in context_maker.timespan_inventory:
                offset_counter[timespan.start_offset] += 1
                offset_counter[timespan.stop_offset] += 1
        if not offset_counter:
            offset_counter[self.target_segment_duration] += 1
        meters = metertools.Meter.fit_meters_to_expr(
            offset_counter,
            self.permitted_time_signatures,
            maximum_repetitions=2,
            )
        return meters

    @staticmethod
    def get_segment_target_duration(
        denominator=None,
        numerator=None,
        tempo=None,
        total_duration_in_seconds=None,
        ):
        segment_target_duration_in_seconds = Duration(
            total_duration_in_seconds * numerator,
            denominator,
            )
        tempo_duration_in_seconds = Duration(
            tempo.duration_to_milliseconds(tempo.duration),
            1000,
            )
        target_segment_duration = Duration((
            segment_target_duration_in_seconds / tempo_duration_in_seconds
            ).limit_denominator(16))
        target_segment_duration *= tempo.duration
        return target_segment_duration

    def iterate_containers_and_music_makers(self):
        from plague_water import makers
        for voice in iterate(self.score).by_class(Voice):
            for container in voice:
                music_maker = \
                    inspect_(container).get_effective(makers.MusicMaker)
                yield container, music_maker

    def populate_rhythms(
        self,
        rewrite_meter=True,
        ):
        print '\tcreating rhythms'
        seed = 0
        for context_maker in self.context_makers:
            context_name = context_maker.context_name
            timespan_inventory = context_maker.timespan_inventory
            realization, seed = self.populate_rhythms_for_one_voice(
                context_map=self.context_map,
                context_name=context_name,
                rewrite_meter=rewrite_meter,
                seed=seed,
                timespan_inventory=timespan_inventory,
                )
            self.score[context_name].extend(realization)

    def populate_rhythms_for_one_voice(
        self,
        context_map=None,
        context_name=None,
        rewrite_meter=True,
        seed=0,
        timespan_inventory=None,
        ):
        result = []
        message = '\t\t{}'.format(context_name)
        with systemtools.ProgressIndicator(message) as progress_indicator:
            change_staff_lines = True
            for music_maker, timespans in itertools.groupby(
                timespan_inventory,
                lambda x: x.annotation,
                ):
                timespans = timespantools.TimespanInventory(timespans)
                durations = [x.duration for x in timespans]
                start_offset = timespans[0].start_offset
                music = music_maker.create_rhythms(
                    durations,
                    change_staff_lines=change_staff_lines,
                    initial_offset=start_offset,
                    meter_cache=self.cached_meters,
                    meters=self.meters,
                    rewrite_meter=rewrite_meter,
                    seed=seed,
                    )
                attach(music_maker, music, scope=scoretools.Context)
                seed += 1
                result.append(music)
                progress_indicator.advance()
        return result, seed

    def populate_time_signature_context(self):
        print '\tpopulating time signature context'
        measures = scoretools.make_spacer_skip_measures(
            self.time_signatures)
        self.score['TimeSignatureContext'].extend(measures)

    @staticmethod
    def remap_sequence(sequence, range_pairs):
        result = []
        for old_element in sequence:
            new_element = old_element
            for input_range, output_range in range_pairs:
                input_low, input_high = input_range
                if input_low <= old_element <= input_high:
                    output_low, output_high = output_range
                    output_difference = output_high - output_low
                    new_element -= input_low
                    new_element %= (output_difference + 1)
                    new_element += output_low
            result.append(new_element)
        return type(sequence)(result)

    def remove_empty_trailing_measures(self):
        print '\tremoving empty trailing measures'
        measure_start_offsets = mathtools.cumulative_sums(
            time_signature.duration
            for time_signature in self.time_signatures
            )[:-1]
        meters = list(self.meters)
        time_signatures = list(self.time_signatures)
        timespan_inventories = [
            context_maker.timespan_inventory
            for context_maker in self.context_makers
            if context_maker.timespan_inventory
            ]
        maximum_performed_offset = max(
            timespan_inventory.stop_offset
            for timespan_inventory in timespan_inventories
            )
        while maximum_performed_offset <= measure_start_offsets[-1]:
            measure_start_offsets.pop()
            meters.pop()
            time_signatures.pop()
        self.meters = tuple(meters)
        self.time_signatures = tuple(time_signatures)
        self.segment_duration = sum(
            time_signature.duration
            for time_signature in self.time_signatures
            )
