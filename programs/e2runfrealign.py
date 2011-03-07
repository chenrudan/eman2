#!/usr/bin/env python

import os
import sys

if len(sys.argv) != 1:
   print "Please use e2runfrealign.py"
   exit(-1)

os.system('clear')
os.system('cp 3DMapInOut.mrc 3DMapInOut.mrc.old')
os.system('cp ptcl_meta_data ptcl_meta_data.old')
dir_list = os.listdir('.')
dir_list.sort()
high = 0
for item in dir_list:
   print len(item)
   if len(item) > 6:
      print item[:4]
      if item[:4] == 'card':
         item = item.replace(".txt",'')
         item = item.replace("card",'')
         print int(item)
         if int(item) > high:
            high = int(item)

print high

for i in range(high):
   os.system('frealign_v8.exe < card' + str(i) + '.txt')
   if i < 10:
      k = '0' + str(i) 
   else:
      k = str(i)
   s = "cp 3DMapInOut.mrc OutputMap_" + k +".mrc"
   os.system(s)
   s = "cp OutParam OutParam_" + k
   os.system(s)
   os.system('mv OutParam ptcl_meta_data')
   s = "cp OutParamShift OutParamShift_" + k
   os.system(s)

os.system('mv 3DMapInOut.mrc.old 3DMapInOut.mrc')
os.system('mv ptcl_meta_data.old ptcl_meta_data')

print "e2runfrealign.py finished"

exit(0)
