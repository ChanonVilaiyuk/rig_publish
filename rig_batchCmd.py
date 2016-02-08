# System modules
import sys
import os
import re
import shutil
import time


# Maya modules
import maya.standalone
maya.standalone.initialize( name='python' )

import maya.cmds as mc
import maya.mel as mm
# import pymel.core as pm

sys.path.append('O:/studioTools/maya/python')
from tool.utils import pipelineTools as pt
reload(pt)

from tool.rig.cmd import rig_cmd as rigCmd
reload(rigCmd)

sysPath = 'O:/studioTools/maya/python/tool/rig/nuTools/pipeline'
sys.path.append(sysPath)
import pipeTools
reload(pipeTools)

from tool.publish.rig import setting
reload(setting)

from tool.utils import entityInfo2 as entityInfo 
reload(entityInfo)

def main() :
    # init maya standalone
    # set arguments 

    src = sys.argv[1]
    dst = sys.argv[2]
    cmdsRaw = sys.argv[3]
    content = sys.argv[4]
    output = sys.argv[5]

    cmds = eval(cmdsRaw)
    asset = entityInfo.info(src)

    # open scene 
    mc.file(src, o = True, f = True)

    for cmd in cmds : 
        # if cmd in setting.cmdList.keys() : 
            # print 'run %s' % setting.cmdList[cmd]
            # eval(setting.cmdList[cmd])
        cmd = 'rigCmd.%s()' % cmd
        eval(cmd)

    print 'run complete'

    if output == 'save' : 
        # save file 
        mc.file(rename = dst)
        mc.file(save = True, f = True, type = 'mayaAscii')
        print 'File saved'

    if output == 'export' : 
        if mc.objExists(content) : 
            mc.select(content)
            mc.file(dst, f = True, options = 'v=0', type = 'mayaAscii', pr = True, es = True)
            print 'File exported'


main()