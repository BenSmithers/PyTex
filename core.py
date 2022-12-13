import os 
import subprocess
import shutil
from glob import glob
from tempfile import NamedTemporaryFile

from warnings import warn
from contextlib import ContextDecorator

import pandas as pd

from math import sqrt

class PyTex(ContextDecorator):
    def __init__(self, outpath, keep_tex=False):
        """
            Usage:
                outpath - filename of the desired output pdf 
                keep_tex - set True to keep the .tex file used for the compilation. 
        """
        self._outpath = outpath

        self._started = False
        self._keep_tex = keep_tex
    
    def __enter__(self):
        """
            Called when we first start the while block
        """
        self._obj = NamedTemporaryFile('wt')
        self._name = self._obj.name

        with open(os.path.join(os.path.dirname(__file__), "header.tex"),'rt') as header:
            for line in header.readlines():
                self._obj.write(line)

        return self
        

    def __exit__(self, *exc):
        """
            Called automatically when we exit the while block 
        """
        self._obj.write(f"\\end{{document}}\n")
        self._obj.flush()

        outdir, outname = os.path.split(self._outpath)

        texname = ".".join(outname.split(".")[0:-1]) +".tex"
        pdfname =  ".".join(outname.split(".")[0:-1]) +".pdf"

        subprocess.run(["pdflatex", self._name, "--output-directory {}".format(outdir)])
        if self._keep_tex:
            shutil.copy(self._obj.name,os.path.join(outdir, texname))
        
        temp_name = os.path.split(self._obj.name)[1]
        shutil.copy(temp_name+".pdf", os.path.join(outdir, pdfname))
        

        self._obj.close()

        all_extra = glob(os.path.join(outdir,temp_name+".*"))
        for each in all_extra:
            print("Cleaning up {}".format(each))
            os.remove(each)

        return False

    def _check_start(self):
        """
            Ensures that the startblock is called before we write anything 
        """
        if not self._started:
            self._obj.write(f"\\begin{{document}}")
            self._obj.write("\n")
            self._obj.write(f"\\maketitle")
            self._obj.write("\n")
            self._started=True
        
    def add_title(self, title:str, subtitle:str):
        """
            Adds a title to this tex file. 
            Needs to be called before anything else

            raises Exception
        """
        if self._started:
            raise Exception("Title must be set before anything else")
        this_str=f"""\\title{{ {title}  \\\\[10pt]{subtitle}}}
\\date{{\\today}}
"""
        self._obj.write(this_str)

    def inject_header(self, what:str):
        """
        Inject some LaTeX code into the header 

        Must be called before anything any document-body calls 
        """

        if self._started:
            raise Exception("Must add to the header before anything else")
        assert isinstance(what, str), "Can only add type 'str' to the object; you passed {}".format(type(what))
        self._obj.write(what)
        self._obj.write("\n")

    def page_break(self):
        """
            Adds a page break 
        """
        self._check_start()
        self._obj.write("\\pagebreak")
        self._obj.write("\n")

    def new_section(self, section_title:str):
        """
            Creates a section header with the given name
        """
        self._check_start()
        self._obj.write(f"\\section{{{section_title}}}")
        self._obj.write("\n")

    def add_table(self, table:pd.DataFrame, table_caption:str, separate_first_column=True, alternate_colors = True, force_header_format=""):
        """
            Takes a Pandas dataframe and uses its headers as headers in the column. 
            Adds in a provided caption.
            
            If you specify "separate_first_column", will put a vertical line after the first column

            You can add a table formatter (like 'rr|ll|cc' or w/e) that is given to LaTeX
        """
        self._check_start()

        headers = table.columns.values.tolist()

        if force_header_format:
            format_str = force_header_format
        else:
            if separate_first_column:
                format_str = "l|"+"l"*(len(headers)-1)
            else:
                format_str = "l"*len(headers)
        if alternate_colors:
            color_str = f"\\rowcolors{{2}}{{gray!25}}{{white}}\n"
            header_row_str= f"\\rowcolor{{gray!50}}\n"
        else:
            color_str=""
            header_row_str = ""

        table_str = f"""
    \\begin{{center}}
    \\begin{{table}}[h]
    \\centering
    {color_str}
    \\caption{{{table_caption}}}
    \\begin{{tabular}}{{{format_str}}}\\hline
    """
        table_str += header_row_str
        table_str += "&".join(headers) 
        table_str += f"\\\\\\hline"
        table_str += "\n"

        for i_entry in range(len(table[headers[0]])):
            row_str = ""
            row_str += "&".join(str(table[header][i_entry])+" " for header in headers)
            row_str += "\\\\"
            row_str += "\n"
            table_str += row_str
        table_str += "\n"
        table_str += f"""
        \\end{{tabular}}
    \\end{{table}}
\\end{{center}}
"""

        self._obj.write(table_str)


    def add_figure(self, caption:str, figurepath:str)->str:
        """
            Adds the figure
        """
        self._check_start()
        if not os.path.exists(figurepath):
            warn("Could not find file {}".format(figurepath))
            return ""

        broken = figurepath.split(".")

        fixed_path = "{" + ".".join(broken[0:-1]) + "}" +"."+ broken[-1]

        this_str = f"""
    \\begin{{figure}}[H]
        \\centering
        \\includegraphics[width=0.8\\linewidth]{{{fixed_path}}}
        \\caption{{{caption}}}
    \end{{figure}}

        """
        self._obj.write(this_str)

    def add_figures(self, caption:str, *figpaths):
        """
            Adds multiple figures together in a minipage, up to 25
            If more than 25 are requested raises ValueError
        """
        self._check_start()
        if len(figpaths)==0:
            raise ValueError("Must provide at least one plot!")
        n_figures = len(figpaths)
        if n_figures==1:
            self.add_figure(caption, figpaths[0])
            return

        rank = int(sqrt(n_figures))
        if (sqrt(n_figures)-rank)<1e-15:
            pass
        else:
            rank += 1

        pagewidth = "{:.2f}".format(0.96/rank)+"\\linewidth"

        feature_string = f"\\begin{{center}}"
        feature_string+="\n"
        feature_string += f"\\begin{{figure}}"
        feature_string+="\n"
        i_row = 0
        i_column = 0
        todo = True
        while todo:
            if i_column==0:
                feature_string+=f"""    \\begin{{minipage}}{{{pagewidth}}}
"""
            
            print(i_row*rank + i_column)
            this_path = figpaths[i_row*rank + i_column]
            feature_string+=f"""    \\begin{{minipage}}{{1.0\linewidth}}
                \\includegraphics[width=0.9\\linewidth]{{{this_path}}}
        \\end{{minipage}}\\\\
""" 
            if (i_row*rank + i_column) == (len(figpaths)-1):
                todo = False
            
            if i_column==(rank-1) or (not todo):
                feature_string+=f"""
\\end{{minipage}}%
"""

            i_column+=1
            if i_column == rank:
                i_column= 0
                i_row += 1

        self._obj.write(feature_string)
        self._obj.write("\n")

        caption_str = f"""
        \\caption{{{caption}}}
        \\end{{figure}}

        """
        self._obj.write(caption_str)

        self._obj.write(f"\\end{{center}}")
        self._obj.write("\n")


    
