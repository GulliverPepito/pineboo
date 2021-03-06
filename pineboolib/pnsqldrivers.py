# -*- coding: utf-8 -*-

import os
import sys
import logging
import importlib

from pineboolib.utils import filedir


logger = logging.getLogger(__name__)

"""
Esta clase gestiona los diferentes controladores de BD.
"""


class PNSqlDrivers(object):
    driverName = None
    driver_ = None
    only_pure_python_ = None

    """
    Constructor
    """

    def __init__(self, _DGI=None):
        self.only_pure_python_ = getattr(sys, 'frozen', False)

        self.driversdict = {}
        self.driversDefaultPort = {}
        self.desktopFile = {}

        dir_list = [file for file in os.listdir(filedir("plugins/sql")) if not file[0] == "_" and file.endswith(".py")]
        for item in dir_list:
            file_name = item[:item.find(".py")]
            mod_ = importlib.import_module("pineboolib.plugins.sql.%s" % file_name)
            driver_ = getattr(mod_, file_name.upper())()
            if driver_.pure_python() or driver_.safe_load():
                self.driversdict[file_name] = driver_.alias_
                self.driversDefaultPort[driver_.alias_] = driver_.defaultPort_
                self.desktopFile[driver_.alias_] = driver_.desktopFile()

        self.defaultDriverName = "FLsqlite"

    """
    Apunta hacia un controlador dado.
    @param driverName. Nombre del controlado que se desea usar.
    @return True o False.
    """

    def loadDriver(self, driverName):
        if driverName is None:
            logger.info("Seleccionado driver por defecto %s", self.defaultDriverName)
            driverName = self.defaultDriverName

        module_ = importlib.import_module(
            "pineboolib.plugins.sql.%s" % driverName.lower())
        self.driver_ = getattr(module_, driverName.upper())()

        if self.driver():
            # self.driverName = driverName
            logger.info("Driver %s v%s", self.driver().driverName(), self.driver().version())
            return True
        else:
            return False

    """
    Retorna el Alias de un controlador a partir de su Nombre
    @param name. Nombre del controlador.
    @return Alias o None.
    """

    def nameToAlias(self, name):
        name = name.lower()
        if name in self.driversdict.keys():
            return self.driversdict[name]
        else:
            return None

    """
    Retorna el Nombre de un controlador a partir de su nombre
    @param alias. Alias con el que se conoce al controlador
    @return Nombre o None.
    """

    def aliasToName(self, alias):
        if not alias:
            return self.defaultDriverName

        for key, value in self.driversdict.items():
            if value == alias:
                return key

        return None

    """
    Puerto por defecto que una un controlador.
    @param alias. Alias del controlador.
    @return Puerto por defecto.
    """

    def port(self, alias):
        for k, value in self.driversDefaultPort.items():
            if k == alias:
                return "%s" % value

    """
    Indica si la BD a la que se conecta el controlador es de tipo escriotrio
    @param alias. Alias del controlador.
    @return True o False.
    """

    def isDesktopFile(self, alias):
        for k, value in self.desktopFile.items():
            if k == alias:
                return value

    """
    Lista los alias de los controladores disponibles
    @return lista.
    """

    def aliasList(self):

        list = []
        for key, value in self.driversdict.items():
            list.append(value)

        return list

    """
    Enlace con el controlador usado
    @return Objecto controlador
    """

    def driver(self):
        return self.driver_

    """
    Informa del nombre del controlador
    @return Nombre del controlador
    """

    def driverName(self):
        return self.driver().name()

    def __getattr__(self, k):
        return getattr(self.driver_, k)
