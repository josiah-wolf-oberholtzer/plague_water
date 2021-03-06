# -*- encoding: utf-8 -*-
from abjad import *
from plague_water.makers.PlagueWaterObject import PlagueWaterObject


class PercussionPitchAgent(PlagueWaterObject):

    ### CLASS VARIABLES ###

    __slots__ = (
        '_lengths',
        '_lengths_cursor',
        '_pitches',
        '_pitches_cursor',
        '_talea',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        lengths=None,
        pitches=None,
        talea=None,
        ):
        if lengths is None:
            lengths = (1,)
        assert len(lengths)
        assert mathtools.all_are_positive_integers(lengths)
        lengths = tuple(lengths)
        self._lengths = lengths
        pitches = pitchtools.PitchSegment(
            items=pitches,
            item_class=pitchtools.NamedPitch,
            )
        assert len(pitches)
        self._pitches = pitches
        if talea is None:
            talea = range(len(pitches))
        talea = tuple(int(x) for x in talea)
        assert 0 <= min(talea)
        assert max(talea) < len(pitches)
        self._talea = talea
        self._lengths_cursor = self._expr_to_statal_server_cursor(
            lengths)
        pitches_cursor = [pitches[x] for x in talea]
        self._pitches_cursor = self._expr_to_statal_server_cursor(
            pitches_cursor)

    ### SPECIAL METHODS ###

    def __call__(
        self,
        logical_tie,
        previous_pitch_set=None,
        segment_duration=None,
        ):
        length = self._lengths_cursor()[0]
        pitches = set(self._pitches_cursor(length))
        while len(pitches) != length:
            pitches.update(self._pitches_cursor())
        pitches = sorted(pitches)
        if len(pitches) == 1:
            for note in logical_tie:
                note.written_pitch = pitches[0]
        else:
            for note in logical_tie:
                chord = Chord(note)
                chord.written_pitches = pitches
                mutate(note).replace(chord)
        pitches = pitchtools.PitchSet(pitches)
        return pitches

    ### PUBLIC METHODS ###

    def rotate(self, n=1):
        n = int(n)
        lengths = sequencetools.rotate_sequence(self.lengths, n)
        pitches = sequencetools.rotate_sequence(self.pitches, n)
        talea = self.talea
        if talea != range(len(pitches)):
            talea = sequencetools.rotate_sequence(talea, n)
        return new(
            self,
            lengths=lengths,
            pitches=pitches,
            talea=talea,
            )

    ### PUBLIC PROPERTIES ###

    @property
    def lengths(self):
        return self._lengths

    @property
    def pitches(self):
        return self._pitches

    @property
    def talea(self):
        return self._talea
