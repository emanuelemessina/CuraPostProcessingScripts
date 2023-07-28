# Author:   Emanuele Messina
# Description:  Displays jobname and current layer number on the LCD with M117.

from ..Script import Script
from UM.Application import Application

def create_message_chunks(prefix, message, max_length):
    max_len_eff = max_length-len(prefix)-4
    if max_len_eff < 1:
        max_len_eff = 1
    max_index = len(message)-max_len_eff
    if max_index < 0:
        max_index = 0
    return [f'M117 {prefix}{".." if i != 0 else ""}{message[i:i+max_len_eff+1]}{".." if i+max_len_eff+1 < len(message) else ""}' for i in range(0, max_index)]

class YouAreHere(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "You Are Here",
            "key": "YouAreHere",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "max_len":
                {
                    "label": "Max display length",
                    "description": "Maximum number of characters printable in one row. Scrolls job name if the displayed string is longer than this number.",
                    "type": "int",
                    "default_value": 25
                },
                "scroll_interval":
                {
                    "label": "Scroll interval",
                    "description": "Interval (in seconds, ex: 0.3) between each scroll of the job name",
                    "type": "float",
                    "default_value": 0.3
                }
            }
        }"""

    def execute(self, data):
        
        # params
        name = Application.getInstance().getPrintInformation().jobName
        
        max_len = self.getSettingValueByKey("max_len")
        scroll_interval = self.getSettingValueByKey("scroll_interval")

        # init
        max_layer = 0
        layer_number = -1
        t1 = 0
        t2 = 0     

        # preprocess
        layers_info = []
        for layer in data:
            
            layer_index = data.index(layer)
            lines = layer.split("\n")
            
            for line in lines:

                # get max layer number
                if line.startswith(";LAYER_COUNT:"):
                    max_layer = line
                    max_layer = max_layer.split(":")[1].strip()

                # get time elapsed
                if line.startswith(";TIME_ELAPSED:"):
                    time_elapsed = line
                    time_elapsed = time_elapsed.split(":")[1]
                    t2 = float(time_elapsed)

            layers_info.append({"delta_time": t2-t1, "num_lines": len(lines)})
            t1 = t2

        # postprocess
        for layer in data:
            
            layer_index = data.index(layer)
            lines = layer.split("\n")

            new_lines = []

            def _cmc(ln):
                if layers_info[layer_index]["delta_time"] == 0 : # still in preparation pseudo layers
                    return create_message_chunks(f'Prep:', f'{name}', max_len)
                return create_message_chunks(f'L{str(int(ln)+1)}/{max_layer}@', f'{name}', max_len)
            
            if layers_info[layer_index]["delta_time"] == 0 :
                skip_lines = 10
            else:
                skip_lines = int(layers_info[layer_index]["num_lines"]/layers_info[layer_index]["delta_time"] * scroll_interval)

            chunks = _cmc(layer_number)
            i = 0
            line_count = 0
            
            for line in lines:

                new_lines.append(line)

                if line.startswith(';LAYER:'):
                    layer_number = int(line.split(':')[1].strip())
                    chunks = _cmc(layer_number)
                    i = 0
                    new_lines.append(f';LAYER:{layer_number} | DELTA_T:{layers_info[layer_index]["delta_time"]} | LINES:{layers_info[layer_index]["num_lines"]} | YOUAREHERE_SKIP_LINES:{skip_lines}')

                if line_count % skip_lines == 0:
                    if i >= len(chunks):
                        i = 0
                    new_lines.append(chunks[i])
                    i += 1 
                
                line_count += 1
            
            new_lines = "\n".join(new_lines)
            data[layer_index] = new_lines

        return data
