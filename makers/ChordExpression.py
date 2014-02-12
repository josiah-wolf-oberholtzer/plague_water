# -*- encoding: utf-8 -*-
from abjad import *
from plague_water.makers.PlagueWaterObject import PlagueWaterObject


class ChordExpression(PlagueWaterObject):
    r'''A chord expression.

    ::

        >>> from plague_water import makers
        >>> chord_expression = makers.ChordExpression(
        ...     arpeggio_direction=Down,
        ...     interval_numbers=(-1, 3, 7),
        ...     )
        >>> print format(chord_expression)
        makers.ChordExpression(
            arpeggio_direction=Down,
            interval_numbers=frozenset([3, -1, 7]),
            )

    ::

        >>> staff = Staff("c'4 d'4 ~ d'4 e'4")
        >>> logical_tie = inspect_(staff[1]).get_logical_tie()
        >>> chord_expression(logical_tie)
        >>> f(staff)
        \new Staff {
            c'4
            \arpeggioArrowDown
            <cs' d' f' a'>4 \arpeggio ~
            <cs' d' f' a'>4
            e'4
        }

    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_arpeggio_direction',
        '_interval_numbers',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        arpeggio_direction=None,
        interval_numbers=None,
        ):
        assert arpeggio_direction in (Up, Down, None)
        interval_numbers = frozenset(
            x for x in interval_numbers
            if x != 0
            )
        assert len(interval_numbers)
        self._arpeggio_direction = arpeggio_direction
        self._interval_numbers = interval_numbers

    ### SPECIAL METHODS ###

    def __call__(self, logical_tie):
        assert isinstance(logical_tie, selectiontools.LogicalTie), logical_tie
        center_pitch = logical_tie[0].written_pitch
        pitches = [center_pitch + x for x in self.interval_numbers]
        pitches.append(center_pitch)
        for i, leaf in enumerate(logical_tie):
            chord = Chord(leaf)
            chord.written_pitches = pitches
            grace_containers = inspect_(leaf).get_grace_containers('after')
            if grace_containers:
                old_grace_container = grace_containers[0]
                grace_notes = old_grace_container.select_leaves()
                detach(scoretools.GraceContainer, leaf)
            mutate(leaf).replace(chord)
            if not i and self.arpeggio_direction is not None:
                arpeggio = indicatortools.Arpeggio(self.arpeggio_direction)
                attach(arpeggio, chord)
            if grace_containers:
                new_grace_container = scoretools.GraceContainer(
                    grace_notes,
                    kind='after',
                    )
                attach(new_grace_container, chord)

    ### PUBLIC PROPERTIES ###

    @property
    def arpeggio_direction(self):
        return self._arpeggio_direction

    @property
    def interval_numbers(self):
        return self._interval_numbers
