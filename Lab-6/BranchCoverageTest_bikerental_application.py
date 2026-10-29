
import pytest

from bike_share_rental import ride_cost, dock_status, can_unlock


# ==================================================
# BRANCH COVERAGE TESTS: ride_cost()
# ==================================================

def test_ride_cost_valid_bike_types():
    assert ride_cost("standard", 30, False, False) == 20
    assert ride_cost("electric", 30, False, False) == 35
    assert ride_cost("cargo", 30, False, False) == 50


def test_ride_cost_unknown_bike_type():
    with pytest.raises(ValueError, match="unknown bike type"):
        ride_cost("mountain", 30, False, False)


def test_ride_cost_invalid_duration():
    with pytest.raises(ValueError, match="invalid duration"):
        ride_cost("standard", 0, False, False)

    with pytest.raises(ValueError, match="invalid duration"):
        ride_cost("standard", -10, False, False)


def test_ride_cost_subscriber_zero_cost_branch():
    # A 30-minute subscriber ride reduces blocks from 1 to 0.
    assert ride_cost("standard", 30, True, False) == 0


def test_ride_cost_subscriber_positive_cost_branch():
    # A 60-minute ride has 2 blocks; subscriber discount leaves 1.
    assert ride_cost("standard", 60, True, False) == 20


def test_ride_cost_non_subscriber():
    assert ride_cost("standard", 30, False, False) == 20


def test_ride_cost_peak_surcharge_applies():
    # Peak surcharge applies to standard and electric bikes.
    assert ride_cost("standard", 30, False, True) == 35
    assert ride_cost("electric", 30, False, True) == 50


def test_ride_cost_peak_surcharge_not_applied_to_cargo():
    assert ride_cost("cargo", 30, False, True) == 50


def test_ride_cost_long_ride_surcharge_applies():
    assert ride_cost("standard", 181, False, False) == 240


def test_ride_cost_long_ride_surcharge_not_applied():
    assert ride_cost("standard", 180, False, False) == 120


def test_ride_cost_both_surcharges():
    assert ride_cost("standard", 181, False, True) == 255


# ==================================================
# BRANCH COVERAGE TESTS: dock_status()
# ==================================================

def test_dock_status_invalid_capacity():
    with pytest.raises(ValueError, match="invalid capacity"):
        dock_status(0, 0)

    with pytest.raises(ValueError, match="invalid capacity"):
        dock_status(0, -1)


def test_dock_status_negative_bike_count():
    with pytest.raises(ValueError, match="invalid bike count"):
        dock_status(-1, 10)


def test_dock_status_bikes_exceed_capacity():
    with pytest.raises(ValueError, match="invalid bike count"):
        dock_status(11, 10)


def test_dock_status_empty():
    assert dock_status(0, 10) == "empty"


def test_dock_status_full():
    assert dock_status(10, 10) == "full"


def test_dock_status_few_bikes():
    assert dock_status(1, 10) == "few bikes"
    assert dock_status(2, 10) == "few bikes"


def test_dock_status_few_slots():
    assert dock_status(8, 10) == "few slots"
    assert dock_status(9, 10) == "few slots"


def test_dock_status_available():
    assert dock_status(5, 10) == "available"


# ==================================================
# BRANCH COVERAGE TESTS: can_unlock()
# ==================================================

def test_can_unlock_active_ride_true():
    assert can_unlock(500, True, 25) is False


def test_can_unlock_active_ride_false():
    assert can_unlock(500, False, 25) is True


def test_can_unlock_age_below_16():
    assert can_unlock(500, False, 15) is False


def test_can_unlock_age_16_with_insufficient_balance():
    assert can_unlock(99, False, 16) is False


def test_can_unlock_age_16_with_exact_balance():
    assert can_unlock(100, False, 16) is True


def test_can_unlock_age_17_with_sufficient_balance():
    assert can_unlock(100, False, 17) is True


def test_can_unlock_age_18_with_insufficient_balance():
    assert can_unlock(49, False, 18) is False


def test_can_unlock_age_18_with_exact_balance():
    assert can_unlock(50, False, 18) is True


def test_can_unlock_adult_with_sufficient_balance():
    assert can_unlock(100, False, 25) is True
