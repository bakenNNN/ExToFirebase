import pandas as pd
import os
import PySimpleGUI as sg
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase import firebase
import http.client as httplib
def have_firebase():
    conn = httplib.HTTPConnection("firebase.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False
def have_internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False
have_firebase()
have_internet()
res = have_firebase()
inter=have_internet()
Connected=0
firebaseConn=0
if res==True and inter==True:
    working_directory_DBJSONdir = os.path.join(os.getcwd(), "attendance-87853.json") #dir a jsonhoz
    cred = credentials.Certificate('./attendance-87853.json')
    default_app = firebase_admin.initialize_app(cred)
    db = firestore.client()
    Connected=1
    firebaseConn=1
    firebase = firebase.FirebaseApplication('https://attendance-87853-default-rtdb.europe-west1.firebasedatabase.app/', None)
if inter==True and res==False:
    Connected=1
layout=[[sg.T("")],
        [sg.Text("Milyen függvény?: "), sg.Input(key="-Operation-")],
        [sg.Text("COLLECTION Neve: "), sg.Input(key="-Coll-", default_text='__UNDEF__')],
        [sg.Text("DOCUMENT Neve: "), sg.Input(key="-Doc-", default_text='__UNDEF__')],
        [sg.Text("Táblázat: "), sg.Input(), sg.FileBrowse(
            button_text="Tallózás", key="-IN-")],
        [sg.Button("OK")],
        [sg.Text("Jelenlegi függvények: Gyermekvedelem, Hagyatek")],
        [sg.Text("===ERR>:FIREBASE CSATLAKOZÁS SIKERTELEN(Lehet nincs internet/Firebase szerverek nem mennek?)===",  visible=False,key='-CSATLAKHIBA-',background_color='#e92d2d')],
        [sg.Text("===ERR>:FIREBASE ÍRÁS SIKERESTELEN(Lehet nem jó a függvénynév?)===",visible=False,key='-FIREBASeERROR-',background_color='#e92d2d')],
        [sg.Text("===ERR>:FIREBASE ÍRÁS SIKERESTELEN(Lehet nincs excel kiválasztva?)===",visible=False,key='-PATHERROR-',background_color='#e92d2d')],
        [sg.Text("===FIREBASE ÍRÁS SIKERES===",visible=False,key='-SUCCESS-',background_color='#5cd715')],
        [sg.Text("===FIREBASE SZERVEREK OK===",visible=False,key='-SUCCESSFB-',background_color='#5cd715')],
        [sg.Text("===INTERNET OK===",visible=False,key='-SUCCESSNET-',background_color='#5cd715')],
        [sg.Button("Bezár",key='-Close-',visible=False)],]
window= sg.Window('ExToFirebase', layout, size=(700,400),resizable=True,finalize=True)
if Connected==0 or firebaseConn==0:
    window['-CSATLAKHIBA-'].update(visible=True)
if Connected==1:
    window['-SUCCESSNET-'].update(visible=True)
if firebaseConn==1:
    window['-SUCCESSFB-'].update(visible=True)
while True:
   events,values = window.read()
   
   if events == "OK":
        nincsExcel=False
        excelfile_path = values["-IN-"]
        if excelfile_path== None or excelfile_path=="":
            nincsExcel=True
        CollName=values["-Coll-"]
        DocName=values["-Doc-"]
        Operation=values["-Operation-"]
        window['-SUCCESS-'].update(visible=False)
        window['-Close-'].update(visible=False)   
        window['-FIREBASeERROR-'].update(visible=False)
        window['-PATHERROR-'].update(visible=False)
        if nincsExcel==False: 
            df=pd.read_excel(excelfile_path)
        kepViseloNeve=''
        Hagyateknev=''
        letezofuggv=False
        Hagyateklakhely=''
        Hagyatekszuletett=''
        Hagyatekmeghalt=''
        Hagyatekfoglalkozasa=''
        Hagyatekmappa=''
        HatSzam=''
        Tipus=''
        sorszam=''
        sorszama=0
        if nincsExcel==False:
            osszesSorokSzama=df.shape[0]
        fuggvenyek=['GYERMEKVEDELEM','HAGYATEK']
        fuggvenylen=len(fuggvenyek)
        fuggvenysorszam=0
        Operation=Operation.upper()
        while fuggvenysorszam<fuggvenylen :
            if fuggvenyek[fuggvenysorszam] == Operation:
                letezofuggv=True
                break
            else: fuggvenysorszam+=1
        def createGyermekVedelem():
            db.collection(CollName).document(sorszam).set(
            {
                'Sorszam':sorszam,
                'Kepviselo':kepViseloNeve,
                'Hatarozatszam':HatSzam,
                'Tipus':Tipus

            }     
            )
        def createHagyatek():
            db.collection(CollName).document(sorszam).set(
                {
                    'nev':Hagyateknev,
                    'lakhely':Hagyateklakhely,
                    'szuletett':Hagyatekszuletett,
                    'meghalt':Hagyatekmeghalt,
                    'foglalkozasa':Hagyatekfoglalkozasa,
                    'mappa':Hagyatekmappa
                }
            )
        if Operation=='GYERMEKVEDELEM' and nincsExcel==False and letezofuggv == True:
            CollName='Gyermekvedelem'
            while sorszama<osszesSorokSzama:
                kepViseloNeve=df.iloc[sorszama,1]
                HatSzam=df.iloc[sorszama,2]
                Tipus=df.iloc[sorszama,3]
                sorszam=df.iloc[sorszama,0]
                sorszam='{0:g}'.format(sorszam)
                createGyermekVedelem()
                sorszama+=1
            window['-SUCCESS-'].update(visible=True)
            window['-Close-'].update(visible=True)
        if Operation=='HAGYATEK'  and nincsExcel==False and letezofuggv == True:
            CollName='HagyatekColl'
            while sorszama<osszesSorokSzama:
                sorszam=df.iloc[sorszama,0]
                Hagyateknev=df.iloc[sorszama,1]
                Hagyateklakhely=df.iloc[sorszama,2]
                Hagyatekszuletett=df.iloc[sorszama,3]
                Hagyatekmeghalt=df.iloc[sorszama,4]
                Hagyatekfoglalkozasa=df.iloc[sorszama,5]
                Hagyatekmappa=df.iloc[sorszama,6]
                sorszam='{0:g}'.format(sorszam)
                createHagyatek()
                sorszama+=1
            window['-SUCCESS-'].update(visible=True)
            window['-Close-'].update(visible=True)
        if nincsExcel==True:
            window['-PATHERROR-'].update(visible=True)
            window['-Close-'].update(visible=True)
        if letezofuggv == False:
            window['-FIREBASeERROR-'].update(visible=True)
   if events=='-Close-':
        exit()
   if events==sg.WIN_CLOSED:
        exit()