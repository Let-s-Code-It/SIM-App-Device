import os
import sys

def RestartProgram():
   os.execl(sys.executable, sys.executable, *sys.argv)