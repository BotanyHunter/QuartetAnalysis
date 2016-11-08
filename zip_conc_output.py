#!/usr/bin/python
#version 2.0.2

import sys,re,os,tarfile

def main():

    try:
        myTar = tarfile.open("finish.tar.gz","w")
        files = os.listdir(".")
        for file in files:
            reString = "^Q[0-9]+\.concordance$"
            if( re.search(reString, file)):
                myTar.add(file)

            reString = "^Q[0-9]+\.txt$"
            if( re.search(reString, file)):
                myTar.add(file)
        return 0
    except:
        return 1
    
main()
