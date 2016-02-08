import sys, os 
import subprocess 

# MAYA_PYTHON = 'C:/Program Files/Autodesk/Maya2015/bin/mayabatch.exe'
MAYA_PYTHON = 'C:\\Program Files\\Autodesk\\Maya2015\\bin\\mayapy.exe'

MAYACMD = 'O:/studioTools/maya/python/tool/publish/rig/rig_batchCmd.py'

def run(src, dst, cmds, content = '', output = 'save') : 
	subprocess.call([MAYA_PYTHON, MAYACMD, src, dst, cmds, content, output])