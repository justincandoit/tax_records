from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import csv
from bs4 import BeautifulSoup

# Lavallette
start_url = "https://wipp.edmundsassoc.com/Wipp/?wippid=1516"
driver = webdriver.Chrome("C:/Users/Justin/Downloads/chromedriver_win32/chromedriver.exe")
wait = WebDriverWait(driver, 3)

# Launch window
driver.get(start_url)


addresses = [
    "101 COLEMAN LANE",
    "2204 BALTIMORE AVE",
    "2206 BALTIMORE AVE"
]



# get tax rows
def get_tax_data():
    outter_table = '/html/body/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td/div/div[1]/table/tbody/tr[2]/td/table/tbody'
    tax_table_total_row_path = "/html/body/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td/div/div[1]/table/tbody/tr[2]/td/table/tbody/tr[@class='tableHeader']"
    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, outter_table)))
    tax_total_rows = driver.find_elements_by_xpath(tax_table_total_row_path)
    d = dict()
    d['address'] = driver.find_element_by_xpath("//td[contains(text(),'Location')]/following-sibling::td[1]").get_attribute("innerText")
    d['owner name'] = driver.find_element_by_xpath("//td[contains(text(),'Owner Name')]/following-sibling::td[1]").get_attribute("innerText")

    for row in tax_total_rows:
        row_html = row.get_attribute('outerHTML')
        soup = BeautifulSoup(row_html, features='lxml')
        cols = soup.find_all('td')
        label = cols[1].get_text()
        billed = cols[3].get_text()
        d[label + " Billed"] = billed
        due = cols[-2].get_text()
        d[label + " Due"] = due

    return d



def search_by_address(address):
    input_box = "/html/body/table/tbody/tr[2]/td/div/table[1]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[5]/input"
    wait.until(EC.presence_of_element_located((By.XPATH, input_box)))
    search_button  = "/html/body/table/tbody/tr[2]/td/div/table[1]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[6]/button"
    input_element = driver.find_element_by_xpath(input_box)
    print("here")
    input_element.clear()
    input_element.send_keys(address)
    search_element = driver.find_element_by_xpath(search_button)
    search_element.click()


output_list = []


with open('lavallette.csv', newline='') as csv_file:
    spamreader = csv.reader(csv_file, delimiter=',', quotechar='"')
    count = 0
    for row in spamreader:
        if count == 50:
            break
        count += 1
        print(count)
        address = row[1]
        search_by_address(address)
        radio_path = "//tbody/tr[2]/td/span/input[@name='picklistGroup']"
        wait.until(EC.presence_of_element_located((By.XPATH, radio_path)))
        # click radio button
        first_radio = driver.find_element_by_xpath(radio_path)
        first_radio.click()
        try:
            output_list.append(get_tax_data())
        except:
            print('failed: '+address)
        driver.execute_script("window.history.go(-1)")


# count=0
# for row in addresses:
#     count += 1
#     print(count)
#     address = row
#     print("searching for row: "+row)
#     search_by_address(address)
#     radio_path = "//tbody/tr[2]/td/span/input[@name='picklistGroup']"
#     wait.until(EC.presence_of_element_located((By.XPATH, radio_path)))
#     # click radio button
#     first_radio = driver.find_element_by_xpath(radio_path)
#     first_radio.click()
#     try:
#         output_list.append(get_tax_data())
#     except:
#         print('failed: ' + address)
#     driver.execute_script("window.history.go(-1)")


with open('taxes.csv', 'w', newline='') as csvfile:
    fieldnames = set()
    for a in output_list:
        fieldnames.update(list(a.keys()))
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for a in output_list:
        writer.writerow(a)
