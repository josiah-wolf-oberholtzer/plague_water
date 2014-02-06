# -*- encoding: utf-8 -*-
from abjad import *
from plague_water.makers.TimespanAgent import TimespanAgent


class DependentTimespanAgent(TimespanAgent):

    ### CLASS VARIABLES ###

    __slots__ = (
        '_use_attacks',
        '_use_releases',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        use_attacks=True,
        use_releases=False,
        ):
        TimespanAgent.__init__(
            self,
            can_be_split=False,
            minimum_timespan_duration=None,
            )
        self._use_attacks = bool(use_attacks)
        self._use_releases = bool(use_releases)

    ### SPECIAL METHODS ###

    def __call__(
        self,
        dependencies=None,
        initial_offset=None,
        maximum_offset=None,
        music_maker=None,
        ):
        assert initial_offset == 0
        assert dependencies
        dependency_timespans = timespantools.TimespanInventory()
        for dependency in dependencies:
            dependency_timespans.extend(dependency.timespan_inventory)
        dependency_timespans.sort()
        timespan_inventory = timespantools.TimespanInventory()
        for group in dependency_timespans.partition(
            include_tangent_timespans=True):
            offsets = set([group.start_offset, group.stop_offset])
            if self.use_attacks:
                for timespan in group:
                    offsets.add(timespan.start_offset)
            if self.use_releases:
                for timespan in group:
                    offsets.add(timespan.stop_offset)
            offsets = sorted(offsets)
            for start, stop in sequencetools.iterate_sequence_nwise(offsets):
                timespan = timespantools.AnnotatedTimespan(
                    annotation=music_maker,
                    start_offset=start,
                    stop_offset=stop,
                    )
                timespan_inventory.append(timespan)
        timespan_inventory.sort()
        return timespan_inventory, maximum_offset

    ### PUBLIC PROPERTIES ###

    @property
    def use_attacks(self):
        return self._use_attacks

    @property
    def use_releases(self):
        return self._use_releases