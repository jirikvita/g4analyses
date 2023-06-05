#!/snap/bin/pyroot
# was: #!/usr/bin/python3
# Ne 5. března 2023, 22:16:34 CET

#from __future__ import print_function

import ROOT
from math import sqrt, pow, log, exp
import os, sys, getopt

cans = []
stuff = []

##########################################
# https://www.tutorialspoint.com/python/python_command_line_arguments.htm
def main(argv):
   
    Es = []
    #Es.extend([1, 2, 3, 4, 5, 7, 10, 15, 20, 25, 30, 40, 50])
    Es.extend([10*x for x in range(6, 11)])
    base='run_el_EX.mac'
    for E in Es:
        cfg = base.replace('EX','E{}GeV'.format(E))
        cmd = 'cat {} | sed "s|XEX|{}|g" > {}'.format(base, E, cfg)
        os.system(cmd)
        cmd='exampleB4d -m {} ; mv {} tree_el_{}GeV.root'.format(cfg, 'B4.root', E)
        print(cmd)
        
    return

###################################
###################################
###################################

if __name__ == "__main__":
    # execute only if run as a script"
    main(sys.argv)
    
###################################
###################################
###################################

