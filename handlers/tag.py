import logging
import re

from slugify import slugify

import constants


class Instrument:
    def __init__(self, tag):
        self.tag = tag
        self.type = self._identify_instrument()

    def _find_identification(self):
        # id characters must be a key
        measured_variables = "".join(measured_variable.keys())
        readout_variables = "".join(readout_variable.keys())
        output_variables = "".join(output_variable.keys())

        separators = "-_"

        # match 2-3 characters before or after -/_
        match = re.search(
            rf"[{measured_variables}][{readout_variables}][{output_variables}]?(?=[{separators}]|(?<=[{separators}])[{measured_variables}][{readout_variables}][{output_variables}]?",
            self.tag
        )

        return match.group(0)

    def _identify_instrument(self):
        # remove id from tag
        identification = self._find_identification()

        # split id by characters
        variables = list(identification)

        try:
            instrument_type = {
                'measurement': measured_variable[variables[0]],
                'readout': readout_variable[variables[1]],
                'output': readout_variable[variables[2]]
            }
        except IndexError as error:
            # if id only has 1 succeeding letter
            instrument_type = {
                'measurement': measured_variable[variables[0]],
                'readout': readout_variable[variables[1]],
            }

        return instrument_type

    @property
    def name(self):
        if 'output' in self.type:
            return f"{self.type['measurement']} {self.type['readout']} {self.type['output']}"
        else:
            return f"{self.type['measurement']} {self.type['readout']}"

    @property
    def measurement(self):
        return self.type['measurement']

    @property
    def readout(self):
        return self.type['readout']

    @property
    def output(self):
        if 'output' in self.type:
            return self.type['output']
        else:
            return None

    @property
    def search(self):
        ls_search = [self.tag,
                     re.search(r"\w+.\w+[-_]\w+|\w+$", self.tag).group(0)]
        return ls_search


def get_search_strings(tag, filter_calibration=False):
    ls_search = []

    # identify instrument
    instrument = Instrument(tag)

    # search filters
    # calibration instruments
    if filter_calibration:
        # if instrument is not the correct type, return not applicable
        if instrument.readout != 'Indicate' or instrument.output != 'Transmit':
            logging.debug(f"Tag {tag} is type {instrument.name}, calibration NOT required")
            ls_search.append(constants.not_applicable)
            return ls_search

    return instrument.search


def create_file_name(tag):
    safe_tag = slugify(tag, separator='.', lowercase=False)
    return f"Calibration Certificate - {safe_tag}"


measured_variable = {
    'A': 'Analysis',
    'B': 'Burner, Combustion',
    'C': 'User Choice',
    'D': 'User Choice',
    'E': 'Voltage',
    'F': 'Flow, Flow Rate',
    'G': 'User Choice',
    'H': 'Hand',
    'I': 'Current',
    'J': 'Power',
    'K': 'Time, Schedule',
    'L': 'Level',
    'M': 'User Choice',
    'N': 'User Choice',
    'O': 'User Choice',
    'P': 'Pressure',
    'Q': 'Quantity',
    'R': 'Radiation',
    'S': 'Speed, Frequency',
    'T': 'Temperature',
    'U': 'Multivariable',
    'V': 'Vibration',
    'W': 'Weight, Force',
    'X': 'Unclassified',
    'Y': 'Event, State, Presence',
    'Z': 'Position, Dimension'
}

readout_variable = {
    'A': 'Alarm',
    'B': 'User Choice',
    'E': 'Sensor, Primary Element',
    'G': 'Glass, Gauge, Viewing Device',
    'I': 'Indicate',
    'J': 'Scan',
    'L': 'Light',
    'N': 'User Choice',
    'O': 'Orifice, Restriction',
    'P': 'Point',
    'Q': 'Integrate, Totalize',
    'R': 'Record',
    'U': 'Multifunction',
    'W': 'Well, Probe',
    'X': 'X-axis'
}

output_variable = {
    'B': 'User Choice',
    'C': 'Control',
    'K': 'Control Station',
    'N': 'User Choice',
    'S': 'Switch',
    'T': 'Transmit',
    'U': 'Multifunction',
    'V': 'Valve, Damper, Louver',
    'X': 'Unclassified',
    'Y': 'Auxiliary Devices',
    'Z': 'Driver, Actuator, Unclassified final control element'
}
