#!/usr/bin/env python

'''
Interface with command line aconvasp
http://aflowlib.org/
Only tested on Linux
inspired by Shyue's qhull_caller
WARNING: you need to have a convasp in your path for this to work
'''

__author__="Geoffroy Hautier"
__copyright__ = "Copyright 2011, The Materials Project"
__version__ = "1.0"
__maintainer__ = "Geoffroy Hautier"
__email__ = "geoffroy.hautier@uclouvain.be"
__status__ = "Production"
__date__ ="$Nov 22, 2011M$"

import subprocess
import numpy as np

from pymatgen.io.vaspio import Poscar 

def run_aconvasp_command(command, structure):
    """
    Helper function for calling aconvasp with different arguments
    """

    poscar = Poscar(structure)
    p = subprocess.Popen(command,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
    output = p.communicate(input=poscar.get_string())
    return output

def get_num_division_kpoints(structure, kppa):
    """
    get kpoint divisions for a given k-point density (per reciprocal-atom): kppa and a given structure  
    """
    output = run_aconvasp_command(['aconvasp', '--kpoints', str(kppa)], structure)
    tmp = output[0].rsplit("\n")[6].rsplit(" ")
    return [int(tmp[5]),int(tmp[6]),int(tmp[7])]

def get_minkowski_red(structure):
    """
    get a minkowski reduced structure
    """
    output = run_aconvasp_command(['aconvasp', '--kpath'], structure)
    started = False
    poscar_string = ""
    for line in output[0].split("\n"):
        if started or line.find("KPOINTS TO RUN") != -1:
            poscar_string=poscar_string+line+"\n"
        if line.find("STRUCTURE TO RUN") != -1:
            started = True
        if line.find("KPOINTS TO RUN") != -1:
            started = False
    return Poscar.from_string(poscar_string).struct


def get_vasp_kpoint_file_sym(structure):
    """
    get a kpoint file ready to be ran in VASP along symmetries of a structure 
    """
    output=run_aconvasp_command(['aconvasp', '--kpath'], structure)
    started = False
    kpoints_string = ""
    for line in output[0].split("\n"):
        #print line
        if started or line.find("END") != -1:
            kpoints_string = kpoints_string + line + "\n"
        if line.find("KPOINTS TO RUN") != -1:
            started = True
        if line.find("END") != -1:
            started = False
    return kpoints_string

def get_point_group_rec(structure):
    """
    gets the point group for the reciprocal lattice of the given structure
    """
    run_aconvasp_command(['aconvasp', '--pgroupk'], structure)
    listUc=[]
    f = open("aflow.pgroupk.out", 'r')
    linetmp = []
    count = -1000
    started = False
    for line in f:
        #print line
        if(line.find("Schoenflies")!=-1):
            count=-1
            linetmp=[]
            started=True
            continue
        count=count+1
        if not started:
            continue
        if count <= 2 :
            linetmp.append([float(x) for x in line.rstrip("\nUc ").split()])
        if count == 2:
            listUc.append(np.array(linetmp))
    f.close()
    return listUc