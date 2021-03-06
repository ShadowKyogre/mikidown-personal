import datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ItemDialog(QDialog):
    def __init__(self, parent=None):
        super(ItemDialog, self).__init__(parent)
        self.editor = QLineEdit()
        editorLabel = QLabel("Page Name:")
        editorLabel.setBuddy(self.editor)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                          QDialogButtonBox.Cancel)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        layout = QGridLayout()
        layout.addWidget(editorLabel, 0, 0)
        layout.addWidget(self.editor, 0, 1)
        layout.addWidget(self.buttonBox, 1, 1)
        self.setLayout(layout)
        self.connect(self.editor, SIGNAL("textEdited(QString)"),
                     self.updateUi)
        self.connect(self.buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(self.buttonBox, SIGNAL("rejected()"), self.reject)

    def setPath(self, path):
        self.path = path
    
    def setText(self, text):
        self.editor.setText(text)
        self.editor.selectAll()

    def updateUi(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
                self.editor.text()!="")
    
    def accept(self):
        if self.path == '':
            notePath = self.editor.text()
        else:
            notePath = self.path + '/' + self.editor.text()

        if QFile.exists(notePath+'.md'):
            QMessageBox.warning(self, 'Error',
                    'Page already exists: %s' % notePath)
        else:
            QDialog.accept(self)

class MikiTree(QTreeWidget):

    def __init__(self, notebookPath, parent=None):
        super(MikiTree, self).__init__(parent)
        self.notebookPath = notebookPath
        self.header().close()
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        #self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        #self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.nvwCallback = lambda item=self.currentItem(): None
        self.customContextMenuRequested.connect(self.treeMenu)
        

    def itemToPagePath(self, item):
        path = ''
        if not hasattr(item, 'text'):
            return path
        path = item.text(0)
        parent = item.parent()
        while parent is not None:
            path = parent.text(0) + '/' + path
            parent = parent.parent()
        return path

    def pagePathToItem(self, name):
        if name[0] == '/': 
            name = name[1:len(name)]
        if name[-1] == '/':
            name = name[0:-1]
        splitPath = name.split('/')
        depth = len(splitPath)
        #print(depth)
        itemList = self.findItems(splitPath[depth-1], Qt.MatchExactly|Qt.MatchRecursive)
        if len(itemList) == 1:
            #print(itemList[0].text(0))
            return itemList[0]
        for item in itemList:
            path = self.itemToPagePath(item)
            if name == path:
                return item
            '''
            parent = item.parent()
            for i in range(depth):
                print(i)
                if parent == None:
                    if i == depth-1:
                        return item
                    else:
                        continue
                if depth-i-2 < 0:
                    break
                if parent.text(0) == splitPath[depth-i-2]:
                    if depth-i-2 == 0:
                        return item
                    else:
                        parent = parent.parent()
            '''
    
    def currentItemName(self):
        item = self.currentItem()
        return self.itemToPagePath(item)

    def getPath(self, item):
        path = ''
        if not hasattr(item, 'text'):
            return path
        item = item.parent()
        while item is not None:
            path = item.text(0) + '/' + path
            item = item.parent()
        return path
    
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            return
        else:
            QTreeWidget.mousePressEvent(self, event)

    def treeMenu(self, qpoint):
        menu = QMenu()
        item = self.itemAt(qpoint)
        menu.addAction("New Page...", lambda: self.newPageCore(self))
        menu.addAction("New Subpage...", lambda: self.newPageCore(item))
        menu.addAction("View separately", lambda: self.nvwCallback(item))
        menu.addSeparator()
        menu.addAction("Collapse This Note Tree", 
            lambda: self.recurseCollapse(item))
        menu.addAction("Uncollapse This Note Tree", 
            lambda:  self.recurseExpand(item))
        menu.addAction("Collapse All", self.collapseAll)
        menu.addAction("Uncollapse All", self.expandAll)
        menu.addSeparator()
        menu.addAction('Rename Page...', lambda: self.renamePage(item))
        self.delCallback = lambda: self.delPage(item)
        menu.addAction("Delete Page", self.delCallback)
        menu.exec_(self.mapToGlobal(qpoint))
#"""
    def newPage(self):
        if self.currentItem() is None:
            self.newPageCore(self)
        else:
            parent = self.currentItem().parent()
            if parent is not None:
                self.newPageCore(parent)
            else:
                self.newPageCore(self)

    def newSubpage(self):
        item = self.currentItem()
        self.newPageCore(item)
#"""            
    def newPageCore(self, item):
        pagePath = self.itemToPagePath(item)
        dialog = ItemDialog(self)
        dialog.setPath(pagePath)
        if dialog.exec_():
            newPageName = dialog.editor.text()
            if hasattr(item, 'text'):
                pagePath = pagePath + '/'
            if not QDir(pagePath).exists():
                QDir(self.notebookPath).mkdir(pagePath)
            fileName = pagePath + newPageName + '.md'
            fh = QFile(fileName)
            fh.open(QIODevice.WriteOnly)
            savestream = QTextStream(fh)
            savestream << '# ' + newPageName + '\n'
            savestream << 'Created ' + str(datetime.date.today()) + '\n\n'
            fh.close()
            QTreeWidgetItem(item, [newPageName])
            self.sortItems(0, Qt.AscendingOrder)
            if pagePath != '':
                self.expandItem(item)

    def dropEvent(self, event):
        sourceItem = self.currentItem()
        sourcePath = self.itemToPagePath(sourceItem)
        targetItem = self.itemAt(event.pos())
        targetPath = self.itemToPagePath(targetItem)
        if targetPath != '':
            targetPath = targetPath + '/'
        oldName = sourcePath + '.md'
        newName = targetPath + sourceItem.text(0) + '.md'
        oldDir = sourcePath
        newDir = targetPath  + sourceItem.text(0)
        print(newName)
        #if QDir(newName).exists():
        if QFile.exists(newName):
            QMessageBox.warning(self, 'Error',
                    'Page already exists: %s' % newName)
            return

        #if not QDir(newName).exists():
        QDir(self.notebookPath).mkpath(targetPath)
        QDir(self.notebookPath).rename(oldName, newName)
        if sourceItem.childCount() != 0: 
            QDir(self.notebookPath).rename(oldDir, newDir)
        if sourceItem.parent() is not None:
            parentItem = sourceItem.parent()
            parentPath = self.itemToPagePath(parentItem)
            if parentItem.childCount() == 1:
                QDir(self.notebookPath).rmdir(parentPath)
        QTreeWidget.dropEvent(self, event)
        self.sortItems(0, Qt.AscendingOrder)

    def renamePageWrapper(self):
        item = self.currentItem()
        self.renamePage(item)

    def renamePage(self, item):
        parent = item.parent()
        parentPath = self.itemToPagePath(parent)
        dialog = ItemDialog(self)
        dialog.setPath(parentPath)
        dialog.setText(item.text(0))
        if dialog.exec_():
            newPageName = dialog.editor.text()
            #pagePath = self.getPath(item)
            #if hasattr(item, 'text'):       # if item is not QTreeWidget
            if parentPath != '':
                parentPath = parentPath + '/'
            oldName = parentPath + item.text(0) + '.md'
            newName = parentPath + newPageName + '.md'
            QDir(self.notebookPath).rename(oldName, newName)
            if item.childCount() != 0:
                oldDir = parentPath + item.text(0)
                newDir = parentPath + newPageName
                QDir(self.notebookPath).rename(oldDir, newDir)
            item.setText(0, newPageName)
            self.sortItems(0, Qt.AscendingOrder)

    def exists(self, item):
        notePath = self.itemToPagePath(item) + '.md'
        return QFile.exists(notePath)

    def delPageWrapper(self):
        item = self.currentItem()
        self.delPage(item)

    def delPage(self, item):
        index = item.childCount()
        while index > 0:
            index = index -1
            self.dirname = item.child(index).text(0)
            self.delPage(item.child(index))

        pagePath = self.itemToPagePath(item)
        QDir(self.notebookPath).remove(pagePath + '.md')
        parent = item.parent()
        parentPath = self.itemToPagePath(parent)
        if parent is not None:
            index = parent.indexOfChild(item)
            parent.takeChild(index)
            if parent.childCount() == 0:    #if no child, dir not needed
                QDir(self.notebookPath).rmdir(parentPath)
        else:
            index = self.indexOfTopLevelItem(item)
            self.takeTopLevelItem(index)    
        QDir(self.notebookPath).rmdir(pagePath)
    
    def recurseCollapse(self, item):
      for i in range(item.childCount()):
        a_item = item.child(i)
        print(a_item)
        self.recurseCollapse(a_item)
      self.collapseItem(item)
    
    def recurseExpand(self, item):
      self.expandItem(item)
      for i in range(item.childCount()):
        a_item = item.child(i)
        print(a_item)
        self.recurseExpand(a_item)

    #def mouseMoveEvent(self, event):
    #   self.startDrag()
    #   QWidget.mouseMoveEvent(self, event)

    #def mousePressEvent(self, event):
        #self.clearSelection()
    #   QWidget.mousePressEvent(self, event)


