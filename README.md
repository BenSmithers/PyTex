# PyTeX

## What does this do?

Allows for automated writing of LaTeX files through Python! 

## What does it use?

Right now, just pdflatex and python; no special modules are needed. 
Only Python 3 is supported. 

I might later on make compilation system more flexible, but I'll never make this Python 2 compatible. 

## How does it work?

See Ex1 in the `examples` folder. It writes templated LaTeX code to a temp file, then runs pdflatex on the tempfile. 