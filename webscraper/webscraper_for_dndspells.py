import requests
from requests import get
from bs4 import BeautifulSoup
import csv
import re

url = "https://dnd5e.wikidot.com/spells"

results = requests.get(url)

soup = BeautifulSoup(results.text, "html.parser")

#this found all the links, and added them into a file
#for a_href in soup.find_all("a", href=True):
#   with open("spell_links.txt", "a") as linkfile:
 #     linkfile.write(a_href["href"] + "\n")
#print("Finished")
#dont uncomment this as it will continuoulsy add more and more to the file

#prints out all the links on the page
with open('spell_links.txt', 'r') as file:
    links = file.read().splitlines()
    #opens this file so that it can be added in to complete the pages

#print(links)
#print(len(links))
#1253

from urllib.parse import urljoin
base = url
full = [urljoin(base, link) for link in links]
#joins my base link with the links pulled from the page

file_name = 'spells.csv'
#csv file for moving it over to sql

def write_csv_header(file_name):
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'Name', 'Level', 'School', 'Casting Time', 'Range', 'Duration', 'Components', 
            'Description', 'Higher Levels', 'Spell Lists'])
        writer.writeheader()

write_csv_header(file_name)

def scrape_spell_data(soup):
    name = name_extract(soup)
    level, school = lvl_and_school(soup)
    casting_time = casting_time_extract(soup)
    range_of_spell = range_extract(soup)
    duration = duration_extract(soup)
    components = components_extract(soup)
    description_text = description(soup)
    higher_levels = higher_level(soup)
    spell_lists = spell_list(soup)
    return {
        'Name': name,
        'Level': level,
        'School': school,
        'Casting Time': casting_time,
        'Range': range_of_spell,
        'Duration': duration,
        'Components': components,
        'Description': description_text,
        'Higher Levels': higher_levels,
        'Spell Lists': spell_lists
    }

def name_extract(soup):
    name_div = soup.find('div', class_='page-title page-header')
    if name_div:
        return name_div.find('span').text.strip()
    return None

def lvl_and_school(soup):
    # Extract level and school from the spell description
    spell_type = soup.find('p', string=re.compile(r".*cantrip.*|.*level.*", re.IGNORECASE))
    if spell_type:
        text = spell_type.text.strip()
        if 'cantrip' in text.lower():
            level = 0
            school = text.split(' ')[0]  # Extract school from the first word
        else:
            parts = text.split(' ')
            level = parts[0]
            school = ' '.join(parts[1:])  # Extract school from the remaining text
        return level, school
    return None, None

def casting_time_extract(soup):
    # Extract Casting Time
    casting_time_tag = soup.find('strong', string="Casting Time:")
    if casting_time_tag:
        return casting_time_tag.next_sibling.strip()
    return None

def range_extract(soup):
    # Extract Range
    range_tag = soup.find('strong', string="Range:")
    if range_tag:
        return range_tag.next_sibling.strip()
    return None

def duration_extract(soup):
    # Extract Duration
    duration_tag = soup.find('strong', string="Duration:")
    if duration_tag:
        return duration_tag.next_sibling.strip()
    return None

def components_extract(soup):
    # Extract Components
    components_tag = soup.find('strong', string="Components:")
    if components_tag:
        return components_tag.next_sibling.strip()
    return None
    # Extract Components
    details_p = soup.find('p', string=re.compile(r"Components:", re.IGNORECASE))
    if details_p:
        text = details_p.text.strip()
        components = re.search(r"Components:\s*(.*)", text)
        if components:
            return components.group(1).strip()
    return None

def description(soup):
    description_div = soup.find_all('p')
    description_text = []
    for p in description_div:
        text = p.text.strip()
        if not text.startswith(("Source:", "Casting Time:", "Range:", "Components:", "Duration:", "At Higher Levels.", "Spell Lists.")):
            description_text.append(text)
    return ' '.join(description_text)

def higher_level(soup):
    # Extract Higher Levels
    for p in soup.find_all('p'):
        if "At Higher Levels." in p.text:
            higher_levels_text = p.text.strip()
            # Remove the "At Higher Levels." prefix
            return higher_levels_text.replace("At Higher Levels.", "").strip()
    return None

def spell_list(soup):
    # Extract all Spell Lists
    spell_lists_div = soup.find('strong', string="Spell Lists.")
    if spell_lists_div:
        spell_lists = []
        # Find all <a> tags after the "Spell Lists." strong tag
        for a_tag in spell_lists_div.find_next_siblings('a'):
            spell_lists.append(a_tag.text.strip())
        return ', '.join(spell_lists)
    return None
    spell_lists_div = soup.find('strong', string="Spell Lists.")
    if spell_lists_div:
        spell_lists = spell_lists_div.find_next('a').text.strip()
        return spell_lists
    return None
#spell list scrape

# Function to store data in CSV format
def store_data(data, file_name):
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'Name', 'Level', 'School', 'Casting Time', 'Range', 'Duration', 'Components', 
            'Description', 'Higher Levels', 'Spell Lists'])
        writer.writerow(data)


count = 0
for url in full:
    response = requests.get(url)
    print("Getting")
    soup = BeautifulSoup(response.text, 'html.parser')
    print("Souping")
    data = scrape_spell_data(soup)
    print("Scraped")
    store_data(data, file_name)
    print("Storing")
    for key, value in data.items():
        print(f"{key}: {value}")
    count+=1
    print(count)
#main for loop to scrape adn then store.
#has counts, becasue it was struggling and i needed to know where along with the prints to see where it was stopping

    

print("Scraping and saving is finished!")