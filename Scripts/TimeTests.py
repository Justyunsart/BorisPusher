'''
Scratchpad to see what kind of data structure operations are the best.
'''

import timeit
import time
import numpy as np
import pandas as pd

from collections import namedtuple

############
# CASE ONE #
############
'''
Assume you have a container that:
1. Contains x particles
2. Has data for n steps
3. Constant order by particle, then step

eg. (3 particles x y z, n steps)
[
    [x1],
    [y1],
    [z1],
    [x2],
    [y2],
    [z2].
    ...
    [xn],
    [yn],
    [zn]
]

How would you most efficiently store these values in separate containers,
for each particle?

Is it efficient to do the above? or just constantly access this combined input container?
'''

def Construct_Case1(n:int, p:int):
    # Create List
    main = []
    for i in range(n):
        for j in range(p):
            main.append(j)
    return main

# Solution 1: Move down linearly, accessing different lists as you go
def Sol1_Case1(main:list, p:int):
    print("Case1 Sol 1")
    out = []
    # Add empty lists for each particle
    for i in range(p):
        out.append([])

    inc = 0
    for i in range(len(main)):
        out[inc].append(main[i])

        inc = inc + 1 if (inc + 1) < p else 0
    
    return out

 # Solution 2: Move down 'p' times, using index stepping
def Sol2_Case2(main:list, p:int):
    print("Case1 Sol2")
    out = []
    # Add empty lists for each particle
    for i in range(p):
        out.append([])
        for j in main[i::p]:
            out[i].append(j)
    
    return out

def Test_Case1():

    oneSetup = '''
from __main__ import Sol1_Case1
from __main__ import Construct_Case1'''

    oneTest = '''
m = Construct_Case1(10000000, 1)
Sol1_Case1(m, 3)'''

    twoSetup = '''
from __main__ import Sol2_Case2
from __main__ import Construct_Case1'''

    twoTest = '''
m = Construct_Case1(10000000, 1)
Sol2_Case2(m, 3)'''
    
    one = timeit.timeit(setup = oneSetup,
                        stmt = oneTest,
                        number = 1)
    
    two = timeit.timeit(setup = twoSetup,
                        stmt = twoTest,
                        number = 1)

    print("Reporting on time data: ")

    print()

    print(f"Case 1: {one}")

    print(f"Case 2: {two}")

##########
# CASE 2 #
##########
'''
Speed of creating myriad entries for namedtuples vs. dictionaries.
'''
lst = [1, 2, 3]

def Dict_Case2(num:int):
    out = {}
    for i in range(num):
        temp = {}
        temp['a'] = i
        temp['b'] = lst
        out[i] = temp
    return out

def NamedTuple_Case2(num:int):
    NTuple = namedtuple("NTuple", ["a", "b"])
    out = []
    for i in range(num):
        out.append(NTuple(i, lst))
    return out

def Test_Cases(num:int):
    start = time.time()
    a = Dict_Case2(num)
    a1 = a[0]["b"][0]

    end = time.time()
    print(f"Dict took {end-start}")

    start = time.time()
    a = NamedTuple_Case2(num)
    a1 = a[0][1][0]
    end = time.time()
    print(f"Ntuple took {end-start}")    

##########
# CASE 3 #
##########
'''
How do Cross Products work on higher dim arrays
'''
def Case3():
    arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    arr2 = np.array([[5, 7, 5], [2, 7, 4], [32, 6, 2]])

    print(np.cross(arr, arr2))
    print(np.cross(arr[1], arr2[1]))


def Case4():
    df = pd.DataFrame([[[1, 1, 1],2,3], [[1, 1, 1],2,3]], columns = ["a", "b", "c"])
    # print(df)
    a = np.array((df["a"].tolist()))
    print(a)
    print(a[:-1,0])


def Case5(n:int):
    x = np.zeros(shape=(n, 3))
    print(f"Memory size of the array with {n} by 3 dims: {x.nbytes}")

# Testing
# Test_Case1()
# Test_Cases(5000000)
# Case3()
# Case4()
Case5(50000000)