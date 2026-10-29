
import pytest

from bike_share_rental import ride_cost, dock_status, can_unlock


def test_standard_ride():
    assert ride_cost("standard", 45, False, False) == 40


def test_electric_ride():
    assert ride_cost("electric", 30, False, False) == 35


def test_cargo_ride():
    assert ride_cost("cargo", 30, False, False) == 50


def test_unknown_bike_type():
    with pytest.raises(ValueError, match="unknown bike type"):
        ride_cost("mountain", 30, False, False)


def test_zero_duration():
    with pytest.raises(ValueError, match="invalid duration"):
        ride_cost("standard", 0, False, False)


def test_negative_duration():
    with pytest.raises(ValueError, match="invalid duration"):
        ride_cost("standard", -10, False, False)

def test_subscriber_gets_one_block_discount():
    assert ride_cost("standard", 45, True, False) == 20


def test_subscriber_free_ride_after_discount():
    assert ride_cost("standard", 30, True, False) == 0


def test_peak_hour_standard_bike():
    assert ride_cost("standard", 30, False, True) == 35


def test_peak_hour_electric_bike():
    assert ride_cost("electric", 30, False, True) == 50


def test_peak_hour_cargo_bike_has_no_peak_surcharge():
    assert ride_cost("cargo", 30, False, True) == 50


def test_long_ride_surcharge():
    assert ride_cost("standard", 181, False, False) == 240


def test_long_peak_hour_ride():
    assert ride_cost("standard", 181, False, True) == 255


def test_exactly_180_minutes_has_no_long_ride_surcharge():
    assert ride_cost("standard", 180, False, False) == 120


# --------------------------------------------------
# DOCK STATUS TESTS
# --------------------------------------------------

def test_dock_available():
    assert dock_status(5, 10) == "available"


def test_empty_dock():
    assert dock_status(0, 10) == "empty"


def test_full_dock():
    assert dock_status(10, 10) == "full"


def test_dock_with_few_bikes():
    assert dock_status(2, 10) == "few bikes"


def test_dock_with_few_slots():
    assert dock_status(8, 10) == "few slots"


def test_dock_with_one_bike():
    assert dock_status(1, 10) == "few bikes"


def test_invalid_zero_capacity():
    with pytest.raises(ValueError, match="invalid capacity"):
        dock_status(0, 0)


def test_invalid_negative_capacity():
    with pytest.raises(ValueError, match="invalid capacity"):
        dock_status(0, -5)


def test_negative_bike_count():
    with pytest.raises(ValueError, match="invalid bike count"):
        dock_status(-1, 10)


def test_bike_count_exceeds_capacity():
    with pytest.raises(ValueError, match="invalid bike count"):
        dock_status(11, 10)


# --------------------------------------------------
# CAN UNLOCK TESTS
# --------------------------------------------------

def test_cannot_unlock_with_active_ride():
    assert can_unlock(500, True, 25) is False


def test_cannot_unlock_under_16():
    assert can_unlock(500, False, 15) is False


def test_under_18_with_insufficient_balance():
    assert can_unlock(99, False, 16) is False

def test_under_18_with_exact_minimum_balance():
    assert can_unlock(100, False, 16) is True




