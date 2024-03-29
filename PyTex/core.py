import os
import subprocess
import shutil
from glob import glob
from tempfile import NamedTemporaryFile

from warnings import warn
from contextlib import ContextDecorator # used to trigger the compilation

import pandas as pd

from math import sqrt

class PyTex(ContextDecorator):
    def __init__(self, outpath:str, keep_tex=False, no_cleaning=False, do_not_compile = False):
        """
            Usage:
                outpath - filename of the desired output pdf
                keep_tex - set True to keep the .tex file used for the compilation.
                no_cleaning - set True to not clean up the TeX compilation files
                do_not_compile - set True to skip LaTeX compilation. Used for debugging; will force-keep the TeX file

            Notes:
                Kept texfiles will only have read permissions for the user who made them, since they're copied from tempfiles
        """
        assert isinstance(outpath, str), "Outpath must be {}, got {}".format(str, type(outpath))
        self._outpath = outpath

        filepath, filename = os.path.split(self._outpath)
        if not os.path.exists(filepath):
            print("Could not find out directory {}".format(filepath))
            try:
                print("Trying to make it")
                os.mkdir(filepath)
            except IOError:
                print("Failed, exiting")
                import sys
                sys.exit()

        self._started = False
        self._no_clean = no_cleaning
        self._keep_tex = keep_tex
        self._do_not_compile = do_not_compile

        if self._do_not_compile:
            self._keep_tex = True

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

        if not self._do_not_compile:
            subprocess.run(["pdflatex","-interaction=nonstopmode", self._name, "--output-directory {}".format(outdir)])
        else:
            print("Skipping compilation step!")
        if self._keep_tex:
            shutil.copyfile(self._obj.name,os.path.join(outdir, texname))

        temp_name = os.path.split(self._obj.name)[1]
        try:
            if not self._do_not_compile:
                shutil.copyfile(temp_name+".pdf", os.path.join(outdir, pdfname))
        except IOError:
            pass # might've failed the compilation

        self._obj.close()

        if not self._no_clean:
            all_extra = glob(os.path.join(os.getcwd(),temp_name+".*"))
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
        this_str=f"""\\title{{{{\Huge {title} }} \\\\[10pt] {{\large {subtitle} }}}}
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

    def inject_tex(self, what:str):
        """
            writes whatever is passed to the the Tex file. Use with caution!
            No line breaks are added
        """
        self._check_start()
        assert isinstance(what, str), "Can only add type 'str' to the object; you passed {}".format(type(what))
        self._obj.write(what)

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

    @classmethod
    def _tabular_wrap(cls, the_string, eol_delimiter='\n')->str:
        """
            Takes a given string and wraps it in a tabular environment, allowing us to have multi-line entries in a table
        """
        if len(the_string.split(eol_delimiter))==1:
            return the_string

        full_str  = f"""\\begin{{tabular}}{{c}}
        """
        the_string = the_string.replace(eol_delimiter, "\\\\")
        full_str += the_string
        full_str += f"""\\end{{tabular}}"""

        return full_str


    def add_table(self, table:pd.DataFrame, table_caption:str,
                    format_str= '',
                    separate_first_column=True,
                    alternate_colors = True, header_justification="", line_break_delimiter='_'):
        """
            Takes a Pandas dataframe and uses its headers as headers in the column.
            Adds in a provided caption.

        Params
        --------------------------------------
            table                   - Pandas dataframe to be table-formatted
            table_caption           - caption that goes under the table
            format_str              - format string, separate values with ","
            separate_first_column   - will put a vertical line after the first column
            alternate_colors        - rows will alternate colors
            header_justification    - (str) tex-format string specifing line alignment
            line_break_delimiter    - (str) instances of this character will be used to split lines in an individual cell

        Format Str notes - these are very tricky to get right.
            we split this string by "," and each entry is given to `format` to format the column's table
                03d   format int as length 3 with leading zeros
                .4f   format float with four digits after decimal
                use an empty entry for no formatting
            try calling `help('FORMATTING')` in a python terminal for more

        """
        self._check_start()

        headers = table.columns.values.tolist()

        if format_str!="":
            formaters = format_str.split(",")
            do_format = True
            if len(formaters) != len(headers):
                raise ValueError("Format string should be same length ({}) as number of columns ({})")
        else:
            do_format = False

        if header_justification:
            justification = header_justification
        else:
            if separate_first_column:
                justification = "l|"+"l"*(len(headers)-1)
            else:
                justification = "l"*len(headers)
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
    \\begin{{tabular}}{{{justification}}}\\hline
    """
        table_str += header_row_str
        table_str += "&".join(headers)
        table_str += f"\\\\\\hline"
        table_str += "\n"

        for i_entry in range(len(table[headers[0]])):
            row_str = ""
            row_str += " & ".join(self._tabular_wrap(format(table[header][i_entry], formaters[i_h] if do_format else ""), line_break_delimiter)+" " if table[header][i_entry] is not None else "null" for i_h, header in enumerate(headers))
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
            Adds the figure.
        """
        self._check_start()
        figurepath = os.path.abspath(figurepath)
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
            Adds multiple figurers together as panels aligned in a grid. Tries to figure out the grid dimensionality on its own
        """
        self._check_start()
        if len(figpaths)==0:
            raise ValueError("Must provide at least one plot!")
        figpaths = [os.path.abspath(each) for each in figpaths]
        n_figures = len(figpaths)
        if n_figures==1:
            self.add_figure(caption, figpaths[0])
            return
        elif n_figures==2:
            rank = 2
            pagewidth = "0.48\\linewidth"
        else:
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
                feature_string+=f"""    \\begin{{minipage}}{{0.98\\linewidth}}
"""

            this_path = figpaths[i_row*rank + i_column]
            feature_string+=f"""    \\begin{{minipage}}{{{pagewidth}}}
                \\includegraphics[width=0.9\\linewidth]{{{this_path}}}
        \\end{{minipage}}%
"""
            if (i_row*rank + i_column) == (len(figpaths)-1):
                todo = False

            if i_column==(rank-1) or (not todo):
                feature_string+=f"""
\\end{{minipage}}\\\\
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



