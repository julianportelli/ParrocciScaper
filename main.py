from bs4 import BeautifulSoup
import pandas as pd
import requests

# Setting up

# A district has many localities
# A locality has many parrocci
# There is a kappillan for each parrocca
df = pd.DataFrame(columns=[
    "Distrett",
    "Lokalità",
    "Parroċċa",
    "Knisja",
    "Tip ta' Knisja"
    "Kappillan",
    "Person In charge",
    "Nru",
    "E-mail"
])

knisjaParrokjali = 'Knisja Parrokkjali'
kappelliTalAdorazzjoni = 'Kappelli tal-Adorazzjoni'
knessjesUKappelliOhra = 'Knejjes u Kappelli Oħra'

churchTypes = [knisjaParrokjali, kappelliTalAdorazzjoni,knessjesUKappelliOhra]

def getSiteBeautifulSoup(url):
    html_result = requests.get(url).text
    bs = BeautifulSoup(html_result, 'html.parser')
    return bs

# Extract site
root_site = "https://parrocci.knisja.mt/parrocci/"
doc = getSiteBeautifulSoup(root_site)

# Concentrate on localities
localitiesWrapperElem = doc.find(class_="js-wpv-loop-wrapper").find(class_="tb-masonry")
print(localitiesWrapperElem.prettify())

# Get localities and loop
localityElems = localitiesWrapperElem.find_all(class_="tb-brick")
for localityElem in localityElems: # type: ResultSet
    localityHeading = localityElem.find(class_="tb-heading")
    localityLink = localityHeading.find('a')

    df_district = ""
    df_locality = localityLink.string # Unique, E.g. Ħ’Attard

    # Get website of parrocca contents to get information
    parroccaDoc = getSiteBeautifulSoup(localityLink['href'])

    parroccaDocTopSection = parroccaDoc.find('article').find(class_="entry-content-post")
    parroccaName = parroccaDocTopSection.find(class_="tb-heading")

    # Remove top section to get kappillan details
    parroccaDocTopSection.find(class_="wp-block-columns").decompose()

    kappillanDetailsElements = parroccaDoc.find_all(class_="tb-fields-and-text")

    parroccaMainKappillanName = kappillanDetailsElements[0].contents[-1].find("strong").string
    parroccaMainKappillanNumber = kappillanDetailsElements[2].contents[-1].find("strong").string
    
    # Knisja parrokjali
    