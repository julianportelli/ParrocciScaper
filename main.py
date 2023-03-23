from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime as dt
import os, datetime as dt
from pathlib import Path
import pandas as pd

"""
A district has many localities
A locality has many parrocci
There is a kappillan for each parrocca
Each parrocca has many Knisja
"""

"""
Variable set up
"""
#Data columns for output file
distrettCol = "Distrett"
lokalitaCol = "Lokalità"
parroccaCol = "Parroċċa"
knisjaNameCol = "Knisja"
tipTaKnisjaCol = "Tip ta' Knisja"
kappillanNameCol = "Kappillan"
personInChargeNameCol = "Person In charge"
personInChargeNruCol = "Nru"
personInChargeEmailCol = "E-mail"

df = pd.DataFrame(columns=[
    distrettCol,
    lokalitaCol,
    parroccaCol,
    knisjaNameCol,
    tipTaKnisjaCol,
    kappillanNameCol,
    personInChargeNameCol,
    personInChargeNruCol,
    personInChargeEmailCol
])

#Church type
knisjaParrokjali = 'Knisja Parrokkjali'
kappelliTalAdorazzjoni = 'Kappelli tal-Adorazzjoni'
knejjesUKappelliOhra = 'Knejjes u Kappelli Oħra'

churchTypes = [knisjaParrokjali, kappelliTalAdorazzjoni, knejjesUKappelliOhra]

# Caching directories
cacheParentDirectory = Path("HtmlCache")
cacheParrocciHTMLPath = cacheParentDirectory / "parrocci.html" 
cacheParroccaSubDirectory = cacheParentDirectory / "parrocca"
cacheKnisjaSubDirectory = cacheParentDirectory / "knisja"
root_site = "https://parrocci.knisja.mt/"

"""
Functions
"""
def getSiteBeautifulSoup(sourceHTMLfileURL: str):
    subfolderPath = sourceHTMLfileURL[sourceHTMLfileURL.rindex(root_site)+len(root_site):len(sourceHTMLfileURL)].strip().lower()

    html_result : str = None
    htmlPath : str = None
    soup : BeautifulSoup = None

    if "parrocci" in subfolderPath: # Parrocci index page
        htmlPath = cacheParrocciHTMLPath
    else:
        subfolderPath = subfolderPath[0:-1]
        htmlPath  = cacheParentDirectory / "{0}.html".format(subfolderPath)

    if os.path.exists(htmlPath):
        # Retrieve document from local cache
        with open(htmlPath, 'rb') as f:
            soup = BeautifulSoup(f.read(), 'lxml')
    else:
        # Retrieve document from URL, and save to cache
        response = requests.get(sourceHTMLfileURL)
        with open(Path(htmlPath), 'wb+') as f:
            f.write(response.content)
        
        soup = BeautifulSoup(response.text, 'html.parser')

    return soup

def saveToExcelFile(dataFrame, directoryPath):
    # Dataframe to Excel
    now = dt.datetime.now()
    dateAndTimeNow = now.strftime("%d-%m-%Y_%H-%M-%S")

    fileName = "Parrocci_{0}.xlsx".format(dateAndTimeNow)
    outputPath = directoryPath / fileName
    # Create 'Output' directory if it does not exist
    os.makedirs(os.path.dirname(outputPath), exist_ok=True)
    # Write dataframe to Excel file
    writer = pd.ExcelWriter(outputPath, engine='openpyxl')
    dataFrame.to_excel(writer, sheet_name='Parroċċi')
    writer.close()

"""
Main execution
"""
# Create HtmlCache directories if not exists
os.makedirs(cacheParentDirectory, exist_ok=True)
os.makedirs(cacheParroccaSubDirectory, exist_ok=True)
os.makedirs(cacheKnisjaSubDirectory, exist_ok=True)

# Extract site HTML
parrocciPage = root_site + "parrocci/"
parrocciDoc = getSiteBeautifulSoup(parrocciPage)

# Concentrate on localities
localitiesWrapperElem = parrocciDoc.find(class_="js-wpv-loop-wrapper").find(class_="tb-masonry")
print(localitiesWrapperElem.prettify())

# Get localities and loop
localityElems = localitiesWrapperElem.find_all(class_="tb-brick")
for localityElem in localityElems: # type: ResultSet
    localityHeading = localityElem.find(class_="tb-heading")
    localityLink = localityHeading.find('a')

    df_district = ""
    df_locality = localityLink.string # Unique, E.g. Ħ’Attard

    # Get website of parrocca contents to get information
    parroccaDoc = getSiteBeautifulSoup(localityLink['href'].strip())

    parroccaDocTopSection = parroccaDoc.find('article').find(class_="entry-content-post")
    df_parroccaName = parroccaDocTopSection.find(class_="tb-heading").string

    # Remove top section to get kappillan details
    parroccaDocTopSection.find(class_="wp-block-columns").decompose()

    kappillanDetailsElements = parroccaDoc.find_all(class_="tb-fields-and-text")

    df_parroccaMainKappillanName = kappillanDetailsElements[0].contents[-1].find("strong").string.strip()
    df_parroccaMainKappillanEmail = kappillanDetailsElements[1].contents[-1].find("strong").find("a")['title'] if len(kappillanDetailsElements[1].contents) > 0 else ""
    df_parroccaMainKappillanNumber = kappillanDetailsElements[2].contents[-1].find("strong").string.strip() if len(kappillanDetailsElements[2].contents) > 0 else ""
    
    # Knisja parrokjali
    knisjaParrokjaliElement = parroccaDoc.find(class_="wpv-view-output") # The Knisja link is in the first wpv-view-output element

    knisjaParrokjaliLink = knisjaParrokjaliElement.find(class_="wp-block-toolset-views-view-editor").find(class_="js-wpv-view-layout").find(class_="js-wpv-loop-wrapper").find(class_="wp-block-toolset-views-view-template-block").find(class_="tb-heading").find("a")

    df_knisjaName = knisjaParrokjaliLink.string.strip()

    # Set person in charge for Knisja parrokjali
    df_tipTaKnijsa = knisjaParrokjali
    df_personInChargeName = df_parroccaMainKappillanName
    df_personInChargeNumber = df_parroccaMainKappillanNumber
    df_personInChargeEmail = df_parroccaMainKappillanEmail
    
    # Remove from document
    knisjaParrokjaliElement.decompose()

    # Remove next wpv-view-output as it is empty
    parroccaDoc.find(class_="wpv-view-output").decompose()

    def addRowToDataframe():
        newRow = {
            distrettCol: df_district,
            lokalitaCol: df_locality,
            parroccaCol: df_parroccaName,
            knisjaNameCol: df_knisjaName,
            tipTaKnisjaCol: df_tipTaKnijsa,
            kappillanNameCol: df_parroccaMainKappillanName,
            personInChargeNameCol: df_personInChargeName,
            personInChargeNruCol: df_personInChargeNumber,
            personInChargeEmailCol: df_personInChargeEmail
        }
        df.loc[len(df)] = newRow

    # Add Knisja Parrokjali to dataframe
    addRowToDataframe()
    
    # Kappelli tal-Adorazzjoni
    df_tipTaKnijsa = kappelliTalAdorazzjoni
    kappelliTalAdorazzjoniElems = parroccaDoc.find(class_="wpv-view-output").find(class_="wp-block-toolset-views-view-editor").find(class_="js-wpv-view-layout")
    
    if not kappelliTalAdorazzjoniElems.find_all("div", string="No items found", recursive=False):
        kappelliTalAdorazzjoniElems = kappelliTalAdorazzjoniElems.find(class_="js-wpv-loop-wrapper").find(class_="tb-masonry").find_all(class_="tb-brick")

        for kappelliTalAdorazzjoniElem in kappelliTalAdorazzjoniElems:
            kappelliTalAdorazzjoniElemLink = kappelliTalAdorazzjoniElem.find(class_="tb-brick__content").find(class_="wp-block-toolset-views-view-template-block").find(class_="tb-heading").find("a")
            
            df_knisjaName = kappelliTalAdorazzjoniElemLink.string.strip()
            # kappellaTalAdorazzjoniDoc = getSiteBeautifulSoup(kappelliTalAdorazzjoniElemLink['href'])
            df_personInChargeName = ""
            df_personInChargeNumber = ""
            df_personInChargeEmail = ""

            # Add Kappella tal-Adorazzjona to dataframe
            addRowToDataframe()

    parroccaDoc.find(class_="wpv-view-output").decompose()

    # Knejjes u Kappelli Oħra
    df_tipTaKnijsa = knejjesUKappelliOhra
    knejjesUKappelliOhraElems = parroccaDoc.find(class_="wpv-view-output").find(class_="wp-block-toolset-views-view-editor").find(class_="js-wpv-view-layout")
    
    if not knejjesUKappelliOhraElems.find_all("div", string="No items found", recursive=False):
       knejjesUKappelliOhraElems = knejjesUKappelliOhraElems.find(class_="js-wpv-loop-wrapper").find(class_="tb-grid").find_all(class_="tb-grid-column")
       for knejjesUKappelliOhraElem in knejjesUKappelliOhraElems:
        knejjesUKappelliOhraElemLink = knejjesUKappelliOhraElem.find(class_="wp-block-toolset-views-view-template-block").find(class_="tb-heading").find("a")

        df_knisjaName = knejjesUKappelliOhraElemLink.string.strip()

        knejjesUKappelliOhraDoc = getSiteBeautifulSoup(knejjesUKappelliOhraElemLink['href'])

        personInChargeSection = knejjesUKappelliOhraDoc.find("article").find(class_="entry-content-post").find(class_="tb-fields-and-text", recursive=False)
        
        lengthOfPersonInChargeSection = len(personInChargeSection.contents[0].contents)
        personInChargeContents = personInChargeSection.contents[0].contents

        if lengthOfPersonInChargeSection == 1:
            df_personInChargeName = ""
            df_personInChargeNumber = ""
        elif lengthOfPersonInChargeSection == 3:
            df_personInChargeName = personInChargeContents[1].string.strip()
            df_personInChargeNumber = ""
        elif lengthOfPersonInChargeSection == 5:
            df_personInChargeName = personInChargeContents[1].string.strip()
            df_personInChargeNumber = personInChargeContents[4].string.strip()

        addRowToDataframe()

# Save to output file
saveToExcelFile(df, Path("Output"))