from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtCore import QMimeData

class MikiEdit(QPlainTextEdit):

    def __init__(self, parent=None):
        super(MikiEdit, self).__init__(parent)

    def mimeFromText(self, text):
        mime = QMimeData()
        mime.setText(text)
        return mime

    def createMimeDataFromSelection(self):
        """ Reimplement this to prevent copied text taken as hasHtml() """
        plaintext = self.textCursor().selectedText()

        # From QTextCursor doc:
        # if the selection obtained from an editor spans a line break,
        # the text will contain a Unicode U+2029 paragraph separator character
        # instead of a newline \n character
        text = plaintext.replace('\u2029', '\n')
        return self.mimeFromText(text)
