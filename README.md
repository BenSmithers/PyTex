# PyTeX

## What does this do?

Allows for automated writing of LaTeX files through Python! 

## What does it use?

Right now, python, pdflatex, and pandas. 
Only Python 3 is supported. 

I may add other non-pandas table functinoality, but that's low-priority for me. 

I might later on make compilation system more flexible, but I'll never make this Python 2 compatible. 

## How does it work?

See Ex1 in the `examples` folder. It writes templated LaTeX code to a temp file, then runs pdflatex on the tempfile. 

Note: this should only be used like 
```
with PyTex("/path/to/out.pdf") as texobj:
    [code]
```
the compiler will otherwise not be called. 