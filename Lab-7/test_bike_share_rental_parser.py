import re

from hypothesis import given, strategies as st

from bike_share_rental_parser import (
    parse_ride_duration,
    format_station_code,
    parse_ride_log
)


@given(st.one_of(st.text(), st.none()))
def test_parse_ride_duration_no_crash(s):
    try:
        result = parse_ride_duration(s)
    except Exception as e:
        assert False, f"parse_ride_duration crashed for input {s!r}: {e}"

    valid = (
        isinstance(s, str)
        and re.fullmatch(r"\d{2}:\d{2}", s.strip()) is not None
        and int(s.strip().split(":")[1]) <= 59
    )

    if valid:
        hours, minutes = map(int, s.strip().split(":"))
        assert result == hours * 60 + minutes
    else:
        assert result is None


@given(st.one_of(st.text(), st.none()))
def test_format_station_code_no_crash(s):
    try:
        result = format_station_code(s)
    except Exception as e:
        assert False, f"format_station_code crashed for input {s!r}: {e}"

    valid = (
        isinstance(s, str)
        and re.fullmatch(r"[A-Za-z]\d+", s.strip()) is not None
    )

    if valid:
        value = s.strip()
        assert result == value[0].upper() + "-" + value[1:]
    else:
        assert result is None


@given(st.one_of(st.text(), st.none()))
def test_parse_ride_log_no_crash(s):
    try:
        result = parse_ride_log(s)
    except Exception as e:
        assert False, f"parse_ride_log crashed for input {s!r}: {e}"

    valid = False
    expected = None

    if isinstance(s, str):
        parts = s.split(",")

        if len(parts) == 3:
            bike_type = parts[0].strip()
            minutes_text = parts[1].strip()
            subscriber_text = parts[2].strip().lower()

            if (
                bike_type
                and re.fullmatch(r"\d+", minutes_text)
                and subscriber_text in {"yes", "no"}
            ):
                valid = True
                expected = (
                    bike_type,
                    int(minutes_text),
                    subscriber_text == "yes"
                )

    if valid:
        assert result == expected
    else:
        assert result is None
