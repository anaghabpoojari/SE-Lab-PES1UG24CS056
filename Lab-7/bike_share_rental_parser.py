import re

def parse_ride_duration(text):
    """
    Convert a ride duration in HH:MM format to total minutes.

    Valid input: exactly two digits for hours, a colon, and two digits
    for minutes (00-59). Invalid input returns None.
    """
    if not isinstance(text, str):
        return None

    value = text.strip()

    if not re.fullmatch(r"\d{2}:\d{2}", value):
        return None

    hours, minutes = map(int, value.split(":"))

    if minutes > 59:
        return None

    return hours * 60 + minutes


def format_station_code(code):
    """
    Format a station code such as 'a12' as 'A-12'.

    A valid code contains one alphabetic zone letter followed by
    one or more digits. Invalid input returns None.
    """
    if not isinstance(code, str):
        return None

    value = code.strip()

    if not re.fullmatch(r"[A-Za-z]\d+", value):
        return None

    return value[0].upper() + "-" + value[1:]


def parse_ride_log(line):
    """
    Parse 'bike_type,minutes,subscriber' into a tuple.

    The bike type must be non-empty, minutes must be a non-negative
    integer, and subscriber must be 'yes' or 'no'.
    Invalid input returns None.
    """
    if not isinstance(line, str):
        return None

    parts = line.split(",")

    if len(parts) != 3:
        return None

    bike_type = parts[0].strip()
    minutes_text = parts[1].strip()
    subscriber_text = parts[2].strip().lower()

    if not bike_type:
        return None

    if not re.fullmatch(r"\d+", minutes_text):
        return None

    if subscriber_text not in {"yes", "no"}:
        return None

    return (
        bike_type,
        int(minutes_text),
        subscriber_text == "yes"
    )


def main():
    print("==== Running parse_ride_duration ====")
    value = input("Enter a ride duration as HH:MM (e.g. 01:15): ")

    result = parse_ride_duration(value)

    if result is not None:
        print("Duration in minutes:", result)
    else:
        print("Invalid duration")

    print("\n==== Running format_station_code ====")
    value = input("Enter a station code (e.g. a12): ")

    result = format_station_code(value)

    if result is not None:
        print("Formatted station code:", result)
    else:
        print("Invalid station code")

    print("\n==== Running parse_ride_log ====")
    value = input(
        "Enter a ride log line as type,minutes,subscriber "
        "(e.g. electric,45,yes): "
    )

    result = parse_ride_log(value)

    if result is not None:
        print("Parsed ride log:", result)
    else:
        print("Invalid ride log")


if __name__ == "__main__":
    main()
