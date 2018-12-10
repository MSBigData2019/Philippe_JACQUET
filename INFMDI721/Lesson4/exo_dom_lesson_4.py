###########################################################################################

import re
import json
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

###########################################################################################

def get_page_url(brand, model, regions, page):
    
    regions_suffix = "FR-" + "%2CFR-".join(regions)     
    
    url = f"https://www.lacentrale.fr/listing?makesModelsCommercialNames={brand}%3A{model}&options=&page={page}" +\
                    f"&regions={regions_suffix}"
    return url

###########################################################################################

def get_pages_number(brand, model, regions, headers):
    
    url = get_page_url(brand, model, regions, 1)
    res = requests.get(url, headers=headers);
    
    if res.status_code == 200:
   
        html_doc =  res.text;
        soup = BeautifulSoup(html_doc,"html.parser");
        ads_number = soup.find("span", class_="numAnn").text;
        pages_number = int(np.ceil(int(ads_number)/16))
        
    return pages_number

###########################################################################################

def get_ads_links_for_page(brand, model, regions, headers, page_number):
    
    ad_links = []
    
    url = get_page_url(brand, model, regions, page_number)
    res = requests.get(url, headers=headers)
    
    if res.status_code == 200:
        
        soup = BeautifulSoup(res.text,"html.parser");
        ad_links += list(map(lambda x : x["href"], soup.findAll('a', class_= "linkAd ann")));
        ad_links += list(map(lambda x : x["href"], soup.findAll('a', class_= "linkAd annJB")));
        
    return ad_links

###########################################################################################

def get_ad_infos(ad_link, headers):
    
    ad_infos = []
    
    site_prefix = "https://www.lacentrale.fr/";
    
    res = requests.get(site_prefix + ad_link, headers=headers);
    
    if res.status_code == 200:
        
        soup = BeautifulSoup(res.text,"html.parser");
        general_infos_table = soup.find("ul", class_ = "infoGeneraleTxt column2");
        table_lines = general_infos_table.findChildren("li");
        model = soup.find("h3", class_="mL20 clearPhone").find("span").text.strip()[2:];
        year = table_lines[0].find("span").text;
        mileage = re.sub("[^0-9]", "", table_lines[1].find("span").text);
        price = re.sub("[^0-9]", "", soup.find("strong", class_ = re.compile(r"sizeD lH35 inlineBlock vMiddle.*"))\
                       .text.strip());
        phone_number = re.sub("[^0-9]", "", soup.find("div", class_="phoneNumber1").text);
        seller_type = soup.find("div", class_="bold italic mB10").text.strip().split(" ")[0];
        department = re.sub("[^0-9]", "", soup.find("h3", class_="mB10 noBold").findAll("div")[1].text)
        argus_price = get_argus_price(year, mileage, department, model, headers)

        ad_infos = [model, year, mileage, price, phone_number, seller_type, department, argus_price]
        
        return ad_infos
    
###########################################################################################

def get_argus_price(year, mileage, department, model, headers):
    
    site_prefix = "https://www.lacentrale.fr/"
    
    model_short = re.search('life|zen|intens', model, re.IGNORECASE)[0].lower()
    
    url = f"https://www.lacentrale.fr/cote-voitures-renault-zoe--{year}-.html"

    res = requests.get(url, headers=headers);

    if res.status_code == 200:

        soup = BeautifulSoup(res.text,"html.parser");
        cote_links = soup.findAll("div", class_ = "listingResultLine auto sizeA")
        cote_links = list(map(lambda x : x.findChild("a")["href"], cote_links))

        referer = ""
        
        for cote_link in cote_links:
            if re.search(model_short, cote_link, re.IGNORECASE):
                referer = site_prefix + cote_link
                break
        
    url = f"https://www.lacentrale.fr/get_co_prox.php?km={mileage}&zipcode={department}000&month=01&year={year}"

    headers["Referer"] = referer

    res = requests.get(url, headers=headers);

    cote = 0
    
    if res.status_code == 200:
        json_content = json.loads(res.text);
        if "cote_perso" in json_content:
            cote = json_content["cote_perso"] 
        
    return cote

###########################################################################################

if __name__ == '__main__':

    brand = "RENAULT"
    model = "ZOE"
    regions = ["IDF", "PAC", "NAQ"]

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection":"keep-alive",  
        "Cookie" : "__uzma=5bdf838a7f2a38.51491685; __uzmb=1541374858; __uzmc=1216062279510; __uzmd=1544292389; __ssds=2; cikneeto_uuid=id:3fccd5ec-908b-4113-ba8c-8dbb5489c385; atidvisitor=%7B%22name%22%3A%22atidvisitor%22%2C%22val%22%3A%7B%22vrn%22%3A%22-251312-%22%2C%22at%22%3A%22undefined%22%2C%22ac%22%3A%22%22%7D%2C%22options%22%3A%7B%22path%22%3A%22%2F%22%2C%22session%22%3A15724800%2C%22end%22%3A15724800%7D%7D; __ssuzjsr2=a9be0cd8e; __uzmaj2=958e739e-10e1-4aa0-9d9c-d66ea90d2e426150; __uzmbj2=1541374957; __uzmcj2=2034437633539; __uzmdj2=1544292188; lc_layout=list; lc_pageSize=16; consulted_offers=299ceb719c6012d1da79bb1367bce507; euconsent=BOWu1HIOWu1HICRBPAFRBX6AAAAeQAAAAQgABAAAAGAARgAAACgAAAgAAAAAABACAAAAAAABCAAgAAAAAIAAAAQAAABABIAAAEAAAAAAAAAAAIA; pubconsent=BOWu1HIOWu1HICRBXAB6AAAE4A; __trossion=1541376229_1800_7_b3d28cf7-5f96-4ebb-850e-9a8b6fa5a6a5%3A1544113218_b3d28cf7-5f96-4ebb-850e-9a8b6fa5a6a5%3A1544291854_1544292192_2; __troRUID=b3d28cf7-5f96-4ebb-850e-9a8b6fa5a6a5; __sonar=11431219853078346113; _mob_=0; retargeting_data=B; user_type=acheteur; php_sessid=62ac967a679b040643b6592b9e66661d; cikneeto=date:1544292201751; __troSYNC=1",
        "Host": "www.lacentrale.fr",    
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0",
    }

    page_numbers = get_pages_number(brand, model, regions, headers)
    ad_links = get_ads_links_for_page(brand, model, regions, headers, 1)
    data = list(map(lambda link : get_ad_infos(link, headers), ad_links))
    df = pd.DataFrame(data, columns=['Modèle', 'Année', 'Kilométrage', 'Prix', 'Téléphone', "Type de vendeur",\
                                        'Département', 'Argus'])

    df[["Kilométrage", "Prix", "Argus"]] = df[["Kilométrage", "Prix", "Argus"]].apply(pd.to_numeric)
    df["Diff prix"] = df["Prix"] - df["Argus"]
    print(df)
    
###########################################################################################
