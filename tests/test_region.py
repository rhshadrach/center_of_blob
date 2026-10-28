import pytest

from cellcensus.region import Region


def test_contains_point_without_points() -> None:
    assert not Region().contains_point((0, 0))


@pytest.mark.parametrize(
    ("point", "expected"),
    [((10, 10), True), ((10, 40), True), ((10, 41), False), ((40, 40), False)],
)
def test_contains_point_within_radius(point: tuple[int, int], expected: bool) -> None:
    # Within 30 pixels of a corner, including exactly 30.
    region = Region([(10, 10), (100, 100)])
    assert region.contains_point(point, radius=30) == expected
