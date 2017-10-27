from enum import Enum

from PyQt4.QtCore import Qt

from pineboolib import decorators
from pineboolib.flcontrols import ProjectClass

from pineboolib.fllegacy.FLPicture import FLPicture

from pineboolib.kugar.mpagecollection import MPageCollection


class FLReportPages(ProjectClass):

    class PageOrientation(Enum):
        Portrait = 0
        Landscape = 1

    class PageSize(Enum):
        A4 = 0
        B5 = 1
        Letter = 2
        Legal = 3
        Executive = 4
        A0 = 5
        A1 = 6
        A2 = 7
        A3 = 8
        A5 = 9
        A6 = 10
        A7 = 11
        A8 = 12
        A9 = 13
        B0 = 14
        B1 = 15
        B10 = 16
        B2 = 17
        B3 = 18
        B4 = 19
        B6 = 20
        B7 = 21
        B8 = 22
        B9 = 23
        C5E = 24
        Comm10E = 25
        DLE = 26
        Folio = 27
        Ledger = 28
        Tabloid = 29
        Custom = 30
        NPageSize = Custom
        CustomOld = 31

    @decorators.BetaImplementation
    def __init__(self):
        super(FLReportPages, self).__init__()
        self.pages_ = MPageCollection(0)

    @decorators.BetaImplementation
    def pageCollection(self):
        return self.pages_

    @decorators.BetaImplementation
    def setPageCollection(self, pages):
        if self.pages_:
            self.pages_.deleteLater()
        if pages:
            self.insertChild(pages)
        self.pages_ = pages

    @decorators.BetaImplementation
    def getCurrentPage(self):
        if self.pages_:
            return FLPicture(self.pages_.getCurrentPage(), self)
        return False

    @decorators.BetaImplementation
    def getFirstPage(self):
        if self.pages_:
            return FLPicture(self.pages_.getFirstPage(), self)
        return False

    @decorators.BetaImplementation
    def getPreviousPage(self):
        if self.pages_:
            return FLPicture(self.pages_.getPreviousPage(), self)
        return False

    @decorators.BetaImplementation
    def getNextPage(self):
        if self.pages_:
            return FLPicture(self.pages_.getNextPage(), self)
        return False

    @decorators.BetaImplementation
    def getLastPage(self):
        if self.pages_:
            return FLPicture(self.pages_.getLastPage(), self)
        return False

    @decorators.BetaImplementation
    def getPageAt(self, i):
        if self.pages_:
            return FLPicture(self.pages_.getPageAt(i), self)
        return False

    @decorators.BetaImplementation
    def clearPages(self):
        if self.pages_:
            self.pages_.clear()

    @decorators.BetaImplementation
    def appendPage(self):
        if self.pages_:
            self.pages_.appendPage()

    @decorators.BetaImplementation
    def getCurrentIndex(self):
        if self.pages_:
            return self.pages_.getCurrentIndex()
        return -1

    @decorators.BetaImplementation
    def setCurrentPage(self, idx):
        if self.pages_:
            self.pages_.setCurrentPage(idx)

    @decorators.BetaImplementation
    def setPageSize(self, s):
        if self.pages_:
            self.pages_.setPageSize(s)

    @decorators.BetaImplementation
    def setPageOrientation(self, o):
        if self.pages_:
            self.pages_.setPageOrientation(o)

    @decorators.BetaImplementation
    def setPageDimensions(self, dim):
        if self.pages_:
            self.pages_.setPageDimensions(dim)

    @decorators.BetaImplementation
    def pageSize(self):
        if self.pages_:
            return self.pages_.pageSize()
        return -1

    @decorators.BetaImplementation
    def pageOrientation(self):
        if self.pages_:
            return self.pages_.pageOrientation()
        return -1

    @decorators.BetaImplementation
    def pageDimensions(self):
        if self.pages_:
            return self.pages_.pageDimensions()
        return Qt.QSize()

    @decorators.BetaImplementation
    def pageCount(self):
        if self.pages_:
            return self.pages_.pageCount()
        return -1