from datetime import datetime, timezone


def value_to_mm_hr(value):
    """
    Convert value from data to millimeters per hour (mm/hr).

    Parameters:
    value (float): The dBZ value to be converted.

    Returns:
    float: The converted value in millimeters per hour.

    """
    # GEO=0.010000*PV+0.000000 (+ knmi describes needing to multiply by 12)
    return (float(value) * 0.01) * 12

    # formula other  h5 file: GEO = 0.500000 * PV + -32.000000
    # return (0.5 * float(value)) + (-32.0)

    # other formulas for non Nowcast data
    # return max(10 ** ((float(value) - 109) / 32), 0)
    # return 10.0 ** ((float(value) - 23.0)/16.0)


def h5_datetime_to_datetime(h5_datetime):
    """
    Converts an HDF5 datetime string to a UTC datetime object.

    Args:
        h5_datetime (str): The HDF5 datetime string in the format "%d-%b-%Y;%H:%M:%S.%f".

    Returns:
        datetime.datetime: The converted UTC datetime object.

    """

    naive_datetime = datetime.strptime(
        h5_datetime, "%d-%b-%Y;%H:%M:%S.%f")
    utc_datetime = naive_datetime.replace(tzinfo=timezone.utc)

    return utc_datetime
