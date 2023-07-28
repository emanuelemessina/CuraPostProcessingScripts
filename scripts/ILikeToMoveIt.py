# Author:   Emanuele Messina
# Description:  Disable heating, strips all extruder movement instruction pieces resulting in pure nozzle movement code. Useful for testing purposes.

from ..Script import Script

import re
import inspect

def transform_line(gcode_lines, transform):
    return [transform(line) for line in gcode_lines]

######################

transformation_functions = [
    lambda gcode_line: re.sub(r'\s*E\d+(\.\d+)?', '', gcode_line), #remove_extrusion_from_g1
    lambda gcode_line: re.sub(r'\s*F\d+(\.\d+)?', '', gcode_line), #remove_feedrate
    lambda gcode_line: re.sub(r'\s*G1', 'G0', gcode_line), #convert_extrusion_movs_to_linear
    lambda gcode_line: gcode_line if not re.match(r'(?i)(M10[49])|(M1[49]0)', gcode_line) else '', #remove_heating_command
    lambda gcode_line: gcode_line if not re.match(r'(?i)G92', gcode_line) else '', #remove_extruder_resets
]

########################

class ILikeToMoveIt(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self): # version 2 is mandatory
        return """{
            "name": "I Like To Move It",
            "key": "ILikeToMoveIt",
            "metadata": {},
            "version": 2,
            "settings":
            {
            }
        }"""

    def execute(self, data):
        
        for layer in data:
            
            layer_index = data.index(layer)
            lines = layer.split("\n")

            new_lines = lines

            for func in transformation_functions:
                new_lines = transform_line(new_lines, func)
            
            new_lines = "\n".join(new_lines)
            data[layer_index] = new_lines

        return data
