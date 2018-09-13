#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2018年9月13号

@author: tjm
'''
from tabulate import tabulate

def test():
    table = [["Sun",696000,1989100000],["Earth",6371,5973.6],["Moon",1737,73.5],["Mars",3390,641.85]]
    print tabulate(table,tablefmt="rst",numalign="right")
    pass
if __name__ == '__main__':
    test()