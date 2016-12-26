#Process:
#1. Get a list of original sdf files
#2. Use chopRDKit02.py generates fragments and list of files with total atom number, carbon atom number, nitrogen and oxygen atom number
#3. Form lists of by atom numbers
#4. Run rmRedLinker03.py or rmRedRigid01.py on different lists generated by step 3. Remove redundancy of linkers and rigids.
#5. Remove temp file and dir.

#main-script:
#   - eMolFrag.py

#sub-scripts used: 
#   - loader.py
#   - chopRDKit02.py,
#   - combineLinkers01.py 
#   - rmRedRigid01.py, 
#   - rmRedLinker03.py, 
#   - mol-ali-04.py. 

#Usage: Read README file for detailed information.
# 1. Configure path: python ConfigurePath.py    # Path only need to be set before the first run if no changes to the paths.
# 2. /Path_to_Python/python /Path_to_scripts/eMolFrag.py /Path_to_input_directory/ /Path_to_output_directory/ Number-Of-Cores

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
# Modification  07/18/2016 - Pack up, format.
# Modification  07/19/2016 - Solve python 2.x/3.x compatibility problem.
# Modification  07/20/2016 - Solve python 2.x/3.x compatibility problem.
# Modification  07/21/2016 - Solve python 2.x/3.x compatibility problem.
# Modification  07/22/2016 - Solve python 2.x/3.x compatibility problem.
# Modification  07/22/2016 - Modify README file
# Last revision 09/13/2016 - Solve output path conflict problem.

import subprocess
import os
import path
import os.path
import shutil
import sys
import time
from multiprocessing import Pool
from functools import partial


def ParseArgs():
    #input and output path define and create
    args=sys.argv
    #inputFolderPath=args[1]
    #outputDir=args[2]
    mainEntryPath=os.path.abspath(args[0])
    
    inputFolderPath = []
    outputDir = []
    processNum = 1
    outputSelection = 0
    outputFormat = 0
    
    if len(args) > 1:
        argList = args[1:]
    else:
        print('Error Code: 1010. Incorrect arguments.')
        return

    if len(argList) == 10:  # -i -o -p -m -c
        paraFlag = 1
        #print('Show')
        if (argList[0] == '-i') and (argList[2] == '-o') and (argList[4] == '-p') and (argList[6] == '-m') and (argList[8] == '-c'):
            # input path
            tempPath1 = os.path.abspath(argList[1])
            #print(tempPath1)
            if os.path.isdir(tempPath1):
                inputFolderPath = tempPath1
                if inputFolderPath[-1]=='/':
                    pass
                else:
                    inputFolderPath=inputFolderPath+'/'
            else:
                paraFlag = 0
            #print(paraFlag)
            # output path
            tempPath2 = os.path.abspath(argList[3])
            #print(tempPath2)
            #if os.path.isdir(tempPath2):
            outputDir = tempPath2
            if outputDir[-1]=='/':
                pass
            else:
                outputDir=outputDir+'/'
            #else:
            #    paraFlag = 0
            #print(outputDir)
            # parallel
            tempCoreNum = int(argList[5])
            if (tempCoreNum >= 1) and (tempCoreNum <= 16):
                processNum = tempCoreNum
            else:
                paraFlag = 0
            #print(paraFlag)
            # output select
            tempOutputSelection = int(argList[7])
            if (tempOutputSelection >= 0) and (tempOutputSelection <= 2):
                outputSelection = tempOutputSelection
            else:
                paraFlag = 0
                
            # output format
            tempOutputFormat = int(argList[9])
            if (tempOutputFormat >= 0) and (tempOutputFormat <= 1):
                outputFormat = tempOutputFormat
            else:
                paraFlag = 0
        else:
            paraFlag = 0
    
        if paraFlag == 1:
            pass
        else:
            print('Error Code: 1012. Incorrect arguments.')
            return
            
    elif len(argList) == 8: # -i -o, two of three (-p -m -c)
        paraFlag = 1
        if (argList[0] == '-i') and (argList[2] == '-o'):
            # input path
            tempPath1 = os.path.abspath(argList[1])
            if os.path.isdir(tempPath1):
                inputFolderPath = tempPath1
                if inputFolderPath[-1]=='/':
                    pass
                else:
                    inputFolderPath=inputFolderPath+'/'
            else:
                paraFlag = 0
            
            # output path
            tempPath2 = os.path.abspath(argList[3])
            #if os.path.isdir(tempPath2):
            outputDir = tempPath2
            if outputDir[-1]=='/':
                pass
            else:
                outputDir=outputDir+'/'
            #else:
            #    paraFlag = 0
        else:
            paraFlag = 0

        if (argList[4] == '-p') and (argList[6] == '-m'):
            # parallel
            tempCoreNum = int(argList[5])
            if (tempCoreNum >= 1) and (tempCoreNum <= 16):
                processNum = tempCoreNum
            else:
                paraFlag = 0

            # output select
            tempOutputSelection = int(argList[7])
            if (tempOutputSelection >= 0) and (tempOutputSelection <= 2):
                outputSelection = tempOutputSelection
            else:
                paraFlag = 0
                
        elif (argList[4] == '-p') and (argList[6] == '-c'):
            # parallel
            tempCoreNum = int(argList[5])
            if (tempCoreNum >= 1) and (tempCoreNum <= 16):
                processNum = tempCoreNum
            else:
                paraFlag = 0

            # output format
            tempOutputFormat = int(argList[9])
            if (tempOutputFormat >= 0) and (tempOutputFormat <= 1):
                outputFormat = tempOutputFormat
            else:
                paraFlag = 0
        elif (argList[4] == '-m') and (argList[6] == '-c'):
            # output select
            tempOutputSelection = int(argList[7])
            if (tempOutputSelection >= 0) and (tempOutputSelection <= 2):
                outputSelection = tempOutputSelection
            else:
                paraFlag = 0
            
            # output format
            tempOutputFormat = int(argList[9])
            if (tempOutputFormat >= 0) and (tempOutputFormat <= 1):
                outputFormat = tempOutputFormat
            else:
                paraFlag = 0
        else:
            paraFlag = 0

        if paraFlag == 1:
            pass
        else:
            print('Error Code: 1013. Incorrect arguments.')
            return

    elif len(argList) == 6: # -i -o, one of three (-p -m -c)
        paraFlag = 1
        if (argList[0] == '-i') and (argList[2] == '-o'):
            # input path
            tempPath1 = os.path.abspath(argList[1])
            if os.path.isdir(tempPath1):
                inputFolderPath = tempPath1
                if inputFolderPath[-1]=='/':
                    pass
                else:
                    inputFolderPath=inputFolderPath+'/'
            else:
                paraFlag = 0
            
            # output path
            tempPath2 = os.path.abspath(argList[3])
            #if os.path.isdir(tempPath2):
            outputDir = tempPath2
            if outputDir[-1]=='/':
                pass
            else:
                outputDir=outputDir+'/'
            #else:
            #    paraFlag = 0
        else:
            paraFlag = 0

        if (argList[4] == '-p'):
            # parallel
            tempCoreNum = int(argList[5])
            if (tempCoreNum >= 1) and (tempCoreNum <= 16):
                processNum = tempCoreNum
            else:
                paraFlag = 0
        elif (argList[4] == '-c'):
            # output format
            tempOutputFormat = int(argList[9])
            if (tempOutputFormat >= 0) and (tempOutputFormat <= 1):
                outputFormat = tempOutputFormat
            else:
                paraFlag = 0
        elif (argList[4] == '-m'):
            # output select
            tempOutputSelection = int(argList[7])
            if (tempOutputSelection >= 0) and (tempOutputSelection <= 2):
                outputSelection = tempOutputSelection
            else:
                paraFlag = 0
        else:
            paraFlag = 0

        if paraFlag == 1:
            pass
        else:
            print('Error Code: 1014. Incorrect arguments.')
            return

    elif len(argList) == 4: # -i -o
        paraFlag = 1
        if (argList[0] == '-i') and (argList[2] == '-o'):
            # input path
            tempPath1 = os.path.abspath(argList[1])
            if os.path.isdir(tempPath1):
                inputFolderPath = tempPath1
                if inputFolderPath[-1]=='/':
                    pass
                else:
                    inputFolderPath=inputFolderPath+'/'
            else:
                paraFlag = 0
            
            # output path
            tempPath2 = os.path.abspath(argList[3])
            #if os.path.isdir(tempPath2):
            outputDir = tempPath2
            if outputDir[-1]=='/':
                pass
            else:
                outputDir=outputDir+'/'
            #else:
            #    paraFlag = 0
        else:
            paraFlag = 0

        if paraFlag == 1:
            pass
        else:
            print('Error Code: 1015. Incorrect arguments.')
            return
    else:
        print('Error Code: 1011. Incorrect arguments.')
        return
    
    return [mainEntryPath, inputFolderPath, outputDir, processNum, outputSelection, outputFormat]



def PrepareEnv(outputDir, mainEntryPath, processNum):
    try:
        # check output folder conflict or not
        # detect output folder
        if os.path.exists(outputDir):
            print('Designate output path already exists, do you want to use another path? [y/n]')
            flagSetPath = 1
            ver = sys.version[0]
            p1 = ''
            p2 = ''
            while flagSetPath:
                if ver == '2':
                    p1 = raw_input()
                    if p1 == 'y':
                        print('Please type a new output path')
                        p2 = raw_input()
                        outputDir=os.path.abspath(p2)
                        print(outputDir)
                        if outputDir[-1]=='/':
                            pass
                        else:
                            outputDir=outputDir+'/'

                        if os.path.exists(outputDir):
                            print('Designate output path already exists, do you want to use another path? [y/n]')
                        else:
                            flagSetPath = 0
                            print('Output path successfully set. Continue...')

                    elif p1 == 'n':
                        print('Old files in this path will be deleted, continue? [y/n]')
                        p3 = raw_input()
                        if p3 == 'y':
                            shutil.rmtree(outputDir)
                            flagSetPath = 0
                        elif p3 == 'n':
                            print('Designate output path already exists, do you want to use another path? [y/n]')
                        else:
                            print('Unrecognizable character, please type again: [y/n]')
                 
                    else:
                        print('Unrecognizable character, please type again: [y/n]')
                elif ver == '3':
                    p1 = input()
                    if p1 == 'y':
                        print('Please type a new output path')
                        p2 = input()
                        outputDir=os.path.abspath(p2)
                        print(outputDir)
                        if outputDir[-1]=='/':
                            pass
                        else:
                            outputDir=outputDir+'/'

                        if os.path.exists(outputDir):
                            print('Designate output path already exists, do you want to use another path? [y/n]')
                        else:
                            flagSetPath = 0
                            print('Output path successfully set. Continue...')

                    elif p1 == 'n':
                        print('Old files in this path will be deleted, continue? [y/n]')
                        p3 = input()
                        if p3 == 'y':
                            shutil.rmtree(outputDir)
                            flagSetPath = 0
                        elif p3 == 'n':
                            print('Designate output path already exists, do you want to use another path? [y/n]')
                        else:
                            print('Unrecognizable character, please type again: [y/n]')

                    else:
                        print('Unrecognizable character, please type again: [y/n]')

                else:
                    print('Error Code: 1021. Get python version failed.')
                    return
    except:
        print('Error Code: 1020.')
        return

    try:
        # check scripts existance and completeness
        if os.path.exists(mainEntryPath):
            mainPath=os.path.dirname(mainEntryPath)
            if os.path.exists(mainPath+'/loader.py'):
                os.chdir(mainPath)
                pass
            else:
                print('Error Code: 1032. Cannot find part of script files.\nExit.')
                sys.exit()
        else:
            print('Error Code: 1031. Error input format.\nExit.')
            sys.exit()
    except:
        print('Error Code: 1030.')
        return
    
    try:
        pool=Pool(processes=processNum)
    except:
        print('Error Code: 1040.')
        return

    try:
        outputFolderPath_log=outputDir+'output-log/'
        outputFolderPath_chop=outputDir+'output-chop/'
        outputFolderPath_active=outputDir+'output-rigid/'
        outputFolderPath_linker=outputDir+'output-linker/'
        outputFolderPath_sdf=outputDir+'output-sdf/'
        outputFolderPath_chop_comb=outputDir+'output-chop-comb/'

        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
        #else:
        #    print('Designate output path already exists, do you want to use another path?')
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
    except:
        print('Error Code: 1050.')
        return

    try:
        try:
            from loader import Loader
        except:
            print('Error Code: 1061. Failed to load loader.')
            return

        try:
            initState=Loader(mainEntryPath)
        except:
            print('Error Code: 1062. Failed to load scripts and configures.')
            return

        if initState == 0:
            pass
        else:
            print('Error Code: 1063. Cannot load prerequisit.\nExit.')
            sys.exit()
    except:
        print('Error Code: 1060.')
        return

    outputPathList = [outputDir, outputFolderPath_log, outputFolderPath_chop, outputFolderPath_active, outputFolderPath_linker, outputFolderPath_sdf, outputFolderPath_chop_comb]
    return [outputPathList, pool]


def ProcessData(inputFolderPath, outputPathList, outputSelection, outputFormat, pool):
    try:
        [outputDir, outputFolderPath_log, outputFolderPath_chop, outputFolderPath_active, outputFolderPath_linker, outputFolderPath_sdf, outputFolderPath_chop_comb] = outputPathList
    except:
        print('Error Code: 1130. Failed to parse output path list.')
        return

    try:
        from combineLinkers01 import combineLinkers
        from rmRedLinker03 import RmLinkerRed
        from rmRedRigid01 import RmRigidRed
        from chopRDKit02 import ChopWithRDKit
    except:
        print('Error Code: 1070. Failed to load required lib files.')
        return

    # Create work
    try:
        path = outputFolderPath_log+'Process.log'
        msg = ' Create Work ' + inputFolderPath+' '+outputDir
        PrintLog(path, msg)
    except:
        print('Error Code: 1071. Failed to write log file.')

    try:
        GetInputList(inputFolderPath, outputFolderPath_log)
    except:
        print('Error Code: 1072.')
        return

    try:
        Chop(outputPathList, pool)
    except:
        print('Error Code: 1073.')
        return

    if (outputSelection == 0) or (outputSelection == 2):
        try:
            RmRigidRedundancy(outputPathList, pool)
        except:
            print('Error Code: 1074.')
            return

        try:
            RmLinkerRedundancy(outputPathList, pool)
        except:
            print('Error Code: 1075.')
            return
    else:
        pass

    # End Work
    try:
        path = outputFolderPath_log+'Process.log'
        msg = ' End Work '
        PrintLog(path, msg)
    except:
        print('Error Code: 1076. Failed to write log file.')
        return



def AdjustOutput(outputPathList, outputSelection, outputFormat):
    try:
        [outputDir, outputFolderPath_log, outputFolderPath_chop, outputFolderPath_active, outputFolderPath_linker, outputFolderPath_sdf, outputFolderPath_chop_comb] = outputPathList
    except:
        print('Error Code: 1130. Failed to parse output path list.')
        return
    #Step 5: Clear temp file and directory.
    if outputSelection == 0: # default output selection, full process and output, left 4 folders: log, rigid, linker, chop-comb
        shutil.rmtree(outputFolderPath_chop)
        shutil.rmtree(outputFolderPath_sdf)
    elif outputSelection == 1: # only chop and reconnect, not remove redundancy, left 2 folders: log, chop-comb
        shutil.rmtree(outputFolderPath_chop)
        shutil.rmtree(outputFolderPath_sdf)
        shutil.rmtree(outputFolderPath_active)
        shutil.rmtree(outputFolderPath_linker)
    elif outputSelection == 2: # chop and remove redundancy, but remove temp files, left 3 folders: log rigid, linker
        shutil.rmtree(outputFolderPath_chop)
        shutil.rmtree(outputFolderPath_sdf)
        shutil.rmtree(outputFolderPath_chop_comb)
    else:
        print('Error Code: 1131. Invalid output selection.')
        return

    if outputFormat == 1: # traditional format, each file only contain one molecule
        pass
    elif outputFormat == 0: # default output format, only one rigid file and only one linker file
        if outputSelection == 0:  # 4 output files, (rigid, linker)*(before remove, after remove)
            try:
                AdjustSub0(outputPathList)
            except:
                print('Error Code: 1134.')
                return
        elif outputSelection == 1:  # 2 output files, (rigid, linker)*(before remove)
            try:
                AdjustSub1(outputPathList)
            except:
                print('Error Code: 1135.')
                return
        elif outputSelection == 2:  # 2 output files, (rigid, linker)*(after remove)
            try:
                AdjustSub2(outputPathList)
            except:
                print('Error Code: 1136.')
                return
        else:
            print('Error Code: 1133.')
            return
    else:
        print('Error Code: 1132. Invalid output format.')
        return


def AdjustSub0(outputPathList):
    try:
        [outputDir, outputFolderPath_log, outputFolderPath_chop, outputFolderPath_active, outputFolderPath_linker, outputFolderPath_sdf, outputFolderPath_chop_comb] = outputPathList
    except:
        print('Error Code: 1140. Failed to parse output path list.')
        return

    try:
        [combFilePath, combFileName] = GetFileList(outputFolderPath_chop_comb)
    except:
        print('Error Code: 1141.')
        return

    try:
        tempRigidContent = []
        tempLinkerContent = []
        b4rmRigidPath = outputDir + 'RigidFull.sdf'
        b4rmLinkerPath = outputDir + 'LinkerFull.sdf'
        for i in range(len(combFilePath)):
            if combFileName[i][0] == 'r':
                with open(combFilePath[i], 'r') as inf:
                    tempRigidContent = inf.readlines()
                with open(b4rmRigidPath, 'at') as outf:
                    outf.writelines(tempRigidContent)
                    outf.write('\n')
                tempRigidContent = []
            elif combFileName[i][0] == 'l':
                with open(combFilePath[i], 'r') as inf:
                    tempLinkerContent = inf.readlines()
                with open(b4rmLinkerPath, 'at') as outf:
                    outf.writelines(tempLinkerContent)
                    outf.write('\n')
                tempLinkerContent = []
            else:
                pass
    except:
        print('Error Code: 1142.')

    try:
        [rigidFilePath, rigidFileName] = GetFileList(outputFolderPath_active)
    except:
        print('Error Code: 1143.')

    try:
        tempRigidContent = []
        rmdRigidPath = outputDir + 'RigidUnique.sdf'
        for i in range(len(rigidFilePath)):
            if rigidFileName[i][0] == 'r':
                with open(rigidFilePath[i], 'r') as inf:
                    tempRigidContent = inf.readlines()
                with open(rmdRigidPath, 'at') as outf:
                    outf.writelines(tempRigidContent)
                    outf.write('\n')
                tempRigidContent = []
    except:
        print('Error Code: 1144.')

    try:
        [linkerFilePath, linkerFileName] = GetFileList(outputFolderPath_linker)
    except:
        print('Error Code: 1145.')

    try:
        tempLinkerContent = []
        rmdLinkerPath = outputDir + 'LinkerUnique.sdf'
        for i in range(len(linkerFilePath)):
            if linkerFileName[i][0] == 'l':
                with open(linkerFilePath[i], 'r') as inf:
                    tempLinkerContent = inf.readlines()
                with open(rmdLinkerPath, 'at') as outf:
                    outf.writelines(tempLinkerContent)
                    outf.write('\n')
                tempLinkerContent = []
    except:
        print('Error Code: 1146.')

    try:
        shutil.rmtree(outputFolderPath_chop_comb)
        shutil.rmtree(outputFolderPath_active)
        shutil.rmtree(outputFolderPath_linker)
    except:
        print('Error Code: 1147. Failed to remove temp files.')



def AdjustSub1(outputPathList):
    try:
        [outputDir, outputFolderPath_log, outputFolderPath_chop, outputFolderPath_active, outputFolderPath_linker, outputFolderPath_sdf, outputFolderPath_chop_comb] = outputPathList
    except:
        print('Error Code: 1150. Failed to parse output path list.')
        return

    try:
        [combFilePath, combFileName] = GetFileList(outputFolderPath_chop_comb)
    except:
        print('Error Code: 1151.')
        return

    try:
        tempRigidContent = []
        tempLinkerContent = []
        b4rmRigidPath = outputDir + 'RigidFull.sdf'
        b4rmLinkerPath = outputDir + 'LinkerFull.sdf'
        for i in range(len(combFilePath)):
            if combFileName[i][0] == 'r':
                with open(combFilePath[i], 'r') as inf:
                    tempRigidContent = inf.readlines()
                with open(b4rmRigidPath, 'at') as outf:
                    outf.writelines(tempRigidContent)
                    outf.write('\n')
                tempRigidContent = []
            elif combFileName[i][0] == 'l':
                with open(combFilePath[i], 'r') as inf:
                    tempLinkerContent = inf.readlines()
                with open(b4rmLinkerPath, 'at') as outf:
                    outf.writelines(tempLinkerContent)
                    outf.write('\n')
                tempLinkerContent = []
            else:
                pass
    except:
        print('Error Code: 1152.')

    try:
        shutil.rmtree(outputFolderPath_chop_comb)
    except:
        print('Error Code: 1157. Failed to remove temp files.')




def AdjustSub2(outputPathList):
    try:
        [outputDir, outputFolderPath_log, outputFolderPath_chop, outputFolderPath_active, outputFolderPath_linker, outputFolderPath_sdf, outputFolderPath_chop_comb] = outputPathList
    except:
        print('Error Code: 1160. Failed to parse output path list.')
        return

    try:
        [rigidFilePath, rigidFileName] = GetFileList(outputFolderPath_active)
    except:
        print('Error Code: 1163.')

    try:
        tempRigidContent = []
        rmdRigidPath = outputDir + 'RigidUnique.sdf'
        for i in range(len(rigidFilePath)):
            if rigidFileName[i][0] == 'r':
                with open(rigidFilePath[i], 'r') as inf:
                    tempRigidContent = inf.readlines()
                with open(rmdRigidPath, 'at') as outf:
                    outf.writelines(tempRigidContent)
                    outf.write('\n')
                tempRigidContent = []
    except:
        print('Error Code: 1164.')

    try:
        [linkerFilePath, linkerFileName] = GetFileList(outputFolderPath_linker)
    except:
        print('Error Code: 1165.')

    try:
        tempLinkerContent = []
        rmdLinkerPath = outputDir + 'LinkerUnique.sdf'
        for i in range(len(linkerFilePath)):
            if linkerFileName[i][0] == 'l':
                with open(linkerFilePath[i], 'r') as inf:
                    tempLinkerContent = inf.readlines()
                with open(rmdLinkerPath, 'at') as outf:
                    outf.writelines(tempLinkerContent)
                    outf.write('\n')
                tempLinkerContent = []
    except:
        print('Error Code: 1166.')

    try:
        shutil.rmtree(outputFolderPath_active)
        shutil.rmtree(outputFolderPath_linker)
    except:
        print('Error Code: 1167. Failed to remove temp files.')




def GetFileList(path):
    try:
        fileNameList = []
        filePathList = []
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    fileNameList.append(file)
                    filePathList.append(path+file)
            return [filePathList, fileNameList]
        except:
            print('Error Code: 1171.')
            return
    except:
        print('Error Code: 1170.')
        return


def GetInputList(inputFolderPath, outputFolderPath_log):
    #Step 1: Get a list of original *.mol2 files
    try:
        fileNameList=[]
        infilePathList=[]
        outfilePathList=[]

        try:
            for root, dirs, files in os.walk(inputFolderPath):
                for file in files:
                    fileNameList.append(file)
                    infilePathList.append(inputFolderPath+file+'\n')
        except:
            print('Error Code: 1081.')
            return

        try:
            with open(outputFolderPath_log+'InputList','at') as outList:
                outList.writelines(infilePathList)
        except:
            print('Error Code: 1082.')
            return

    except:
        print('Error Code: 1080. Failed to get input file list.')
        return


def Chop(outputPathList, pool):
    try:
        [outputDir, outputFolderPath_log, outputFolderPath_chop, outputFolderPath_active, outputFolderPath_linker, outputFolderPath_sdf, outputFolderPath_chop_comb] = outputPathList
    except:
        print('Error Code: 1130. Failed to parse output path list.')
        return
    
    try:
        from chopRDKit02 import ChopWithRDKit
    except:
        print('Error Code: 1090-01.')
        return

    #Step 2: chop and generate list
    # Log
    try:
        path = outputFolderPath_log+'Process.log'
        msg = ' Start Chop '
        PrintLog(path, msg)
    except:
        print('Error Code: 1090. Failed to write log file.')
        return
    
    try:
        inputList=[]
        with open(outputFolderPath_log+'InputList','r') as inList:
            for lines in inList:
                inputList.append(lines.replace('\n',''))
    except:
        print('Error Code: 1091.')
        return

    try:
        partial_Chop=partial(ChopWithRDKit, outputDir)
        pool.map(partial_Chop,inputList)
    except:
        print('Error Code: 1092.')
        return

    try:
        # Log
        path = outputFolderPath_log+'Process.log'
        msg = ' End Chop '
        PrintLog(path, msg)
    except:
        print('Error Code: 1093.')
        return

def RmRigidRedundancy(outputPathList, pool):
    try:
        [outputDir, outputFolderPath_log, outputFolderPath_chop, outputFolderPath_active, outputFolderPath_linker, outputFolderPath_sdf, outputFolderPath_chop_comb] = outputPathList
    except:
        print('Error Code: 1130. Failed to parse output path list.')
        return
    try:
        from rmRedRigid01 import RmRigidRed
    except:
        print('Error Code: 1100-01')
        return

    # Rigid Part
    #Step 3: Form and group lists by atom numbers
    fileNameAndAtomNumList_R=[]
    try:
        with open(outputFolderPath_log+'RigidListAll.txt','r') as inList:
            fileNameAndAtomNumList_R=inList.readlines()
    except:
        print('Error Code: 1100.')
        return

    FNAANLList_R=[] #file name and atom number list list
    try:
        for FNAAN in fileNameAndAtomNumList_R: #FNAAN: file name and atom number
            FNAANList=FNAAN.split() #FNAANList: file name and atom number list
            FNAANLList_R.append([FNAANList[0],FNAANList[1:]])
    except:
        print('Error Code: 1101.')
        return

    atomNumPro_R=[]
    try:
        for tempValue in FNAANLList_R: #tempValue: [[filename],['T','','C','','N','','O','']]
            if tempValue[1] not in atomNumPro_R: #tempValue[1]: ['T','','C','','N','','O',''],Group Property
                atomNumPro_R.append(tempValue[1])
    except:
        print('Error Code: 1102.')
        return

    try:
        fileNameGroup_R=[[y[0] for y in FNAANLList_R if y[1]==x] for x in atomNumPro_R]
    except:
        print('Error Code: 1103.')
        return

    try:
        with open(outputFolderPath_log+'RigidGroupList.txt','w') as groupOut:
            for i in range(len(atomNumPro_R)):
                groupOut.write(' '.join(atomNumPro_R[i])+' - ')
                groupOut.write('File Num: ')
                groupOut.write(str(len(fileNameGroup_R[i])))
                groupOut.write('\n')
    except:
        print('Error Code: 1104.')
        return

    try:
        # Log
        path = outputFolderPath_log+'Process.log'
        msg = ' Start Remove Rigid Redundancy '
        PrintLog(path, msg)
    except:
        print('Error Code: 1105.')
        return

    #Step 4: Generate similarity data and etc.
    try:
        fileNameGroup_Rs=sorted(fileNameGroup_R,key=lambda x:len(x),reverse=True) #process long list first
    except:
        print('Error Code: 1106.')
        return

    try:
        partial_RmRigid=partial(RmRigidRed, outputDir)
        pool.map(partial_RmRigid,fileNameGroup_Rs)
    except:
        print('Error Code: 1107.')
        return

    try:
        # Log
        path = outputFolderPath_log+'Process.log'
        msg = ' End Remove Rigid Redundancy '
        PrintLog(path, msg)
    except:
        print('Error Code: 1108.')
        return


def RmLinkerRedundancy(outputPathList, pool):
    try:
        [outputDir, outputFolderPath_log, outputFolderPath_chop, outputFolderPath_active, outputFolderPath_linker, outputFolderPath_sdf, outputFolderPath_chop_comb] = outputPathList
    except:
        print('Error Code: 1130. Failed to parse output path list.')
        return

    try:
        from combineLinkers01 import combineLinkers
        from rmRedLinker03 import RmLinkerRed
    except:
        print('Error Code: 1110-01')
        return

    # Linker Part
    #Step 3: Form and group lists by atom numbers
    fileNameAndAtomNumList_L=[]
    try:
        with open(outputFolderPath_log+'LinkerListAll.txt','r') as inList:
            fileNameAndAtomNumList_L=inList.readlines()
    except:
        print('Error Code: 1110.')
        return

    FNAANLList_L=[] #file name and atom number list list
    try:
        for FNAAN in fileNameAndAtomNumList_L: #FNAAN: file name and atom number
            FNAANList=FNAAN.split() #FNAANList: file name and atom number list
            FNAANLList_L.append([FNAANList[0],FNAANList[1:]])
    except:
        print('Error Code: 1111.')
        return

    atomNumPro_L=[]
    try:
        for tempValue in FNAANLList_L:
            if tempValue[1] not in atomNumPro_L:
                atomNumPro_L.append(tempValue[1])
    except:
        print('Error Code: 1112.')
        return

    try:
        fileNameGroup_L=[[y[0] for y in FNAANLList_L if y[1]==x] for x in atomNumPro_L]
    except:
        print('Error Code: 1113.')
        return

    try:
        with open(outputFolderPath_log+'LinkerGroupList.txt','w') as groupOut:
            for i in range(len(atomNumPro_L)):
                groupOut.write(' '.join(atomNumPro_L[i])+' - ')
                groupOut.write('File Num: ')
                groupOut.write(str(len(fileNameGroup_L[i])))
                groupOut.write('\n')
    except:
        print('Error Code: 1114.')
        return

    try:
        # Log
        path = outputFolderPath_log+'Process.log'
        msg = ' Start Remove Linker Redundancy '
        PrintLog(path, msg)
    except:
        print('Error Code: 1115.')
        return

    #Step 4: Generate similarity data and etc.
    try:
        partial_RmLinker=partial(RmLinkerRed, outputDir)
    except:
        print('Error Code: 1116.')
        return

    inputL=[]

    try:
        for i in range(len(fileNameGroup_L)):
            inputL.append([fileNameGroup_L[i],atomNumPro_L[i]])
    except:
        print('Error Code: 1117.')
        return

    try:
        inputLs=sorted(inputL,key=lambda x:len(x[0]),reverse=True)
    except:
        print('1118.')
        return

    try:
        pool.map(partial_RmLinker,inputLs)
    except:
        print('1119.')
        return

    try:
        # Log
        path = outputFolderPath_log+'Process.log'
        msg = ' End Remove Linker Redundancy '
        PrintLog(path, msg)
    except:
        print('Error Code: 1120.')
        return



def PrintLog(path, msg):
    # write log
    with open(path, 'at') as outLog:
        outLog.write(time.asctime( time.localtime(time.time()) ))
        outLog.write(msg)
        outLog.write('\n')

def main():
    try:
        try:
            [mainEntryPath, inputFolderPath, outputDir, processNum, outputSelection, outputFormat] = ParseArgs()
        except:
            print('Error Code: 1001. Failed to parse input commands.')
            return
        
        try:
            [outputPathList, pool] = PrepareEnv(outputDir, mainEntryPath, processNum)
        except:
            print('Error Code: 1002. Failed to prepare running evnironment.')
            return
        
        try:
            ProcessData(inputFolderPath, outputPathList, outputSelection, outputFormat, pool)
        except:
            print('Error Code: 1003. Failed to process data.')
            return
        
        try:
            AdjustOutput(outputPathList, outputSelection, outputFormat)
        except:
            print('Error Code: 1004. Failed to adjust output format.')
            return
            
    except:
        print('Error Code: 1000')
        return


if __name__ == "__main__":
    main()
