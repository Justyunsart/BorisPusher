'''
Scratchpad to see what kind of data structure operations are the best.
'''

import timeit
import time
import numpy as np
import pandas as pd
import magpylib as mp
from math import sqrt

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
# Case5(50000000)

s1 = mp.current.Circle(diameter=3)
s2 = mp.current.Circle(diameter=3).rotate_from_angax(90, [0, 1, 0])
s3 = mp.current.Circle(diameter=3).rotate_from_angax(90, [1, 0, 0])
s4 = mp.current.Circle(diameter=3).rotate_from_angax(90, [0, 0, 1])
# mp.show(s1, s2)

#print(sqrt(4))

a = np.array([[1,2,3], [2,5,6]])
b = a - np.array([1,1,1])

a = np.array([-800, 0, 0])
b = np.array([2.2e-21, 2.2e-21, 2.2e-21])
#print(np.divide(2,a))

a = np.array(6.17654719e-03)
b = np.array(1.63736781e-01)
c = np.sqrt(a**2 + b**2)
#print(np.subtract(a,b))

def EfieldX(p:np.ndarray):
    A = 1
    #B = 1.44
    B = .8

    E = np.multiply(A * np.exp(-(p[0] / B)** 4), (p[0]/B)**15)
    return np.array([E,0,0])

position = np.array([0,0,0])
#print(EfieldX(position))

vels = np.array([[0,0,0], [0,1,0], [1,1,1]])
v_mag_sq = np.array(list((map(lambda x: np.dot(x,x), vels))), dtype=float)

#print(v_mag_sq)

q = 1.6e-19 #coulomb
M = 1.67e-27 #kilograms
#print(q/M)

points = np.linspace([-3,0,0], [3,0,0], 100)
#print(points)

from magpylib import Collection
from magpylib.current import Circle

c1 = Circle(current=10)
c2 = Circle(current=1000)

collection = Collection()
collection.add(c1, c2)

#for child in collection:
    #print(child.current)

string = "1e-11"
#print(float(string))