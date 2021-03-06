# -*- encoding: utf-8 -*-
from abjad import *
from plague_water.makers.PlagueWaterObject import PlagueWaterObject


class KeyClusterExpression(PlagueWaterObject):
    r'''A key cluster expression.

        >>> from plague_water import makers
        >>> key_cluster_expression = makers.KeyClusterExpression(
        ...     arpeggio_direction=Up,
        ...     include_black_keys=False,
        ...     )
        >>> print(format(key_cluster_expression))
        plague_water.makers.KeyClusterExpression(
            arpeggio_direction=Up,
            include_black_keys=False,
            include_white_keys=True,
            staff_space_width=5,
            )

    ::

        >>> staff = Staff("c'4 d'4 ~ d'4 e'4")
        >>> logical_tie = inspect_(staff[1]).get_logical_tie()
        >>> key_cluster_expression(logical_tie)
        >>> f(staff)
        \new Staff {
            c'4
            \arpeggioArrowUp
            \once \override Accidental.stencil = ##f
            \once \override AccidentalCautionary.stencil = ##f
            \once \override Arpeggio.X-offset = #-2
            \once \override NoteHead.stencil = #ly:text-interface::print
            \once \override NoteHead.text = \markup {
                \filled-box #'(-0.6 . 0.6) #'(-0.7 . 0.7) #0.25
            }
            <b d' f'>4 \arpeggio ~
                ^ \markup {
                    \center-align
                        \natural
                    }
            \once \override Accidental.stencil = ##f
            \once \override AccidentalCautionary.stencil = ##f
            \once \override Arpeggio.X-offset = #-2
            \once \override NoteHead.stencil = #ly:text-interface::print
            \once \override NoteHead.text = \markup {
                \filled-box #'(-0.6 . 0.6) #'(-0.7 . 0.7) #0.25
            }
            <b d' f'>4
            e'4
        }

    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_arpeggio_direction',
        '_include_black_keys',
        '_include_white_keys',
        '_staff_space_width',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        arpeggio_direction=None,
        include_black_keys=True,
        include_white_keys=True,
        staff_space_width=5,
        ):
        assert 2 < staff_space_width and (int(staff_space_width) % 2)
        assert include_black_keys or include_white_keys
        assert arpeggio_direction in (Up, Down, None)
        self._arpeggio_direction = arpeggio_direction
        self._include_black_keys = bool(include_black_keys)
        self._include_white_keys = bool(include_white_keys)
        self._staff_space_width = int(staff_space_width)

    ### SPECIAL METHODS ###

    def __call__(self, logical_tie):
        assert isinstance(logical_tie, selectiontools.LogicalTie), logical_tie
        center_pitch = logical_tie[0].written_pitch
        starting_diatonic_number = \
            center_pitch.diatonic_pitch_number - (self.staff_space_width / 2)
        diatonic_numbers = [starting_diatonic_number]
        for i in range(1, (self.staff_space_width / 2) + 1):
            step = 2 * i
            diatonic_number = starting_diatonic_number + step
            diatonic_numbers.append(diatonic_number)
        chromatic_numbers = [
            (12 * (x // 7)) +
            pitchtools.PitchClass._diatonic_pitch_class_number_to_pitch_class_number[
                x % 7]
            for x in diatonic_numbers
            ]
        chord_pitches = [pitchtools.NamedPitch(x)
            for x in chromatic_numbers]
        for i, leaf in enumerate(logical_tie):
            chord = Chord(leaf)
            chord.written_pitches = chord_pitches
            grace_containers = inspect_(leaf).get_grace_containers('after')
            if grace_containers:
                old_grace_container = grace_containers[0]
                grace_notes = old_grace_container.select_leaves()
                detach(scoretools.GraceContainer, leaf)
            mutate(leaf).replace(chord)
            if i:
                key_cluster = indicatortools.KeyCluster(
                    include_black_keys=self.include_black_keys,
                    include_white_keys=self.include_white_keys,
                    suppress_markup=True,
                    )
                attach(key_cluster, chord)
            else:
                key_cluster = indicatortools.KeyCluster(
                    include_black_keys=self.include_black_keys,
                    include_white_keys=self.include_white_keys,
                    markup_direction=Up,
                    )
                attach(key_cluster, chord)
                if self.arpeggio_direction is not None:
                    arpeggio = indicatortools.Arpeggio(
                        direction=self.arpeggio_direction,
                        )
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
    def include_black_keys(self):
        return self._include_black_keys

    @property
    def include_white_keys(self):
        return self._include_white_keys

    @property
    def staff_space_width(self):
        return self._staff_space_width