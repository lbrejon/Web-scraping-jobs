#! /usr/bin/env python3
# coding: utf-8

import pandas as pd 
import os
 
import json, csv

import requests
from bs4 import BeautifulSoup

import iso3166
from geopy.geocoders import Nominatim
from functools import partial
import numpy as np

import webbrowser
import datetime
from datetime import date


# Global variable
LI_AT_COOKIE = "ENTER YOUR LI AT COOKIE"

# Displaying the full text of a pandas DataFrame (with none of its values truncated).
pd.set_option("display.max_colwidth", -1)


def convert_csv2json(csv_filename, json_filename):
    """ Convert csv file to json file
    Args:
        csv_filename: String, csv filename
        json_filename: String, json filename
    Returns:
        None
    """
    json_tab = []
    with open(csv_filename, encoding='utf-8') as csv_f: 
        # Load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csv_f, delimiter=';') 

        # Convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            json_tab.append(row)
  
    # Convert python json_tab to Json string and write to file
    with open(json_filename, 'w', encoding='utf-8') as json_f: 
        json_str = json.dumps(json_tab, indent=4, separators=(', ', ': '))
        json_f.write(json_str)


#######################################################
# Clean geoId data (required for LinkedIn)
#######################################################

def read_data(csv_file):
    """ Read data from csv file
    Args:
        csv_file: String, csv filename
    Returns:
        df: Dataframe, contains data from csv file
    """
    try:
        df = pd.read_csv(csv_file)
    except:
        df = pd.read_csv(csv_file, delimiter=';')
    return df


def transform_address(address, address_type):
    """ Process data address to country, region and city
    Args:
        address: String, whole address (city, region, country)
        address_type: String, address type to process
    Returns:
        addr: String, processed address (either country, region or city)
    """
    addr_tab = address.split(",")
    if len(addr_tab) == 3:
        
        if address_type == "CITY":
            addr = addr_tab[0]
        elif address_type == "REGION":
            addr = addr_tab[1]
        elif address_type == "COUNTRY":
            addr = addr_tab[2]
            
    elif len(addr_tab) == 2:
        if address_type == "CITY" or address_type == "REGION":
            addr = addr_tab[0]
        elif address_type == "COUNTRY":
            addr = addr_tab[1]
    else:
        addr = "None"
    return addr   


def clean_data(df):
    """ Clean data into dataframe
    Args:
        df: Dataframe to clean
    Returns:
        df: Dataframe, cleaned dataframe
    """
    # Create 3 rows with location information
    df['CITY'] = df['ADDRESS'].apply(transform_address, address_type='CITY')
    df['REGION'] = df['ADDRESS'].apply(transform_address, address_type='REGION')
    df['COUNTRY'] = df['ADDRESS'].apply(transform_address, address_type='COUNTRY')
    
    # Select columns to process and sort df by country code
    df = df[['COUNTRY_CODE', 'COUNTRY', 'REGION', 'CITY', 'GEO_ID']].sort_values(by='COUNTRY_CODE')
    
    # Remove duplicates, unknowned country code and country
    df.dropna(subset = ['COUNTRY_CODE'], inplace=True)
    df = df.drop(df[df['COUNTRY'] == 'None'].index)
    df = df.drop_duplicates().reset_index()
    df = df.drop(columns=['index'])
    
    return df


def clean_data_geoId(geoId_csv = "../../data/raw/geoId.csv"):
    """ Clean geoId data for jobs recommendation algorithm
    Args:
        geoId_csv: String, csv filename to clean
    Returns:
        df_geoId: Dataframe, contains geoId data
    """
    # Read geoId data
    df = read_data(geoId_csv)
    
    # Clean geoId data
    df_geoId = clean_data(df)
    
    # Save processed df into csv file
    geoId_csv_processed = "../../data/processed/geoId.csv"
    try:
        df_geoId.to_csv(geoId_csv_processed)
        print("CSV file '{}' has been cleaned and saved into '{}'".format(geoId_csv, geoId_csv_processed))
    except:
        print("Error while saving CSV file  into '{}'".format(geoId_csv_processed))
        
    return df_geoId


#######################################################
# Jobs recommendation algorithm
#######################################################

def get_field_in_dic_recursively(search_dict, field):
    """
    Takes a dict with nested lists and dicts, and searches all dicts for a key of the field provided.
    Args:
        search_dict: Dictionary
        field: String, field to find
    Returns:
        fields_found: Array of strings, contains fiels found
    """
    fields_found = []

    for key, value in search_dict.items():

        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = get_field_in_dic_recursively(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_field_in_dic_recursively(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found

def remove_elements_end_sentence(sentence):
    """
    Remove elements at the end of sentence
    Args:
        sentence: String, sentence
    Returns:
        sentence: String, processed sentence
    """
    excluded_elements = [".", ",", ";", " "]
    if isinstance(sentence, str):
        while (len(sentence)>1) and (sentence[-1] in excluded_elements):
            sentence = sentence[:-2]
    return sentence

def get_job_title(website, item, jobs_parameters):
    """ Scrap title
    Args:
        website: String, website name
        item: Array of strings, contains HTML elements
        jobs_parameters: Dictionay, contains information about user request
    Returns:
        job_title: String, job title
        job_title_rating: Integer, job title rating
    """
    job_title = ""
    title_keywords_must = [word.lower() for word in jobs_parameters['title_keywords_must']]
    title_keywords_excluded = [word.lower() for word in jobs_parameters['title_keywords_excluded']]
    
    if website == 'Indeed':
        job_title = item.find_all('h2', class_="jobTitle")[0].find_all('span')[-1]

    elif website == 'LinkedIn':
        job_title = item.find_all('h3', class_="base-search-card__title")[0]
    
    # Check valid title and rate title
    job_title = job_title.text.strip()
    title_tmp = job_title.lower()

    # Remove title without must have keywords
    if len(title_keywords_must)>0 and title_keywords_must[0] != '':
        for title_must in title_keywords_must:
            if title_must not in title_tmp:
                job_title = ""
                break

    # Remove excluded title keywords
    if len(title_keywords_excluded)>0 and title_keywords_excluded[0] != '':
        for title_excluded in title_keywords_excluded:
            if title_excluded in title_tmp:
                job_title = ""
                break
            
    return job_title


def get_job_company_name(website, item):
    """ Scrap job company name
    Args:
        website: String, website name
        item: Array of strings, contains HTML elements
    Returns:
        job_company_name: String, job company name
    """
    job_company_name = ""

    if website == 'Indeed':
        job_company_name = item.find_all('span', class_="companyName")[0]
    elif website == 'LinkedIn':
        job_company_name = item.find_all('h4', class_="base-search-card__subtitle")[0]
            
    job_company_name = job_company_name.text.strip().upper()
    return job_company_name


def get_job_company_location(website, item):
    """ Scrap job company location
    Args:
        website: String, website name
        item: Array of strings, contains HTML elements
    Returns:
        job_company_location: String job company location
    """
    job_company_location = ""
 
    if website == 'Indeed':
        job_company_location = item.find_all('div', class_="companyLocation")[0]
    elif website == 'LinkedIn':
        job_company_location = item.find_all('span', class_="job-search-card__location")[0]

    job_company_location = job_company_location.text.strip().split(',')[0]
    return job_company_location


def get_job_rating(website, item):
    """ Scrap job rating
    Args:
        website: String, website name
        item: Array of strings, contains HTML elements
    Returns:
        job_rating: String job rating
    """
    job_rating = ""
    if website == 'Indeed':
        try:
            job_rating = item.find_all('span', class_="ratingNumber")[0].text
        except:
            job_rating = ""
            
    return job_rating


def get_job_salary(website, item):
    """ Scrap job salary
    Args:
        website: String, website name
        item: Array of strings, contains HTML elements
    Returns:
    """
    job_salary = ""
    
    if website == 'Indeed':
        try:
            job_salary = item.find_all('div', class_="metadata salary-snippet-container")[0]
            job_salary = job_salary.text.strip()
        except:
            job_salary = ""
            
    return job_salary
    
    
def get_job_summary(website, item):
    """ Scrap job summary
    Args:
        website: String, website name
        item: Array of strings, contains HTML elements
    Returns:
        job_summary: String, job summary
    """
    job_summary = ""
    
    if website == 'Indeed':
        job_summary = item.find_all('div', class_="job-snippet")[0]
        job_summary = job_summary.text.strip().replace('\n', ' ')
        
    elif website == 'LinkedIn':
        pass
        
    return job_summary

    
def get_job_date(website, item):
    """ Scrap job date
    Args:
        website: String, website name
        item: Array of strings, contains HTML elements
    Returns:
        job_date: String, job date
    """
    job_date = ""
    
    if website == 'Indeed':
        job_date = item.find_all('span', class_='date')[0]
        
    elif website == 'LinkedIn':
        job_date = item.find_all('time')[0]
    
    job_date = job_date.text.strip()
    digits = [digit for digit in job_date if digit.isdigit()]
    digits = ''.join(digits)
    
    if website == 'LinkedIn':
        if 'minute' in job_date:
            digits = "<1"
        elif 'hour' in job_date:
            digits = "<1"
        elif 'week' in job_date:
            digits = 7*int(digits)
        elif 'month' in job_date:
            digits = 30*int(digits)
        else:
            digits = int(digits)
       
    job_date = "{} day ago".format(digits)
    if not job_date[1].isdigit():
        job_date = "0{}".format(job_date)
    return job_date


def get_job_id(website, item):
    """ Scrap job id
    Args:
        website: String, website name
        item: Array of strings, contains HTML elements
    Returns:
        job_id: String, job id
    """
    if website == 'Indeed':
        job_id = item['data-jk']
    elif website == 'LinkedIn':
        job_id = item['data-entity-urn'].split(':')[-1]
    return job_id


def get_job_url(website, item, url, job_id):
    """ Scrap job url
    Args:
        website: String, website name
        item: Array of strings, contains HTML elements
    Returns:
        job_url: String, job url
    """
    if website == 'Indeed':
        try:
            data_empn = item['data-empn']
            job_url = "{}&advn={}&vjk={}".format(url, data_empn, job_id)
        except:
            job_url = "{}&vjk={}".format(url, job_id)
    elif website == 'LinkedIn':
        try:
            job_url = item.find_all('a', class_='base-card__full-link')[0]['href']
        except:
            job_url = ""
    return job_url


def set_company_type(nb_employees):
    """ Scrap job company location
    Args:
        nb_employees: String, employees number in the company
    Returns:
        job_company_type: String job company type
    """
    # Set min and max employees
    try:
        start, end = nb_employees.split('-')
        start, end = int(start), int(end)
    except:
        start = int(nb_employees)
        end = None

    if start >= 5000: # Large Enterprise 
        job_company_type = 'Large Enterprise (+5000 employees)'
    elif end is not None:
        if end < 5000: # Intermediate-sized Enterprise
            job_company_type = 'Intermediate-sized Enterprise (251-5000 employees)'
        if end <= 250: # Medium-sized Enterprise
            job_company_type = 'Medium-sized Enterprise (51-250 employees)'
        if end <= 50 : # Small-sized Enterprise
            job_company_type = 'Small-sized Enterprise (11-50 employees)'   
        if end <= 10: # Startup
            job_company_type = 'Startup (1-10 employees)'
    else:
        job_company_type = "Unknown"
    
    return job_company_type


def get_job_company_type(website, job_company_name, recurs=2):
    """ Scrap job company location
    Args:
        website: String, website name
        job_company_name: String, company name
    Returns:
        job_company_type: String job company type
    """
    job_company_type = ""
    job_company_name = job_company_name.lower().replace(' ','-').replace('&','and')
    url = "https://www.linkedin.com/company/{}/about/".format(job_company_name)
    
    try:        
        # Make request with Beautiful Soup (headers='<headers={'cookie': 'li_at=<cookie_li_at_value>'})```>' as explained in the summary)
        headers = {'cookie': 'li_at={}'.format(LI_AT_COOKIE)}
        soup = request_bs4(url, headers=headers)

        # Parse data
        item_tab = soup.find_all('code')
        nb_employees = 0
        i = 0
        while i<len(item_tab) and nb_employees == 0 :
            item = item_tab[i].text.strip()
            
            # Convert object into dictionary
            item_dic = json.loads(item)
            
            # Find the key 'staffCountRange' recursively in the dictionary
            if isinstance(item_dic, dict):
                staff_tab = get_field_in_dic_recursively(item_dic, 'staffCountRange')
                for staff_dic in staff_tab:
                    
                     # Find the key 'start' recursively in the dictionary
                    if isinstance(staff_dic, dict):
                        start = get_field_in_dic_recursively(staff_dic, 'start')
                        try:
                            nb_employees = staff_dic['start']

                            # Try to extract maximum company size ('end' variable)
                            try:
                                end = get_field_in_dic_recursively(staff_dic, 'end')[0]
                                nb_employees = "{}-{}".format(nb_employees, end)
                            except:
                                break
                        except:
                            pass
            i+=1
        # Select company size type 
        job_company_type = set_company_type(nb_employees)
        
    except:
        job_company_type = "Unknown"
        if recurs > 0:
            job_company_name = job_company_name.rsplit('-', 1)[0] # remove last word
            while job_company_name[-1] == '-':
                job_company_name = job_company_name[:-1]
            recurs -= 1
            job_company_type = get_job_company_type(website, job_company_name, recurs=recurs)
        
    return job_company_type


def get_job_company_sector(website, job_company_name, recurs=2):
    """ Scrap job company location
    Args:
        website: String, website name
        job_company_name: String, company name
    Returns:
        job_company_sector: String, job company sector
    """
    job_company_sector = ""
    job_company_name = job_company_name.lower().replace(' ','-').replace('&','and')
    url = "https://www.linkedin.com/company/{}/about/".format(job_company_name)

    try:        
        # Make request with Beautiful Soup (headers='<headers={'cookie': 'li_at=<cookie_li_at_value>'})```>' as explained in the summary)
        headers = {'cookie': 'li_at={}'.format(LI_AT_COOKIE)}
        soup = request_bs4(url, headers=headers)

        # Parse data
        item_tab = soup.find_all('code')
        i = 0
        job_company_sector = ""
        while i<len(item_tab) and job_company_sector == "":
            item = item_tab[i].text.strip()

            # Convert object into dictionary
            item_dic = json.loads(item)

            # Find the key 'companyType' recursively in the dictionary
            if isinstance(item_dic, dict):
                sector_tab = get_field_in_dic_recursively(item_dic, 'specialities')
                for sector in sector_tab:
                    if isinstance(sector, list):
                        job_company_sector = ', '.join(sector)
            i+=1
        
    except:
        job_company_sector = "Unknown"
        if recurs > 0:
            job_company_name = job_company_name.rsplit('-', 1)[0] # remove last word
            while job_company_name[-1] == '-':
                job_company_name = job_company_name[:-1]
            recurs -= 1
            job_company_sector = get_job_company_sector(website, job_company_name, recurs=recurs)
        
    return job_company_sector

def create_countries_dic(city_tab):
    """ Create dictionary with countries and cities
    Args:
        city_tab: Array of strings, cities name
    Returns:
        country_dic: Dictionary, contains cities in country ({COUNTRY_A:[CITY_A, CITY_B], COUNTRY_B:CITY_C})
    """
    # Tool to search OSM (Open Street Map) data by name and address (geocoding) 
    geolocator = Nominatim(user_agent="http")
    geocode = partial(geolocator.geocode, language="en")
    
    # Fill country/cities dictionary
    country_dic = {}
    city_tab = set(city_tab)
    for city_to_add in city_tab:
        
        # Find country by selected city
        country_to_add = geocode(city_to_add)
        country_to_add = str(country_to_add).upper().split(',')[-1]
        
        if country_to_add[0] == ' ':
            country_to_add = country_to_add[1:]
        
        if len(country_dic) == 0:
            country_dic.update({country_to_add:city_to_add})
        else:
            for countries, cities in country_dic.items():
                # if country already exists
                if countries == country_to_add:
                    
                    # If there is one city
                    if type(cities) is str:
                        city_to_add = [cities, city_to_add]
                    else:
                        city_to_add = cities + [city_to_add]   
                        
                    country_dic[country_to_add] = city_to_add
                    break

            country_dic.update({country_to_add:city_to_add})

    return country_dic


def get_country_code(country):
    """ Get country code from country
    Args:
        country: String, country name
    Returns:
        country_code: Integer, country code
    """
    # List of country codes
    country_code_list = iso3166.countries_by_name
    
    # Country code search
    for countries, information in country_code_list.items():
        if country in countries:
            country_code = country_code_list[countries].alpha2.lower()
            break
    return country_code


def find_geoId(city, geoId_csv = "../../data/processed/geoId.csv"):
    """
    Args:
        city: String, name of the city to find geoId
        geoId_csv: String, csv filename where geoIds are stored
    Returns:
        geoId: Integer, geoId of the city
    """
    df = read_data(geoId_csv)
    geoId = df[df['CITY'] == city]['GEO_ID'].values[0]
    return geoId


def create_url_indeed(country, city, page, jobs_parameters):
    """ Create url for indeed scrapping
    Args:
        country: String, country name
        city: String, city name
        page: Integer, page numero
        jobs_parameters: Dictionay, contains information about user request
    Returns:
        url: String, url
    """
    country_code = get_country_code(country) 
    query = jobs_parameters['query'].replace(' ', '%20')
    distance = jobs_parameters['distance']
    page = str(page*10)
    url = "https://{}.indeed.com/jobs?q={}&l={}&radius={}&start={}&lang=en".format(country_code, query, city, distance, page)
    return url


def create_url_linkedin(country, city, page, jobs_parameters):
    """ Create url for linkedin scrapping
    Args:
        country: String, country name
        city: String, city name
        page: Integer, page numero
        jobs_parameters: Dictionay, contains information about user request
    Returns:
        url: String, url
    """
    geoId = find_geoId(city)    
    query = jobs_parameters['query'].replace(' ', '%20')
    distance = jobs_parameters['distance']
    page = str(page*25)
    url = "https://www.linkedin.com/jobs/search/?geoId={}&keywords={}&location={}%20{}&start={}".format(geoId, query, city, country, page)
    return url


def request_bs4(url, headers=None):
    """ Make request with Beautiful Soup
    Args:
        url: String, url
    Returns:
        soup: Soup object, contains extracted data
    """
    if headers is None:
        # Use of headers to make HTTP requests
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}
    
    # Extract data
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.content, 'html.parser')
    
    return soup


def extract_data(website, country, city, page, jobs_parameters):
    """ Extract data from website 
    Args:
        website: String, website name
        country: String, country name
        city: String, city name
        page: Integer, page numero
        jobs_parameters: Dictionay, contains information about user request
    Returns:
        url: String, url
        soup: Soup object, contains extracted data
    """
    # Generate url
    if website == 'Indeed':
        url = create_url_indeed(country, city, page, jobs_parameters)
    elif website == 'LinkedIn':
        url = create_url_linkedin(country, city, page, jobs_parameters)
    else:
        print(f"WEBSITE: '{website}'")
    # Make request with Beautiful Soup
    soup = request_bs4(url)
    return url, soup
       

def transform_data(website, country, url, soup, jobs_parameters):
    """ Create dictionary with job information
    Args:
        website: String, website name
        country: String, country name
        url: String, url
        soup: Soup object, contains extracted data
        jobs_parameters: Dictionay, contains information about user request
    Returns:
        job_info_tab: Array of strings, contains job information 
    """
    job_info_tab = []
    
    if website == 'Indeed':
        whole_jobs = soup.find_all('div', class_=['mosaic-provider-jobcards'])
        sample_jobs = whole_jobs[0].find_all('a', class_=['tapItem'])
        
    elif website == 'LinkedIn':
        whole_jobs = soup.find_all(class_="base-card base-card--link base-search-card base-search-card--link job-search-card")
        sample_jobs = whole_jobs

    # Retrieve title, company name, company location, salary, summary, date, id and url
    for item in sample_jobs:
        job_title = get_job_title(website, item, jobs_parameters)
        if job_title != "":
            job_company_name = get_job_company_name(website, item)
            job_company_type = get_job_company_type(website, job_company_name)
            job_company_sector = get_job_company_sector(website, job_company_name)
            job_company_location = get_job_company_location(website, item)
            job_salary = get_job_salary(website, item)
            job_summary = get_job_summary(website, item)
            job_date = get_job_date(website, item)
            job_id = get_job_id(website, item)
            job_url = get_job_url(website, item, url, job_id)
            
            country_code = get_country_code(country)
            
            # Create dictionary to retrieve data
            job = {
                'Title': job_title,
                'Company': job_company_name,
                'Company_type': job_company_type,
                'Company_sector':job_company_sector,
                'Country': country,
                'Country_code': country_code,
                'City': job_company_location,
                'Salary': job_salary,
                'Summary': job_summary,
                'Date': job_date,
                'Job_id': job_id,
                'Job_url': job_url                
            }
            
            # Add job dictionary into jobs tab
            job_info_tab.append(job)
            
    return job_info_tab


def rate_title(title, title_keywords_ordered):
    """ Rate job title
    Args:
        title: String, job title
        title_keywords_ordered: Array of strings, contains title keywords ordered
    Returns:
        job_title_rating: Integer, job title rating
    """
    job_title_rating = 0
    for title_ordered in title_keywords_ordered:
        if len(title_ordered) > 0:
            if title_ordered.lower() in title.lower():
                job_title_rating += 1
    return job_title_rating


def rate_company_size_type(company_size_type, company_size_type_ordered):
    """ Rate job title
    Args:
        company_size_type: String, job company size type
        company_size_type_ordered: Array of strings, contains company size type ordered
    Returns:
        job_company_size_type: Integer, job company size type rating
    """
    job_company_size_type = 0
    company_size_type_ordered = [company_size_type_key for company_size_type_key, company_size_type_value in company_size_type_ordered.items() if company_size_type_value is True]
    for company_size in company_size_type_ordered:
        if company_size_type == company_size:
            job_company_size_type += 1
    return job_company_size_type


def save_df2csv(df_jobs, filename_csv):
    """ Save dataframe into csv file
    Args:
        df_jobs: Dataframe, contains information about scrapped jobs
        filename_csv: String, filename csv
    Returns:
        None
    """
    try:
        df_jobs.to_csv(filename_csv, sep=';')
        print(">> File '{}' successfully saved".format(filename_csv))
    except:
        print(">> Error while saving file '{}'".format(filename_csv))

        
def rate_jobs(df_jobs, jobs_parameters):
    """ Rate jobs
    Args:
        df_jobs: Dataframe, contains information about scrapped jobs
        jobs_parameters: Dictionay, contains information about user request
    Returns:
        df_jobs: Dataframe, contains information about scrapped jobs with general rating column
    """
    df_rating = df_jobs['Job_id']
    
    # Rate title
    title_keywords_ordered = [word.lower() for word in jobs_parameters['title_keywords_ordered']]
    df_rating['Title rating'] = df_jobs['Title'].apply(rate_title, title_keywords_ordered=title_keywords_ordered)
    
    # Rate company size type
    company_size_type_ordered = jobs_parameters['company_size_type']
    df_rating['Company type rating'] = df_jobs['Company_type'].apply(rate_company_size_type, company_size_type_ordered=company_size_type_ordered)
    
    # Add general rating to job dataframe
    df_rating['General rating'] =  df_rating['Title rating'] + df_rating['Company type rating']
    df_jobs.insert(1, 'General rating', df_rating['General rating'])
    return df_jobs
    
    
def scrape_jobs(jobs_parameters):
    """ Scrap jobs from several websites
    Args:
        jobs_parameters: Dictionay, contains information about user request
    Returns:
        df_jobs: Dataframe, contains information about scrapped jobs
    """
    website_nb = 0
    
    # Loop on websites
    for website in jobs_parameters['website']:
        job_tab = []
        countries_dic = create_countries_dic(jobs_parameters['location'])
        
        # Loop on countries
        for country, cities in countries_dic.items():
            
            # Loop on cities
            if type(cities) is str:
                cities = [cities]
            for city in cities:
                
                # Loop on pages
                for page in range(0, jobs_parameters['pages']):
                    
                    # Extract whole data from 1 page
                    url, soup = extract_data(website, country, city, page, jobs_parameters)
                    print(url)
#                     print(soup)

                    # Create dictionary with job information
                    job_dic = transform_data(website, country, url, soup, jobs_parameters)
                    job_tab += job_dic

                # Create df with jobs information
                df = pd.DataFrame(data=job_tab, columns=['Title', 'Company', 'Company_type', 'Company_sector', 'Country', 'Country_code', 'City', 'Summary', 'Date', 'Job_id', 'Job_url'])
                df.insert(0, 'Website', [website[0].upper() + website[1:] for i in range(len(df))])
        
        if website_nb == 0:
            df_jobs = df
        else:
            df_jobs = pd.concat([df_jobs, df])
        website_nb += 1
        
    df_jobs = df_jobs.drop_duplicates(subset=['Job_id'])
    for col in list(df_jobs.columns):
        df_jobs[col] = df_jobs[col].apply(remove_elements_end_sentence)
        
    # Rate jobs
    df_jobs = rate_jobs(df_jobs, jobs_parameters)
    df_jobs = df_jobs.sort_values(by='General rating', ascending=False).reset_index(drop=False)

    return df_jobs


def check_jobs_parameters(jobs_parameters):
    """ Check jobs parameters values
    Args:
        jobs_parameters: Dictionary, contains jobs parameters
    Returns:
        website: String, websites
        distance: Integer, distance from the location
        pages: Integer, pages number
    """
    website = jobs_parameters['website'] if len(jobs_parameters['website']) > 0 else "Indeed"
    distance = int(jobs_parameters['distance']) if jobs_parameters['distance'].isdigit() else 0
    pages = int(jobs_parameters['pages']) if jobs_parameters['pages'].isdigit() else 3
    return website, distance, pages


def read_jobs_parameters(json_jobs_parameters):
    """ Read json jobs_parameters
    Args:
        json_jobs_parameters: String, json jobs parameters filename
    Returns:
        jobs_parameters: Dictionary, contains jobs parameters
    """
    with open(json_jobs_parameters, "r") as json_file:
        data = json.load(json_file)

    # Check and set default value if no user request
    website, distance, pages = check_jobs_parameters(data)

    # Fill job parameters dictionary
    jobs_parameters = {
        'website': website,
        'query': data['query'],
        'location': data['location'],
        'distance': distance,
        'title_keywords_must': set(data['title_keywords_must']),
        'title_keywords_excluded': set(data['title_keywords_excluded']),
        'pages': pages,    
        'title_keywords_ordered': set(data['title_keywords_ordered']),
        'company_size_type': data['company_size_type'],
    }
    return jobs_parameters



if __name__ == "__main__":
    # Clean and create processed geoId csv file
    geoId_csv = "../../data/raw/geoId.csv"
    geoId_csv_processed = geoId_csv.replace('raw', 'processed')

    if not os.path.isfile(geoId_csv_processed):
        df_geoId = clean_data_geoId(geoId_csv)
        print("File '{}' created".format(geoId_csv_processed))
    else:
        print("File '{}' already exists".format(geoId_csv_processed))
        df_geoId = read_data(geoId_csv_processed)

    # Scraping parameters
    json_jobs_parameters = "../../data/jobs_parameters_user_request.json"
    jobs_parameters = read_jobs_parameters(json_jobs_parameters)
    print("\nJobs parameters user request received", jobs_parameters, "\n")
    df_jobs = scrape_jobs(jobs_parameters)

    # Save jobs as csv file
    filename_csv = "../../data/jobs.csv"
    save_df2csv(df_jobs, filename_csv)

    # Save jobs as json file
    csv_filename = filename_csv
    json_filename = filename_csv.replace("csv","json")
    convert_csv2json(csv_filename, json_filename)
