import requests
import pandas as pd
import numpy as np

path = r"C:/Users/felix/Dropbox/python_projects/OpenAlex/Output" # set Path
email = "" # add your email for quick response times
endpoint = 'works'
## iso 2 letter country codes ##
iso_country_codes = ["AF", "AX", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR",
"AM", "AW", "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY", "BE",
"BZ", "BJ", "BM", "BT", "BO", "BQ", "BA", "BW", "BV", "BR", "IO",
"BN", "BG", "BF", "BI", "CV", "KH", "CM", "CA", "KY", "CF", "TD",
"CL", "CN", "CX", "CC", "CO", "KM", "CG", "CD", "CK", "CR", "CI",
"HR", "CU", "CW", "CY", "CZ", "DK", "DJ", "DM", "DO", "EC", "EG",
"SV", "GQ", "ER", "EE", "ET", "FK", "FO", "FJ", "FI", "FR", "GF",
"PF", "TF", "GA", "GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD",
"GP", "GU", "GT", "GG", "GN", "GW", "GY", "HT", "HM", "VA", "HN",
"HK", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT",
"JM", "JP", "JE", "JO", "KZ", "KE", "KI", "KP", "KR", "KW", "KG",
"LA", "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO", "MK",
"MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ", "MR", "MU", "YT",
"MX", "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM", "NA",
"NR", "NP", "NL", "NC", "NZ", "NI", "NE", "NG", "NU", "NF", "MP",
"NO", "OM", "PK", "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN",
"PL", "PT", "PR", "QA", "RE", "RO", "RU", "RW", "BL", "SH", "KN",
"LC", "MF", "PM", "VC", "WS", "SM", "ST", "SA", "SN", "RS", "SC",
"SL", "SG", "SX", "SK", "SI", "SB", "SO", "ZA", "GS", "SS", "ES",
"LK", "SD", "SR", "SJ", "SZ", "SE", "CH", "SY", "TW", "TJ", "TZ",
"TH", "TL", "TG", "TK", "TO", "TT", "TN", "TR", "TM", "TC", "TV",
"UG", "UA", "AE", "GB", "US", "UM", "UY", "UZ", "VU", "VE", "VN",
"VG", "VI", "WF", "EH", "YE", "ZM", "ZW"]

# calls the openalex api to get the number of papers that have only affiliations in 1 country and number of papers that have affiliations in >1 one country
def get_total_national_international_papers(): # national papers = 1 distinct country, international papers > 1 distinct countries
    total_national_international_papers = pd.DataFrame(columns=["national_papers", "international_papers"],index=range(1900,2024))
    year = 1900
    while year < 2024:
        for number_of_countries in ["1", ">1"]:
            filters = ",".join((
                f'publication_year:{year}',
                f'countries_distinct_count:{number_of_countries}',
                ))
            filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}'
            
            r = requests.get(filtered_works_url)
            try:
                results = r.json()
                if number_of_countries == "1":
                    total_national_international_papers["national_papers"][year] = results['meta']['count']
                else:
                    total_national_international_papers["international_papers"][year] = results['meta']['count']
                print(year)
            except:
                year -= 1 # repeats the year, where an error occured
                print("repeating year")
                break
        year += 1
    total_national_international_papers["country_code"] = "Gesamt"
    total_national_international_papers.to_excel(f"{path}/total_national_international_papers.xlsx")

## we need to check for a given year from 1900 to 2023 if a given country has a paper count >0 ##
def paper_count():
    exceptions = []
    years = range(1900,2024)
    total_papers = pd.DataFrame(columns=iso_country_codes,index=years)
    for country_code in iso_country_codes:
        for year in years:
            filters = ",".join((
                f'publication_year:{year}',
                f'institutions.country_code:{country_code}',
            ))
            filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}'
            
            r = requests.get(filtered_works_url)
            try:
                results = r.json()
                total_papers[country_code][year] = results['meta']['count']
                print(f"{country_code},{year}")
            except:
                exceptions.append(filtered_works_url)
    total_papers.to_excel(f"{path}/total_papers.xlsx")
    print(exceptions)

def remove_countries():
    '''remove countries with 0 papers'''
    total_papers = pd.read_excel(f"{path}/total_papers.xlsx", index_col=0)
    for country_code in iso_country_codes:
        total_papers.loc[(total_papers[country_code] < 1), country_code] = np.NaN
    total_papers.to_excel(f"{path}/total_papers_removed_countries.xlsx")

def wide_to_long_format_total():
    total_papers = pd.read_excel(f"{path}/total_papers_removed_countries.xlsx", index_col=0)
    total_papers = total_papers.T
    total_papers = total_papers.reset_index()
    total_papers = total_papers.rename(columns={"index": "country_code"})
    total_papers_long = pd.melt(total_papers, id_vars=['country_code'])
    total_papers_long = total_papers_long.rename(columns={"variable": "year", "value": "paper_count"})
    total_papers_long = total_papers_long.dropna(subset=["paper_count"]).reset_index(drop=True) #
    print(total_papers_long)
    total_papers_long.to_excel(f"{path}/total_papers_long.xlsx")


def get_amount_of_national_papers_new(): # gets amount of papers of a country with only home coauthors (national papers)
    total_papers = pd.read_excel(f"{path}/total_papers_removed_countries.xlsx", index_col=0)
    national_papers = pd.DataFrame(columns=iso_country_codes,index=range(1900,2024))
    email = "Felix.Radde@campus.lmu.de"
    exceptions = []
    year = 1995 # start year
    while year < 2024:
        papers_year = total_papers.loc[year].copy()
        papers_year.dropna(inplace=True)
        # print(len(papers_year.index.to_list()))
        for country_code in papers_year.index.to_list():
            filters = ",".join((
                f'publication_year:{year}',
                # 'has_raw_affiliation_string:true',
                f'institutions.country_code:{country_code}',
                # 'institutions.type:education',
            ))
            other_countries_str1 = ""
            other_countries_str2 = ""
            other_countries_str3 = ""
            other_countries_str4 = ""
            other_countries_str5 = ""
            count1 = 0
            count2 = 0
            count3 = 0
            count4 = 0
            count5 = 0
            for other_country in papers_year.index.to_list(): # institutions.country_code can each contain at most 50 conditions, therefore we need more than one institutions.country_code
                if other_country == country_code:
                    continue
                if count1 < 50:
                    if other_countries_str1 == "":
                        other_countries_str1 = f'institutions.country_code:!{other_country}'
                        count1 = 1
                    else:
                        other_countries_str1 = "+".join((other_countries_str1,f'!{other_country}',))
                        count1 += 1
                        if count1 == 50:
                            continue
                if count1 >= 50 and count2 < 50:
                    if other_countries_str2 == "":
                        other_countries_str2 = f'institutions.country_code:!{other_country}'
                        count2 = 1
                    else:
                        other_countries_str2 = "+".join((other_countries_str2,f'!{other_country}',))
                        count2 += 1
                        if count2 == 50:
                            continue                                     
                if count1 >= 50 and count2 >= 50 and count3 < 50:
                    if other_countries_str3 == "":
                        other_countries_str3 = f'institutions.country_code:!{other_country}'
                        count3 = 1
                    else:
                        other_countries_str3 = "+".join((other_countries_str3,f'!{other_country}',))
                        count3 += 1
                        if count3 == 50:
                            continue        
                if count1 >= 50 and count2 >= 50 and count3 >= 50 and count4 < 50:
                    if other_countries_str4 == "":
                        other_countries_str4 = f'institutions.country_code:!{other_country}'
                        count4 = 1
                    else:
                        other_countries_str4 = "+".join((other_countries_str4,f'!{other_country}',))
                        count4 += 1
                        if count4 == 50:
                            continue  
                if count1 >= 50 and count2 >= 50 and count3 >= 50 and count4 >= 50 and count5 < 50:
                    if other_countries_str5 == "":
                        other_countries_str5 = f'institutions.country_code:!{other_country}'
                        count5 = 1
                    else:
                        other_countries_str5 = "+".join((other_countries_str5,f'!{other_country}',))
                        count5 += 1
                        if count5 == 50:
                            continue
            if len(other_countries_str2) > 0:
                if len(other_countries_str3) > 0:
                    if len(other_countries_str4) > 0:
                        if len(other_countries_str5) > 0:
                            filters = ",".join((filters,other_countries_str1,other_countries_str2,other_countries_str3,other_countries_str4,other_countries_str5))
                        else:
                            filters = ",".join((filters,other_countries_str1,other_countries_str2,other_countries_str3,other_countries_str4))
                    else:
                        filters = ",".join((filters,other_countries_str1,other_countries_str2,other_countries_str3))
                else:
                    filters = ",".join((filters,other_countries_str1,other_countries_str2))
            else:
                filters = ",".join((filters,other_countries_str1))

            filtered_works_url = f'https://api.openalex.org/works?filter={filters}&mailto={email}'

            
            try: 
                r = requests.get(filtered_works_url)
                results = r.json()
                national_papers[country_code][year] = results['meta']['count']
                print(f"{country_code},{year}")
            except: # if some api error happens this simply repeats the process for the same year by substracting 1 year and breaking the country loop
                year -= 1
                exceptions.append(filtered_works_url)
                print(filtered_works_url)
                break
        year += 1


    national_papers.to_excel(f"{path}/national_papers1.xlsx")
    with open(f'{path}/exceptions.txt', 'w') as f:
        for line in exceptions:
            f.write(f"{line}\n")

def wide_to_long_format_national():
    national_papers = pd.read_excel(f"{path}/national_papers.xlsx", index_col=0)
    national_papers = national_papers.T
    national_papers = national_papers.reset_index()
    national_papers = national_papers.rename(columns={"index": "country_code"})
    national_papers_long = pd.melt(national_papers, id_vars=['country_code'])
    national_papers_long = national_papers_long.rename(columns={"variable": "year", "value": "national_papers"})
    national_papers_long = national_papers_long.dropna(subset=["national_papers"]).reset_index(drop=True) #
    print(national_papers_long)
    national_papers_long.to_excel(f"{path}/national_papers_long.xlsx")

def merge_total_national_papers():
    total_papers_long = pd.read_excel(f"{path}/total_papers_long.xlsx", index_col=0)
    national_papers_long = pd.read_excel(f"{path}/national_papers_long.xlsx", index_col=0)
    total_national_international_papers = pd.read_excel(f"{path}/total_national_international_papers.xlsx", index_col=0)
    total_national_international_papers.reset_index(inplace=True)
    total_national_international_papers["paper_count"] = total_national_international_papers["national_papers"] + total_national_international_papers["international_papers"]
    merged_df = pd.merge(left=total_papers_long, right=national_papers_long,how="left",on=["country_code","year"])
    # calculate international papers
    merged_df["international_papers"] = merged_df["paper_count"] - merged_df["national_papers"]
    merged_df = merged_df.loc[merged_df["international_papers"] > 1, :]
    merged_df = pd.concat([merged_df,total_national_international_papers])
    merged_df.reset_index(drop=True,inplace=True)
    merged_df["international_paper_rate"] = merged_df["international_papers"]/merged_df["paper_count"]
    merged_df["international_papers_3yr_avg"] = merged_df.sort_values(['country_code','year']).groupby('country_code').international_papers.rolling(3, center=True).mean().reset_index(level=0,drop=True)
    merged_df["paper_count_3yr_avg"] = merged_df.sort_values(['country_code','year']).groupby('country_code').paper_count.rolling(3, center=True).mean().reset_index(level=0,drop=True)
    merged_df.sort_values(['country_code','year'],inplace=True)
    merged_df.reset_index(drop=True,inplace=True)
    merged_df.to_excel(f"{path}/merged_total_national_papers.xlsx")



def data_for_continents_chord_diagram_2019():
    year = 2019
    continents = ["Q46", "Q49", "Q18", "Q48", "Q55643", "Q15"]

    flows_between_continents = pd.DataFrame(index=continents,columns=continents)
    flows_between_continents.columns.name = "Dimension"

    for continent in continents:
        filters = ",".join((
            f'publication_year:{year}',
            f'institutions.continent:{continent}',
            ))
            
        filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}&group-by=institutions.continent'
        print(filtered_works_url)
        r = requests.get(filtered_works_url)
        results = r.json()
        counter = 0
        while counter < 7:
            if results["group_by"][counter]["key"] in [continent, "unknown", "Q51"]:
                counter += 1
                continue
            flows_between_continents[results["group_by"][counter]["key"]][continent] = results["group_by"][counter]["count"]
            counter += 1
        other_continents_str = ""
        for other_continents in continents:
            if continent == other_continents:
                continue
            elif other_continents_str == "":
                other_continents_str = f"!{other_continents}"
            other_continents_str = "".join((other_continents_str,f"+!{other_continents}"))
        filters = ",".join((filters,f"institutions.continent:{other_continents_str}"))
        filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}&group-by=institutions.continent'
        r = requests.get(filtered_works_url)
        results = r.json()
        counter = 0
        while counter < 7:
            if results["group_by"][counter]["key"] == continent:
                flows_between_continents[results["group_by"][counter]["key"]][continent] = results["group_by"][counter]["count"]
                break
            else:
                counter += 1
    flows_between_continents.rename(index={"Q46" : "Europe", "Q49" : "North America", "Q18": "South America", "Q48" : "Asia", "Q55643" : "Oceania", "Q15" : "Africa"},
                                    columns={"Q46" : "Europe", "Q49" : "North America", "Q18": "South America", "Q48" : "Asia", "Q55643" : "Oceania", "Q15" : "Africa"}, inplace=True)
    flows_between_continents.to_excel(f"{path}/chord_diagram_flows_between_continents_2019.xlsx")

def data_for_continents_chord_diagram_1980():
    year = 1980
    continents = ["Q46", "Q49", "Q18", "Q48", "Q55643", "Q15"]

    flows_between_continents = pd.DataFrame(index=continents,columns=continents)
    flows_between_continents.columns.name = "Dimension"

    for continent in continents:
        filters = ",".join((
            f'publication_year:{year}',
            f'institutions.continent:{continent}',
            ))
            
        filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}&group-by=institutions.continent'
        print(filtered_works_url)
        r = requests.get(filtered_works_url)
        results = r.json()
        counter = 0
        while counter < 7:
            if results["group_by"][counter]["key"] in [continent, "unknown", "Q51"]:
                counter += 1
                continue
            flows_between_continents[results["group_by"][counter]["key"]][continent] = results["group_by"][counter]["count"]
            counter += 1
        other_continents_str = ""
        for other_continents in continents:
            if continent == other_continents:
                continue
            elif other_continents_str == "":
                other_continents_str = f"!{other_continents}"
            other_continents_str = "".join((other_continents_str,f"+!{other_continents}"))
        filters = ",".join((filters,f"institutions.continent:{other_continents_str}"))
        filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}&group-by=institutions.continent'
        r = requests.get(filtered_works_url)
        results = r.json()
        counter = 0
        while counter < 7:
            if results["group_by"][counter]["key"] == continent:
                flows_between_continents[results["group_by"][counter]["key"]][continent] = results["group_by"][counter]["count"]
                break
            else:
                counter += 1
    flows_between_continents.rename(index={"Q46" : "Europe", "Q49" : "North America", "Q18": "South America", "Q48" : "Asia", "Q55643" : "Oceania", "Q15" : "Africa"},
                                    columns={"Q46" : "Europe", "Q49" : "North America", "Q18": "South America", "Q48" : "Asia", "Q55643" : "Oceania", "Q15" : "Africa"}, inplace=True)
    flows_between_continents.to_excel(f"{path}/chord_diagram_flows_between_continents_1980.xlsx")

def get_papers_camps_ww1():
    # ALLIES: US, UK, IRELAND, FRANCE, CANADA; JAPAN, ITALY, BELGIUM, AUSTRALIA, ROMANIA, POLAND, BRAZIL, SOUTH AFRICA, GREECE, NEW ZEALAND, PORTUGAL, SERBIA RUSSIA? , "RU"
    ALLIES = ["US","GB","FR","IE","CA", "JP", "IT", "BE", "AU", "RO", "PL", "BR", "ZA", "GR", "NZ", "PT","RS"]
    # CENTRALS: GERMANY, AUSTRIA, HUNGARY, BULGARIA, OTTOMAN Empire
    CENTRALS = ["DE", "AT", "HU", "BG", "TR"]
    # NEUTRALS: Swiss, NL, Sweden, Denmark, Norway, Czechoslovakia, Finland, Spain, Monaco and everyone else
    total_papers_from_countries = pd.read_excel(f"{path}/total_papers_removed_countries.xlsx", index_col=0)

    Cooperations = ["Alliierte_national", "Alliierte_innerhalb_international", "Mittelmächte_national", "Mittelmächte_innerhalb_international","Alliierte-Mittelmächte"] #, "NEUTRALS-ALLIES", "CENTRALS-NEUTRALS"]
    WW1_data = pd.DataFrame(columns=Cooperations,index=range(1906,1927))
    for Bündnis in ["Alliierte", "Mittelmächte"]:
        year = 1906
        if Bündnis == "Alliierte":
            country_codes = ALLIES
            opposing_country_codes = CENTRALS
        elif Bündnis == "Mittelmächte":
            country_codes = CENTRALS
            opposing_country_codes = ALLIES        
        while year < 1927:
            for number_of_countries in ["1", ">1"]:
                filters = ",".join((
                    f'publication_year:{year}',
                    f'countries_distinct_count:{number_of_countries}',
                    ))
                countries_str = ""
                for country in country_codes:
                    if countries_str == "":
                        countries_str = country
                        continue
                    countries_str = "|".join((countries_str,country))

                if number_of_countries == "1":
                    filters = ",".join((filters,f'institutions.country_code:{countries_str}'))
                    filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}'
                    try: 
                        r = requests.get(filtered_works_url)
                        results = r.json()
                        if Bündnis == "Alliierte":
                            WW1_data["Alliierte_national"][year] = results['meta']['count']
                        elif Bündnis == "Mittelmächte":
                            WW1_data["Mittelmächte_national"][year] = results['meta']['count']
                        continue
                    except: # if some api error happens this simply repeats the process for the same year by substracting 1 year and breaking the country loop
                        year -= 1
                        print(filtered_works_url)
                        break
                if number_of_countries == ">1":
                    opposing_countries_str = ""
                    for opposing_country in opposing_country_codes:
                        if opposing_countries_str == "":
                            opposing_countries_str = f'!{opposing_country}'
                            continue
                        opposing_countries_str = "|".join((opposing_countries_str,opposing_country))
                    # exclude neutral countries
                    papers_year = total_papers_from_countries.loc[year].copy()
                    papers_year.dropna(inplace=True)
                    
                    neutral_countries_str_1 = ""
                    neutral_countries_str_2 = ""
                    len_neutral_countries_str_1 = 0
                    len_neutral_countries_str_2 = 0
                    for neutral_country in papers_year.index.to_list():
                        if neutral_country in ALLIES:
                            continue
                        elif neutral_country in CENTRALS:
                            continue
                        if len_neutral_countries_str_1 < 50:
                            if neutral_countries_str_1 == "":
                                neutral_countries_str_1 = f'!{neutral_country}'
                                len_neutral_countries_str_1 = 1
                                continue
                            neutral_countries_str_1 = "|".join((neutral_countries_str_1,neutral_country))
                            len_neutral_countries_str_1 += 1
                            continue
                        if len_neutral_countries_str_1 >= 50 and  len_neutral_countries_str_2 < 50:
                            if neutral_countries_str_2 == "":
                                neutral_countries_str_2 = f'!{neutral_country}'
                                len_neutral_countries_str_2 = 1
                                continue
                            neutral_countries_str_2 = "|".join((neutral_countries_str_2,neutral_country))
                            len_neutral_countries_str_2 += 1
                            continue
                    print(len_neutral_countries_str_1)
                    print(len_neutral_countries_str_2)

                    filters = ",".join((filters,f'institutions.country_code:{countries_str}',f'institutions.country_code:{opposing_countries_str}',
                                        # f'institutions.country_code:{neutral_countries_str_1}'
                                        ))
                    filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}'
                    try: 
                        r = requests.get(filtered_works_url)
                        results = r.json()
                        if Bündnis == "Alliierte":
                            WW1_data["Alliierte_innerhalb_international"][year] = results['meta']['count']
                        elif Bündnis == "Mittelmächte":
                            WW1_data["Mittelmächte_innerhalb_international"][year] = results['meta']['count']
                        continue
                    except: # if some api error happens this simply repeats the process for the same year by substracting 1 year and breaking the country loop
                        year -= 1
                        print(filtered_works_url)
                        break        
            year += 1
    # Cooperational papers ww1 allies centrals
    allied_countries_str = ""
    centrals_countries_str = ""
    for allied_country in ALLIES:
        if allied_countries_str == "":
            allied_countries_str = allied_country
            continue
        allied_countries_str = "|".join((allied_countries_str,allied_country))      
    for centrals_country in CENTRALS:
        if centrals_countries_str == "":
            centrals_countries_str = centrals_country
            continue
        centrals_countries_str = "|".join((centrals_countries_str,centrals_country))
    year = 1906
    while year < 1927:
        filters = ",".join((
            f'publication_year:{year}',
            'countries_distinct_count:>1',
            f'institutions.country_code:{allied_countries_str}',
            f'institutions.country_code:{centrals_countries_str}'
            ))
        filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}'
        try: 
            r = requests.get(filtered_works_url)
            results = r.json()
            WW1_data["Alliierte-Mittelmächte"][year] = results['meta']['count']
        except: # if some api error happens this simply repeats the process for the same year by substracting 1 year and breaking the country loop
            year -= 1
            print(filtered_works_url)
        year += 1

    WW1_data.to_excel(f"{path}/WW1_data_neutr.xlsx")

def get_papers_camps_ww2():
    # ALLIES: US, UK, SOVIET UNION, POLAND, CZ, NORWAY, NL, BE, LUXEMBOURG, FRANCE, GREECE, CANADA, CHINA, AUSTRALIA, NEW ZEALAND, SOUTH AFRICA, BRAZIL, MEXICO
    ALLIES = ["US","GB", "PL", "CZ", "SK", "NO", "NL", "BE", "LU", "FR", "GR", "AU", "NZ", "CA", "ZA", "BR", "MX"]
    # AXIS: GERMANY, AUSTRIA, ITALY, HUNGARY, ROMANIA, BULGARIA, FINLAND, JAPAN
    AXIS = ["DE", "AT", "IT", "HU", "RO", "BG", "FI", "JP"]
    total_papers_from_countries = pd.read_excel(f"{path}/total_papers_removed_countries.xlsx", index_col=0)

    Cooperations = ["Alliierte_national", "Alliierte_innerhalb_international", "Achsenmächte_national", "Achsenmächte_innerhalb_international","Alliierte-Achsenmächte"] #, "NEUTRALS-ALLIES", "CENTRALS-NEUTRALS"]
    WW2_data = pd.DataFrame(columns=Cooperations,index=range(1931,1954))
    for Bündnis in ["Alliierte", "Achsenmächte"]:
        year = 1931
        if Bündnis == "Alliierte":
            country_codes = ALLIES
            opposing_country_codes = AXIS
        elif Bündnis == "Achsenmächte":
            country_codes = AXIS
            opposing_country_codes = ALLIES        
        while year < 1954:
            for number_of_countries in ["1", ">1"]:
                filters = ",".join((
                    f'publication_year:{year}',
                    f'countries_distinct_count:{number_of_countries}',
                    ))
                countries_str = ""
                for country in country_codes:
                    if countries_str == "":
                        countries_str = country
                        continue
                    countries_str = "|".join((countries_str,country))

                if number_of_countries == "1":
                    filters = ",".join((filters,f'institutions.country_code:{countries_str}'))
                    filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}'
                    try: 
                        r = requests.get(filtered_works_url)
                        results = r.json()
                        if Bündnis == "Alliierte":
                            WW2_data["Alliierte_national"][year] = results['meta']['count']
                        elif Bündnis == "Achsenmächte":
                            WW2_data["Achsenmächte_national"][year] = results['meta']['count']
                        continue
                    except: # if some api error happens this simply repeats the process for the same year by substracting 1 year and breaking the country loop
                        year -= 1
                        print(filtered_works_url)
                        break
                if number_of_countries == ">1":
                    opposing_countries_str = ""
                    for opposing_country in opposing_country_codes:
                        if opposing_countries_str == "":
                            opposing_countries_str = f'!{opposing_country}'
                            continue
                        opposing_countries_str = "|".join((opposing_countries_str,opposing_country))
                    # exclude neutral countries
                    papers_year = total_papers_from_countries.loc[year].copy()
                    papers_year.dropna(inplace=True)
                    
                    neutral_countries_str_1 = ""
                    neutral_countries_str_2 = ""
                    neutral_countries_str_3 = ""
                    len_neutral_countries_str_1 = 0
                    len_neutral_countries_str_2 = 0
                    len_neutral_countries_str_3 = 0
                    for neutral_country in papers_year.index.to_list():
                        if neutral_country in ALLIES:
                            continue
                        elif neutral_country in AXIS:
                            continue
                        if len_neutral_countries_str_1 < 50:
                            if neutral_countries_str_1 == "":
                                neutral_countries_str_1 = f'!{neutral_country}'
                                len_neutral_countries_str_1 = 1
                                continue
                            neutral_countries_str_1 = "|".join((neutral_countries_str_1,neutral_country))
                            len_neutral_countries_str_1 += 1
                            continue
                        if len_neutral_countries_str_1 >= 50 and  len_neutral_countries_str_2 < 50:
                            if neutral_countries_str_2 == "":
                                neutral_countries_str_2 = f'!{neutral_country}'
                                len_neutral_countries_str_2 = 1
                                continue
                            neutral_countries_str_2 = "|".join((neutral_countries_str_2,neutral_country))
                            len_neutral_countries_str_2 += 1
                            continue

                        if len_neutral_countries_str_1 >= 50 and  len_neutral_countries_str_2 >= 50 and len_neutral_countries_str_3 < 50:
                            if neutral_countries_str_3 == "":
                                neutral_countries_str_3 = f'!{neutral_country}'
                                len_neutral_countries_str_3 = 1
                                continue
                            neutral_countries_str_3 = "|".join((neutral_countries_str_3,neutral_country))
                            len_neutral_countries_str_3 += 1
                            continue
                    print(len_neutral_countries_str_1)
                    print(len_neutral_countries_str_2)

                    filters = ",".join((filters,f'institutions.country_code:{countries_str}',
                                        f'institutions.country_code:{opposing_countries_str}',
                                        # f'institutions.country_code:{neutral_countries_str_1}',
                                        # f'institutions.country_code:{neutral_countries_str_2}',
                                        # f'institutions.country_code:{neutral_countries_str_3}'
                                        ))
                    filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}'
                    try: 
                        r = requests.get(filtered_works_url)
                        results = r.json()
                        if Bündnis == "Alliierte":
                            WW2_data["Alliierte_innerhalb_international"][year] = results['meta']['count']
                        elif Bündnis == "Achsenmächte":
                            WW2_data["Achsenmächte_innerhalb_international"][year] = results['meta']['count']
                        continue
                    except: # if some api error happens this simply repeats the process for the same year by substracting 1 year and breaking the country loop
                        year -= 1
                        print(filtered_works_url)
                        break        
            year += 1
    # Cooperational papers ww1 allies centrals
    allied_countries_str = ""
    centrals_countries_str = ""
    for allied_country in ALLIES:
        if allied_countries_str == "":
            allied_countries_str = allied_country
            continue
        allied_countries_str = "|".join((allied_countries_str,allied_country))      
    for centrals_country in AXIS:
        if centrals_countries_str == "":
            centrals_countries_str = centrals_country
            continue
        centrals_countries_str = "|".join((centrals_countries_str,centrals_country))
    year = 1931
    while year < 1954:
        filters = ",".join((
            f'publication_year:{year}',
            'countries_distinct_count:>1',
            f'institutions.country_code:{allied_countries_str}',
            f'institutions.country_code:{centrals_countries_str}'
            ))
        filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}'
        try: 
            r = requests.get(filtered_works_url)
            results = r.json()
            WW2_data["Alliierte-Achsenmächte"][year] = results['meta']['count']
        except: # if some api error happens this simply repeats the process for the same year by substracting 1 year and breaking the country loop
            year -= 1
            print(filtered_works_url)
        year += 1

    WW2_data.to_excel(f"{path}/WW2_data.xlsx")


def get_papers_ukr_war():
    # ALLIES: US, UK, SOVIET UNION, POLAND, CZ, NORWAY, NL, BE, LUXEMBOURG, FRANCE, GREECE, CANADA, CHINA, AUSTRALIA, NEW ZEALAND, SOUTH AFRICA, BRAZIL, MEXICO
    Ukraine = ["UA"]
    # AXIS: GERMANY, AUSTRIA, ITALY, HUNGARY, ROMANIA, BULGARIA, FINLAND, JAPAN
    Russland = ["RU"]
    total_papers_from_countries = pd.read_excel(f"{path}/total_papers_removed_countries.xlsx", index_col=0)

    Cooperations = ["Ukraine_national", "Ukraine_innerhalb_international", "Russland_national", "Russland_innerhalb_international","Ukraine-Russland"] #, "NEUTRALS-ALLIES", "CENTRALS-NEUTRALS"]
    Ukr_Krieg = pd.DataFrame(columns=Cooperations,index=range(2014,2024))
    for Bündnis in ["Ukraine", "Russland"]:
        year = 2014
        if Bündnis == "Ukraine":
            country_codes = Ukraine
            opposing_country_codes = Russland
        elif Bündnis == "Russland":
            country_codes = Russland
            opposing_country_codes = Ukraine
        while year < 2024:
            for number_of_countries in ["1", ">1"]:
                filters = ",".join((
                    f'publication_year:{year}',
                    f'countries_distinct_count:{number_of_countries}',
                    ))
                countries_str = ""
                for country in country_codes:
                    if countries_str == "":
                        countries_str = country
                        continue
                    countries_str = "|".join((countries_str,country))

                if number_of_countries == "1":
                    filters = ",".join((filters,f'institutions.country_code:{countries_str}'))
                    filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}'
                    try: 
                        r = requests.get(filtered_works_url)
                        results = r.json()
                        if Bündnis == "Ukraine":
                            Ukr_Krieg["Ukraine_national"][year] = results['meta']['count']
                        elif Bündnis == "Russland":
                            Ukr_Krieg["Russland_national"][year] = results['meta']['count']
                        continue
                    except: # if some api error happens this simply repeats the process for the same year by substracting 1 year and breaking the country loop
                        year -= 1
                        print(filtered_works_url)
                        break
                if number_of_countries == ">1":
                    opposing_countries_str = ""
                    for opposing_country in opposing_country_codes:
                        if opposing_countries_str == "":
                            opposing_countries_str = f'!{opposing_country}'
                            continue
                        opposing_countries_str = "|".join((opposing_countries_str,opposing_country))
                    # exclude neutral countries
                    papers_year = total_papers_from_countries.loc[year].copy()
                    papers_year.dropna(inplace=True)
                    

                    filters = ",".join((filters,f'institutions.country_code:{countries_str}',
                                        f'institutions.country_code:{opposing_countries_str}',
                                        ))
                    filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}'
                    try: 
                        r = requests.get(filtered_works_url)
                        results = r.json()
                        if Bündnis == "Ukraine":
                            Ukr_Krieg["Ukraine_innerhalb_international"][year] = results['meta']['count']
                        elif Bündnis == "Russland":
                            Ukr_Krieg["Russland_innerhalb_international"][year] = results['meta']['count']
                        continue
                    except: # if some api error happens this simply repeats the process for the same year by substracting 1 year and breaking the country loop
                        year -= 1
                        print(filtered_works_url)
                        break        
            year += 1
    # Cooperational papers ww1 allies centrals
    allied_countries_str = ""
    centrals_countries_str = ""
    for allied_country in Ukraine:
        if allied_countries_str == "":
            allied_countries_str = allied_country
            continue
        allied_countries_str = "|".join((allied_countries_str,allied_country))      
    for centrals_country in Russland:
        if centrals_countries_str == "":
            centrals_countries_str = centrals_country
            continue
        centrals_countries_str = "|".join((centrals_countries_str,centrals_country))
    year = 2014
    while year < 2024:
        filters = ",".join((
            f'publication_year:{year}',
            'countries_distinct_count:>1',
            f'institutions.country_code:{allied_countries_str}',
            f'institutions.country_code:{centrals_countries_str}'
            ))
        filtered_works_url = f'https://api.openalex.org/{endpoint}?filter={filters}&mailto={email}'
        try: 
            r = requests.get(filtered_works_url)
            results = r.json()
            Ukr_Krieg["Ukraine-Russland"][year] = results['meta']['count']
        except: # if some api error happens this simply repeats the process for the same year by substracting 1 year and breaking the country loop
            year -= 1
            print(filtered_works_url)
        year += 1

    Ukr_Krieg.to_excel(f"{path}/Ukr_Krieg.xlsx")






