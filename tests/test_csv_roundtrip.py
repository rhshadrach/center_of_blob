import warnings
from pathlib import Path

import pandas as pd
import pytest
import pytestqt.qtbot

import center_of_blob as cob
from center_of_blob.main import MainWindow
from tests import actions

SQUARE = [(90, 90), (110, 90), (110, 110), (90, 110)]


def write_and_reload(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    main: MainWindow,
    path: Path,
) -> MainWindow:
    actions.save_csv(monkeypatch, qtbot, main, str(path))
    reloaded = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, reloaded, "data/sample.tif")
    actions.load_csv(monkeypatch, qtbot, reloaded, str(path))
    return reloaded


def test_round_trip(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    tmp_path: Path,
    error_messages: list[str],
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_set_origin(qtbot, main)
    actions.click_main_image(qtbot, main, [(50, 50)])
    actions.draw_region(monkeypatch, qtbot, main, SQUARE, "inner")
    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(100, 100)])
    actions.click_color_channel(qtbot, main, channel=3)
    actions.click_main_image(qtbot, main, [(300, 200)])

    reloaded = write_and_reload(monkeypatch, qtbot, main, tmp_path / "out.csv")
    assert reloaded.origin == main.origin
    assert reloaded.centers.keys() == main.centers.keys()
    for point, center in main.centers.items():
        assert reloaded.centers[point].color == center.color
        # Centers without a region are covered by test_loaded_center_without_region.
        if center.region:
            assert reloaded.centers[point].region == center.region
    assert [(r.name, r.points) for r in reloaded.regions] == [
        (r.name, r.points) for r in main.regions
    ]
    assert error_messages == []


def test_write_then_rewrite_is_identical(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot, tmp_path: Path
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    main.centers = cob.Centers({(20, 30): cob.Center(20, 30, (255, 0, 0), "")})
    main.regions = [cob.Region([(10, 10), (10, 40), (40, 40), (40, 10)], "a")]
    reloaded = write_and_reload(monkeypatch, qtbot, main, tmp_path / "first.csv")
    actions.save_csv(monkeypatch, qtbot, reloaded, str(tmp_path / "second.csv"))
    pd.testing.assert_frame_equal(
        pd.read_csv(tmp_path / "first.csv"), pd.read_csv(tmp_path / "second.csv")
    )


def test_round_trip_center_at_origin(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot, tmp_path: Path
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    main.centers = cob.Centers({(50, 50): cob.Center(50, 50, (255, 0, 0), "")})
    reloaded = write_and_reload(monkeypatch, qtbot, main, tmp_path / "out.csv")
    assert reloaded.centers.keys() == {(50, 50)}


def test_loaded_center_without_region(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.load_csv(monkeypatch, qtbot, main, "data/sample.csv")
    assert [center.region for center in main.centers.values()] == ["", ""]


def test_round_trip_regions_with_same_name(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot, tmp_path: Path
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    main.centers = cob.Centers({(20, 30): cob.Center(20, 30, (255, 0, 0), "")})
    main.regions = [
        cob.Region([(10, 10), (10, 40), (40, 40), (10, 10)], "a"),
        cob.Region([(100, 100), (100, 140), (140, 140), (100, 100)], "a"),
    ]
    reloaded = write_and_reload(monkeypatch, qtbot, main, tmp_path / "out.csv")
    assert [r.points for r in reloaded.regions] == [r.points for r in main.regions]


def test_round_trip_region_with_empty_name(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot, tmp_path: Path
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    main.centers = cob.Centers({(20, 30): cob.Center(20, 30, (255, 0, 0), "")})
    main.regions = [cob.Region([(10, 10), (10, 40), (40, 40), (10, 10)], "")]
    reloaded = write_and_reload(monkeypatch, qtbot, main, tmp_path / "out.csv")
    assert len(reloaded.regions) == 1


@pytest.mark.parametrize("name", ["NA", "nan", "12", "None"])
def test_round_trip_region_name_kept_as_written(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    tmp_path: Path,
    name: str,
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    main.centers = cob.Centers({(20, 20): cob.Center(20, 20, (255, 0, 0), name)})
    main.regions = [cob.Region([(10, 10), (10, 40), (40, 40), (10, 10)], name)]
    reloaded = write_and_reload(monkeypatch, qtbot, main, tmp_path / "out.csv")
    assert [region.name for region in reloaded.regions] == [name]
    assert reloaded.centers[20, 20].region == name


def test_round_trip_keeps_region_order(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot, tmp_path: Path
) -> None:
    # When regions overlap, the first one decides a center's region, so the
    # order they were drawn in must survive a round trip.
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    main.centers = cob.Centers({(20, 30): cob.Center(20, 30, (255, 0, 0), "")})
    main.regions = [
        cob.Region([(10, 10), (10, 40), (40, 40), (10, 10)], "b"),
        cob.Region([(100, 100), (100, 140), (140, 140), (100, 100)], "a"),
    ]
    reloaded = write_and_reload(monkeypatch, qtbot, main, tmp_path / "out.csv")
    assert [(r.name, r.points) for r in reloaded.regions] == [
        (r.name, r.points) for r in main.regions
    ]


def test_load_unclosed_region(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    tmp_path: Path,
    error_messages: list[str],
) -> None:
    # A hand-written file whose regions don't repeat their first point.
    path = tmp_path / "unclosed.csv"
    path.write_text(
        "kind,x,y,distance,red,green,blue,region\n"
        "origin,10,10,0.0,0,0,0,\n"
        "center,20,30,5.0,255,0,0,a\n"
        "region,10,10,-1,255,69,0,a\n"
        "region,10,40,-1,255,69,0,a\n"
        "region,40,40,-1,255,69,0,a\n"
        "region,100,100,-1,255,69,0,b\n"
        "region,100,140,-1,255,69,0,b\n"
        "region,140,140,-1,255,69,0,b\n"
    )
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.load_csv(monkeypatch, qtbot, main, str(path))
    assert error_messages == []
    assert [(r.name, r.points) for r in main.regions] == [
        ("a", [(10, 10), (10, 40), (40, 40)]),
        ("b", [(100, 100), (100, 140), (140, 140)]),
    ]


def test_write_csv_has_no_warnings(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot, tmp_path: Path
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    main.centers = cob.Centers({(20, 30): cob.Center(20, 30, (255, 0, 0), "")})
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        actions.save_csv(monkeypatch, qtbot, main, str(tmp_path / "out.csv"))


def test_write_csv_requires_origin(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    tmp_path: Path,
    error_messages: list[str],
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.centers = cob.Centers({(20, 30): cob.Center(20, 30, (255, 0, 0), "")})
    actions.save_csv(monkeypatch, qtbot, main, str(tmp_path / "out.csv"))
    assert error_messages == ["Must set origin to write CSV file."]
    assert not (tmp_path / "out.csv").exists()


def test_write_csv_requires_center(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    tmp_path: Path,
    error_messages: list[str],
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    actions.save_csv(monkeypatch, qtbot, main, str(tmp_path / "out.csv"))
    assert error_messages == ["Must set at least one center to write CSV file."]
    assert not (tmp_path / "out.csv").exists()


def test_cancel_save_dialog(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    error_messages: list[str],
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    main.centers = cob.Centers({(20, 30): cob.Center(20, 30, (255, 0, 0), "")})
    before = actions.snapshot(main)
    actions.save_csv(monkeypatch, qtbot, main, "")
    assert error_messages == []
    assert actions.snapshot(main) == before


def test_cancel_load_centers_dialog(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    error_messages: list[str],
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    before = actions.snapshot(main)
    monkeypatch.setattr(cob.popups, "get_centers_filename", lambda *args, **kwargs: "")
    qtbot.mouseClick(main.centers_path_button, actions.QtCore.Qt.LeftButton)
    assert error_messages == []
    assert actions.snapshot(main) == before


def test_load_centers_outside_image(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    tmp_path: Path,
    error_messages: list[str],
) -> None:
    path = tmp_path / "outside.csv"
    path.write_text(
        "kind,x,y,distance,red,green,blue,region\n"
        "origin,10,10,0.0,0,0,0,\n"
        "center,99999,10,5.0,255,0,0,\n"
    )
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    before = actions.snapshot(main)
    actions.load_csv(monkeypatch, qtbot, main, str(path))
    assert error_messages == [
        "Centers file has points outside of image bounds. Refusing file."
    ]
    assert actions.snapshot(main) == before


@pytest.mark.parametrize(
    "contents",
    [
        "origin,10,10,0.0,0,0,0,\ncenter,99999,10,5.0,255,0,0,\n",
        "center,20,30,5.0,255,0,0,\n",
    ],
    ids=["center_outside_image", "no_origin"],
)
def test_refused_centers_file_keeps_existing_work(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    tmp_path: Path,
    error_messages: list[str],
    contents: str,
) -> None:
    path = tmp_path / "refused.csv"
    path.write_text("kind,x,y,distance,red,green,blue,region\n" + contents)
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    main.centers = cob.Centers({(20, 30): cob.Center(20, 30, (255, 0, 0), "")})
    main.regions = [cob.Region([(10, 10), (10, 40), (40, 40), (10, 10)], "a")]
    before = actions.snapshot(main)
    actions.load_csv(monkeypatch, qtbot, main, str(path))
    assert len(error_messages) == 1
    assert actions.snapshot(main) == before


def test_load_centers_without_origin(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    tmp_path: Path,
    error_messages: list[str],
) -> None:
    path = tmp_path / "no_origin.csv"
    path.write_text(
        "kind,x,y,distance,red,green,blue,region\ncenter,20,30,5.0,255,0,0,\n"
    )
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    before = actions.snapshot(main)
    actions.load_csv(monkeypatch, qtbot, main, str(path))
    assert len(error_messages) == 1
    assert error_messages[0].startswith("Failed to find origin in centers file.")
    assert actions.snapshot(main) == before


def test_load_centers_malformed(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    tmp_path: Path,
    error_messages: list[str],
) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("not,a,centers,file\n1,2,3,4\n")
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    main.centers = cob.Centers({(20, 30): cob.Center(20, 30, (255, 0, 0), "")})
    main.regions = [cob.Region([(10, 10), (10, 40), (40, 40), (10, 10)], "a")]
    before = actions.snapshot(main)
    actions.load_csv(monkeypatch, qtbot, main, str(path))
    assert len(error_messages) == 1
    assert error_messages[0].startswith("Failed to load file")
    assert actions.snapshot(main) == before
