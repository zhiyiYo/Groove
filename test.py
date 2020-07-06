import os
a=['hzz',16]
b = [555, 999]
c=[1,2,3]
for index, (ai, bi,ci) in enumerate(zip(a,b,c)):
    print(index,ai,bi,ci)