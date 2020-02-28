import sudoku_maker
from defaults import *
import pickle
import os
import tempfile
import sys

g = sudoku_maker.SudokuGenerator()
puzzles = g.make_unique_puzzles(int(sys.argv[1]))
for puz, d in puzzles:
    print d.value_string(), d.value
    fd, outfile = tempfile.mkstemp(dir=os.path.join(DATA_DIR, d.value_string()))
    print outfile
    out = os.fdopen(fd, 'w')
    pickle.dump(puz, out)
    out.close()
