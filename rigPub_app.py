import maya.OpenMayaUI as mui
import maya.cmds as mc
import maya.mel as mm
import sys,shiboken, os
from datetime import datetime

from PySide import QtGui  
from PySide import QtCore
from PySide import QtUiTools
from shiboken import wrapInstance, delete

sys.path.append('O:/studioTools/maya/python')

from tool.utils import fileUtils, mayaTools, pipelineTools
reload(fileUtils)
reload(mayaTools)
reload(pipelineTools)

from tool.utils import entityInfo2 as entityInfo
reload(entityInfo)

from tool.utils import abcUtils
reload(abcUtils)

from tool.publish.rig import setting
reload(setting)

from tool.publish.rig import rig_batch as rigBatch 
reload(rigBatch)

from tool.rig.cmd import rig_cmd as rigCmd 
reload(rigCmd)

from inspect import getmembers, isfunction

moduleDir = sys.modules[__name__].__file__


def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    if ptr is not  None:
        # ptr = mui.MQtUtil.mainWindow()
        return wrapInstance(long(ptr), QtGui.QMainWindow)



class MyForm(QtGui.QMainWindow):
    def __init__(self,parent=None):

        # QtGui.QWidget.__init__(self,parent)
        super(MyForm, self).__init__(parent)


        if mc.window('rigPublishWin', exists = True) : 
            mc.deleteUI('rigPublishWin')
        # apply(QtGui.QMainWindow.__init__, (self,))


        loader = QtUiTools.QUiLoader()
        loader.setWorkingDirectory('O:/studioTools/maya/python/tool/publish/rig')
        file = QtCore.QFile("O:/studioTools/maya/python/tool/publish/rig/ui.ui")
        file.open(QtCore.QFile.ReadOnly)
        self.myWidget = loader.load(file, self)
        # self.myWidget = loader.load(file, parent)
        self.ui = self.myWidget
        file.close()

        self.ui.show()
        self.ui.setWindowTitle('PT rig publish v.3.0')

        self.okIcon = '%s/%s' % (os.path.dirname(moduleDir), 'icons/ok_icon.png')
        self.xIcon = '%s/%s' % (os.path.dirname(moduleDir), 'icons/x_icon.png')
        self.rdyIcon = '%s/%s' % (os.path.dirname(moduleDir), 'icons/rdy_icon.png')
        self.cmdIcon = '%s/%s' % (os.path.dirname(moduleDir), 'icons/cmd_icon.png')

        self.cmdPath = 'O:/studioTools/maya/python/tool/rig/cmd/rig_cmd.py'
        self.presetPath = 'O:/studioTools/maya/python/tool/publish/rig/presets.yml'

        self.initFunctions()
        self.initSignals()


    def initFunctions(self) : 
        self.refreshData()
        self.setAssetUI()
        self.initPath()
        self.listCommands()
        self.listExeList()


    def initSignals(self) : 
        self.ui.add_pushButton.clicked.connect(self.doAddList)
        self.ui.remove_pushButton.clicked.connect(self.doRemoveList)
        self.ui.preset_comboBox.currentIndexChanged.connect(self.listExeList)
        self.ui.publish_pushButton.clicked.connect(self.doPublish)
        self.ui.clear_pushButton.clicked.connect(self.clearList)
        self.ui.savePreset_pushButton.clicked.connect(self.doSavePreset)

        self.ui.workFile_pushButton.clicked.connect(self.doOpenWorkFile)
        self.ui.outputFile_pushButton.clicked.connect(self.doOpenOutputFile)
        self.ui.task_comboBox.currentIndexChanged.connect(self.setOutputPath)

        self.ui.cmd_listWidget.itemSelectionChanged.connect(self.showDocString)


    def refreshData(self) : 
        self.asset = entityInfo.info()
        self.workFile = self.asset.thisScene()


    def initPath(self) : 
        path = self.asset.getPath(self.asset.department(), self.asset.task())
        dataPath = '%s/data/%s.yml' % (path, self.asset.name())

        self.dataPath = '%s/%s' % (os.path.dirname(moduleDir), 'tmp/temp.yml')

        if os.path.exists(dataPath) : 
            self.dataPath = dataPath


    def setAssetUI(self) : 
        self.ui.scene_label.setText(os.path.basename(self.asset.thisScene()))
        self.ui.asset_label.setText(self.asset.name())
        self.ui.cmd_lineEdit.setText(self.cmdPath)
        self.setPresetComboBox()
        self.ui.output_lineEdit.setText(self.getDefaultOutput())
        self.setOutputLog('Start %s' % str(datetime.now()), True)
        self.setPublishTask()

    def listCommands(self) : 
        self.ui.cmd_listWidget.clear()
        listWidget = 'cmd_listWidget'
        cmds = self.getFunctions()

        for each in cmds : 
            funcName = each[0]
            color = [0, 0, 0]
            self.addListWidgetItem(listWidget, funcName, self.cmdIcon, color)


    def getFunctions(self) : 
        allFuncs = getmembers(rigCmd)
        cmds = [a for a in allFuncs if isfunction(a[1])]

        return cmds



    def listExeList(self) : 
        # read list 
        preset = str(self.ui.preset_comboBox.currentText())
        self.ui.exe_listWidget.clear()
        listWidget = 'exe_listWidget'

        if preset == 'Default' : 
            data = self.readDataPath()
            if data : 
                for each in data['commands'] : 
                    iconPath = self.rdyIcon
                    color = [0, 0, 0]

                    self.addListWidgetItem(listWidget, each, iconPath, color)

        else : 
            data = self.readPreset()
            if preset in data.keys() : 

                for each in data[preset] : 
                    iconPath = self.rdyIcon
                    color = [0, 0, 0]

                    self.addListWidgetItem(listWidget, each, iconPath, color)


    def readDataPath(self) : 
        data = None
        if os.path.exists(self.dataPath) : 
            data = fileUtils.ymlLoader(self.dataPath)

        else : 
            data = {'commands': []}

            if not os.path.exists(os.path.dirname(self.dataPath)) : 
                os.makedirs(os.path.dirname(self.dataPath))

            result = fileUtils.ymlDumper(self.dataPath, data)
            return self.readDataPath()

        return data

    def doAddList(self) : 
        sels = self.ui.cmd_listWidget.selectedItems()

        if sels : 
            items = [str(a.text()) for a in sels]
            # get data 
            dataUI = self.getAllExeList()

            # change preset back to default 
            self.ui.preset_comboBox.setCurrentIndex(0)

            # add to txt 
            data = {'commands': dataUI}
            fileUtils.ymlDumper(self.dataPath, data)

            data = self.readDataPath()

            for each in items : 
                data['commands'].append(each)

            fileUtils.ymlDumper(self.dataPath, data)

            self.listExeList()

    def doRemoveList(self) : 
        if self.ui.exe_listWidget.currentItem() : 
            row = self.ui.exe_listWidget.currentRow()
            data = self.readDataPath()

            if data : 
                del data['commands'][row]
                fileUtils.ymlDumper(self.dataPath, data)

            self.listExeList()


    def getAllExeList(self) : 
        count = self.ui.exe_listWidget.count()
        items = [str(self.ui.exe_listWidget.item(a).text()) for a in range(count)]
        
        return items


    def doPublish(self) : 
        cmds = self.getAllExeList()
        save = self.ui.save_checkBox.isChecked()
        output = str(self.ui.output_lineEdit.text())
        batch = self.ui.batch_checkBox.isChecked()

        if not batch : 

            # run cmd 
            for cmd in cmds : 
                print 'run %s' % cmd
                self.setOutputLog('run %s' % cmd)

                try : 
                    # eval(setting.cmdList[cmd])
                    cmd = 'rigCmd.%s()' % cmd
                    eval(cmd)
                    print '-> OK'
                    self.setOutputLog('-> OK')

                except Exception as e : 
                    print '-> error %s' % e
                    self.setOutputLog('-> error %s' % e)

            if save : 
                fileUtils.checkDir(output)
                mc.file(rename = output)
                mc.file(save = True, type = 'mayaAscii', f = True)
                self.setOutputLog('Saved %s' % output)

                self.outputFile = output

        else : 
            self.setOutputLog('Run batch')
            src = self.asset.thisScene()
            dst = output
            rigBatch.run(src, dst, str(cmds))
            self.setOutputLog('Run batch complete')

        self.savePresetToDefault()
        self.listExeList()

    def doSavePreset(self) : 
        cmds = self.getAllExeList()
        name = str(self.ui.preset_lineEdit.text())
        presetData = self.readPreset()

        if not name in presetData.keys() : 
            presetData.update({name: cmds})
            fileUtils.ymlDumper(self.presetPath, presetData)

            self.setOutputLog('Saved preset %s complete.' % name)

            self.setPresetComboBox()

        else : 
            self.setOutputLog('Name %s exists' % name)

    def clearList(self) : 
        data = {'commands': []}
        fileUtils.ymlDumper(self.dataPath, data)
        self.listExeList()


    def getDefaultOutput(self) : 
        currentFile = self.asset.thisScene()
        dirname = os.path.dirname(currentFile)
        filename = os.path.basename(currentFile)
        newFilename = '%s_runCmd.%s' % (filename.split('.')[0], filename.split('.')[-1])

        outputName = '%s/%s' % (dirname, newFilename)
        self.outputFile = outputName 

        return outputName


    def setOutputPath(self) : 
        item = str(self.ui.task_comboBox.currentText())
        filename = self.asset.getRefNaming(item)
        path = self.asset.getPath('ref')

        if item == 'devRig' : 
            path = self.asset.getPath('dev')

        filePath = '%s/%s' % (path, filename)

        if item == 'default' : 
            filePath = self.getDefaultOutput()


        self.ui.output_lineEdit.setText(filePath)


    def setOutputLog(self, text, underline = False) : 
        self.ui.log_textEdit.append(text)
        line = str()
        if underline : 
            for each in range(len(text)) : 
                line += '-'

            self.ui.log_textEdit.append(line)


    def setInfoLog(self, text, underline = False) : 
        self.ui.log_textEdit.clear()
        self.ui.log_textEdit.append(text)
        line = str()
        if underline : 
            for each in range(len(text)) : 
                line += '-'

            self.ui.log_textEdit.append(line)


    def readPreset(self) : 
        data = None 

        if not os.path.exists(self.presetPath) : 
            data = {'Default': [], 'Examples': ['clean']}

            fileUtils.checkDir(self.presetPath)
            fileUtils.ymlDumper(self.presetPath, data)

        else : 
            data = fileUtils.ymlLoader(self.presetPath)

        return data


    def setPresetComboBox(self) : 
        self.ui.preset_comboBox.clear()
        self.ui.preset_comboBox.addItems(sorted(self.readPreset().keys()))


    def savePresetToDefault(self) : 
        # get data 
        dataUI = self.getAllExeList()

        # change preset back to default 
        self.ui.preset_comboBox.setCurrentIndex(0)

        # add to txt 
        data = {'commands': dataUI}
        fileUtils.ymlDumper(self.dataPath, data)


    def doOpenWorkFile(self) : 
        mc.file(self.workFile, o = True, f = True)
        self.setOutputLog('Open file %s' % self.workFile)
        self.setOutputLog('Success', True)


    def doOpenOutputFile(self) : 
        if os.path.exists(self.outputFile) : 
            mc.file(self.outputFile, o = True, f = True)

            self.setOutputLog('Open output file %s' % self.outputFile)
            self.setOutputLog('Success', True)

        else : 
            self.setOutputLog('Path not exists')


    def showDocString(self) : 
        doc = str()
        sel = str(self.ui.cmd_listWidget.currentItem().text())
        doc += '--  %s  --\n' % sel
        cmd = 'rigCmd.%s.__doc__' % sel
        doc += eval(cmd)

        self.setInfoLog(doc)


    def setPublishTask(self) : 
        lists = ['default', 'anim', 'devRig', 'render', 'cache']
        self.ui.task_comboBox.clear()
        self.ui.task_comboBox.addItems(lists)


    def addListWidgetItem(self, listWidget, text, iconPath, color) : 
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(iconPath),QtGui.QIcon.Normal,QtGui.QIcon.Off)
        cmd = 'QtGui.QListWidgetItem(self.ui.%s)' % listWidget
        item = eval(cmd)
        item.setIcon(icon)
        item.setText(text)
        item.setBackground(QtGui.QColor(color[0], color[1], color[2]))
        size = 16

        cmd2 = 'self.ui.%s.setIconSize(QtCore.QSize(%s, %s))' % (listWidget, size, size)
        eval(cmd2)
        # QtGui.QApplication.processEvents()


    def messageBox(self, title, description) : 
        # result = QtGui.QMessageBox.question(self,title,description ,QtGui.QMessageBox.AcceptRole, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
        result = QtGui.QMessageBox.question(self,title,description ,QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)

        return result