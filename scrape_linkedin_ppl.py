

"""

Goal:
scrape summary information from linkedin people search result pages


Output:
csv file in current directory saved from a pandas dataframe


Method:
First, modify the script to provide 3 things: login id, password, and search word

Default, first search result page pulls up is divided into multiple sections:
    1. jobs
    2. people

Once next page is clicked, linkedin assumes you are looking for people;

We want to grab people and then look for 5 pieces of information by inspecting the tags
    i.      name
    ii.     job title + current company
    iii.    degree of separation (if over 3, it will appear blank)
    iv.     location
    v.      linkedin url
    vi.     quick summary

Define the number of pages to crawl (we want to be safe with our limits)

After crawling, convert the lists of results into a pandas dataframe and output it to a csv

"""

# require libraries
import time, string, re
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

# create lists of name, job title, current position, shared connection, degree of separation

name = []
job_and_company = []
degree_sep = []
location = []
prof_url = []
quick_summary = []


# enter your linkedin email
my_email = input("Enter login: ")

# enter your linkedin email
my_pw = input("Enter pw: ")

# run a headless browser option
opts = FirefoxOptions()
opts.add_argument("--headless")

# open browser and go to linkedin
driver = webdriver.Firefox(firefox_options = opts)
driver.get("http://www.linkedin.com")

# separater after each action for visual purposes
def print_sep():
    print("")
    print("")
    print("")
    print("")
    print("")
    print("")
    time.sleep(5)
    print("#" * 100)

def print_sep_short():
    print("")
    print("")
    print("")
    print("")
    print("")
    print("")
    time.sleep(1)
    print("#" * 100)

# enter in login and wait 3 seconds
un_box = driver.find_element_by_id('login-email')
un_box.send_keys(my_email)
print("Entering id")
print_sep()

# enter in password and wait 3 seconds
pw_box = driver.find_element_by_id('login-password')
pw_box.send_keys(my_pw)
print("Entering pw")
print_sep()

# submit credentials and wait 3 seconds
driver.find_element_by_id('login-submit').click()
print("Loggin in")
print_sep()

search_item = input('What word should be searched: ')

# type into the search box and hit enter on keyboard
srch_box = driver.find_element_by_tag_name("input")
srch_box.send_keys(search_item)
srch_box.send_keys(Keys.RETURN)
print("Entering search item and hit enter 'key'")
print_sep()

# select the people's button because that's what we want, a list of people
driver.find_element_by_xpath('//button[@data-vertical="PEOPLE"]').click()
print("Switching to People section")
print_sep()

"""
enter in whatever scraping that needs done here now
"""

# name, title/company, and url will always be provided
# degree of separation and crnt/past summary may not always be provided


# initiate count to loop through search results page
page_count = 0
page_limit_set = 10

# loop through each page until the page page limit set
while page_count < page_limit_set:

    # scroll down to bottom of the page (because 'next button' won't work otherwise)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    print("scrolled a little to the bottom")
    print_sep()

    # get the page source in HTML for the current page and make a bs4 object
    html = driver.page_source
    time.sleep(1)
    bs = BeautifulSoup(html, "html.parser")
    srch_div = bs.findAll('div', {'class':'search-result__info pt3 pb4 ph0'})
    print("pull html code from source")
    print_sep()

    # loop through each search result profile
    for profile in range(len(srch_div)):

        # add full name
        a = srch_div[profile].findAll('span', {'class':'actor-name'})[0].text
        name.append(a)
        print("name: ", a)

        # add job title and company
        a = srch_div[profile].findAll('p', {'class':'subline-level-1 Sans-15px-black-85% search-result__truncate'})[0].text
        a = re.sub("\n", "", a)
        a = re.sub("  ", "", a)
        job_and_company.append(a)
        print("job title + company: ", a)

        # add degree of separation
        if len(srch_div[profile].findAll('span', {'class':'visually-hidden'})[0].text) > 0:
            a = srch_div[profile].findAll('span', {'class':'visually-hidden'})[0].text
            degree_sep.append(a)
            print("degree of sep: ", a)

        # if degree of separation summary is not shown, return 'not available'
        else:
            a = "not available"
            degree_sep.append(a)
            print("degree of sep: ", a)

        # quick search result summary
        if len(srch_div[profile].findAll('p', {'class':'search-result__snippets mt2 Sans-13px-black-55% ember-view'})) > 0:
            a = srch_div[profile].findAll('p', {'class':'search-result__snippets mt2 Sans-13px-black-55% ember-view'})[0].text
            a = re.sub("\n", "", a)
            a = re.sub("  ", "", a)
            quick_summary.append(a)
            print("quick summary: ", a)

        # if quick result summary is not shown, return 'not available'
        else:
            a = "not available"
            quick_summary.append(a)
            print("quick summary: ", a)

        # add current location
        a = srch_div[profile].findAll('p', {'class':'subline-level-2 Sans-13px-black-55% search-result__truncate'})[0].text
        a = re.sub("\n", "", a)
        a = re.sub("  ", "", a)
        location.append(a)
        print("current location: ", a)

        # add linkedin profile url
        sublink = srch_div[profile].findAll('a')[0]['href']
        a = "www.linkedin.com" + sublink
        prof_url.append(a)
        print("linkedin profile link: ", a)
        print_sep_short()

    page_count += 1

    # click next to move to next page and repeat the process
    driver.find_element_by_class_name('next').click()
    print("hit next")
    print_sep()

# close the browser window
driver.quit()

# combine the separate lists into a pandas dataframe
result_set = pd.DataFrame(np.column_stack([name, job_and_company, degree_sep, location, prof_url, quick_summary]),
                            columns = ["Name", "Job_And_Company", "Degree_Of_Separation", "Location", "Professional_URL", "Quick_Summary"])

# export the pandas dataframe into a csv file into current folder location
result_set.to_csv("linkedin_search_"+search_item+".csv")
