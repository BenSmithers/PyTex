import pandas as pd


import os 
from glob import glob 

this_dir = os.path.abspath(os.path.split(os.path.dirname(__file__))[1])
this_dir = os.path.dirname(__file__)
all_plots = glob(os.path.join(this_dir, "ex_plots", "*"))
from PyTex import PyTex

data = pd.read_csv(os.path.join(this_dir, "dataset.csv"))

fstr = "d,,.2f,, .6f"

with PyTex("/home/bsmithers/software/PyTex/out/test.pdf",keep_tex=True, do_not_compile=False) as obj:
    obj.add_title("This test file", "Has a subtitle")
    obj.new_section("Section header")
    obj.add_table(data, "and tables have captions", line_break_delimiter='\n', format_str=fstr)
    obj.new_section("Figures Can go in another section")
    obj.add_figures("Minipages!", *all_plots[0:2])
    obj.add_figures("Minipages!", *all_plots[0:4])
    obj.add_figures("Minipages!", *all_plots[0:9])
    obj.add_figures("Minipages!", *all_plots[0:12])
    obj.add_figures("Minipages!", *all_plots)
   # obj.add_figure("First plot", all_plots[0])
