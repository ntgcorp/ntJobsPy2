#
# Interface for ntJobsOS FrontEnd Application
# JOBS_Start_Read: Legge INI di Configurazione
# JOBS_End_Write: Scrive INI di Fine attività
# JOBS_ARGS: Recupero parametri secondo varie opzioni permesse nel lancio FrontEnd ntJobsOS
#
import nlSys, nlExt
import nlDataFiles
import argparse
import os
import locale

# Test mode
NT_ENV_TEST_APP = True
NT_ENV_APP_EXT = "py"

# ----------------------- CLASSI ---------------------------

# ---------- NC_SYS - jData - ntJobs.App -------------------
class NC_Sys:
# Arguments and Setup
    sID = ""              # ID Applicazione
    bTest = False         # Test Mode Attivo - Deve esserci inifile
    bLive = False         # Verifica processo in Live
    bIni = False          # Obbligatorio INI come riga di comando
    sIniAppFile = ""      # INI File - File di inizializzazine applicazione
    sIniJobsFile= ""      # INI fILE - File dei jobs
# App Path
    sSysPath = ""         # ntJobs Kit Path Root
    sApp_Path = ""        # Application Path
    sApp_File = ""        # Applicatioon File Name
# Argomenti di lancio applicazione (iniziali file.ini file.csv facoltativo)
    dictArgs = None       # Argomenti
# jOBS.INI Path
    sJob_Path = ""        # Job File Path
    sJob_File = ""        # Job File (Normalizzato completo)
    sJob_Name = ""        # JOB.ID come somma di più JOBS
# TimeStamp
    sTS_Live=""           # TimeStamp Live, all'inizio = start
    sTS_Start = ""        # TimeStamp: Start
    sTS_End = ""          # TimeStart: End
# INI Config + Actions in sequenza
    dictConfig = {}       # Config (Sezione Config) - Da file INI.APP+INI.JOBS
    dictConfigFields = {} # Tipizzazione particolare (per tutte le sezioni).
    dictJobs = {}         # Jobs/Sections - Config(NON USATO estrattoin dictConfig) + Parametri richiamo Actions in sequenza
    asJobs = []           # Jobs Names List (config....ecc)
# Job/Azione Corrente: Ingresso
    dictJob = {}          # JobCorrente. Action, Files.*=, Vars.*= )
    sAction = ""          # Azione Corrente - NON VIENE CONTROLLATO DIRITTO DI ESEGUIRLA - SOLO PER QUESTA APP
    sJob = ""             # Job corrente ID
    sJobPath = ""         # Path singolo job (dopo lettura file INI del JOB) --- !!! DA VERIRICARE SE SERVE !!!!
# Sezione(jobs) Corrente da cui deriva dictJob che viene separato in singolo jobs.ini e passato a ntjobs.OS
# Azione Corrente - RITORNO
    lResult = []          # Return from CallBack
    cbActions = None      # CallBack Function
    sResult = ""          # Return Value
    sRetType = ""         # Return Type, E=Errore, ""=Ok, W=Warning
    dictReturnFiles = {}  # Eventuali file di ritorno dict [FILE.ID=FILE.PATH.NORM]
    dictReturnVars = {}   # Variabili di ritorno del job corrente
    dictReturn = {}       # dictReturn di Ritorno Calcolata per scrittura - SINGOLA SEZIONE - Da aggiungere da ReturnAdd
# Ritorno di tutte le azioni Eseguite (sezione= nome_sezione_non_config, RET.VAL, RET.TYPE, FILE.ID=VALORE, CONFIG=Sezione ritorni prima delle azioni)
    dictReturnS = {}      # Sezioni dictReturn di Ritorno Calcolata per scrittura - UNA VOLTA SOLA VIENE SCRITTO il file
# File di LOG Singola Sessione (job) e Globale (File)
    sLogFile = ""         # File di log Globale
    sLiveFile=""          # File di Live
    sLogJobFile  = ""     # File di log Singolo Job - Se avvalorato allora presente

# Metodi (Init)
# --------------------------------------------------------------------------------
    def __init__(self):
        pass

# Inizializzazione ntJobsApp
    def Init(self, sID_set, **kwargs):
        sProc="JOBS.APP.INIT"
        sResult=""

# TS Start
        self.sTS_Start=nlSys.NF_TS_ToStr()

# Init jData
        try:
            locale.setlocale(locale.LC_ALL, "it_IT.UTF8")
            self.sID = sID_set
            self.sSys_Path = os.getcwd()
            print("ntJob.Start: " + self.sID + ", TS: " + self.sTS_Start)
        except:
            sResult="Errore App Init"

# Inizializazione parametri App
        if (kwargs != None) and (sResult == ""):
            for key, value in kwargs.keys:
        # Attiva LOG
                if key=="log":
                    self.sLogFile = self.sSys_Path + "\\Log\\" + self.sID + ".log"
                    sResult=self.Log("Start", type="s", proc="init")
        # Attiva INI
                elif key=="ini":
                    self.bIni=value
        # Attiva
                elif key=="test":
                    self.bTest=nlSys.NF_DictGet(kwargs,"test", False)
        # Actions
                elif key=="actions":
                    self.actions=("MAIL.SEND"),
        # Callback
                elif key=="cb":
                    self.cbactions=value,
        # Live
                elif key=="live":
                    self.bLive=True
        # Config Required
                elif key=="config":
                    self.dictConfigFields = {"WAIT":"I", "SMTP.SSL":"B", "SMTP.PORT":"I","MASSIVE":"B"}

# Primo Log
        if sResult=="":
            self.Log("Start")

# Legge Argomenti
        if sResult=="":
            sResult=self.Args()
            if sResult=="": nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Args ", sProc)

# File Ini Jobs - Setup
        if sResult=="":
            if self.bIni:
                self.sIniJobs_File=self.TestFile(self.NF_PathNormal(self.sIniJobs_File))
                sResult=nlSys.NF_FileExistErr(self.sIniJobs_File,"non presente ini jobs")

# Scompose App(py) - Get App Path/Name
            if sResult=="":
                self.sApp_file=nlSys.NF_PathScript("ID.NE")
                self.sApp_path=nlSys.NF_PathScript("PATH")
                self.sIniAppFile=self.TestFile(nlSys.NF_PathMake(self.sApp_Path,self.sApp_Name,NT_ENV_APP_EXT))

# Scompose Job - Get Path & Name
        if (sResult=="") and (self.sIniJobs_File!=""):
            # Normalizzazione e JobPath
            # 0=Ritorno, 1=Dir, 2=File, 3=Ext, 4=FileConExt, 5=FileNormalizzato
            lResult=nlSys.NF_PathNormal(self.sJob_File)
            self.sJob_Path=lResult[1]
            self.sJob_File=lResult[5]
            self.sJob_Name=lResult[2]
# Debug
        if sResult == "":
            nlSys.NF_DebugFase(self.bTest, f"File INI.APP {self.sFileIni_app}, File INI.JOBS {self.sFileIni_app}, File CSV {self.sFileCsv}", sProc)
            dictParams={"INI.YES": self.bINI, "TEST.YES": self.bTest, "INI.TEST": self.sIniTest, "ACTIONS": self.asJobs}
            nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Parametri job: " + nlSys.NF_StrObj(dictParams), sProc)

# Read INI.APP - Legge se c'è, test mode o no
        if sResult=="":
            if nlSys.NF_FileExist(self.sIniAppFile):
                sResult=self.NF_ReadIni("app")
# dictConfig: Conversioni di Tipi e Verifica che ci siano i parametri "obbligatori"
        if sResult == "":
            self.dictConfig = nlSys.NF_DictConvert(self.dictConfig, self.dictConfigFields)
            nlSys.NF_DebugFase(NT_ENV_TEST_APP, "INI CONFIG. Keys " + nlSys.NF_DictStr(self.dictConfig), sProc)

# Read INI.JOBS
        if sResult=="":
            sResult=self.NF_ReadIni("jobs")
            # Parametri: Lettura INI JOB
        if sResult=="":
            # Impostazioni Post caricamento Jobs
            self.asJobs=self.dictJobs.Keys()
            nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Jobs letti:" + str(nlSys.NF_DictLen(self.dictJobs)), sProc)
# dictJobs: Conversioni di Tipi e Verifica che ci siano i parametri "obbligatori"
            for sKey in self.asJobs:
                dictJob=nlSys.NF_DictConvert(self.dictJobs[sKey], self.dictConfigFields)
                self.dictJobs[sKey]=dictJob

# Se Live scrive file di live iniziale
        if sResult=="" and self.bLive:
            self.sTS_Live=nlSys.NF_TS_ToStr()
            self.sLiveFile=nlSys.NF_PathMake(self.sJob_Path,self.sJobMame,"live")
            sResult=self.Live()

# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)

# Scrive Riga LOG. Parametri:
# Log(Obbligatorio): Riga di commento Log
# type=tipo log (s=start.app, tk=trans.ok, te=trans.err, e=errore generico, w=warning, l(default)=log, f=end.app),
# tag=Log.Tag, proc=Log.Proc
# Formato Log. TYPE;TS;TAG;LOG.NOTE
# DA Completare
# ---------------------------------------------------------------------------------------------------------------
    def Log(self, sLog, **kaArgs):
        sProc="JOBS.APP.LOG"
        sResult=""

    # Parametri Facoltativi
        if (kaArgs != None):
            for sKey,sValue in kaArgs.keys:
                sValue=str(sValue)
                if sKey=="type":
                    if sValue=="s":
                        sLogP="App.Start"
                    elif sValue=="tk":
                        sLogP="Trans.End.Ok"
                    elif sValue=="te":
                        sLogP="Trans.End.Err"
                    elif sValue=="e":
                        sLogP="Error"
                    elif sValue=="w":
                        sLogP="Warning"
                    elif sValue=="l":
                        sLogP="Log"
                    elif sValue=="f":
                        sLog="App.Start"
                    else:
                        sLogP="NA"
                elif sKey=="tag":
                    sLogTag=sValue
                elif sKey=="proc":
                    sLogProc=sValue
                else:
                    sResult="Log key not supported: " + sKey

    # Creazione riga di LOG
        sText = f"{self.sID}.{sLogProc}.{sLogTag}"
        sText = sText + ", " + nlSys.NF_TS_ToStr() + "," + sLogTag + ": "  + sLog

    # Scrive riga di Job su LogFile e LogTrans
        if self.sLogFile != "":
            nlSys.NF_FileFromStr(sText, self.sLogFile, "a")
        else:
            print(sLog)
        if self.sLogJob != "": nlSys.NF_FileFromStr(sText, self.sLogJob, "a")

    # Ritorno
        return sText

# Sezione Legge file INI (type= app/jobs)
# Ritorno lResult. 0=Stato, 1=dictINI se trovato File.INI di config con sezione [CONFIG] o None, 2=FileCSV_normalizzato, 3=Records
# Ritorno: sResult
# --------------------------------------------------------------------------------
    def ReadINI(self,sType):
        sProc = "JOBS.APP.ReadINI"
        sResult = ""

# Tipo File
        if sType=="app":
            sFileIni=self.sIniAppFile
        elif sType=="jobs":
            sFileIni=self.sIniJobs_File
        else:
            sResult="Type ini non supportato " + sType

# INI/CSV Obbligatorio check
        if sResult=="":
            sResult=nlSys.NF_FileExistErr(self.sIniJobs_File)

# Legge INI
        if sResult=="":
            nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Lettura file INI:" + self.sJob_File, sProc)
            lResult=nlDataFiles.NF_INI_Read(sFileIni)
            sResult=lResult[0]

# Caso 1: App - Imposta config
        if (sType=="app") and (sResult==""):
        # Prende sezione CONFIG
            self.dictConfig=lResult[1]
        else:
# Caso 2: Jobs - Aggiunta a config + jobs
            self.dictJobs=lResult[1]
            dictConfig=nlSys.NF_DictGet(self.dictJobs, "CONFIG", {})
            if nlSys.NF_DictLen(dictConfig)<1:
                sResult="sezione CONFIG vuota o non esistente"
            else:
                nlSys.NF_DictMerge(self.dictConfig,dictConfig)
# Completamento:
        nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Letto file INI. Eventuali errori: " + sResult, sProc)

# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)

# Arguments
# Parametri
# INI.YES: Obbligatorio File INI
# TEST.YES: Previsti file di test, allora ci deve essere anche TEST.INI
# Ritorno lResult. 0=sFileINI
# ------------------------------------------------------------------------------------
    def Args(self):
        sProc="JOBS.APP.ARGS"
        sResult=""

# Argomenti
        lResult=self.NF_Args()
        sResult=lResult[0]
        if sResult=="":
            dictArgs=lResult[1]
            self.sIniJobs_File=nlSys.NF_DictGet(dictArgs,1,"")
# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)

# Aggiunge dictReturn a dictReturnS
# ------------------------------------------------------------------------------------
    def ReturnAdd(self):
        self.dictReturnS[self.sJob]=self.dictReturn.copy()

# Scrive dictReturnS in file JOBS.END nella stessa cartella file JOBS.INI . Per tutte le sezioni di ritorno
# Se vuoto scrive file vuoto
# Parametri:
#   JOB.PATH: Cartella del JOB.
# Ritorno: sResult
# ------------------------------------------------------------------------------------
    def ReturnWrite(self):
        sProc="JOBS.APP.RETURN.WRITE"
        sResult=""

# Calcola File End
        sFileEnd=nlSys.NF_PathMake(self.sJob_Path, "jobs", "end")
        nlSys.NF_DebugFase(NT_ENV_TEST_APP, "File END: " + sFileEnd, sProc)

# Scrive File END di ritorno
        sResult=nlDataFiles.NF_INI_Write(sFileEnd, self.dictReturnS)
# Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Calcola Dictionary di Ritorno da Scrivere su File
# Imposta dictReturn, Ritorno: sResult
#   RETURN.TYPE: RETURN.TYPE=E=Errore/W=Working/Nulla=OK
#   RETURN.VALUE=Messaggio di ritorno
#   TS.START, TS.END = TimeStamp di inizio e fine
# ---------------------------------------------------------------------------------------------------------------
    def ReturnCalc(self,lResult):

# Conclusione JOB.SECTION
        self.sTS_End=nlSys.NF_TS_ToStr()
        print ("JOB.SECTION.END: " + self.sJob + ", TS: " + self.sTS_End)

# Calcola RetType
        self.sResult=lResult[0]
        if self.sResult!="":
            self.sRetType="E"
        else:
            self.sRetType=""

# Prende Files - Anche un EMPTY
# Prende Variabili di Ritorno
        nLen=len(lResult)
        if nLen>1: self.dictReturnFiles=lResult[1]
        if nLen>2: self.dictReturnVars=lResult[2]

# Crea dictReturn
        self.dictReturn={
            "TS.START": self.sTS_Start,
            "TS.END": self.sTS_End,
            "RETURN.TYPE": self.sRetType,
            "RETURN.VALUE": self.sResult,
            "JOB.PATH": self.sSys_Path
            }
# Aggiunge Files PDF Creati
        self.ReturnCalcAddExtra("FILES")
        self.ReturnCalcAddExtra("VARS")

# Aggiuge Files o Vars al ritorno
# Ritorno: sResult
# Parametro: sType(VARS,FILES,"")
# ---------------------------------------------------------------------------------------------------------------
    def ReturnCalcAddExtra(self, sType=""):
        sProc="JOBS.APP.ReturnCalcAddExtra"
        dictAdd={}
        sResult=""
        sTag=""

    # dict Da Aggiungere
        if sType=="VARS":
                dictAdd=self.dictReturnVars
                sTag="VAR"
        if sType=="FILES":
                dictAdd=self.dictReturnFiles
                sTag="FILE"
    # Aggiunta
        if nlSys.NF_DictLen(dictAdd)>0:
            nCounter=0
            for sKey in nlSys.NF_DictKeys(dictAdd):
                nCounter=nCounter+1
                sValue=nlSys.NF_DictGet(dictAdd, sKey,"")
                self.dictReturn[sTag + "." + sKey]=sValue
    # Uscita Nulla
        return sResult

# Calcola Ritorno e Lo Aggiunge al Pool di Ritorni
#   Oggetto ntJobs.App, Scrive sResult e dictReturnFiles
# Ritorno: sResult
# ---------------------------------------------------------------------------------------------------------------
    def ReturnCalcAdd(self,lResult):
# Calcola Ritorno e Scrive
        self.ReturnCalc(lResult)
        self.ReturnAdd()

# Esecuzione Singoli jobs (Azioni) del JOB.INI complessivo
# ------------------------------------------------------------------------------
    def Run(self):
        sProc="JOBS.APP.RUN"
        sResult=""
        lResult=[]

    # Setup
        dictReturnS=[]

    # Ciclo Azioni
        for sJob in self.asJobs:
        # TimeStamp e Reset Return
            self.dictReturn={}
            self.dictReturnFiles={}
            self.dictReturnVars={}
       # Job/Azione Corrente
            self.dictJob=self.dictJobs[sJob]
        # Start Azione mediante CallBack - Ritorno previsto lResult, ad uso dinamico
            nlSys.NF_DebugFase(NT_ENV_TEST_APP, "JOB.SECTION.END: " + self.sJob + ", TS: " + self.sTS_Start, sProc)
        # Verifica Parametri Job
            sResult=self.JobVerify()
            if sResult=="":
                lResult=self.cbActions(self.dictJob)
        # Memorizzazione ritorni per ritorno locale e jData 0=Result, 1=Files, 2=Vars
                self.lResult=lResult
                self.sResult=lResult[0]
                if len(lResult) > 1: self.dictReturnFiles=lResult[1]
                if len(lResult) > 2: self.dictReturnVars=lResult[2]
        # Aggiunge Ritorno
                self.ReturnCalcAdd(lResult)
        # Debug
                print("Ritorno JOB: " + sJob + ", Files: " + nlSys.NF_DictStr(self.dictReturnFiles) + ", Vars: " + nlSys.NF_DictStr(self.dictReturnVars))
        # Uscita in caso di errore di un job
            else:
                if self.bBreak:
                    break
        # Live
            if sResult=="" and (self.bLive):
                sResult=self.Live()
                if sResult != "": break

    # END Job.Complessivo
        self.End()
        print(self.ReturnStr())

    # Scrive Return
        sResult=self.ReturnWrite()
        nlSys.NF_DebugFase(NT_ENV_TEST_APP, "Risultato scrittura ritorno" + sResult, sProc)

    # Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

# Prende parametro da dictionary job, oppure ritorna errore, tipizzazione di default se precisata
# -----------------------------------------------------------------------------------------------------
    def GetParam(self, sParam, sError, sType=None):
        sResult,vDato=nlSys.NF_DictGetParam(self.dictJob, sParam, sError, sType)
        return sResult,vDato

# Fine Job (subito dopo RUN. Separato per motivi di test)
# -----------------------------------------------------------------------------------------------------
    def End(self):
        sProc = "JOBS.APP.END"
        sResult = ""
    # PER ORA NON FA NULLA
    # Ritorno
        sResult=nlSys.NF_ErrorProc(sResult,sProc)
        return sResult

# String del Return
    def ReturnStr(self):
        sResult=f"Ritorno JOB. Nome: {self.sJob_Name} , Section: {self.sJob}, LenDict: {str(len(self.dictReturnS))}\n"
        for xKey in self.dictReturnS.keys():
            sResult = sResult + str(xKey) + " " + nlSys.NF_DictStr(self.dictReturnS[xKey]) + "\n"
        return sResult

# Job Verify: Verifica parametri del JOB
# -----------------------------------------------------------------------------------------------------
    def JobVerify(self):
        sProc="JOBS.VERIFY"
        sResult=""

    # Verifica Azione
        sAction=nlSys.NF_DictGet(self.dictJob,"ACTION","")
        if sAction=="": sResult="Azione non dichiarata in INI"

        # Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)

# TestFile
# Aggiunge _test se siamo in testmobe
# ----------------------------------------------------------------------------------------------------
    def TestFile(self,sFile):
        sResult=""
# Solo se test mode
        if self.bTest:
            sPath,sFile,sExt=nlSys.NF_FileScompose(sFile)
            sResult=nlSys.NF_PathMake(sPath,sFile + "_test", sExt)
        else:
            sResult=sFile
# Ritorno
        return sResult

# Live: Aggiunge Live ogni x secondi
# Utilizza un TS di Live specifico
# ----------------------------------------------------------------------------------------------------
    def Live(self):
        sResult=""
        sProc="APP.LIVE"

        self.sTS_Live=nlSys.NF_TS_ToStr()
        sResult=nlSys.NF_FileWrite(self.sLive_file, self.sTS_Live)

# Ritorno
        return nlSys.NF_ErrorProc(sResult,sProc)