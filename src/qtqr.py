#!/usr/bin/env python2
#-*- encoding: utf-8 -*-

"""
GUI front end for qrencode based on the work of David Green:
<david4dev@gmail.com> https://launchpad.net/qr-code-creator/
and inspired by
http://www.omgubuntu.co.uk/2011/03/how-to-create-qr-codes-in-ubuntu/
uses python-zbar for decoding from files and webcam
"""

import sys, os
from math import ceil
from PyQt5 import QtCore, QtGui, QtWidgets
from qrtools import QR
try:
    import pynotify
    if not pynotify.init("QtQR"):
        print("DEBUG: There was a problem initializing the pynotify module")
    NOTIFY = True
except:
    NOTIFY = False
    
__author__ = "Ramiro Algozino"
__email__ = "algozino@gmail.com"
__copyright__ = "copyright (C) 2011 Ramiro Algozino"
__credits__ = "David Green"
__license__ = "GPLv3"
__version__ = "1.1"

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        self.setWindowTitle("QtQR: QR Code Generator")
        icon = os.path.join(os.path.dirname(__file__), u'icon.png')
        if not QtCore.QFile(icon).exists():
            icon = u'/usr/share/pixmaps/qtqr.png'
        self.setWindowIcon(QtGui.QIcon(icon))
        self.w = QtWidgets.QWidget()
        self.setCentralWidget(self.w)
        self.setAcceptDrops(True)

        # Templates for creating QRCodes supported by qrtools
        self.templates = {
            "text": unicode("Text"),
            "url": unicode("URL"),
            "bookmark": unicode("Bookmark"),
            "emailmessage": unicode("E-Mail"),
            "telephone": unicode("Telephone Number"),
            "phonebook": unicode("Contact Information (PhoneBook)"),
            "sms": unicode("SMS"),
            "mms": unicode("MMS"),
            "geo": unicode("Geolocalization"),
            }
        # With this we make the dict bidirectional
        self.templates.update( dict((self.templates[k], k) for k in self.templates))

        # Tabs
        # We use this to put the tabs in a desired order.
        self.templateNames = (
            self.templates["text"],
            self.templates["url"],
            self.templates["bookmark"],
            self.templates["emailmessage"],
            self.templates["telephone"],
            self.templates["phonebook"],
            self.templates["sms"],
            self.templates["mms"],
            self.templates["geo"],
            )
        self.selector = QtWidgets.QComboBox()
        self.selector.addItems(self.templateNames)
        self.tabs = QtWidgets.QStackedWidget()
        self.textTab = QtWidgets.QWidget()
        self.urlTab = QtWidgets.QWidget()
        self.bookmarkTab = QtWidgets.QWidget()
        self.emailTab = QtWidgets.QWidget()
        self.telTab = QtWidgets.QWidget()
        self.phonebookTab = QtWidgets.QWidget()
        self.smsTab = QtWidgets.QWidget()
        self.mmsTab = QtWidgets.QWidget()
        self.geoTab = QtWidgets.QWidget()
        self.tabs.addWidget(self.textTab)
        self.tabs.addWidget(self.urlTab)
        self.tabs.addWidget(self.bookmarkTab)
        self.tabs.addWidget(self.emailTab)
        self.tabs.addWidget(self.telTab)
        self.tabs.addWidget(self.phonebookTab)
        self.tabs.addWidget(self.smsTab)
        self.tabs.addWidget(self.mmsTab)
        self.tabs.addWidget(self.geoTab)

        #Widgets for Text Tab
        self.l1 = QtWidgets.QLabel('Text to be encoded:')
        self.textEdit = QtWidgets.QPlainTextEdit()

        #Widgets for URL Tab
        self.urlLabel = QtWidgets.QLabel('URL to be encoded:')
        self.urlEdit = QtWidgets.QLineEdit(u'http://')

        #Widgets for BookMark Tab
        self.bookmarkTitleLabel = QtWidgets.QLabel("Title:")
        self.bookmarkTitleEdit = QtWidgets.QLineEdit()
        self.bookmarkUrlLabel = QtWidgets.QLabel("URL:")
        self.bookmarkUrlEdit = QtWidgets.QLineEdit()

        #Widgets for EMail Tab
        self.emailLabel = QtWidgets.QLabel('E-Mail address:')
        self.emailEdit = QtWidgets.QLineEdit("@.com")
        self.emailSubLabel = QtWidgets.QLabel('Subject:')
        self.emailSubjectEdit = QtWidgets.QLineEdit()
        self.emailBodyLabel = QtWidgets.QLabel('Message Body:')
        self.emailBodyEdit = QtWidgets.QPlainTextEdit()

        #Widgets for Telephone Tab
        self.telephoneLabel = QtWidgets.QLabel('Telephone Number:')
        self.telephoneEdit = QtWidgets.QLineEdit()

        #Widgets for Contact Information Tab
        self.phonebookNameLabel = QtWidgets.QLabel("Name:")
        self.phonebookNameEdit = QtWidgets.QLineEdit()
        self.phonebookTelLabel = QtWidgets.QLabel("Telephone:")
        self.phonebookTelEdit = QtWidgets.QLineEdit()
        self.phonebookEMailLabel = QtWidgets.QLabel("E-Mail:")
        self.phonebookEMailEdit = QtWidgets.QLineEdit()
        self.phonebookNoteLabel = QtWidgets.QLabel("Note:")
        self.phonebookNoteEdit = QtWidgets.QLineEdit()
        self.phonebookBirthdayLabel = QtWidgets.QLabel("Birthday:")
        self.phonebookBirthdayEdit = QtWidgets.QDateEdit()
        self.phonebookBirthdayEdit.setCalendarPopup(True)
        self.phonebookAddressLabel = QtWidgets.QLabel("Address:")
        self.phonebookAddressEdit =  QtWidgets.QLineEdit()
        self.phonebookAddressEdit.setToolTip("Insert separated by commas the PO Box, room number, house number, city, prefecture, zip code and country in order")
        self.phonebookUrlLabel = QtWidgets.QLabel("URL:")
        self.phonebookUrlEdit =  QtWidgets.QLineEdit()

        #Widgets for SMS Tab
        self.smsNumberLabel = QtWidgets.QLabel('Telephone Number:')
        self.smsNumberEdit = QtWidgets.QLineEdit()
        self.smsBodyLabel = QtWidgets.QLabel('Message:')
        self.smsBodyEdit = QtWidgets.QPlainTextEdit()
        self.smsCharCount = QtWidgets.QLabel("characters count: 0")

        #Widgets for MMS Tab
        self.mmsNumberLabel = QtWidgets.QLabel('Telephone Number:')
        self.mmsNumberEdit = QtWidgets.QLineEdit()
        self.mmsBodyLabel = QtWidgets.QLabel('Content:')
        self.mmsBodyEdit = QtWidgets.QPlainTextEdit()

        #Widgets for GEO Tab
        self.geoLatLabel = QtWidgets.QLabel("Latitude:")
        self.geoLatEdit = QtWidgets.QLineEdit()
        self.geoLongLabel = QtWidgets.QLabel("Longitude:")
        self.geoLongEdit = QtWidgets.QLineEdit()

        #Widgets for QREncode Parameters Configuration
        self.optionsGroup = QtWidgets.QGroupBox('Parameters:')

        self.l2 = QtWidgets.QLabel('&Pixel Size:')
        self.pixelSize = QtWidgets.QSpinBox()

        self.l3 = QtWidgets.QLabel('&Error Correction:')
        self.ecLevel = QtWidgets.QComboBox()
        self.ecLevel.addItems(
                (
                'Lowest',
                'Medium', 
                'QuiteGood',
                'Highest'
                )
            )

        self.l4 = QtWidgets.QLabel('&Margin Size:')
        self.marginSize = QtWidgets.QSpinBox()

        #QLabel for displaying the Generated QRCode
        self.qrcode = QtWidgets.QLabel('Start typing to create QR Code\n or  drop here image files for decoding.')
        self.qrcode.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.qrcode)

        #Save and Decode Buttons
        self.saveButton = QtWidgets.QPushButton(QtGui.QIcon.fromTheme(u'document-save'), '&Save QRCode')
        self.decodeButton = QtWidgets.QPushButton(QtGui.QIcon.fromTheme(u'preview-file'), '&Decode')

        self.decodeMenu = QtWidgets.QMenu()
        self.decodeFileAction = self.decodeMenu.addAction(QtGui.QIcon.fromTheme(u'document-open'), 'Decode from &File')
        self.decodeWebcamAction = self.decodeMenu.addAction(QtGui.QIcon.fromTheme(u'image-png'), 'Decode from &Webcam')
        self.decodeButton.setMenu(self.decodeMenu)

        self.exitAction = QtWidgets.QAction(QtGui.QIcon.fromTheme(u'application-exit'), 'E&xit', self)
        self.addAction(self.exitAction)
        self.aboutAction = QtWidgets.QAction(QtGui.QIcon.fromTheme(u"help-about"), "&About", self)
        self.addAction(self.aboutAction)

        # UI Tunning
        self.saveButton.setEnabled(False)
        self.pixelSize.setValue(3)
        self.pixelSize.setMinimum(1)
        self.marginSize.setValue(4)
        self.l1.setBuddy(self.textEdit)
        self.l2.setBuddy(self.pixelSize)
        self.l3.setBuddy(self.ecLevel)
        self.l4.setBuddy(self.marginSize)
        self.ecLevel.setToolTip('Error Correction Level')
        self.l3.setToolTip('Error Correction Level')
        self.decodeFileAction.setShortcut(u"Ctrl+O")
        self.decodeWebcamAction.setShortcut(u"Ctrl+W")
        self.saveButton.setShortcut(u"Ctrl+S")
        self.exitAction.setShortcut(u"Ctrl+Q")
        self.aboutAction.setShortcut(u"F1")

        self.buttons = QtWidgets.QHBoxLayout()
        self.buttons.addWidget(self.saveButton)
        self.buttons.addWidget(self.decodeButton)

        #Text Tab
        self.codeControls = QtWidgets.QVBoxLayout()
        self.codeControls.addWidget(self.l1)
        self.codeControls.addWidget(self.textEdit, 1)
        self.textTab.setLayout(self.codeControls)

        #URL Tab
        self.urlTabLayout = QtWidgets.QVBoxLayout()
        self.urlTabLayout.addWidget(self.urlLabel)
        self.urlTabLayout.addWidget(self.urlEdit)
        self.urlTabLayout.addStretch()
        self.urlTab.setLayout(self.urlTabLayout)

        #Bookmark Tab
        self.bookmarkTabLayout = QtWidgets.QVBoxLayout()
        self.bookmarkTabLayout.addWidget(self.bookmarkTitleLabel)
        self.bookmarkTabLayout.addWidget(self.bookmarkTitleEdit)
        self.bookmarkTabLayout.addWidget(self.bookmarkUrlLabel)
        self.bookmarkTabLayout.addWidget(self.bookmarkUrlEdit)
        self.bookmarkTabLayout.addStretch()
        self.bookmarkTab.setLayout(self.bookmarkTabLayout)

        #Email Tab
        self.emailTabLayout = QtWidgets.QVBoxLayout()
        self.emailTabLayout.addWidget(self.emailLabel)
        self.emailTabLayout.addWidget(self.emailEdit)
        self.emailTabLayout.addWidget(self.emailSubLabel)
        self.emailTabLayout.addWidget(self.emailSubjectEdit)
        self.emailTabLayout.addWidget(self.emailBodyLabel)
        self.emailTabLayout.addWidget(self.emailBodyEdit, 1)
        self.emailTabLayout.addStretch()
        self.emailTab.setLayout(self.emailTabLayout)

        #Telephone Tab
        self.telTabLayout = QtWidgets.QVBoxLayout()
        self.telTabLayout.addWidget(self.telephoneLabel)
        self.telTabLayout.addWidget(self.telephoneEdit)
        self.telTabLayout.addStretch()
        self.telTab.setLayout(self.telTabLayout)

        #Contact Tab
        self.phonebookTabLayout = QtWidgets.QVBoxLayout()
        self.phonebookTabLayout.addWidget(self.phonebookNameLabel)
        self.phonebookTabLayout.addWidget(self.phonebookNameEdit)
        self.phonebookTabLayout.addWidget(self.phonebookTelLabel)
        self.phonebookTabLayout.addWidget(self.phonebookTelEdit)
        self.phonebookTabLayout.addWidget(self.phonebookEMailLabel)
        self.phonebookTabLayout.addWidget(self.phonebookEMailEdit)
        self.phonebookTabLayout.addWidget(self.phonebookNoteLabel)
        self.phonebookTabLayout.addWidget(self.phonebookNoteEdit)
        self.phonebookTabLayout.addWidget(self.phonebookBirthdayLabel)
        self.phonebookTabLayout.addWidget(self.phonebookBirthdayEdit)
        self.phonebookTabLayout.addWidget(self.phonebookAddressLabel)
        self.phonebookTabLayout.addWidget(self.phonebookAddressEdit)
        self.phonebookTabLayout.addWidget(self.phonebookUrlLabel)
        self.phonebookTabLayout.addWidget(self.phonebookUrlEdit)
        self.phonebookTabLayout.addStretch()
        self.phonebookTab.setLayout(self.phonebookTabLayout)

        #SMS Tab
        self.smsTabLayout = QtWidgets.QVBoxLayout()
        self.smsTabLayout.addWidget(self.smsNumberLabel)
        self.smsTabLayout.addWidget(self.smsNumberEdit)
        self.smsTabLayout.addWidget(self.smsBodyLabel)
        self.smsTabLayout.addWidget(self.smsBodyEdit, 1)
        self.smsTabLayout.addWidget(self.smsCharCount)
        self.smsTabLayout.addStretch()
        self.smsTab.setLayout(self.smsTabLayout)

        #MMS Tab
        self.mmsTabLayout = QtWidgets.QVBoxLayout()
        self.mmsTabLayout.addWidget(self.mmsNumberLabel)
        self.mmsTabLayout.addWidget(self.mmsNumberEdit)
        self.mmsTabLayout.addWidget(self.mmsBodyLabel)
        self.mmsTabLayout.addWidget(self.mmsBodyEdit, 1)
        self.mmsTabLayout.addStretch()
        self.mmsTab.setLayout(self.mmsTabLayout)

        #Geolocalization Tab
        self.geoTabLayout = QtWidgets.QVBoxLayout()
        self.geoTabLayout.addWidget(self.geoLatLabel)
        self.geoTabLayout.addWidget(self.geoLatEdit)
        self.geoTabLayout.addWidget(self.geoLongLabel)
        self.geoTabLayout.addWidget(self.geoLongEdit)
        self.geoTabLayout.addStretch()
        self.geoTab.setLayout(self.geoTabLayout)

        #Pixel Size Controls
        self.pixControls = QtWidgets.QVBoxLayout()
        self.pixControls.addWidget(self.l2)
        self.pixControls.addWidget(self.pixelSize)

        #Error Correction Level Controls
        self.levelControls = QtWidgets.QVBoxLayout()
        self.levelControls.addWidget(self.l3)
        self.levelControls.addWidget(self.ecLevel)

        #Margin Size Controls
        self.marginControls = QtWidgets.QVBoxLayout()
        self.marginControls.addWidget(self.l4)
        self.marginControls.addWidget(self.marginSize)

        #Controls Layout
        self.controls = QtWidgets.QHBoxLayout()
        self.controls.addLayout(self.pixControls)
        self.controls.addSpacing(10)
        self.controls.addLayout(self.levelControls)
        self.controls.addSpacing(10)
        self.controls.addLayout(self.marginControls)
        self.controls.addStretch()
        self.optionsGroup.setLayout(self.controls)

        #Main Window Layout
        self.selectorBox = QtWidgets.QGroupBox("Select data type:")

        self.vlayout1 = QtWidgets.QVBoxLayout()
        self.vlayout1.addWidget(self.selector)
        self.vlayout1.addWidget(self.tabs, 1)

        self.vlayout2 = QtWidgets.QVBoxLayout()
        self.vlayout2.addWidget(self.optionsGroup)
        self.vlayout2.addWidget(self.scroll, 1)
        self.vlayout2.addLayout(self.buttons)

        self.layout = QtWidgets.QHBoxLayout(self.w)
        self.selectorBox.setLayout(self.vlayout1)
        self.layout.addWidget(self.selectorBox)
        self.layout.addLayout(self.vlayout2, 1)

        #Signals
        self.selector.currentIndexChanged.connect(self.tabs.setCurrentIndex)
        self.tabs.currentChanged.connect(self.selector.setCurrentIndex)
        self.textEdit.textChanged.connect(self.qrencode)
        self.urlEdit.textChanged.connect(self.qrencode)
        self.bookmarkTitleEdit.textChanged.connect(self.qrencode)
        self.bookmarkUrlEdit.textChanged.connect(self.qrencode)
        self.emailEdit.textChanged.connect(self.qrencode)
        self.emailSubjectEdit.textChanged.connect(self.qrencode)
        self.emailBodyEdit.textChanged.connect(self.qrencode)
        self.phonebookNameEdit.textChanged.connect(self.qrencode)
        self.phonebookTelEdit.textChanged.connect(self.qrencode)
        self.phonebookEMailEdit.textChanged.connect(self.qrencode)
        self.phonebookNoteEdit.textChanged.connect(self.qrencode)
        self.phonebookAddressEdit.textChanged.connect(self.qrencode)
        self.phonebookBirthdayEdit.dateChanged.connect(self.qrencode)
        self.phonebookUrlEdit.textChanged.connect(self.qrencode)
        self.smsNumberEdit.textChanged.connect(self.qrencode)
        self.smsBodyEdit.textChanged.connect(self.qrencode)
        self.smsBodyEdit.textChanged.connect(
            lambda: self.smsCharCount.setText(
                unicode("characters count: %s - %d message(s)") % (
                len(self.smsBodyEdit.toPlainText()),
                ceil(len(self.smsBodyEdit.toPlainText()) / 160.0)
                )                    
                )
            )
        self.mmsNumberEdit.textChanged.connect(self.qrencode)
        self.mmsBodyEdit.textChanged.connect(self.qrencode)
        self.telephoneEdit.textChanged.connect(self.qrencode)
        self.geoLatEdit.textChanged.connect(self.qrencode)
        self.geoLongEdit.textChanged.connect(self.qrencode)
        self.pixelSize.valueChanged.connect(self.qrencode)
        self.ecLevel.currentIndexChanged.connect(self.qrencode)
        self.marginSize.valueChanged.connect(self.qrencode)
        self.saveButton.clicked.connect(self.saveCode)
        self.exitAction.triggered.connect(self.close)
        self.aboutAction.triggered.connect(self.about)
        self.decodeFileAction.triggered.connect(self.decodeFile)
        self.decodeWebcamAction.triggered.connect(self.decodeWebcam)

        self.qrcode.setAcceptDrops(True)
        self.qrcode.__class__.dragEnterEvent = self.dragEnterEvent
        self.qrcode.__class__.dropEvent = self.dropEvent

    def qrencode(self):
        #Functions to get the correct data
        data_fields = {
            "text": unicode(self.textEdit.toPlainText()),
            "url": unicode(self.urlEdit.text()),
            "bookmark": ( unicode(self.bookmarkTitleEdit.text()), unicode(self.bookmarkUrlEdit.text()) ),
            "email": unicode(self.emailEdit.text()),
            "emailmessage": ( unicode(self.emailEdit.text()), unicode(self.emailSubjectEdit.text()), unicode(self.emailBodyEdit.toPlainText()) ),
            "telephone": unicode(self.telephoneEdit.text()),
            "phonebook": (('N',unicode(self.phonebookNameEdit.text())),
                          ('TEL', unicode(self.phonebookTelEdit.text())),
                          ('EMAIL',unicode(self.phonebookEMailEdit.text())),
                          ('NOTE', unicode(self.phonebookNoteEdit.text())),
                          ('BDAY', unicode(self.phonebookBirthdayEdit.date().toString("yyyyMMdd"))), #YYYYMMDD
                          ('ADR', unicode(self.phonebookAddressEdit.text())),  #The fields divided by commas (,) denote PO box, room number, house number, city, prefecture, zip code and country, in order.
                          ('URL', unicode(self.phonebookUrlEdit.text())),
                          # ('NICKNAME', ''),
                        ),
            "sms": ( unicode(self.smsNumberEdit.text()), unicode(self.smsBodyEdit.toPlainText()) ),
            "mms": ( unicode(self.mmsNumberEdit.text()), unicode(self.mmsBodyEdit.toPlainText()) ),
            "geo": ( unicode(self.geoLatEdit.text()), unicode(self.geoLongEdit.text()) ),
        }

        data_type = unicode(self.templates[unicode(self.selector.currentText())])
        data = data_fields[data_type]
        
        level = (u'L',u'M',u'Q',u'H')

        if data:
            if data_type == 'emailmessage' and data[1] == '' and data[2] == '':
                data_type = 'email'
                data = data_fields[data_type]
            qr = QR(pixel_size = unicode(self.pixelSize.value()),
                    data = data,
                    level = unicode(level[self.ecLevel.currentIndex()]),
                    margin_size = unicode(self.marginSize.value()),
                    data_type = data_type,
                    )
            if qr.encode() == 0:
                self.qrcode.setPixmap(QtGui.QPixmap(qr.filename))
                self.saveButton.setEnabled(True)
            else:
                if NOTIFY:
                    n = pynotify.Notification(
                        "QtQR",
                        unicode("ERROR: Something went wrong while trying to generate the QR Code."),
                        "qtqr"
                        )
                    n.show()
                else:
                    print("Something went worng while trying to generate the QR Code")
        else:
            self.saveButton.setEnabled(False)

    def saveCode(self):
        fn = QtWidgets.QFileDialog.getSaveFileName(
            self,
            'Save QRCode', 
            filter='PNG Images (*.png);; All Files (*.*)'
            )
        fname = fn[0]
        if fname:
            if not fname.lower().endswith(u".png"):
                fname += u".png"
            
            self.qrcode.pixmap().save(fname)
            if NOTIFY:
                n = pynotify.Notification(
                    unicode("Save QR Code"),
                    unicode("QR Code succesfully saved to %s") % fname,
                    "qtqr"
                    )
                n.show()
            else:
               QtWidgets.QMessageBox.information(
                    self, 
                    unicode('Save QRCode'),
                    unicode('QRCode succesfully saved to <b>%s</b>.') % fname
                    )

    def decodeFile(self, fn=None):
        if not fn:
            fn = QtWidgets.QFileDialog.getOpenFileName(
                self,
                'Open QRCode',
                filter='Images (*.png *.jpg);; All Files (*.*)'
                )
            fname = fn[0]
        else:
            fname = fn 

        if os.path.isfile(fname):
            qr = QR(filename=fname)
            if qr.decode():
                self.showInfo(qr)
            else:
                QtWidgets.QMessageBox.information(
                    self,
                    'Decode File',
                    unicode('No QRCode could be found in file: <b>%s</b>.') % fname
                )
#        else:
#            QtWidgets.QMessageBox.information(
#                self,
#                u"Decode from file",
#                u"The file <b>%s</b> doesn't exist." %
#                os.path.abspath(fn),
#                QtWidgets.QMessageBox.Ok
#            )

    def showInfo(self, qr):
        dt = qr.data_type
        data = qr.data_decode[dt](qr.data)
        print(dt.encode(u"utf-8") + ':', data)
        if type(data) == tuple:
            for d in data:
                print(d.encode(u"utf-8"))
        elif type(data) == dict:
                # FIX-ME: Print the decoded symbols
                print("Dict")
                print(data.keys())
                print(data.values())
        else:
            print(data.encode(u"utf-8"))
        msg = {
            'text': lambda : unicode("QRCode contains the following text:\n\n%s") % (data),
            'url': lambda : unicode("QRCode contains the following url address:\n\n%s") % (data),
            'bookmark': lambda: unicode("QRCode contains a bookmark:\n\nTitle: %s\nURL: %s") % (data),
            'email': lambda : unicode("QRCode contains the following e-mail address:\n\n%s") % (data),
            'emailmessage': lambda : unicode("QRCode contains an e-mail message:\n\nTo: %s\nSubject: %s\nMessage: %s") % (data),
            'telephone': lambda : unicode("QRCode contains a telephone number: ") + (data),
            'phonebook': lambda : unicode("QRCode contains a phonebook entry:\n\nName: %s\nTel: %s\nE-Mail: %s\nNote: %s\nBirthday: %s\nAddress: %s\nURL: %s") %
                (data.get('N') or "", 
                 data.get('TEL') or "", 
                 data.get('EMAIL') or "", 
                 data.get('NOTE') or "",
                 QtCore.QDate.fromString(data.get('BDAY') or "",'yyyyMMdd').toString(), 
                 data.get('ADR') or "",
                 data.get('URL') or ""),
            'sms': lambda : unicode("QRCode contains the following SMS message:\n\nTo: %s\nMessage: %s") % (data),
            'mms': lambda : unicode("QRCode contains the following MMS message:\n\nTo: %s\nMessage: %s") % (data),
            'geo': lambda : unicode("QRCode contains the following coordinates:\n\nLatitude: %s\nLongitude:%s") % (data),
        }
        wanna = "\n\nDo you want to "
        action = {
            'text': u"",
            'url': wanna + "open it in a browser?",
            'bookmark': wanna + "open it in a browser?",
            'email': wanna + "send an e-mail to the address?",
            'emailmessage': wanna + "send the e-mail?",
            'telephone': u"",
            'phonebook': u"",
            'sms': u"",
            'mms': u"",
            'geo': wanna + "open it in Google Maps?",
        }
        if action[qr.data_type] != u"":
            msgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Question,
                'Decode QRCode',
                msg[qr.data_type]() + action[qr.data_type],
                QtWidgets.QMessageBox.No |
                QtWidgets.QMessageBox.Yes,
                self
                )
            msgBox.addButton("&Edit", QtWidgets.QMessageBox.ApplyRole)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Yes)
            rsp = msgBox.exec_()
        else:
            msgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Information,
                "Decode QRCode",
                msg[qr.data_type]() + action[qr.data_type],
                QtWidgets.QMessageBox.Ok,
                self
                )
            msgBox.addButton("&Edit", QtWidgets.QMessageBox.ApplyRole)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
            rsp = msgBox.exec_()

        if rsp == QtWidgets.QMessageBox.Yes:
            #Open Link
            if qr.data_type == 'email':
                link = 'mailto:'+ data
            elif qr.data_type == 'emailmessage':
                link = 'mailto:%s?subject=%s&body=%s' % (data)
            elif qr.data_type == 'geo':
                link = 'http://maps.google.com/maps?q=%s,%s' % data
            elif qr.data_type == 'bookmark':
                link = data[1]
            else:
                link = qr.data_decode[qr.data_type](qr.data)
            print(u"Opening " + link)
            QtWidgets.QDesktopServices.openUrl(QtCore.QUrl(link))
        elif rsp == 0:
            #Edit the code
            data = qr.data_decode[qr.data_type](qr.data)
            try:
                tabIndex = self.templateNames.index(self.templates[qr.data_type])
            except KeyError:
                if qr.data_type == 'email':
                    #We have to use the same tab index as EMail Message
                    tabIndex = self.templateNames.index(self.templates["emailmessage"])
            if qr.data_type == 'text':
                self.tabs.setCurrentIndex(tabIndex)
                self.textEdit.setPlainText(data)
            elif qr.data_type == 'url':
                self.tabs.setCurrentIndex(tabIndex)
                self.urlEdit.setText(data)
            elif qr.data_type == 'bookmark':
                self.bookmarkTitleEdit.setText(data[0])
                self.bookmarkUrlEdit.setText(data[1])
                self.tabs.setCurrentIndex(tabIndex)
            elif qr.data_type == 'emailmessage':
                self.emailEdit.setText(data[0])
                self.emailSubjectEdit.setText(data[1])
                self.emailBodyEdit.setPlainText(data[2])
                self.tabs.setCurrentIndex(tabIndex)
            elif qr.data_type == 'email':
                self.emailEdit.setText(data)
                self.emailSubjectEdit.setText("")
                self.emailBodyEdit.setPlainText("")
                self.tabs.setCurrentIndex(tabIndex)
            elif qr.data_type == 'telephone':
                self.telephoneEdit.setText(data)
                self.tabs.setCurrentIndex(tabIndex)
            elif qr.data_type == 'phonebook':
                self.phonebookNameEdit.setText(data.get("N") or "")
                self.phonebookTelEdit.setText(data.get("TEL") or "")
                self.phonebookEMailEdit.setText(data.get("EMAIL") or "")
                self.phonebookNoteEdit.setText(data.get("NOTE") or "")
                self.phonebookBirthdayEdit.setDate(QtCore.QDate.fromString(data.get("BDAY") or "", "yyyyMMdd"))
                self.phonebookAddressEdit.setText(data.get("ADR") or "")
                self.phonebookUrlEdit.setText(data.get("URL") or "")
                self.tabs.setCurrentIndex(tabIndex)
            elif qr.data_type == 'sms':
                self.smsNumberEdit.setText(data[0])
                self.smsBodyEdit.setPlainText(data[1])
                self.tabs.setCurrentIndex(tabIndex)
            elif qr.data_type == 'mms':
                self.mmsNumberEdit.setText(data[0])
                self.mmsBodyEdit.setPlainText(data[1])
                self.tabs.setCurrentIndex(tabIndex)
            elif qr.data_type == 'geo':
                self.geoLatEdit.setText(data[0])
                self.geoLongEdit.setText(data[1])
                self.tabs.setCurrentIndex(tabIndex)

    def decodeWebcam(self):
        vdDialog = VideoDevices()
        if vdDialog.exec_():
            device = vdDialog.videoDevices[vdDialog.videoDevice.currentIndex()][1]
            qr = QR()
            qr.decode_webcam(device=device)
            if qr.data_decode[qr.data_type](qr.data) == 'NULL':
                QtWidgets.QMessageBox.warning(
                    self,
                    "Decoding Failed",
                    "<p>Oops! no code was found.<br /> Maybe your webcam didn't focus.</p>",
                    QtWidgets.QMessageBox.Ok
                )
            else:
                self.showInfo(qr)

    def about(self):
        QtWidgets.QMessageBox.about(
            self,
            "About QtQR",
            unicode('<h1>QtQR %s</h1><p>A simple software for creating and decoding QR Codes that uses <a href="https://code.launchpad.net/~qr-tools-developers/qr-tools/python-qrtools-trunk">python-qrtools</a> as backend. Both are part of the <a href="https://launchpad.net/qr-tools">QR Tools</a> project.</p><p></p><p>This is Free Software: GNU-GPLv3</p><p></p><p>Please visit our website for more information and to check out the code:<br /><a href="https://launchpad.net/~qr-tools-developers/qtqr">https://launchpad.net/~qr-tools-developers/qtqr</p><p>copyright &copy; Ramiro Algozino &lt;<a href="mailto:algozino@gmail.com">algozino@gmail.com</a>&gt;</p>') % __version__,
        )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for fn in event.mimeData().urls():
            fn = fn.toLocalFile()
            self.decodeFile(unicode(fn))


class VideoDevices(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)

        self.videoDevices = []
        for vd in self.getVideoDevices():
            self.videoDevices.append(vd)

        self.setWindowTitle(self.tr('Decode from Webcam'))
        self.cameraIcon = QtGui.QIcon.fromTheme("camera")
        self.icon = QtWidgets.QLabel()
        self.icon.setPixmap(self.cameraIcon.pixmap(64,64).scaled(64,64))
        self.videoDevice = QtWidgets.QComboBox()
        self.videoDevice.addItems([vd[0] for vd in self.videoDevices])
        self.label = QtWidgets.QLabel(self.tr("You are about to decode from your webcam. Please put the code in front of your camera with a good light source and keep it steady.\nOnce you see a green rectangle you can close the window by pressing any key.\n\nPlease select the video device you want to use for decoding:"))
        self.label.setWordWrap(True)
        self.Buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.Buttons.accepted.connect(self.accept)
        self.Buttons.rejected.connect(self.reject)
        self.layout = QtWidgets.QVBoxLayout()
        self.hlayout = QtWidgets.QHBoxLayout()
        self.vlayout = QtWidgets.QVBoxLayout()
        self.hlayout.addWidget(self.icon, 0, QtCore.Qt.AlignTop)
        self.vlayout.addWidget(self.label)
        self.vlayout.addWidget(self.videoDevice)
        self.hlayout.addLayout(self.vlayout)
        self.layout.addLayout(self.hlayout)
        self.layout.addStretch()
        self.layout.addWidget(self.Buttons)
        
        self.setLayout(self.layout)
        

    def getVideoDevices(self):
        for dev in os.listdir("/dev/v4l/by-id"):
            try:
                yield([
                    " ".join(dev.split("-")[1].split("_")), 
                    os.path.join("/dev/v4l/by-id", dev)
                ])
            except:
                yield([
                    dev, 
                    os.path.join("/dev/v4l/by-id", dev)
                ])


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # This is to make Qt use locale configuration; i.e. Standard Buttons
    # in your system's language. 
    locale = unicode(QtCore.QLocale.system().name())
    translator=QtCore.QTranslator()
    # translator.load(os.path.join(os.path.abspath(
        # os.path.dirname(__file__)),
        # "qtqr_" + locale))
    # We load from standard location the translations
    translator.load("qtqr_" + locale,
                    QtCore.QLibraryInfo.location(
                    QtCore.QLibraryInfo.TranslationsPath)
                    )
    app.installTranslator(translator)    
    qtTranslator=QtCore.QTranslator()
    qtTranslator.load("qt_" + locale,
                    QtCore.QLibraryInfo.location(
                    QtCore.QLibraryInfo.TranslationsPath)
                    )
    app.installTranslator(qtTranslator);   
    
    mw = MainWindow()
    mw.show()
    if len(app.arguments())>1:
        #Open the file and try to decode it
        for fn in app.argv()[1:]:
            # We should check if the file exists.
            mw.decodeFile(fn)
    sys.exit(app.exec_())
