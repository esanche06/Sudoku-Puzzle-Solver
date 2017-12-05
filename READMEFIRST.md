# Sudoku-Puzzle-Solver

This is yet another project I worked on while at UCI (with my cohort Jeremy Hobson). It was actually built upon by the project
at this github repo: https://github.com/rimoung/PythonSudoku.

Jeremy and I developed the heuristics the solver uses, but the credit for the skeleton code should be given to the wonderful TAs for the class.

This project is really cool.

It takes a bit of work to get its magic working, so I'll run through that here.
First things first, you'll need to download Python3 to run in your command console. Do that here:
https://www.python.org/downloads/

Once you're done, open your console and navigate to the directory you saved this project in.
Once there, you can run the program by typing:

python3 main.py inputfile.txt outputfile.txt maxTime args

Where inputfile.txt is one of the included example Sudoku puzzle files, and outputfile.txt is the file you would like 
the output of the program written to (the program will either create a new one, or overwrite an existing one so be careful).

"maxTime" is the time in seconds you want the program to timeout at. For example, if I want to test that it succeeds in less than 10 minutes, I would enter 6000.

Finally, "args" can be up to 5 heuristics, basically the logic allowed to the program in solving the puzzle. More heuristics generally means faster solving, although this is not always the case (we discovered during our analysis that some heuristics actually impede each other when used in conjuntion).

Here is a list of possible inputs to the args values:

Arg1: 'FC' OR 'ACP' YOU MUST INCLUDE ONE OF THESE OR THE SOLVER WILL BE VERY, VERY DUMB -- LITERALLY
Arg2: 'MRV' OR 'DH' OR none
Arg3: 'LCV' OR none
Arg4: 'NKP' OR 'NKT' OR none

For lightning fast solving times, even for the 16x16 puzzles (lightning fast meaning a few minutes or less in those cases),
I suggest ACP LCV NKP NKT as your args.

There is an additional README.md for anyone who wishes to develop on this project explaining more of the underlying
architecture of this project, but this README is sufficient if you just want to try it out.

Thanks! And feel free to give feedback.
