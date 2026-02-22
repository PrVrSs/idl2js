import pytest

from idl2js.generators.coverage import CoverageTracker
from idl2js.generators.strategy import GenerationStrategy


class TestCoverageTracker:
    def test_initial_state(self):
        tracker = CoverageTracker()
        assert tracker.total_samples == 0

    def test_record_type(self):
        tracker = CoverageTracker()
        tracker.record_type('long')
        tracker.record_type('long')
        tracker.record_type('short')
        report = tracker.report()
        assert report['type_distribution'] == {'long': 2, 'short': 1}

    def test_record_sample(self):
        tracker = CoverageTracker()
        tracker.record_sample()
        tracker.record_sample()
        assert tracker.total_samples == 2

    def test_record_enum_value(self):
        tracker = CoverageTracker()
        tracker.record_enum_value('Color', 'red')
        tracker.record_enum_value('Color', 'blue')
        tracker.record_enum_value('Color', 'red')
        report = tracker.report()
        assert report['enum_coverage']['Color'] == 2

    def test_record_value_class(self):
        tracker = CoverageTracker()
        tracker.record_value_class('long', 'boundary')
        tracker.record_value_class('long', 'zero')
        tracker.record_value_class('long', 'boundary')
        report = tracker.report()
        assert set(report['value_classes']['long']) == {'boundary', 'zero'}

    def test_record_array_size(self):
        tracker = CoverageTracker()
        tracker.record_array_size('sequence<long>', 0)
        tracker.record_array_size('sequence<long>', 5)
        tracker.record_array_size('sequence<long>', 0)
        report = tracker.report()
        assert report['array_sizes']['sequence<long>'] == [0, 5]

    def test_type_coverage(self):
        tracker = CoverageTracker()
        tracker.record_type('long')
        tracker.record_type('short')
        all_types = ['long', 'short', 'byte', 'octet']
        assert tracker.type_coverage(all_types) == 0.5

    def test_type_coverage_empty(self):
        tracker = CoverageTracker()
        assert tracker.type_coverage([]) == 1.0

    def test_type_coverage_full(self):
        tracker = CoverageTracker()
        tracker.record_type('long')
        tracker.record_type('short')
        assert tracker.type_coverage(['long', 'short']) == 1.0

    def test_enum_coverage(self):
        tracker = CoverageTracker()
        tracker.record_enum_value('Color', 'red')
        tracker.record_enum_value('Color', 'blue')
        all_values = ['red', 'blue', 'green']
        assert tracker.enum_coverage('Color', all_values) == pytest.approx(2 / 3)

    def test_enum_coverage_empty(self):
        tracker = CoverageTracker()
        assert tracker.enum_coverage('Color', []) == 1.0

    def test_uncovered_enum_values(self):
        tracker = CoverageTracker()
        tracker.record_enum_value('Color', 'red')
        all_values = ['red', 'blue', 'green']
        uncovered = tracker.uncovered_enum_values('Color', all_values)
        assert uncovered == {'blue', 'green'}

    def test_suggest_weights_initial(self):
        tracker = CoverageTracker()
        weights = tracker.suggest_weights('long')
        assert weights[GenerationStrategy.BOUNDARY] > \
               weights[GenerationStrategy.RANDOM]

    def test_suggest_weights_after_boundary(self):
        tracker = CoverageTracker()
        tracker.record_value_class('long', 'boundary')
        weights = tracker.suggest_weights('long')
        assert weights[GenerationStrategy.SPECIAL] > \
               weights[GenerationStrategy.BOUNDARY]

    def test_reset(self):
        tracker = CoverageTracker()
        tracker.record_type('long')
        tracker.record_sample()
        tracker.record_enum_value('Color', 'red')
        tracker.reset()
        assert tracker.total_samples == 0
        report = tracker.report()
        assert report['types_covered'] == 0

    def test_report_structure(self):
        tracker = CoverageTracker()
        report = tracker.report()
        assert 'total_samples' in report
        assert 'types_covered' in report
        assert 'type_distribution' in report
        assert 'enum_coverage' in report
        assert 'value_classes' in report
        assert 'array_sizes' in report
