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

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://www.bop.gov/inmateloc/")

def scrap_data(numbers):
    content = []
    wait = WebDriverWait(driver, 10)
    for count, no in enumerate(numbers, 1):
        print("************************\nNow doing: ", no)

        search = wait.until(EC.element_to_be_clickable((By.ID, 'inmNumber')))
        search.clear()
        search.send_keys(no)

        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button#searchNumber'))).click()
        name = wait.until(EC.element_to_be_clickable((By.ID, 'numResultTDName'))).text
        rd = wait.until(EC.element_to_be_clickable((By.ID, 'numResultTDBot2'))).text
        release_date = re.sub("[^0-9,/]", "", rd)
        con2 = [name, release_date]

        # find if further info available or not
        try:
            wait.until(EC.element_to_be_clickable((By.ID, 'numResultTDBot1'))).click()
            driver.switch_to.window(driver.window_handles[1])
            wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Inmate Mail"))).click()
            address = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='address-item']/div"))).text

            con = re.sub("[\n]", ",", address).rsplit(",")
            con.pop(0)
            last_addr = con[3] + "," + con[4]
            del con[-2:]
            con.append(last_addr)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            con = [""]

        # append all info from single search
        print(con2 + con)
        print("Completed : ", count, "\n************************\n")
        content.append(con2 + con)

    # print this huge list containing all info
    print(content)
    driver.close()

    # write into a csv with unicode support
    with open("out.csv", 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Release', 'Address1', 'Address2', 'Address3', 'Address4']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        csvfile.write('\ufeff')
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, delimiter=',')
        writer.writerows(content)

with open('in.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    no = []
    for row in csv_reader:
        number = re.sub("[^0-9]", "", (f'\t{row["Name"]}'))
        no.append(number)
    scrap_data(no)
