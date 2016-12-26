#Process:
#1. Get a list of original sdf files
#2. Use chopRDKit02.py generates fragments and list of files with total atom number, carbon atom number, nitrogen and oxygen atom number
#3. Form lists of by atom numbers
#4. Run rmRedLinker03.py or rmRedRigid01.py on different lists generated by step 3. Remove redundancy of linkers and rigids.
#5. Remove temp file and dir.

#main-script:
#   - echop.py

#sub-scripts used: 
#   - chopRDKit02.py,
#   - combineLinkers01.py 
#   - rmRedRigid01.py, 
#   - rmRedLinker03.py, 
#   - mol-ali-04.py. 

#Usage: /Path to Python/python /Path to scripts/echop.py /Path to input directory/ /Path to output directory/ Number-Of-Cores

#Example: /home/username/apps/.../python /home/username/scripts/echop.py /work/username/run-xxxx/lib-source-mol2/ /work/username/run-xxxx/outputp-libname-x/ 16

#Args:
#   - /Path to Python/           ... Use python to run the script
#   - /Path to scripts/echop.py ... The directory of scripts and the name of the entrance to the software
#   - /Path to input directory/  ... The path to the input directory, in which is the input molecules in *.mol2 format
#   - /Path to output directory/ ... The path to the output directory, in which is the output files
#   - Number-Of-Cores            ... Number of processings to be used in the run 

#Update Log:
#This script is written by Tairan Liu.
# Created       01/17/2016 - Chop
# Modification  01/17/2016 - Remove bug
# Modification  01/18/2016 - Reconnect linkers
# Modification  01/21/2016 - Remove redundancy
# Modification  02/29/2016 - Remove bug
# Modification  03/16/2016 - Remove bug
# Modification  03/17/2016 - Remove bug
# Modification  03/24/2016 - Remove bug
# Modification  03/25/2016 - Change each step to functions
# Modification  04/03/2016 - Remove bug
# Modification  04/06/2016 - Reduce temp output files
# Modification  04/06/2016 - Remove bug
# Modification  04/06/2016 - Start parallel with chop
# Modification  04/17/2016 - Improve efficiency
# Modification  04/18/2016 - Remove bug
# Modification  05/24/2016 - Start parallel with remove redundancy
# Modification  06/14/2016 - Add parallel option as arg
# Modification  06/14/2016 - Remove bug
# Modification  06/29/2016 - Remove bug
# Modification  07/08/2016 - Change similarity criteria of rigids from 0.95 to 0.97
# Modification  07/11/2016 - Improve efficiency
# Last revision 07/18/2016 - Pack up, format.

import subprocess
import os
import path
import os.path
import shutil
import sys
import time
from multiprocessing import Pool
from functools import partial

from loader import Loader

initState=Loader()
if initState==0:
    pass
else:
    sys.exit()

from combineLinkers01 import combineLinkers
from rmRedLinker03 import RmLinkerRed
from rmRedRigid01 import RmRigidRed
from chopRDKit02 import ChopWithRDKit

#input and output path define and create
args=sys.argv
inputFolderPath=args[1]
outputDir=args[2]
if inputFolderPath[-1]=='/':
    pass
else:
    inputFolderPath=inputFolderPath+'/'

if outputDir[-1]=='/':
    pass
else:
    outputDir=outputDir+'/'


processNum=int(args[3])
#inputFolderPath='/work/username/xxx/test-set/' #'ARGV[0]/'
#outputDir='/work/username/xxx/outputDir/'   #'ARGV[0]/outputDir/'

pool=Pool(processes=processNum)

outputFolderPath_log=outputDir+'output-log/'
outputFolderPath_chop=outputDir+'output-chop/'
outputFolderPath_active=outputDir+'output-active/'
outputFolderPath_linker=outputDir+'output-linker/'
outputFolderPath_sdf=outputDir+'output-sdf/'
outputFolderPath_chop_comb=outputDir+'output-chop-comb/'

if not os.path.exists(outputDir):
    os.mkdir(outputDir)
if not os.path.exists(outputFolderPath_log):
    os.mkdir(outputFolderPath_log)
if not os.path.exists(outputFolderPath_chop):
    os.mkdir(outputFolderPath_chop)
if not os.path.exists(outputFolderPath_active):
    os.mkdir(outputFolderPath_active)
if not os.path.exists(outputFolderPath_linker):
    os.mkdir(outputFolderPath_linker)
if not os.path.exists(outputFolderPath_sdf):
    os.mkdir(outputFolderPath_sdf)
if not os.path.exists(outputFolderPath_chop_comb):
    os.mkdir(outputFolderPath_chop_comb)
#Write Log
with open(outputFolderPath_log+'Process.log','at') as outLog:
    outLog.write(time.asctime( time.localtime(time.time()) ))
    outLog.write(' Create Work ')
    outLog.write(inputFolderPath+' '+outputDir)
    outLog.write('\n')


#Step 1: Get a list of original *.mol2 files

fileNameList=[]
infilePathList=[]
outfilePathList=[]

for root, dirs, files in os.walk(inputFolderPath):
    for file in files:
        fileNameList.append(file)
        infilePathList.append(inputFolderPath+file+'\n')

with open(outputFolderPath_log+'InputList','at') as outList:
    outList.writelines(infilePathList)


#Write Log
with open(outputFolderPath_log+'Process.log','at') as outLog:
    outLog.write(time.asctime( time.localtime(time.time()) ))
    outLog.write(' Start Chop ')
    outLog.write('\n')


#Step 2: chop and generate list
inputList=[]
with open(outputFolderPath_log+'InputList','r') as inList:
    for lines in inList:
	inputList.append(lines.replace('\n',''))


partial_Chop=partial(ChopWithRDKit, outputDir)
pool.map(partial_Chop,inputList)


#Write Log
with open(outputFolderPath_log+'Process.log','at') as outLog:
    outLog.write(time.asctime( time.localtime(time.time()) ))
    outLog.write(' End Chop ')
    outLog.write('\n')

# Rigid Part
#Step 3: Form and group lists by atom numbers
fileNameAndAtomNumList_R=[]
with open(outputFolderPath_log+'RigidListAll.txt','r') as inList:
    fileNameAndAtomNumList_R=inList.readlines()

FNAANLList_R=[] #file name and atom number list list
for FNAAN in fileNameAndAtomNumList_R: #FNAAN: file name and atom number
    FNAANList=FNAAN.split() #FNAANList: file name and atom number list
    FNAANLList_R.append([FNAANList[0],FNAANList[1:]])

atomNumPro_R=[]
for tempValue in FNAANLList_R: #tempValue: [[filename],['T','','C','','N','','O','']]
    if tempValue[1] not in atomNumPro_R: #tempValue[1]: ['T','','C','','N','','O',''],Group Property
	atomNumPro_R.append(tempValue[1])

fileNameGroup_R=[[y[0] for y in FNAANLList_R if y[1]==x] for x in atomNumPro_R]


with open(outputFolderPath_log+'RigidGroupList.txt','w') as groupOut:
    for i in range(len(atomNumPro_R)):
	groupOut.write(' '.join(atomNumPro_R[i])+' - ')
	groupOut.write('File Num: ')
	groupOut.write(str(len(fileNameGroup_R[i])))
	groupOut.write('\n')


#Write Log
with open(outputFolderPath_log+'Process.log','at') as outLog:
    outLog.write(time.asctime( time.localtime(time.time()) ))
    outLog.write(' Start Remove Rigid Redundancy ')
    outLog.write('\n')


#Step 4: Generate similarity data and etc.
fileNameGroup_Rs=sorted(fileNameGroup_R,key=lambda x:len(x),reverse=True) #process long list first
partial_RmRigid=partial(RmRigidRed, outputDir)
pool.map(partial_RmRigid,fileNameGroup_Rs)

#Write Log
with open(outputFolderPath_log+'Process.log','at') as outLog:
    outLog.write(time.asctime( time.localtime(time.time()) ))
    outLog.write(' End Remove Rigid Redundancy ')
    outLog.write('\n')


# Linker Part
#Step 3: Form and group lists by atom numbers
fileNameAndAtomNumList_L=[]
with open(outputFolderPath_log+'LinkerListAll.txt','r') as inList:
    fileNameAndAtomNumList_L=inList.readlines()

FNAANLList_L=[] #file name and atom number list list
for FNAAN in fileNameAndAtomNumList_L: #FNAAN: file name and atom number
    FNAANList=FNAAN.split() #FNAANList: file name and atom number list
    FNAANLList_L.append([FNAANList[0],FNAANList[1:]])

atomNumPro_L=[]
for tempValue in FNAANLList_L:
    if tempValue[1] not in atomNumPro_L:
        atomNumPro_L.append(tempValue[1])

fileNameGroup_L=[[y[0] for y in FNAANLList_L if y[1]==x] for x in atomNumPro_L]

with open(outputFolderPath_log+'LinkerGroupList.txt','w') as groupOut:
    for i in range(len(atomNumPro_L)):
        groupOut.write(' '.join(atomNumPro_L[i])+' - ')
        groupOut.write('File Num: ')
        groupOut.write(str(len(fileNameGroup_L[i])))
        groupOut.write('\n')


#Write Log
with open(outputFolderPath_log+'Process.log','at') as outLog:
    outLog.write(time.asctime( time.localtime(time.time()) ))
    outLog.write(' Start Remove Linker Redundancy ')
    outLog.write('\n')


#Step 4: Generate similarity data and etc.

partial_RmLinker=partial(RmLinkerRed, outputDir)
inputL=[]
for i in range(len(fileNameGroup_L)):
    inputL.append([fileNameGroup_L[i],atomNumPro_L[i]])

inputLs=sorted(inputL,key=lambda x:len(x[0]),reverse=True)
pool.map(partial_RmLinker,inputLs)


#Write Log
with open(outputFolderPath_log+'Process.log','at') as outLog:
    outLog.write(time.asctime( time.localtime(time.time()) ))
    outLog.write(' End Remove Linker Redundancy ')
    outLog.write('\n')


#Step 5: Clear temp file and directory.


#Write Log
with open(outputFolderPath_log+'Process.log','at') as outLog:
    outLog.write(time.asctime( time.localtime(time.time()) ))
    outLog.write(' End Work ')
    outLog.write('\n')
