# -*- coding: utf-8 -*-
from pineboolib.qsa import *
import ast


class AQGlobalFunctions(object):
    functions_ = Array()
    mappers_ = Array()
    count_ = 0

    @classmethod
    def set(self, functionName=None, globalFunction=None):
        functions_[functionName] = globalFunction

    @classmethod
    def get(self, functionName=None):
        return functions_[functionName]

    @classmethod
    def exec_(self, functionName=None):
        fn = functions_[functionName]
        if fn != None:
            fn()

    @classmethod
    def mapConnect(self, obj=None, signal=None, functionName=None):
        c = self.count_ % 100
        sigMap = AQSignalMapper(obj)
        mappers_[c] = sigMap

        def _():
            mappers_[c] = None

        connect(sigMap, u"mapped(QString)", sys.AQGlobalFunctions, u"exec()")
        sigMap.setMapping(obj, functionName)
        connect(obj, signal, sigMap, u"map()")
        count_ += 1


class AQTimer(QtCore.QTimer):
    pass


class AbanQUpdater(object):
    w_ = None
    prBar_ = None
    urlOp_ = None
    state_ = None
    data_ = None

    def __init__(self):
        self.w_ = QDialog()
        self.w_.caption = u"Eneboo"
        self.w_.name = u"abanqUpdaterDialog"
        self.w_.modal = True
        lay = QVBoxLayout(self.w_)
        lay.margin = 0
        lay.spacing = 0
        self.prBar_ = QProgressBar(self.w_)
        self.prBar_.setCenterIndicator(True)
        self.prBar_.setTotalSteps(100)
        lay.addWidget(self.prBar_)
        self.data_ = u""
        self.urlOp_ = QUrlOperator(sys.decryptFromBase64(
            u"lKvF+hkDxk2dS6hrf0jVURL4EceyJIFPeigGw6lZAU/3ovk/v0iZfhklru4Q6t6M"))
        connect(self.urlOp_, u"finished(QNetworkOperation*)", self, u"transferFinished()")
        connect(self.urlOp_, u"dataTransferProgress(int,int,QNetworkOperation*)", self, u"transferProgress()")
        connect(self.urlOp_, u"data(const QByteArray&,QNetworkOperation*)", self, u"transferData()")
        self.urlOp_.get(sys.decryptFromBase64(u"wYZ6GifNhk4W+qnjzToiKooKL24mrW5bt0+RS6hQzW0="))

    @classmethod
    def transferFinished(self, netOp=None):
        self.state_ = netOp.state()
        self.w_.close()
        if self.state_ == AQS.StFailed:
            self.errorMsgBox(netOp.protocolDetail())

    @classmethod
    def transferProgress(self, bytesDone=None, bytesTotal=None, netOp=None):
        if bytesTotal > 0:
            self.prBar_.setTotalSteps(bytesTotal)
        self.prBar_.setProgress(bytesDone)

    @classmethod
    def transferData(self, data=None, netOp=None):
        dat = QByteArray(data)
        self.data_ += dat.toVariant


class AbanQDbDumper(object):
    SEP_CSV = u'\u00b6'
    db_ = None
    showGui_ = None
    dirBase_ = None
    fileName_ = None
    w_ = None
    lblDirBase_ = None
    pbChangeDir_ = None
    tedLog_ = None
    pbInitDump_ = None
    state_ = Object()
    funLog_ = None
    proc_ = None

    def __init__(self, db=None, dirBase=None, showGui=None, funLog=None):
        self.db_ = ((aqApp.db() if (db == None) else db))
        self.showGui_ = (True if (showGui == None) else showGui)
        self.dirBase_ = (Dir.home if (dirBase == None) else dirBase)
        self.funLog_ = (self.addLog if (funLog == None) else funLog)
        self.fileName_ = self.genFileName()
        import sys
        self.encoding = sys.getfilesystemencoding()

    def init(self):
        if self.showGui_:
            self.buildGui()
            self.w_.exec_()

    def buildGui(self):
        self.w_ = QDialog()
        self.w_.caption = sys.translate(u"Copias de seguridad")
        self.w_.modal = True
        self.w_.resize(800, 600)
        #lay = QVBoxLayout(self.w_, 6, 6)
        lay = QVBoxLayout(self.w_)
        frm = QFrame(self.w_)
        frm.frameShape = AQS.Box
        frm.lineWidth = 1
        frm.frameShadow = AQS.Plain
        #layFrm = QVBoxLayout(frm, 6, 6)
        layFrm = QVBoxLayout(frm)
        lbl = QLabel(frm)
        lbl.text = sys.translate(u"Driver: %s") % (str(self.db_.driverNameToDriverAlias(self.db_.driverName())))
        lbl.alignment = AQS.AlignTop
        layFrm.addWidget(lbl)
        lbl = QLabel(frm)
        lbl.text = sys.translate(u"Base de datos: %s") % (str(self.db_.database()))
        lbl.alignment = AQS.AlignTop
        layFrm.addWidget(lbl)
        lbl = QLabel(frm)
        lbl.text = sys.translate(u"Host: %s") % (str(self.db_.host()))
        lbl.alignment = AQS.AlignTop
        layFrm.addWidget(lbl)
        lbl = QLabel(frm)
        lbl.text = sys.translate(u"Puerto: %s") % (str(self.db_.port()))
        lbl.alignment = AQS.AlignTop
        layFrm.addWidget(lbl)
        lbl = QLabel(frm)
        lbl.text = sys.translate(u"Usuario: %s") % (str(self.db_.user()))
        lbl.alignment = AQS.AlignTop
        layFrm.addWidget(lbl)
        layAux = QHBoxLayout(frm)
        self.lblDirBase_ = QLabel(frm)
        self.lblDirBase_.text = sys.translate(u"Directorio Destino: %s") % (str(self.dirBase_))
        self.lblDirBase_.alignment = AQS.AlignVCenter
        layAux.addWidget(self.lblDirBase_)
        self.pbChangeDir_ = QPushButton(sys.translate(u"Cambiar"), frm)
        self.pbChangeDir_.setSizePolicy(AQS.Maximum, AQS.Preferred)
        connect(self.pbChangeDir_, u"clicked()", self, u"changeDirBase()")
        layAux.addWidget(self.pbChangeDir_)
        lay.addWidget(frm)
        self.pbInitDump_ = QPushButton(sys.translate(u"INICIAR COPIA"), self.w_)
        connect(self.pbInitDump_, u"clicked()", self, u"initDump()")
        lay.addWidget(self.pbInitDump_)
        lbl = QLabel(self.w_)
        lbl.text = u"Log:"
        lay.addWidget(lbl)
        self.tedLog_ = QTextEdit(self.w_)
        self.tedLog_.textFormat = TextEdit.LogText
        self.tedLog_.alignment = AQS.AlignHCenter or AQS.AlignVCenter
        lay.addWidget(self.tedLog_)

    def initDump(self):
        gui = self.showGui_ and self.w_ != None
        if gui:
            self.w_.enabled = False
        self.dumpDatabase()
        if gui:
            self.w_.enabled = True
        if self.state_.ok:
            if gui:
                self.infoMsgBox(self.state_.msg)
            self.w_.close()
        else:
            if gui:
                sys.errorMsgBox(self.state_.msg)

    def genFileName(self):
        now = Date()
        timeStamp = parseString(now)
        regExp = ["-", ":"]
        #regExp.global_ = True
        for rE in regExp:
            timeStamp = timeStamp.replace(rE, u"")

        fileName = ustr(self.dirBase_, u"/dump_", self.db_.database(), u"_", timeStamp)
        fileName = Dir.cleanDirPath(fileName)
        fileName = Dir.convertSeparators(fileName)
        return fileName

    def changeDirBase(self, dir_=None):
        dirBasePath = dir_
        if not dirBasePath:
            dirBasePath = FileDialog.getExistingDirectory(self.dirBase_)
            if not dirBasePath:
                return
        self.dirBase_ = dirBasePath
        if self.showGui_ and self.lblDirBase_ != None:
            self.lblDirBase_.text = sys.translate(u"Directorio Destino: %s") % (str(self.dirBase_))
        self.fileName_ = self.genFileName()

    def addLog(self, msg=None):
        if self.showGui_ and self.tedLog_ != None:
            self.tedLog_.append(msg)
        else:
            debug(msg)

    def setState(self, ok=None, msg=None):
        self.state_.ok = ok
        self.state_.msg = msg

    def state(self):
        return self.state_

    def launchProc(self, command):
        self.proc_ = QProcess()
        self.proc_.setProgram(command[0])
        self.proc_.setArguments(command[1:])
        # FIXME: Mejorar lectura linea a linea
        self.proc_.readyReadStandardOutput.connect(self.readFromStdout)
        self.proc_.readyReadStandardError.connect(self.readFromStderr)
        self.proc_.start()

        while self.proc_.Running:
            sys.processEvents()

        return self.proc_.exitcode() == self.proc_.normalExit

    def readFromStdout(self):
        t = self.proc_.readLine().data().decode(self.encoding)
        if t not in (None, ""):
            self.funLog_(t)

    def readFromStderr(self):
        t = self.proc_.readLine().data().decode(self.encoding)
        if t not in (None, ""):
            self.funLog_(t)

    def dumpDatabase(self):
        driver = self.db_.driverName()
        typeBd = 0
        if driver.startswith(u"FLQPSQL"):
            typeBd = 1
        else:
            if driver.startswith(u"FLQMYSQL"):
                typeBd = 2

        if typeBd == 0:
            self.setState(False, sys.translate(u"Este tipo de base de datos no soporta el volcado a disco."))
            self.funLog_(self.state_.msg)
            self.dumpAllTablesToCsv()
            return False

        file = File(self.fileName_)
        try:
            if not os.path.exists(self.fileName_):
                dir_ = Dir(self.fileName_)

        except Exception as e:
            e = traceback.format_exc()
            self.setState(False, ustr(u"", e))
            self.funLog_(self.state_.msg)
            return False

        ok = True
        if typeBd == 1:
            ok = self.dumpPostgreSQL()

        if typeBd == 2:
            ok = self.dumpMySQL()

        if not ok:
            self.dumpAllTablesToCsv()
        if not ok:
            self.setState(False, sys.translate(u"No se ha podido realizar la copia de seguridad."))
            self.funLog_(self.state_.msg)
        else:
            self.setState(True, sys.translate(u"Copia de seguridad realizada con éxito en:\n%s") %
                          (str(self.fileName_)))
            self.funLog_(self.state_.msg)

        return ok

    def dumpPostgreSQL(self):
        pgDump = u"pg_dump"
        command = None
        fileName = ustr(self.fileName_, u".sql")
        db = self.db_
        if sys.osName() == u"WIN32":
            pgDump += u".exe"
            System.setenv(u"PGPASSWORD", db.password())
            command = [pgDump, u"-f", fileName, u"-h", db.host(), u"-p", db.port(), u"-U", db.user(), db.database()]
        else:
            System.setenv(u"PGPASSWORD", db.password())
            command = [pgDump, u"-v", u"-f", fileName, u"-h", db.host(), u"-p", db.port(), u"-U",
                       db.user(), db.database()]

        if not self.launchProc(command):
            self.setState(False, sys.translate(u"No se ha podido volcar la base de datos a disco.\n") +
                          sys.translate(u"Es posible que no tenga instalada la herramienta ") + pgDump)
            self.funLog_(self.state_["msg"])
            return False
        self.setState(True, u"")
        return True

    def dumpMySQL(self):
        myDump = u"mysqldump"
        command = None
        fileName = ustr(self.fileName_, u".sql")
        db = self.db_
        if sys.osName() == u"WIN32":
            myDump += u".exe"
            command = [myDump, u"-v", ustr(u"--result-file=", fileName), ustr(u"--host=", db.host()), ustr(u"--port=",
                                                                                                           db.port()), ustr(u"--password=", db.password()), ustr(u"--user=", db.user()), db.database()]
        else:
            command = [myDump, u"-v", ustr(u"--result-file=", fileName), ustr(u"--host=", db.host()), ustr(u"--port=",
                                                                                                           db.port()), ustr(u"--password=", db.password()), ustr(u"--user=", db.user()), db.database()]

        if not self.launchProc(command):
            self.setState(False, sys.translate(u"No se ha podido volcar la base de datos a disco.\n") +
                          sys.translate(u"Es posible que no tenga instalada la herramienta ") + myDump)
            self.funLog_(self.state_.msg)
            return False
        self.setState(True, u"")
        return True

    def dumpTableToCsv(self, table=None, dirBase=None):
        fileName = ustr(dirBase, table, u".csv")
        file = QFile(fileName)
        if not file.open(File.WriteOnly):
            return False
        ts = QTextStream(file.ioDevice())
        ts.setCodec(AQS.TextCodec_codecForName(u"utf8"))
        qry = AQSqlQuery()
        qry.setSelect(ustr(table, u".*"))
        qry.setFrom(table)
        if not qry.exec_():
            return False
        rec = u""
        fieldNames = qry.fieldList()
        i = 0
        while_pass = True
        while i < len(fieldNames):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            if i > 0:
                rec += self.SEP_CSV
            rec += fieldNames[i]
            i += 1
            while_pass = True
            try:
                i < len(fieldNames)
            except Exception:
                break

        ts.opIn(ustr(rec, u"\n"))
        AQUtil.createProgressDialog(sys.translate(u"Haciendo copia en CSV de ") + table, qry.size())
        p = 0
        while qry.next():
            rec = u""
            i = 0
            while_pass = True
            while i < len(fieldNames):
                if not while_pass:
                    i += 1
                    while_pass = True
                    continue
                while_pass = False
                if i > 0:
                    rec += self.SEP_CSV
                rec += parseString(qry.value(i))
                i += 1
                while_pass = True
                try:
                    i < len(fieldNames)
                except Exception:
                    break

            ts.opIn(ustr(rec, u"\n"))
            p += 1
            AQUtil.setProgress(p)

        file.close()
        AQUtil.destroyProgressDialog()
        return True

    def dumpAllTablesToCsv(self):
        fileName = self.fileName_
        db = self.db_
        tables = db.tables(AQSql.Tables)
        dir_ = Dir(fileName)
        dir_.mkdir()
        dirBase = Dir.convertSeparators(ustr(fileName, u"/"))
        i = 0
        while_pass = True
        for table_ in tables:
            self.dumpTableToCsv(table_, dirBase)
        return True


class FormInternalObj(FormDBWidget):
    def _class_init(self):
        self.form = self
        self.iface = self

    def init(self):
        if sys.isLoadedModule(u"flfactppal"):
            util = FLUtil()
            codEjercicio = flfactppal.iface.pub_ejercicioActual()
            nombreEjercicio = util.sqlSelect(u"ejercicios", u"nombre", ustr(u"codejercicio='", codEjercicio, u"'"))
            if AQUtil.sqlSelect(u"flsettings", u"valor", u"flkey='PosInfo'") == u"true":
                texto = ""
                if nombreEjercicio:
                    texto = ustr(u"[ ", nombreEjercicio, u" ]")
                texto = ustr(texto, u" [ ", aqApp.db().driverNameToDriverAlias(aqApp.db().driverName()),
                             u" ] * [ ", sys.nameBD(), u" ] * [ ", sys.nameUser(), u" ] ")
                aqApp.setCaptionMainWidget(texto)

            else:
                if nombreEjercicio:
                    aqApp.setCaptionMainWidget(nombreEjercicio)

            settings = AQSettings()
            oldApi = settings.readBoolEntry(u"application/oldApi")
            if not oldApi:
                valor = util.readSettingEntry(u"ebcomportamiento/ebCallFunction")
                if valor:
                    funcion = Function(valor)
                    try:
                        funcion()
                    except Exception as e:
                        e = traceback.format_exc()
                        debug(e)

    @classmethod
    def afterCommit_flfiles(self, curFiles=None):
        if curFiles.modeAccess() != curFiles.Browse:
            qry = FLSqlQuery()
            qry.setTablesList(u"flserial")
            qry.setSelect(u"sha")
            qry.setFrom(u"flfiles")
            qry.setForwardOnly(True)
            if qry.exec_():
                if qry.first():
                    util = FLUtil()
                    v = util.sha1(qry.value(0))
                    while qry.next():
                        v = util.sha1(v + qry.value(0))
                    curSerial = FLSqlCursor(u"flserial")
                    curSerial.select()
                    if not curSerial.first():
                        curSerial.setModeAccess(curSerial.Insert)
                    else:
                        curSerial.setModeAccess(curSerial.Edit)

                    curSerial.refreshBuffer()
                    curSerial.setValueBuffer(u"sha", v)
                    curSerial.commitBuffer()

            else:
                curSerial = FLSqlCursor(u"flserial")
                curSerial.select()
                if not curSerial.first():
                    curSerial.setModeAccess(curSerial.Insert)
                else:
                    curSerial.setModeAccess(curSerial.Edit)

                curSerial.refreshBuffer()
                curSerial.setValueBuffer(u"sha", curFiles.valueBuffer(u"sha"))
                curSerial.commitBuffer()

        return True

    @classmethod
    def statusDbLocksDialog(self, locks=None):
        util = FLUtil()
        diag = Dialog()
        txtEdit = TextEdit()
        diag.caption = util.translate(u"scripts", u"Bloqueos de la base de datos")
        diag.width = 500
        html = u"<html><table border=\"1\">"
        if locks != None and len(locks):
            i = 0
            j = 0
            item = u""
            fields = locks[0].split(u"@")
            closeInfo = False
            closeRecord = False
            headInfo = u"<table border=\"1\"><tr>"
            i = 0
            while_pass = True
            while i < len(fields):
                if not while_pass:
                    i += 1
                    while_pass = True
                    continue
                while_pass = False
                headInfo += ustr(u"<td><b>", fields[i], u"</b></td>")
                i += 1
                while_pass = True
                try:
                    i < len(fields)
                except Exception:
                    break

            headInfo += u"</tr>"
            headRecord = ustr(u"<table border=\"1\"><tr><td><b>", util.translate(
                u"scripts", u"Registro bloqueado"), u"</b></td></tr>")
            i = 1
            while_pass = True
            while i < len(locks):
                if not while_pass:
                    i += 1
                    while_pass = True
                    continue
                while_pass = False
                item = locks[i]
                if item[0:2] == u"##":
                    if closeInfo:
                        html += u"</table>"
                    if not closeRecord:
                        html += headRecord
                    html += ustr(u"<tr><td>", item[(len(item) - (len(item) - 2)):], u"</td></tr>")
                    closeRecord = True
                    closeInfo = False

                else:
                    if closeRecord:
                        html += u"</table>"
                    if not closeInfo:
                        html += headInfo
                    html += u"<tr>"
                    fields = item.split(u"@")
                    j = 0
                    while_pass = True
                    while j < len(fields):
                        if not while_pass:
                            j += 1
                            while_pass = True
                            continue
                        while_pass = False
                        html += ustr(u"<td>", fields[j], u"</td>")
                        j += 1
                        while_pass = True
                        try:
                            j < len(fields)
                        except Exception:
                            break

                    html += u"</tr>"
                    closeRecord = False
                    closeInfo = True

                i += 1
                while_pass = True
                try:
                    i < len(locks)
                except Exception:
                    break

        html += u"</table></table></html>"
        txtEdit.text = html
        diag.add(txtEdit)
        diag.exec_()

    @classmethod
    def terminateChecksLocks(self, sqlCursor=None):
        if sqlCursor != None:
            sqlCursor.checkRisksLocks(True)

    @classmethod
    def execQSA(self, fileQSA=None, args=None):
        file = File(fileQSA)
        try:
            file.open(File.ReadOnly)
        except Exception as e:
            e = traceback.format_exc()
            debug(e)
            return

        fn = Function(file.read())
        fn(args)

    @classmethod
    def mvProjectXml(self):
        docRet = QDomDocument()
        strXml = AQUtil.sqlSelect(u"flupdates", u"modulesdef", u"actual='true'")
        if not strXml:
            return docRet
        doc = QDomDocument()
        if not doc.setContent(strXml):
            return docRet
        strXml = u""
        nodes = doc.childNodes()
        i = 0
        while_pass = True
        while i < len(nodes):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            it = nodes.item(i)
            if it.isComment():
                data = it.toComment().data()
                if not data == '' and data.startswith(u"<mvproject "):
                    strXml = data
                    break

            i += 1
            while_pass = True
            try:
                i < len(nodes)
            except Exception:
                break

        if strXml == '':
            return docRet
        docRet.setContent(strXml)
        return docRet

    @classmethod
    def mvProjectModules(self):
        ret = Array()
        doc = mvProjectXml()
        mods = doc.elementsByTagName(u"module")
        i = 0
        while_pass = True
        while i < len(mods):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            it = mods.item(i).toElement()
            mod = {name: (it.attribute(u"name")), version: (it.attribute(u"version")), }
            if len(mod.name) == 0:
                continue
            ret[mod.name] = mod
            i += 1
            while_pass = True
            try:
                i < len(mods)
            except Exception:
                break

        return ret

    @classmethod
    def mvProjectExtensions(self):
        ret = Array()
        doc = mvProjectXml()
        exts = doc.elementsByTagName(u"extension")
        i = 0
        while_pass = True
        while i < len(exts):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            it = exts.item(i).toElement()
            ext = {name: (it.attribute(u"name")), version: (it.attribute(u"version")), }
            if len(ext.name) == 0:
                continue
            ret[ext.name] = ext
            i += 1
            while_pass = True
            try:
                i < len(exts)
            except Exception:
                break

        return ret

    @classmethod
    def calculateShaGlobal(self):
        v = u""
        qry = AQSqlQuery()
        qry.setSelect(u"sha")
        qry.setFrom(u"flfiles")
        if qry.exec_() and qry.first():
            v = AQUtil.sha1(parseString(qry.value(0)))
            while qry.next():
                v = AQUtil.sha1(v + parseString(qry.value(0)))
        return v

    @classmethod
    def registerUpdate(self, input_=None):
        if not input_:
            return
        unpacker = AQUnpacker(input_)
        errors = unpacker.errorMessages()
        if len(errors) != 0:
            msg = sys.translate(u"Hubo los siguientes errores al intentar cargar los módulos:")
            msg += u"\n"
            i = 0
            while_pass = True
            while i < len(errors):
                if not while_pass:
                    i += 1
                    while_pass = True
                    continue
                while_pass = False
                msg += ustr(errors[i], u"\n")
                i += 1
                while_pass = True
                try:
                    i < len(errors)
                except Exception:
                    break

            self.errorMsgBox(msg)
            return

        unpacker.jump()
        unpacker.jump()
        unpacker.jump()
        now = Date()
        file = File(input_)
        fileName = file.name
        modulesDef = sys.toUnicode(unpacker.getText(), u"utf8")
        filesDef = sys.toUnicode(unpacker.getText(), u"utf8")
        shaGlobal = calculateShaGlobal()
        AQSql.update(u"flupdates", Array([u"actual"]), Array([False]))
        AQSql.insert(u"flupdates", Array([u"fecha", u"hora", u"nombre", u"modulesdef", u"filesdef", u"shaglobal"]), Array(
            [now, parseString(now)[(len(parseString(now)) - (8)):], fileName, modulesDef, filesDef, shaGlobal]))

    @classmethod
    def warnLocalChanges(self, changes=None):
        if changes == None:
            changes = localChanges()
        if changes.size == 0:
            return True
        diag = QDialog()
        diag.caption = sys.translate(u"Detectados cambios locales")
        diag.modal = True
        txt = u""
        txt += sys.translate(u"¡¡ CUIDADO !! DETECTADOS CAMBIOS LOCALES\n\n")
        txt += sys.translate(u"Se han detectado cambios locales en los módulos desde\n")
        txt += sys.translate(u"la última actualización/instalación de un paquete de módulos.\n")
        txt += sys.translate(u"Si continua es posible que estos cambios sean sobreescritos por\n")
        txt += sys.translate(u"los cambios que incluye el paquete que quiere cargar.\n\n")
        txt += u"\n\n"
        txt += sys.translate(u"Registro de cambios")
        lay = QVBoxLayout(diag)
        lay.margin = 6
        lay.spacing = 6
        lbl = QLabel(diag)
        lbl.text = txt
        lbl.alignment = AQS.AlignTop or AQS.WordBreak
        lay.addWidget(lbl)
        ted = QTextEdit(diag)
        ted.textFormat = TextEdit.LogText
        ted.alignment = AQS.AlignHCenter or AQS.AlignVCenter
        ted.append(reportChanges(changes))
        lay.addWidget(ted)
        lbl2 = QLabel(diag)
        lbl2.text = sys.translate(u"¿Que desea hacer?")
        lbl2.alignment = AQS.AlignTop or AQS.WordBreak
        lay.addWidget(lbl2)
        lay2 = QHBoxLayout(lay)
        lay2.margin = 6
        lay2.spacing = 6
        pbCancel = QPushButton(diag)
        pbCancel.text = sys.translate(u"Cancelar")
        pbAccept = QPushButton(diag)
        pbAccept.text = sys.translate(u"continue")
        lay2.addWidget(pbCancel)
        lay2.addWidget(pbAccept)
        connect(pbAccept, u"clicked()", diag, u"accept()")
        connect(pbCancel, u"clicked()", diag, u"reject()")
        return (False if (diag.exec_() == 0) else True)

    @classmethod
    def reportChanges(self, changes=None):
        ret = u""
        # DEBUG:: FOR-IN: ['key', 'changes']
        for key in changes:
            if key == u"size":
                continue
            chg = changes[key].split(u'@')
            ret += ustr(u"Nombre: ", chg[0], u"\n")
            ret += ustr(u"Estado: ", chg[1], u"\n")
            ret += ustr(u"ShaOldTxt: ", chg[2], u"\n")
            ret += ustr(u"ShaNewTxt: ", chg[4], u"\n")
            ret += u"###########################################\n"

        return ret

    @classmethod
    def localChanges(self):
        ret = Array()
        ret[u"size"] = 0
        strXmlUpt = AQUtil.sqlSelect(u"flupdates", u"filesdef", u"actual='true'")
        if not strXmlUpt:
            return ret
        docUpt = QDomDocument()
        if not docUpt.setContent(strXmlUpt):
            self.errorMsgBox(sys.translate(u"Error XML al intentar cargar la definición de los ficheros."))
            return ret
        docBd = xmlFilesDefBd()
        ret = diffXmlFilesDef(docBd, docUpt)
        return ret

    @classmethod
    def diffXmlFilesDef(self, xmlOld=None, xmlNew=None):
        arrOld = filesDefToArray(xmlOld)
        arrNew = filesDefToArray(xmlNew)
        ret = Array()
        size = 0
        # DEBUG:: FOR-IN: ['key', 'arrOld']
        for key in arrOld:
            if not (key in arrNew):
                info = Array([key, u"del", arrOld[key].shatext, arrOld[key].shabinary, u"", u""])
                ret[key] = u'@'.join(info)
                size += 1
        # DEBUG:: FOR-IN: ['key', 'arrNew']

        for key in arrNew:
            if not (key in arrOld):
                info = Array([key, u"new", u"", u"", arrNew[key].shatext, arrNew[key].shabinary])
                ret[key] = u'@'.join(info)
                size += 1
            else:
                if arrNew[key].shatext != arrOld[key].shatext or arrNew[key].shabinary != arrOld[key].shabinary:
                    info = Array([key, u"mod", arrOld[key].shatext, arrOld[key].shabinary,
                                  arrNew[key].shatext, arrNew[key].shabinary])
                    ret[key] = u'@'.join(info)
                    size += 1

        ret[u"size"] = size
        return ret

    @classmethod
    def filesDefToArray(self, xml=None):
        root = xml.firstChild()
        files = root.childNodes()
        ret = Array()
        i = 0
        while_pass = True
        while i < len(files):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            it = files.item(i)
            fil = {id: (it.namedItem(u"name").toElement().text()), module: (it.namedItem(u"module").toElement().text()), text: (it.namedItem(u"text").toElement().text()), shatext: (
                it.namedItem(u"shatext").toElement().text()), binary: (it.namedItem(u"binary").toElement().text()), shabinary: (it.namedItem(u"shabinary").toElement().text()), }
            if len(fil.id) == 0:
                continue
            ret[fil.id] = fil
            i += 1
            while_pass = True
            try:
                i < len(files)
            except Exception:
                break

        return ret

    @classmethod
    def xmlFilesDefBd(self):
        doc = QDomDocument(u"files_def")
        root = doc.createElement(u"files")
        doc.appendChild(root)
        qry = AQSqlQuery()
        qry.setSelect(u"idmodulo,nombre,contenido")
        qry.setFrom(u"flfiles")
        if not qry.exec_():
            return doc
        shaSum = u""
        shaSumTxt = u""
        shaSumBin = u""
        while qry.next():
            idMod = parseString(qry.value(0))
            if idMod == u"sys":
                continue
            fName = parseString(qry.value(1))
            ba = QByteArray()
            ba.string = sys.fromUnicode(parseString(qry.value(2)), u"iso-8859-15")
            sha = ba.sha1()
            nf = doc.createElement(u"file")
            root.appendChild(nf)
            ne = doc.createElement(u"module")
            nf.appendChild(ne)
            nt = doc.createTextNode(idMod)
            ne.appendChild(nt)
            ne = doc.createElement(u"name")
            nf.appendChild(ne)
            nt = doc.createTextNode(fName)
            ne.appendChild(nt)
            if textPacking(fName):
                ne = doc.createElement(u"text")
                nf.appendChild(ne)
                nt = doc.createTextNode(fName)
                ne.appendChild(nt)
                ne = doc.createElement(u"shatext")
                nf.appendChild(ne)
                nt = doc.createTextNode(sha)
                ne.appendChild(nt)
                ba = QByteArray()
                ba.string = shaSum + sha
                shaSum = ba.sha1()
                ba = QByteArray()
                ba.string = shaSumTxt + sha
                shaSumTxt = ba.sha1()

            try:
                if binaryPacking(fName):
                    ne = doc.createElement(u"binary")
                    nf.appendChild(ne)
                    nt = doc.createTextNode(ustr(fName, u".qso"))
                    ne.appendChild(nt)
                    sha = AQS.sha1(qry.value(3))
                    ne = doc.createElement(u"shabinary")
                    nf.appendChild(ne)
                    nt = doc.createTextNode(sha)
                    ne.appendChild(nt)
                    ba = QByteArray()
                    ba.string = shaSum + sha
                    shaSum = ba.sha1()
                    ba = QByteArray()
                    ba.string = shaSumBin + sha
                    shaSumBin = ba.sha1()

            except Exception:
                e = traceback.format_exc()

        qry = AQSqlQuery()
        qry.setSelect(u"idmodulo,icono")
        qry.setFrom(u"flmodules")
        if qry.exec_():
            while qry.next():
                idMod = parseString(qry.value(0))
                if idMod == u"sys":
                    continue
                fName = ustr(idMod, u".xpm")
                ba = QByteArray()
                ba.string = parseString(qry.value(1))
                sha = ba.sha1()
                nf = doc.createElement(u"file")
                root.appendChild(nf)
                ne = doc.createElement(u"module")
                nf.appendChild(ne)
                nt = doc.createTextNode(idMod)
                ne.appendChild(nt)
                ne = doc.createElement(u"name")
                nf.appendChild(ne)
                nt = doc.createTextNode(fName)
                ne.appendChild(nt)
                if textPacking(fName):
                    ne = doc.createElement(u"text")
                    nf.appendChild(ne)
                    nt = doc.createTextNode(fName)
                    ne.appendChild(nt)
                    ne = doc.createElement(u"shatext")
                    nf.appendChild(ne)
                    nt = doc.createTextNode(sha)
                    ne.appendChild(nt)
                    ba = QByteArray()
                    ba.string = shaSum + sha
                    shaSum = ba.sha1()
                    ba = QByteArray()
                    ba.string = shaSumTxt + sha
                    shaSumTxt = ba.sha1()

        ns = doc.createElement(u"shasum")
        ns.appendChild(doc.createTextNode(shaSum))
        root.appendChild(ns)
        ns = doc.createElement(u"shasumtxt")
        ns.appendChild(doc.createTextNode(shaSumTxt))
        root.appendChild(ns)
        ns = doc.createElement(u"shasumbin")
        ns.appendChild(doc.createTextNode(shaSumBin))
        root.appendChild(ns)
        return doc

    @classmethod
    def textPacking(self, ext=None):
        return ext.endswith(u".ui") or ext.endswith(u".qry") or ext.endswith(u".kut") or ext.endswith(u".jrxml") or ext.endswith(u".ar") or ext.endswith(u".mtd") or ext.endswith(u".ts") or ext.endswith(u".qs") or ext.endswith(u".xml") or ext.endswith(u".xpm") or ext.endswith(u".svg")

    @classmethod
    def binaryPacking(self, ext=None):
        return ext.endswith(u".qs")

    @classmethod
    def loadModules(self, input_=None, warnBackup=None):
        if input_ == None:
            dir_ = Dir(ustr(sys.installPrefix(), u"/share/eneboo/packages"))
            dir_.setCurrent()
            input_ = FileDialog.getOpenFileName(u"Eneboo Packages (*.eneboopkg)\nAbanQ Packages (*.abanq)",
                                                AQUtil.translate(u"scripts", u"Seleccionar Fichero"))
        if warnBackup == None:
            warnBackup = True
        if input_:
            self.loadAbanQPackage(input_, warnBackup)

    @classmethod
    def loadAbanQPackage(self, input_=None, warnBackup=None):
        if warnBackup and interactiveGUI():
            txt = u""
            txt += sys.translate(u"Asegúrese de tener una copia de seguridad de todos los datos\n")
            txt += sys.translate(u"y de que  no hay ningun otro  usuario conectado a la base de\n")
            txt += sys.translate(u"datos mientras se realiza la carga.\n\n")
            txt += u"\n\n"
            txt += sys.translate(u"¿Desea continuar?")
            if MessageBox.Yes != MessageBox.warning(txt, MessageBox.No, MessageBox.Yes):
                return

        if input_:
            ok = True
            changes = localChanges()
            if changes.size != 0:
                if not warnLocalChanges(changes):
                    return
            if ok:
                unpacker = AQUnpacker(input_)
                errors = unpacker.errorMessages()
                if len(errors) != 0:
                    msg = sys.translate(u"Hubo los siguientes errores al intentar cargar los módulos:")
                    msg += u"\n"
                    i = 0
                    while_pass = True
                    while i < len(errors):
                        if not while_pass:
                            i += 1
                            while_pass = True
                            continue
                        while_pass = False
                        msg += ustr(errors[i], u"\n")
                        i += 1
                        while_pass = True
                        try:
                            i < len(errors)
                        except Exception:
                            break

                    self.errorMsgBox(msg)
                    ok = False

                unpacker.jump()
                unpacker.jump()
                unpacker.jump()
                if ok:
                    ok = loadModulesDef(unpacker)
                if ok:
                    ok = loadFilesDef(unpacker)

            if not ok:
                self.errorMsgBox(sys.translate(u"No se ha podido realizar la carga de los módulos."))
            else:
                self.registerUpdate(input)
                self.infoMsgBox(sys.translate(u"La carga de módulos se ha realizado con éxito."))
                sys.AQTimer.singleShot(0, sys.reinit)
                tmpVar = FLVar()
                tmpVar.set(u"mrproper", u"dirty")

    @classmethod
    def loadFilesDef(self, un=None):
        filesDef = sys.toUnicode(un.getText(), u"utf8")
        doc = QDomDocument()
        if not doc.setContent(filesDef):
            self.errorMsgBox(sys.translate(u"Error XML al intentar cargar la definición de los ficheros."))
            return False
        ok = True
        root = doc.firstChild()
        files = root.childNodes()
        AQUtil.createProgressDialog(sys.translate(u"Registrando ficheros"), len(files))
        i = 0
        while_pass = True
        while i < len(files):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            it = files.item(i)
            fil = {id: (it.namedItem(u"name").toElement().text()), skip: (it.namedItem(u"skip").toElement().text()), module: (it.namedItem(u"module").toElement().text()), text: (it.namedItem(u"text").toElement(
            ).text()), shatext: (it.namedItem(u"shatext").toElement().text()), binary: (it.namedItem(u"binary").toElement().text()), shabinary: (it.namedItem(u"shabinary").toElement().text()), }
            AQUtil.setProgress(i)
            AQUtil.setLabelText(ustr(sys.translate(u"Registrando fichero"), u" ", fil.id))
            if len(fil.id) == 0 or fil.skip == u"true":
                continue
            if not registerFile(fil, un):
                self.errorMsgBox(ustr(sys.translate(u"Error registrando el fichero"), u" ", fil.id))
                ok = False
                break
            i += 1
            while_pass = True
            try:
                i < len(files)
            except Exception:
                break

        AQUtil.destroyProgressDialog()
        return ok

    @classmethod
    def registerFile(self, fil=None, un=None):
        if fil.id.endswith(u".xpm"):
            cur = AQSqlCursor(u"flmodules")
            if not cur.select(ustr(u"idmodulo='", fil.module, u"'")):
                return False
            if not cur.first():
                return False
            cur.setModeAccess(AQSql.Edit)
            cur.refreshBuffer()
            cur.setValueBuffer(u"icono", un.getText())
            return cur.commitBuffer()

        cur = AQSqlCursor(u"flfiles")
        if not cur.select(ustr(u"nombre='", fil.id, u"'")):
            return False
        cur.setModeAccess((AQSql.Edit if cur.first() else AQSql.Insert))
        cur.refreshBuffer()
        cur.setValueBuffer(u"nombre", fil.id)
        cur.setValueBuffer(u"idmodulo", fil.module)
        cur.setValueBuffer(u"sha", fil.shatext)
        if len(fil.text) > 0:
            if fil.id.endswith(u".qs"):
                cur.setValueBuffer(u"contenido", sys.toUnicode(un.getText(), u"ISO8859-15"))
            else:
                cur.setValueBuffer(u"contenido", un.getText())

        if len(fil.binary) > 0:
            un.getBinary()
        return cur.commitBuffer()

    @classmethod
    def checkProjectName(self, proName=None):
        if not proName or proName == None:
            proName = u""
        dbProName = AQUtil.readDBSettingEntry(u"projectname")
        if not dbProName:
            dbProName = u""
        if proName == dbProName:
            return True
        if not proName == '' and dbProName == '':
            return AQUtil.writeDBSettingEntry(u"projectname", proName)
        txt = u""
        txt += sys.translate(u"¡¡ CUIDADO !! POSIBLE INCOHERENCIA EN LOS MÓDULOS\n\n")
        txt += sys.translate(u"Está intentando cargar un proyecto o rama de módulos cuyo\n")
        txt += sys.translate(u"nombre difiere del instalado actualmente en la base de datos.\n")
        txt += sys.translate(u"Es posible que la estructura de los módulos que quiere cargar\n")
        txt += sys.translate(u"sea completamente distinta a la instalada actualmente, y si continua\n")
        txt += sys.translate(u"podría dañar el código, datos y la estructura de tablas de Eneboo.\n\n")
        txt += sys.translate(u"- Nombre del proyecto instalado: %s\n") % (str(dbProName))
        txt += sys.translate(u"- Nombre del proyecto a cargar: %s\n\n") % (str(proName))
        txt += u"\n\n"
        if not interactiveGUI():
            debug(txt)
            return False
        txt += sys.translate(u"¿Desea continuar?")
        return (MessageBox.Yes == MessageBox.warning(txt, MessageBox.No, MessageBox.Yes, MessageBox.NoButton, u"AbanQ"))

    @classmethod
    def loadModulesDef(self, un=None):
        modulesDef = sys.toUnicode(un.getText(), u"utf8")
        doc = QDomDocument()
        if not doc.setContent(modulesDef):
            self.errorMsgBox(sys.translate(u"Error XML al intentar cargar la definición de los módulos."))
            return False
        root = doc.firstChild()
        if not checkProjectName(root.toElement().attribute(u"projectname", u"")):
            return False
        ok = True
        modules = root.childNodes()
        AQUtil.createProgressDialog(sys.translate(u"Registrando módulos"), len(modules))
        i = 0
        while_pass = True
        while i < len(modules):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            it = modules.item(i)
            mod = {id: (it.namedItem(u"name").toElement().text()), alias: (trTagText(it.namedItem(u"alias").toElement().text())), area: (it.namedItem(
                u"area").toElement().text()), areaname: (trTagText(it.namedItem(u"areaname").toElement().text())), version: (it.namedItem(u"version").toElement().text()), }
            AQUtil.setProgress(i)
            AQUtil.setLabelText(ustr(sys.translate(u"Registrando módulo"), u" ", mod.id))
            if not registerArea(mod) or not registerModule(mod):
                self.errorMsgBox(ustr(sys.translate(u"Error registrando el módulo"), u" ", mod.id))
                ok = False
                break
            i += 1
            while_pass = True
            try:
                i < len(modules)
            except Exception:
                break

        AQUtil.destroyProgressDialog()
        return ok

    @classmethod
    def registerArea(self, mod=None):
        cur = AQSqlCursor(u"flareas")
        if not cur.select(ustr(u"idarea='", mod.area, u"'")):
            return False
        cur.setModeAccess((AQSql.Edit if cur.first() else AQSql.Insert))
        cur.refreshBuffer()
        cur.setValueBuffer(u"idarea", mod.area)
        cur.setValueBuffer(u"descripcion", mod.areaname)
        return cur.commitBuffer()

    @classmethod
    def registerModule(self, mod=None):
        cur = AQSqlCursor(u"flmodules")
        if not cur.select(ustr(u"idmodulo='", mod.id, u"'")):
            return False
        cur.setModeAccess((AQSql.Edit if cur.first() else AQSql.Insert))
        cur.refreshBuffer()
        cur.setValueBuffer(u"idmodulo", mod.id)
        cur.setValueBuffer(u"idarea", mod.area)
        cur.setValueBuffer(u"descripcion", mod.alias)
        cur.setValueBuffer(u"version", mod.version)
        return cur.commitBuffer()

    @classmethod
    def infoMsgBox(self, msg=None):
        if (msg) != u"string":
            return
        msg += u"\n"
        if interactiveGUI():
            MessageBox.information(msg, MessageBox.Ok, MessageBox.NoButton, MessageBox.NoButton, u"Eneboo")
        else:
            debug(ustr(u"INFO: ", msg))

    @classmethod
    def warnMsgBox(self, msg=None):
        if (msg) != u"string":
            return
        msg += u"\n"
        if interactiveGUI():
            MessageBox.warning(msg, MessageBox.Ok, MessageBox.NoButton, MessageBox.NoButton, u"AbanQ")
        else:
            debug(ustr(u"WARN: ", msg))

    @classmethod
    def errorMsgBox(self, msg=None):
        if (msg) != u"string":
            return
        msg += u"\n"
        if interactiveGUI():
            MessageBox.critical(msg, MessageBox.Ok, MessageBox.NoButton, MessageBox.NoButton, u"Eneboo")
        else:
            debug(ustr(u"ERROR: ", msg))

    @classmethod
    def infoPopup(self, msg=None):
        if (msg) != u"string":
            return
        caption = sys.translate(u"AbanQ Información")
        regExp = RegExp(u"\n")
        regExp.global_ = True
        msgHtml = ustr(u"<img source=\"about.png\" align=\"right\">", u"<b><u>", caption,
                       u"</u></b><br><br>", msg.replace(regExp, u"<br>"), u"<br>")
        sys.popupWarn(msgHtml, [])

    @classmethod
    def warnPopup(self, msg=None):
        if (msg) != u"string":
            return
        caption = sys.translate(u"AbanQ Aviso")
        regExp = RegExp(u"\n")
        regExp.global_ = True
        msgHtml = ustr(u"<img source=\"bug.png\" align=\"right\">", u"<b><u>", caption,
                       u"</u></b><br><br>", msg.replace(regExp, u"<br>"), u"<br>")
        sys.popupWarn(msgHtml, [])

    @classmethod
    def errorPopup(self, msg=None):
        if (msg) != u"string":
            return
        caption = sys.translate(u"AbanQ Error")
        regExp = RegExp(u"\n")
        regExp.global_ = True
        msgHtml = ustr(u"<img source=\"remove.png\" align=\"right\">", u"<b><u>", caption,
                       u"</u></b><br><br>", msg.replace(regExp, u"<br>"), u"<br>")
        sys.popupWarn(msgHtml, [])

    @classmethod
    def trTagText(self, tagText=None):
        if not tagText.startswith(u"QT_TRANSLATE_NOOP"):
            return tagText
        txt = QString(tagText).mid(len(String(u"QT_TRANSLATE_NOOP")) + 1)
        txt = ustr(u"[", QString(txt).mid(0, len(txt) - 1), u"]")
        arr = ast.literal_eval(txt)
        return sys.translate(arr[0], arr[1])

    @classmethod
    def questionMsgBox(self, msg=None, keyRemember=None, txtRemember=None, forceShow=None, txtCaption=None, txtYes=None, txtNo=None):
        settings = AQSettings()
        key = u"QuestionMsgBox/"
        valRemember = False
        if keyRemember:
            valRemember = settings.readBoolEntry(key + keyRemember)
            if valRemember and not forceShow:
                return MessageBox.Yes
        if not interactiveGUI():
            return True
        diag = QDialog()
        diag.caption = (txtCaption if txtCaption else u"Eneboo")
        diag.modal = True
        lay = QVBoxLayout(diag)
        lay.margin = 6
        lay.spacing = 6
        lay2 = QHBoxLayout(lay)
        lay2.margin = 6
        lay2.spacing = 6
        lblPix = QLabel(diag)
        lblPix.pixmap = AQS.Pixmap_fromMimeSource(u"help_index.png")
        lblPix.alignment = AQS.AlignTop
        lay2.addWidget(lblPix)
        lbl = QLabel(diag)
        lbl.text = msg
        lbl.alignment = AQS.AlignTop or AQS.WordBreak
        lay2.addWidget(lbl)
        lay3 = QHBoxLayout(lay)
        lay3.margin = 6
        lay3.spacing = 6
        pbYes = QPushButton(diag)
        pbYes.text = (txtYes if txtYes else sys.translate(u"Sí"))
        pbNo = QPushButton(diag)
        pbNo.text = (txtNo if txtNo else sys.translate(u"No"))
        lay3.addWidget(pbYes)
        lay3.addWidget(pbNo)
        connect(pbYes, u"clicked()", diag, u"accept()")
        connect(pbNo, u"clicked()", diag, u"reject()")
        chkRemember = None
        if keyRemember and txtRemember:
            chkRemember = QCheckBox(txtRemember, diag)
            chkRemember.checked = valRemember
            lay.addWidget(chkRemember)
        ret = (MessageBox.No if (diag.exec_() == 0) else MessageBox.Yes)
        if chkRemember != None:
            settings.writeEntry(key + keyRemember, chkRemember.checked)
        return ret

    @classmethod
    def decryptFromBase64(self, str_=None):
        ba = QByteArray()
        ba.string = str_
        return parseString(AQS.decryptInternal(AQS.fromBase64(ba)))

    @classmethod
    def updateAbanQ(self):
        MessageBox.warning(sys.translate(u"Funcionalidad no soportada aún en Eneboo."),
                           MessageBox.Ok, MessageBox.NoButton, MessageBox.NoButton, u"Eneboo")
        return

    @classmethod
    def exportModules(self):
        dirBasePath = FileDialog.getExistingDirectory(Dir.home)
        if not dirBasePath:
            return
        dataBaseName = aqApp.db().database()
        dirBasePath = Dir.cleanDirPath(ustr(dirBasePath, u"/modulos_exportados_",
                                            QString(dataBaseName).mid(dataBaseName.rfind(u"/") + 1)))
        dir = Dir()
        if not dir.fileExists(dirBasePath):
            try:
                dir.mkdir(dirBasePath)
            except Exception as e:
                e = traceback.format_exc()
                self.errorMsgBox(ustr(u"", e))
                return

        else:
            self.warnMsgBox(dirBasePath + sys.translate(u" ya existe,\ndebe borrarlo antes de continuar"))
            return

        qry = AQSqlQuery()
        qry.setSelect(u"idmodulo")
        qry.setFrom(u"flmodules")
        if not qry.exec_() or qry.size() == 0:
            return
        p = 0
        AQUtil.createProgressDialog(sys.translate(u"Exportando módulos"), qry.size() - 1)
        while qry.next():
            idMod = qry.value(0)
            if idMod == u"sys":
                continue
            AQUtil.setLabelText(String(u"%s") % (str(idMod)))
            p += 1
            AQUtil.setProgress(p)
            try:
                self.exportModule(idMod, dirBasePath)
            except Exception as e:
                e = traceback.format_exc()
                AQUtil.destroyProgressDialog()
                self.errorMsgBox(ustr(u"", e))
                return

        dbProName = AQUtil.readDBSettingEntry(u"projectname")
        if not dbProName:
            dbProName = u""
        if not dbProName == '':
            doc = QDomDocument()
            tag = doc.createElement(u"mvproject")
            tag.toElement().setAttribute(u"name", dbProName)
            doc.appendChild(tag)
            try:
                File.write(ustr(dirBasePath, u"/mvproject.xml"), doc.toString(2))
            except Exception as e:
                e = traceback.format_exc()
                AQUtil.destroyProgressDialog()
                errorMsgBoxl(ustr(u"", e))
                return

        AQUtil.destroyProgressDialog()
        self.infoMsgBox(sys.translate(u"Módulos exportados en:\n") + dirBasePath)

    @classmethod
    def xmlModule(self, idMod=None):
        qry = AQSqlQuery()
        qry.setSelect(u"descripcion,idarea,version")
        qry.setFrom(u"flmodules")
        qry.setWhere(ustr(u"idmodulo='", idMod, u"'"))
        if not qry.exec_() or not qry.next():
            return
        doc = QDomDocument(u"MODULE")
        tagMod = doc.createElement(u"MODULE")
        doc.appendChild(tagMod)
        tag = doc.createElement(u"name")
        tag.appendChild(doc.createTextNode(idMod))
        tagMod.appendChild(tag)
        trNoop = u"QT_TRANSLATE_NOOP(\"Eneboo\",\"%1\")"
        tag = doc.createElement(u"alias")
        tag.appendChild(doc.createTextNode(trNoop.argStr(qry.value(0))))
        tagMod.appendChild(tag)
        idArea = qry.value(1)
        tag = doc.createElement(u"area")
        tag.appendChild(doc.createTextNode(idArea))
        tagMod.appendChild(tag)
        areaName = AQUtil.sqlSelect(u"flareas", u"descripcion", ustr(u"idarea='", idArea, u"'"))
        tag = doc.createElement(u"areaname")
        tag.appendChild(doc.createTextNode(trNoop.argStr(areaName)))
        tagMod.appendChild(tag)
        tag = doc.createElement(u"entryclass")
        tag.appendChild(doc.createTextNode(idMod))
        tagMod.appendChild(tag)
        tag = doc.createElement(u"version")
        tag.appendChild(doc.createTextNode(qry.value(2)))
        tagMod.appendChild(tag)
        tag = doc.createElement(u"icon")
        tag.appendChild(doc.createTextNode(ustr(idMod, u".xpm")))
        tagMod.appendChild(tag)
        return doc

    @classmethod
    def fileWriteIso(self, fileName=None, content=None):
        fileISO = QFile(fileName)
        if not fileISO.open(File.WriteOnly):
            debug(ustr(u"Error abriendo fichero ", fileName, u" para escritura"))
            return False
        tsISO = QTextStream(fileISO.ioDevice())
        tsISO.setCodec(AQS.TextCodec_codecForName(u"ISO8859-15"))
        tsISO.opIn(content)
        fileISO.close()

    @classmethod
    def fileWriteUtf8(self, fileName=None, content=None):
        fileUTF = QFile(fileName)
        if not fileUTF.open(File.WriteOnly):
            debug(ustr(u"Error abriendo fichero ", fileName, u" para escritura"))
            return False
        tsUTF = QTextStream(fileUTF.ioDevice())
        tsUTF.setCodec(AQS.TextCodec_codecForName(u"utf8"))
        tsUTF.opIn(content)
        fileUTF.close()

    @classmethod
    def exportModule(self, idMod=None, dirBasePath=None):
        dir = Dir()
        dirPath = Dir.cleanDirPath(ustr(dirBasePath, u"/", idMod))
        if not dir.fileExists(dirPath):
            dir.mkdir(dirPath)
        if not dir.fileExists(ustr(dirPath, u"/forms")):
            dir.mkdir(ustr(dirPath, u"/forms"))
        if not dir.fileExists(ustr(dirPath, u"/scripts")):
            dir.mkdir(ustr(dirPath, u"/scripts"))
        if not dir.fileExists(ustr(dirPath, u"/queries")):
            dir.mkdir(ustr(dirPath, u"/queries"))
        if not dir.fileExists(ustr(dirPath, u"/tables")):
            dir.mkdir(ustr(dirPath, u"/tables"))
        if not dir.fileExists(ustr(dirPath, u"/reports")):
            dir.mkdir(ustr(dirPath, u"/reports"))
        if not dir.fileExists(ustr(dirPath, u"/translations")):
            dir.mkdir(ustr(dirPath, u"/translations"))
        xmlMod = xmlModule(idMod)
        sys.fileWriteIso(ustr(dirPath, u"/", idMod, u".mod"), xmlMod.toString(2))
        xpmMod = AQUtil.sqlSelect(u"flmodules", u"icono", ustr(u"idmodulo='", idMod, u"'"))
        sys.fileWriteIso(ustr(dirPath, u"/", idMod, u".xpm"), xpmMod)
        qry = AQSqlQuery()
        qry.setSelect(u"nombre,contenido")
        qry.setFrom(u"flfiles")
        qry.setWhere(ustr(u"idmodulo='", idMod, u"'"))
        if not qry.exec_() or qry.size() == 0:
            return
        while qry.next():
            name = qry.value(0)
            content = qry.value(1)
            type = name[(len(name) - (len(name) - name.rfind(u"."))):]
            if content == '':
                continue
            s02_when = type
            s02_do_work, s02_work_done = False, False
            if s02_when == u".xml":
                s02_do_work, s02_work_done = True, True
            if s02_do_work:
                sys.fileWriteIso(ustr(dirPath, u"/", name), content)
                s02_do_work = False  # BREAK
            if s02_when == u".ui":
                s02_do_work, s02_work_done = True, True
            if s02_do_work:
                sys.fileWriteIso(ustr(dirPath, u"/forms/", name), content)
                s02_do_work = False  # BREAK
            if s02_when == u".qs":
                s02_do_work, s02_work_done = True, True
            if s02_do_work:
                sys.fileWriteIso(ustr(dirPath, u"/scripts/", name), content)
                s02_do_work = False  # BREAK
            if s02_when == u".qry":
                s02_do_work, s02_work_done = True, True
            if s02_do_work:
                sys.fileWriteIso(ustr(dirPath, u"/queries/", name), content)
                s02_do_work = False  # BREAK
            if s02_when == u".mtd":
                s02_do_work, s02_work_done = True, True
            if s02_do_work:
                sys.fileWriteIso(ustr(dirPath, u"/tables/", name), content)
                s02_do_work = False  # BREAK
            if s02_when == u".kut":
                s02_do_work, s02_work_done = True, True
            if s02_do_work:
                pass
            if s02_when == u".ar":
                s02_do_work, s02_work_done = True, True
            if s02_do_work:
                pass
            if s02_when == u".jrxml":
                s02_do_work, s02_work_done = True, True
            if s02_do_work:
                pass
            if s02_when == u".svg":
                s02_do_work, s02_work_done = True, True
            if s02_do_work:
                sys.fileWriteIso(ustr(dirPath, u"/reports/", name), content)
                s02_do_work = False  # BREAK
            if s02_when == u".ts":
                s02_do_work, s02_work_done = True, True
            if s02_do_work:
                sys.fileWriteIso(ustr(dirPath, u"/translations/", name), content)
                s02_do_work = False  # BREAK

    @classmethod
    def importModules(self, warnBackup=None):
        if warnBackup == None:
            warnBackup = True
        if warnBackup and interactiveGUI():
            txt = u""
            txt += sys.translate(u"Asegúrese de tener una copia de seguridad de todos los datos\n")
            txt += sys.translate(u"y de que  no hay ningun otro  usuario conectado a la base de\n")
            txt += sys.translate(u"datos mientras se realiza la importación.\n\n")
            txt += sys.translate(u"Obtenga soporte en")
            txt += u" http://www.infosial.com\n(c) InfoSiAL S.L."
            txt += u"\n\n"
            txt += sys.translate(u"¿Desea continuar?")
            if MessageBox.Yes != MessageBox.warning(txt, MessageBox.No, MessageBox.Yes):
                return

        key = ustr(u"scripts/sys/modLastDirModules_", sys.nameBD())
        dirAnt = AQUtil.readSettingEntry(key)
        dirMods = FileDialog.getExistingDirectory(
            (dirAnt if dirAnt else False), sys.translate(u"Directorio de Módulos"))
        if not dirMods:
            return
        dirMods = Dir.cleanDirPath(dirMods)
        dirMods = Dir.convertSeparators(dirMods)
        Dir.current = dirMods
        listFilesMod = selectModsDialog(AQUtil.findFiles(Array([dirMods]), u"*.mod", False))
        AQUtil.createProgressDialog(sys.translate(u"Importando"), len(listFilesMod))
        AQUtil.setProgress(1)
        i = 0
        while_pass = True
        while i < len(listFilesMod):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            AQUtil.setLabelText(listFilesMod[i])
            AQUtil.setProgress(i)
            if not importModule(listFilesMod[i]):
                self.errorMsgBox(sys.translate(u"Error al cargar el módulo:\n") + listFilesMod[i])
                break
            i += 1
            while_pass = True
            try:
                i < len(listFilesMod)
            except Exception:
                break

        AQUtil.destroyProgressDialog()
        AQUtil.writeSettingEntry(key, dirMods)
        self.infoMsgBox(sys.translate(u"Importación de módulos finalizada."))
        sys.AQTimer.singleShot(0, sys.reinit)

    @classmethod
    def selectModsDialog(self, listFilesMod=None):
        dialog = Dialog()
        dialog.okButtonText = sys.translate(u"Aceptar")
        dialog.cancelButtonText = sys.translate(u"Cancelar")
        bgroup = GroupBox()
        bgroup.title = sys.translate(u"Seleccione módulos a importar")
        dialog.add(bgroup)
        res = Array()
        cB = Array()
        i = 0
        while_pass = True
        while i < len(listFilesMod):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            cB[i] = CheckBox()
            bgroup.add(cB[i])
            cB[i].text = listFilesMod[i]
            cB[i].checked = True
            i += 1
            while_pass = True
            try:
                i < len(listFilesMod)
            except Exception:
                break

        idx = 0
        if dialog.exec_():
            i = 0
            while_pass = True
            while i < len(listFilesMod):
                if not while_pass:
                    i += 1
                    while_pass = True
                    continue
                while_pass = False
                if cB[i].checked == True:
                    res[idx] = listFilesMod[i]
                    idx += 1
                i += 1
                while_pass = True
                try:
                    i < len(listFilesMod)
                except Exception:
                    break

        return res

    @classmethod
    def importModule(self, modPath=None):
        fileMod = File(modPath)
        contentMod = u""
        try:
            fileMod.open(File.ReadOnly)
            contentMod = fileMod.read()
        except Exception as e:
            e = traceback.format_exc()
            self.errorMsgBox(ustr(sys.translate(u"Error leyendo fichero."), u"\n", e))
            return False

        mod = None
        xmlMod = QDomDocument()
        if xmlMod.setContent(contentMod):
            nodeMod = xmlMod.namedItem(u"MODULE")
            if not nodeMod:
                self.errorMsgBox(sys.translate(u"Error en la carga del fichero xml .mod"))
                return False
            mod = {id: (nodeMod.namedItem(u"name").toElement().text()), alias: (trTagText(nodeMod.namedItem(u"alias").toElement().text())), area: (nodeMod.namedItem(
                u"area").toElement().text()), areaname: (trTagText(nodeMod.namedItem(u"areaname").toElement().text())), version: (nodeMod.namedItem(u"version").toElement().text()), }
            if not registerArea(mod) or not registerModule(mod):
                self.errorMsgBox(ustr(sys.translate(u"Error registrando el módulo"), u" ", mod.id))
                return False
            if not importFiles(fileMod.path, u"*.xml", mod.id):
                return False
            if not importFiles(fileMod.path, u"*.ui", mod.id):
                return False
            if not importFiles(fileMod.path, u"*.qs", mod.id):
                return False
            if not importFiles(fileMod.path, u"*.qry", mod.id):
                return False
            if not importFiles(fileMod.path, u"*.mtd", mod.id):
                return False
            if not importFiles(fileMod.path, u"*.kut", mod.id):
                return False
            if not importFiles(fileMod.path, u"*.ar", mod.id):
                return False
            if not importFiles(fileMod.path, u"*.jrxml", mod.id):
                return False
            if not importFiles(fileMod.path, u"*.svg", mod.id):
                return False
            if not importFiles(fileMod.path, u"*.ts", mod.id):
                return False

        else:
            self.errorMsgBox(sys.translate(u"Error en la carga del fichero xml .mod"))
            return False

        return True

    @classmethod
    def importFiles(self, dirPath=None, ext=None, idMod=None):
        ok = True
        listFiles = AQUtil.findFiles(Array([dirPath]), ext, False)
        AQUtil.createProgressDialog(sys.translate(u"Importando"), len(listFiles))
        AQUtil.setProgress(1)
        i = 0
        while_pass = True
        while i < len(listFiles):
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            AQUtil.setLabelText(listFiles[i])
            AQUtil.setProgress(i)
            if not importFile(listFiles[i], idMod):
                self.errorMsgBox(sys.translate(u"Error al cargar :\n") + listFiles[i])
                ok = False
                break
            i += 1
            while_pass = True
            try:
                i < len(listFiles)
            except Exception:
                break

        AQUtil.destroyProgressDialog()
        return ok

    @classmethod
    def importFile(self, filePath=None, idMod=None):
        file = File(filePath)
        content = u""
        try:
            file.open(File.ReadOnly)
            content = file.read()
        except Exception as e:
            e = traceback.format_exc()
            self.errorMsgBox(ustr(sys.translate(u"Error leyendo fichero."), u"\n", e))
            return False

        ok = True
        name = file.name
        if (not AQUtil.isFLDefFile(content) and not name.endswith(u".qs") and not name.endswith(u".ar") and not name.endswith(u".svg")) or name.endswith(u"untranslated.ts"):
            return ok
        cur = AQSqlCursor(u"flfiles")
        cur.select(ustr(u"nombre = '", name, u"'"))
        if not cur.first():
            if name.endswith(u".ar"):
                if not importReportAr(filePath, idMod, content):
                    return True
            cur.setModeAccess(AQSql.Insert)
            cur.refreshBuffer()
            cur.setValueBuffer(u"nombre", name)
            cur.setValueBuffer(u"idmodulo", idMod)
            ba = QByteArray()
            ba.string = content
            cur.setValueBuffer(u"sha", ba.sha1())
            cur.setValueBuffer(u"contenido", content)
            ok = cur.commitBuffer()

        else:
            cur.setModeAccess(AQSql.Edit)
            cur.refreshBuffer()
            ba = QByteArray()
            ba.string = content
            shaCnt = ba.sha1()
            if cur.valueBuffer(u"sha") != shaCnt:
                contenidoCopia = cur.valueBuffer(u"contenido")
                cur.setModeAccess(AQSql.Insert)
                cur.refreshBuffer()
                d = Date()
                cur.setValueBuffer(u"nombre", name + parseString(d))
                cur.setValueBuffer(u"idmodulo", idMod)
                cur.setValueBuffer(u"contenido", contenidoCopia)
                cur.commitBuffer()
                cur.select(ustr(u"nombre = '", name, u"'"))
                cur.first()
                cur.setModeAccess(AQSql.Edit)
                cur.refreshBuffer()
                cur.setValueBuffer(u"idmodulo", idMod)
                cur.setValueBuffer(u"sha", shaCnt)
                cur.setValueBuffer(u"contenido", content)
                ok = cur.commitBuffer()
                if name.endswith(u".ar"):
                    if not importReportAr(filePath, idMod, content):
                        return True

        return ok

    @classmethod
    def importReportAr(self, filePath=None, idMod=None, content=None):
        if not sys.isLoadedModule(u"flar2kut"):
            return False
        if AQUtil.readSettingEntry(u"scripts/sys/conversionAr") != u"true":
            return False
        content = sys.toUnicode(content, u"UTF-8")
        content = flar2kut.iface.pub_ar2kut(content)
        filePath = ustr(filePath[0:len(filePath) - 3], u".kut")
        if content:
            localEnc = util.readSettingEntry(u"scripts/sys/conversionArENC")
            if not localEnc:
                localEnc = u"ISO-8859-15"
            content = sys.fromUnicode(content, localEnc)
            try:
                File.write(filePath, content)
            except Exception as e:
                e = traceback.format_exc()
                self.errorMsgBox(ustr(sys.translate(u"Error escribiendo fichero."), u"\n", e))
                return False

            return importFile(filePath, idMod)

        return False

    @classmethod
    def dumpDatabase(self):
        aqDumper = AbanQDbDumper()
        aqDumper.init()

    @classmethod
    def setObjText(self, container=None, component=None, value=None):
        c = self.testObj(container, component)
        if not c:
            return False
        clase = (u"FLFieldDB" if (u"editor" in c) else c.className())
        s03_when = clase
        s03_do_work, s03_work_done = False, False
        if s03_when == u"QPushButton":
            s03_do_work, s03_work_done = True, True
        if s03_do_work:
            pass
        if s03_when == u"QToolButton":
            s03_do_work, s03_work_done = True, True
        if s03_do_work:
            pass
        if s03_when == u"QLabel":
            s03_do_work, s03_work_done = True, True
        if s03_do_work:
            self.runObjMethod(container, component, u"text", ustr(u"\"", value, u"\""))
            s03_do_work = False  # BREAK
        if s03_when == u"FLFieldDB":
            s03_do_work, s03_work_done = True, True
        if s03_do_work:
            self.runObjMethod(container, component, u"setValue", value)
            s03_do_work = False  # BREAK
        if not s03_work_done:
            s03_do_work, s03_work_done = True, True
        if s03_do_work:
            return False
        return True

    @classmethod
    def disableObj(self, container=None, component=None):
        c = testObj(container, component)
        if not c:
            return False
        clase = (u"FLFieldDB" if (u"editor" in c) else ((u"FLTableDB" if (u"tableName" in c) else c.className())))
        s04_when = clase
        s04_do_work, s04_work_done = False, False
        if s04_when == u"QPushButton":
            s04_do_work, s04_work_done = True, True
        if s04_do_work:
            pass
        if s04_when == u"QToolButton":
            s04_do_work, s04_work_done = True, True
        if s04_do_work:
            self.runObjMethod(container, component, u"setEnabled", False)
            s04_do_work = False  # BREAK
        if s04_when == u"FLFieldDB":
            s04_do_work, s04_work_done = True, True
        if s04_do_work:
            self.runObjMethod(container, component, u"setDisabled", True)
            s04_do_work = False  # BREAK
        if not s04_work_done:
            s04_do_work, s04_work_done = True, True
        if s04_do_work:
            return False
        return True

    @classmethod
    def enableObj(self, container=None, component=None):
        c = testObj(container, component)
        if not c:
            return False
        clase = (u"FLFieldDB" if (u"editor" in c) else ((u"FLTableDB" if (u"tableName" in c) else c.className())))
        s05_when = clase
        s05_do_work, s05_work_done = False, False
        if s05_when == u"QPushButton":
            s05_do_work, s05_work_done = True, True
        if s05_do_work:
            pass
        if s05_when == u"QToolButton":
            s05_do_work, s05_work_done = True, True
        if s05_do_work:
            self.runObjMethod(container, component, u"setEnabled", True)
            s05_do_work = False  # BREAK
        if s05_when == u"FLFieldDB":
            s05_do_work, s05_work_done = True, True
        if s05_do_work:
            self.runObjMethod(container, component, u"setDisabled", False)
            s05_do_work = False  # BREAK
        if not s05_work_done:
            s05_do_work, s05_work_done = True, True
        if s05_do_work:
            return False
        return True

    @classmethod
    def filterObj(self, container=None, component=None, filter=None):
        c = testObj(container, component)
        if not c:
            return False
        clase = (u"FLFieldDB" if (u"editor" in c) else ((u"FLTableDB" if (u"tableName" in c) else c.className())))
        s06_when = clase
        s06_do_work, s06_work_done = False, False
        if s06_when == u"FLTableDB":
            s06_do_work, s06_work_done = True, True
        if s06_do_work:
            pass
        if s06_when == u"FLFieldDB":
            s06_do_work, s06_work_done = True, True
        if s06_do_work:
            self.runObjMethod(container, component, u"setFilter", filter)
            s06_do_work = False  # BREAK
        if not s06_work_done:
            s06_do_work, s06_work_done = True, True
        if s06_do_work:
            return False
        return True

    @classmethod
    def testObj(self, container=None, component=None):
        if not container or container == None:
            return False
        c = container.child(component)
        if not c or c == None:
            debug(ustr(component, u" no existe"))
            return False
        return c

    @classmethod
    def testAndRun(self, container=None, component=None, method=None, param=None):
        c = testObj(container, component)
        if not c:
            return False
        if not runObjMethod(container, component, method, param):
            return False
        return True

    @classmethod
    def runObjMethod(self, container=None, component=None, method=None, param=None):
        c = container.child(component)
        if method in c:
            s = ustr(container.name, u".child(\"", component, u"\").", method)
            m = ast.literal_eval(s)
            if m == u"function":
                m(param)
            else:
                ast.literal_eval("%s = %s" % (s, param))

        else:
            debug(ustr(method, u" no existe"))

        return True

    @classmethod
    def connectSS(self, ssSender=None, ssSignal=None, ssReceiver=None, ssSlot=None):
        if not ssSender:
            return False
        connect(ssSender, ssSignal, ssReceiver, ssSlot)
        return True

    @classmethod
    def runTransaction(self, f=None, oParam=None):
        curT = FLSqlCursor(u"flfiles")
        curT.transaction(False)
        valor = None
        errorMsg = None
        gui = interactiveGUI()
        if gui:
            try:
                AQS.Application_setOverrideCursor(AQS.WaitCursor)
            except Exception as e:
                e = traceback.format_exc()

        try:
            valor = f(oParam)
            errorMsg = (oParam.errorMsg if (u"errorMsg" in oParam) else False)
            if valor:
                curT.commit()
            else:
                curT.rollback()
                if gui:
                    try:
                        AQS.Application_restoreOverrideCursor()
                    except Exception:
                        e = traceback.format_exc()

                if errorMsg:
                    self.warnMsgBox(errorMsg)
                else:
                    self.warnMsgBox(translate(u"Error al ejecutar la función"))

                return False

        except Exception:
            e = traceback.format_exc()
            curT.rollback()
            if gui:
                try:
                    AQS.Application_restoreOverrideCursor()
                except Exception:
                    e = traceback.format_exc()

            if errorMsg:
                self.warnMsgBox(ustr(errorMsg, u": ", parseString(e)))
            else:
                self.warnMsgBox(ustr(translate(u"Error ejecutando la función"), u":\n", e))

            return False

        if gui:
            try:
                AQS.Application_restoreOverrideCursor()
            except Exception as e:
                e = traceback.format_exc()

        return valor

    @classmethod
    def openUrl(self, url=None):
        if not url:
            return False
        s07_when = sys.osName()
        s07_do_work, s07_work_done = False, False
        if s07_when == u"LINUX":
            s07_do_work, s07_work_done = True, True
        if s07_do_work:
            if self.launchCommand([u"xdg-open", url]):
                return True
            if self.launchCommand([u"gnome-open", url]):
                return True
            if self.launchCommand([u"kfmclient openURL", url]):
                return True
            if self.launchCommand([u"kfmclient exec", url]):
                return True
            if self.launchCommand([u"firefox", url]):
                return True
            if self.launchCommand([u"mozilla", url]):
                return True
            if self.launchCommand([u"opera", url]):
                return True
            if self.launchCommand([u"google-chrome", url]):
                return True
            s07_do_work = False  # BREAK

        if s07_when == u"WIN32":
            s07_do_work, s07_work_done = True, True
        if s07_do_work:
            if url.startswith(u"mailto"):
                rxp = RegExp(u"&")
                rxp.global_ = True
                url = url.replace(rxp, u"^&")
            return self.launchCommand([u"cmd.exe", u"/C", u"start", u"", url])
            s07_do_work = False  # BREAK

        if s07_when == u"MACX":
            s07_do_work, s07_work_done = True, True
        if s07_do_work:
            return self.launchCommand([u"open", url])
            s07_do_work = False  # BREAK
        return False

    @classmethod
    def launchCommand(self, comando):
        try:
            Process.execute(comando)
            return True
        except Exception as e:
            e = traceback.format_exc()
            return False

    @classmethod
    def isUserBuild(self):
        return sys.version().upper().indexOf(u"USER") != - 1

    @classmethod
    def isDeveloperBuild(self):
        return sys.version().upper().indexOf(u"DEVELOPER") != - 1

    @classmethod
    def interactiveGUI(self):
        return aqApp.db().interactiveGUI()

    @classmethod
    def qsaExceptions(self):
        return aqApp.db().qsaExceptions()

    @classmethod
    def serverTime(self):
        db = aqApp.db().db()
        sql = u"select current_time"
        ahora = None
        q = QSqlSelectCursor(sql, db)
        if q.isActive() and q.next():
            ahora = q.value(0)
        return ahora


form = None
