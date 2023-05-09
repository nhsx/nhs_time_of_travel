"""This module exists just to allow an easy check that the nhstravel module dependencies work.

It has two basic ways to test it:

from nhstravel.info import description

or

from nhstravel.info import NHS_TRAVEL_DESCRIPTION

"""

NHS_TRAVEL_DESCRIPTION = (
    "A library to help calculate geographical information for the NHS."
)


def description():
    """Get a string that describes what the nhstravle library does"""
    return NHS_TRAVEL_DESCRIPTION
