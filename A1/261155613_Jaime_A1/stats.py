import numpy as np
import matplotlib.pyplot as plt
from controllers import all_controllers
import json

class Record:
    def __init__(self, rec_type: str, rec_time: float, rec_error: float):
        self.type = rec_type
        self.time = rec_time
        self.error = rec_error
       
        
class Recorder:
    def __init__(self ):
        self.records = []
        self.type_counts = {}
        self.num_bins = 20
        try:
            with open('timing.txt', 'r') as f:
                self.type_counts = json.load(f)
        except OSError:
            for c in all_controllers:
                self.type_counts[str(c.name)] = {'count': 0, 'times': [], 'errors': []}
            # for controller in ControllerType:
            #     self.type_counts[str(controller)] = {'count': 0, 'times': [], 'errors': []}
            self.write_to_file()

    def add(self, record: Record):
        self.type_counts[record.type]['count'] += 1
        self.type_counts[record.type]['times'].append(record.time)
        self.type_counts[record.type]['errors'].append(record.error)
        self.write_to_file() # sloth! would be nice not to write every time like this

    def write_to_file(self):        
        obj = json.dumps(self.type_counts, indent=4)  
        with open('timing.txt', 'w') as f:
            f.write(obj)

    def show(self):
        bins = np.linspace(0, 60, 11)
        for i,key in enumerate(self.type_counts):
            # small offset for each set of bins so that they don't overlap so much
            plt.hist(self.type_counts[key]['times'], bins=bins+i, density=True, linewidth=1.5, histtype='step', label=key)
        plt.legend()
        plt.show()
        