import streamlit as st
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

# Function to extract Gig ID from URL
def extract_gig_id(gig_url):
    match = re.search(r'\/([^\/]+)-\d+$', gig_url)
    return match.group(1) if match else None

# Function to get Fiverr search results
def get_fiverr_rank(keyword, gig_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    
    service = Service(executable_path="chromedriver")  # Use the correct path to your chromedriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    search_url = f"https://www.fiverr.com/search/gigs?query={keyword}"
    driver.get(search_url)

    gig_found = False
    gig_position = -1

    for page in range(1, 6):  # Search up to 5 pages
        time.sleep(3)  # Allow page to load

        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        gigs = soup.find_all("a", class_="gig-link")  # Fiverr gig links
        
        for index, gig in enumerate(gigs, start=1):
            if gig_id in gig["href"]:
                gig_found = True
                gig_position = ((page - 1) * len(gigs)) + index
                break

        if gig_found:
            break

        # Click "Next Page" if exists
        next_page = driver.find_element(By.CSS_SELECTOR, "a[rel='next']")
        if next_page:
            next_page.click()
        else:
            break

    driver.quit()
    
    return gig_position if gig_found else "Not in first 5 pages"

# Streamlit UI
st.title("🛠️ Fiverr Gig Rank Tracker")
st.write("Enter your Fiverr Gig URL and the keyword you want to track.")

# User Inputs
gig_u
