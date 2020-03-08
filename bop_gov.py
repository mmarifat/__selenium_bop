# Author Minhaz Ahamed<mma.rifat66@gmail.com>
# Email: mma.rifat66@gmail.com
# Web: https://mma.champteks.us
# Do not edit file without permission of author
# All right reserved by Minhaz Ahamed<mma.rifat66@gmail.com>
# Created on: 08/03/2020 4:15 PM

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import re
from os import path

# check for existing files
if not path.exists("out.csv"):
    with open("out.csv", 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['No', 'Name', 'Release', 'Address1', 'Address2', 'Address3', 'Address4']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

# initialize
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://www.bop.gov/inmateloc/")

def scrap_data(numbers):
    wait = WebDriverWait(driver, 20)
    for count, no in enumerate(numbers, 1):
        print("************************\nNow doing: ", no)

        # check existing files in the csv
        with open('out.csv', mode='r') as file:
            reader = csv.DictReader(file)
            check = []
            for row in reader:
                to_check = re.sub("[^0-9]", "", (f'\t{row["No"]}'))
                check.append(to_check)

        # if not available in the csv , add it via browsing
        if not no in check:
            search = wait.until(EC.element_to_be_clickable((By.ID, 'inmNumber')))
            search.clear()
            search.send_keys(no)

            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button#searchNumber'))).click()
            try:
                name = wait.until(EC.element_to_be_clickable((By.ID, 'numResultTDName'))).text
                rd = wait.until(EC.element_to_be_clickable((By.ID, 'numResultTDBot2'))).text
                release_date = re.sub("[^0-9,/]", "", rd)
                con2 = [no, name, release_date]
            except:
                continue

            # find if further info available or not
            try:
                wait.until(EC.element_to_be_clickable((By.ID, 'numResultTDBot1'))).click()
                driver.switch_to.window(driver.window_handles[1])
                wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Inmate Mail"))).click()
                address = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='address-item']/div"))).text

                # manipulation
                con = re.sub("[\n]", ",", address).rsplit(",")
                con.pop(0)
                last_addr = con[3] + "," + con[4]
                del con[-2:]
                con.append(last_addr)

                driver.close()
                time.sleep(1)
                driver.switch_to.window(driver.window_handles[0])
            except:
                con = [""]

            # append all info from single search
            content = [con2 + con]
            print(content)
            print("Completed : ", count, "\n************************\n")

            # write into a csv with unicode support
            with open("out.csv", 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, delimiter=',')
                writer.writerows(content)
        else:
            print("Data already available")

    # close and finish
    driver.close()

# take input search no's
with open('in.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    no = []
    for row in csv_reader:
        number = re.sub("[^0-9]", "", (f'\t{row["Name"]}'))
        no.append(number)
    scrap_data(no)
