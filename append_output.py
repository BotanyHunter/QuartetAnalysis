#!/usr/bin/python
#version 2.0.2

import sys

def append_output(append_filename, to_filename):

    try:
        appendfile = open(to_filename, 'a')
        inputfile  = open(append_filename, 'r')

        appendfile.write(inputfile.read())
        appendfile.close()
        inpufile.close()
        return 0
    except:
        return 1
