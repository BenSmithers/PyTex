import pandas as pd


import os 
from glob import glob 

all_plots = glob(os.path.join(os.path.dirname(__file__), "ex_plots", "*"))
print(all_plots)
from PyTex import PyTex

data = pd.read_csv("./dataset.csv")

with PyTex("./test.pdf", True) as obj:
    obj.add_title("This test file", "Has a subtitle")
    obj.new_section("Section header")
    obj.add_table(data, "and tables have captions")
    obj.new_section("Figures Can go in another section")
    obj.add_figures("Minipages!", *all_plots[0:3])
    obj.add_figures("Minipages!", *all_plots[0:4])
    obj.add_figures("Minipages!", *all_plots[0:9])
    obj.add_figures("Minipages!", *all_plots[0:13])
   # obj.add_figure("First plot", all_plots[0])