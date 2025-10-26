from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.ess.gov.si/",
    "Origin": "https://www.ess.gov.si",
    "Content-Type": "application/json",
    "Accept-Language": "sl-SI,sl;q=0.9,en-GB;q=0.8,en;q=0.7",
}

def get_jobs_id():
    """
        Fetch today's job basic info
        INPUT: /
        OUTPUT: list of jobs id and titles

    """
    url = "https://apigateway-osk8sdmz.ess.gov.si/iskalnik-po-pdm/" \
           "v1/delovno-mesto/prosta-delovna-mesta-filtri"

    params = {
        "user_key": "5ab0803785c1c97d8e3331d671fcbaa9"
    }

    payload = {
        "nazivDelovnegaMesta": "",
        "lokacija": "",
        "drzave": ["SI", ""],
        "datumObjave": "THIS_WEEK",
        "delovniCas": "",
        "jeziki": [],
        "podrocjaIzobrazbe": [],
        "poklicnaPodrocja": ["0020", ""],
        "ravniIzobrazbe": [],
        "referenceDelodajalca": [],
        "regije": ["Osrednjeslovenska", ""],
        "stZadetkov": 30,
        "stran": 1,
        "urejevalniPojem": 0,
        "urnikDela": [],
        "vrniFiltre": True
    }

    response = requests.post(url, headers=headers, params=params, json=payload)

    print("Status code:", response.status_code)

    # Get jobs id and titles
    jobs_id = []
    titles = []
    if response.status_code == 200:
        data = response.json()
        for job in data.get("seznamDelovnihMest", []):
            jobs_id.append(job.get("idDelovnoMesto"))
            titles.append(data.get("nazivDelovnegaMesta"))
            #print(job)
    else:
        print("Failed:", response.text)
    #print(jobs_id)
    
    return jobs_id, titles

def get_job_info(job_id):
    """
        Fetch today's job comprehensive info
        INPUT: job id
        OUTPUT: job description and location

    """
    api_key = "5ab0803785c1c97d8e3331d671fcbaa9"

    url = "https://apigateway-osk8sdmz.ess.gov.si/iskalnik-po-pdm/" \
          "v1/delovno-mesto/podrobnosti-prosto-delovno-mesto"
    
    params = {
        "idDelovnoMesto": job_id,
        "user_key": api_key
    }

    response = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"[{job_id}] Status:", response.status_code)
    
    if not response.text.strip():
        print(f"[{job_id}] has empty response.")
    else:
        data = response.json()

        description = data.get("opisDelInNalog")
        location = f"{data.get("delodajalec")}, {data.get("delodajalecNaslov")}"

        return (description, location)

def scrap_ZRSZZ(inserted_func, to_lower):
    jobs_id, titles = get_jobs_id()

    for i in range(0, len(jobs_id)):
        description, location = get_job_info(jobs_id[i])
        inserted_func(to_lower(titles[i]),to_lower(location),to_lower((description)))

# Example
"""
get_jobs_id:
{'idDelovnoMesto': '3349316', 
'nazivDelovnegaMesta': 'SISTEMSKI ADMINISTRATOR VII/2 (I) V SLUŽBI ZA INFORMACIJSKO TEHNOLOGIJO NA TAJNIŠTVU UL MEDICINSKE FAKULTETE - M/Ž', 
'delodajalec': 'UNIVERZA V LJUBLJANI, MEDICINSKA FAKULTETA', 
'krajDM': 'LJUBLJANA', 
'trajanjeZaposlitve': 'Nedoločen čas', 
'delovniCas': '40 ur/teden', 
'ravenIzobrazbe': 'visokošolska 2.stopnje, visokošolska univerzitetna (prejšnja) ipd.', 
'datumObjave': '2025-10-24T00:00:00+02:00', 
'ikonaReferenca': 'NE', 
'zrszNapotovanje': 'NE', 
'topNapovedi': 'NE', 
'poklicniBarometer': 'ravnovesje', 
'poklicniBarometer1': 2, 
'poklic': 'Sistemski administratorji', 
'datumSpremembe': '2025-10-24T11:08:00+02:00', 
'ikonaNegativnaReferenca': 'NE'}

get_job_info:
{'idDelovnoMesto': '3348232', 
'registerskaStevilka': 'PX38740', 
'steviloOgledov': 73, 
'opisDelInNalog': 'SWARMCHESTRATE:  - PRIPRAVA IN DOKUMENTIRANJE POSTOPKOV ZA SKLADNOST Z VARSTVOM PODATKOV IN ZASEBNOSTJO (GDPR, EIDAS 2.0) ZA SISTEM UPRAVLJANJA ZAUPANJA.  - PRISPEVANJE K PERIODIČNIM POROČILOM IN REZULTATOM, KI POVZEMAJO PRAVNE, ETIČNE IN UPRAVLJAVSKE VIDIKE SISTEMA ZAUPANJA.  - PRIPRAVA NOTRANJIH POLITIK IN SMERNIC ZA IZDAJO, PREVERJANJE IN PREKLIC DECENTRALIZIRANIH IDENTITET.  - KOORDINACIJA PRAVNIH IN ETIČNIH PREGLEDOV, POVEZANIH Z UPRAVLJANJEM IDENTITET NA OSNOVI VERIŽENJA BLOKOV.  - POMOČ PRI ZBIRANJU IN ORGANIZACIJI PRAVNIH IN REGULATIVNIH ZAHTEV ZA VARSTVO PODATKOV (NPR. SKLADNOST Z GDPR).   EXTREMEXP:  - KOORDINACIJA IN SPREMLJANJE AKTIVNOSTI, POVEZANIH Z RAZVOJEM APLIKACIJSKIH PROGRAMSKIH VMESNIKOV TER PRIPRAVA USTREZNE PROJEKTNE DOKUMENTACIJE.  - POMOČ PRI ADMINISTRATIVNEM SPREMLJANJU AKTIVNOSTI STOHASTIČNEGA MODELIRANJA V OKVIRU DELOVNEGA PAKETA 2 (WP2), VKLJUČNO Z ZBIRANJEM PODATKOV IN PRIPRAVO POROČIL O NAPREDKU.  - ARHIVIRANJE, VODENJE EVIDENCE IN ZAGOTAVLJANJE SKLADNOSTI DOKUMENTACIJE Z INTERNIMI POSTOPKI.  KANDIDATI NAJ V PROŠNJI PRILOŽIJO: - ŽIVLJENJEPIS, - DOKAZILO O IZOBRAZBI.  PRIJAVO S PRILOGAMI KANDIDATI POŠLJEJO NA ELEKTRONSKI NASLOV KADROVSKA@FRI.UNI-LJ.SI Z OBVEZNIM PRIPISOM: »SDVD LPT_IME PRIIMEK«.  UL FRI SI PRIDRŽUJE PRAVICO, DA V SKLADU Z POGODBENO SVOBODO PO 24. ČLENU ZDR-1 KANDIDATA NE IZBERE, NAVKLJUB TEMU, DA IZPOLNJUJE POGOJE. UL FRI SI PRIDRUŽUJE PRAVICO, DA NE ZAPOLNI VSEH RAZPISANIH DELOVNIH MEST', 'trajanjeZaposlitve': 'določen čas  oz. predvidoma od 1. 1. 2026 do 31. 12. 2026', 
'poskusnoDelo': '3 mes.', 
'delovniCas': '40 ur/teden', 
'urnikDela': '', 'okvirnaPlaca': '', 
'izobrazba': 'višješolska (prejšnja), višja strokovna; Načrtovanje in administracija podatkovnih baz in računalniških omrežij', 
'alternativnaIzobrazba': 'visokošolska 1.stopnje, visokošolska strokovna (prejšnja) ipd., Načrtovanje in administracija podatkovnih baz in računalniških omrežij', 'nacionalnaPoklicnaKvalifikacija': '', 
'delovneIzkusnje': 'ni zahtevano', 
'vozniskoDovoljenje': '', 
'znanjeJezikov': '', 'racunalniskaZnanja': '', 
'nacinPrijaveKandidata': 'kandidati naj pošljejo vlogo po e-pošti', 
'kontaktZaKandidata': {'kontaktnaOseba': 'LEA SEDEVČIČ', 'telefon': '01 479 8012', 'eNaslov': 'kadrovska@fri.uni-lj.si', 'naslov': 'Večna pot 113 , 1000 LJUBLJANA', 'koncesionar': ''}, 
'objavaKraj': 'LJUBLJANA', 
'drugiPogoji': 'znanje enega svetovnega jezika, znanje uporabe računalniških programov, komunikacijske spretnosti, organizacijske sposobnosti. Prednost pri izbiri bodo imeli kandidati z ustreznimi delovnimi izkušnjami. Kandidati naj v prošnji priložijo: življenjepis, dokazilo o izobrazbi.  Prijavo s prilogami kandidati pošljejo na elektronski naslov kadrovska@fri.uni-lj.si z obveznim pripisom: &quot;SDVD LPT_ime priimek&quot', 
'ostalo': '', 
'nazivDelovnegaMesta': 'STROKOVNI DELAVEC V VISOKOŠOLSKI DEJAVNOSTI VII/1-II (ŠIFRA DM: D057004) V LABORATORIJU ZA PODATKOVNE TEHNOLOGIJE - M/Ž', 
'delodajalec': 'UNIVERZA V LJUBLJANI, FAKULTETA ZA RAČUNALNIŠTVO IN INFORMATIKO, LJUBLJANA', 
'delodajalecNaslov': 'Večna pot 113 , 1000 LJUBLJANA', 
'idSubjekta': 311461, 
'upravnaEnota': 'LJUBLJANA', '
steviloDelovnihMest': '1', 
'datumObjave': '22. 10. 2025', 
'prijavaDo': '27. 10. 2025'}
"""