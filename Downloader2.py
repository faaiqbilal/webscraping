from selenium import webdriver
import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import selenium.webdriver.support.ui as ui
import lxml
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import filedownloader
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

def createDir(dir_):    
    try:
        dir_ = dir_.replace("<","")
        dir_ = dir_.replace(">","")
        dir_ = dir_.replace(":","")
        os.mkdir(dir_)
    except FileExistsError:
        pass

def __firefox_driver(download_dir):
    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.helperApps.alwaysAsk.force", False);
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.manager.showAlertOnComplete", False)
    fp.set_preference('browser.helperApps.neverAsk.saveToDisk','application/zip,application/octet-stream,application/x-zip-compressed,multipart/x-zip,application/x-rar-compressed, application/octet-stream,application/msword,application/vnd.ms-word.document.macroEnabled.12,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/rtf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,application/vnd.ms-word.document.macroEnabled.12,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/xls,application/msword,text/csv,application/vnd.ms-excel.sheet.binary.macroEnabled.12,text/plain,text/csv/xls/xlsb,application/csv,application/download,application/vnd.openxmlformats-officedocument.presentationml.presentation,application/octet-stream')
    fp.set_preference("browser.download.dir", download_dir)
    return webdriver.Firefox(firefox_profile=fp)

#In this case our driver is basically our browser, everything is being passed through this object
driver = __firefox_driver("D:\\Web Scraper Python\\Downloads")

#####URL and basic setup######
URL = "https://lms.lums.edu.pk/portal/"
driver.get(URL)

#####Login#####
username = driver.find_element_by_id("eid")
username.clear()
username.send_keys("23100104")

password = driver.find_element_by_id("pw")
password.clear()
password.send_keys("Machoumisty2001!")

driver.find_element_by_id("submit").click()

######Traversing website to reach files#######
driver.find_element_by_link_text("Resources").click()

tool_link = driver.find_element_by_class_name("portletMainIframe").get_attribute('src')
driver.get(tool_link)

driver.find_element_by_link_text("Copy Content from My Other Sites").click()

course_title = "SS 101 S"
#Note: We will be using Course Name, and specify whether it is a lab, section, or recitation.
driver.find_elements_by_partial_link_text(course_title)[1].click()

new_directory = "LMS"
createDir(new_directory)

# Create directory for Course
course_directory = os.path.join(new_directory, course_title)
createDir(course_directory)

# Looking for the documents to be opened
# xpath = //tagname[@Attribute='Value']

# soup = BeautifulSoup(driver.page_source, "lxml")
# f = open("WebsiteCode.html", "w")
# f.write(str(soup))
# f.close()

#########COMMENTS MADE WHILE WORKING ON THIS ################
# I've currenty left out the repeating iterator definitions because they look redundant, but given their placement I think they might be necessary later
# The code isn't downloading anything with the code we have below, which could be because of the missing redundant code. I'll have to add it and check again I guess

#############################################################

# We will now create a function that will loop through the directory, the function will be recursive for each 'level'. This is determined by the file structure in the Sakai tool.
# We will start with level 1 in the structure, which is the first and outermost level
def recursive_folder_traversal(level=1, new_directory=""):
	
	print(driver.find_elements_by_xpath(f"//tbody/tr/td[@style='text-indent:{level}em']"))
	content_elements = driver.find_elements_by_xpath(f"//tbody/tr/td[@style='text-indent:{level}em']")
	# print(driver.find_elements_by_css_selector("text-indent:{}em".format(level)))
	# Checking whether or not we're done with this level
	if content_elements == []:
		print(f"Done with level {level}")
	# Creating a new directory
	createDir(new_directory)
	# Check enumerate documentation if you need to, the second variable can be anything when using enumerate, it just represents the counter
	for i,counter in enumerate(content_elements):
		content_elements[i] = driver.find_elements_by_xpath("//tbody/tr/td[@style='text-indent:{}em']".format(level))[i]
		folder = content_elements[i].driver.find_elements_by_xpath(".//a[@title='Open this Folder']")
		if folder != []: # then it is a folder
			folder[0].click()
			element_loaded = EC.presence_of_element_located((By.XPATH,"//td[@style='text-indent:{}em']//a[@title='Close this folder']".format(level)))
			try:
				WebDriverWait(driver, 20).until(element_loaded)
			except TimeoutException:
				print("Either Folder is empty or took too long to load")
			content_elements[i] = driver.find_elements_by_xpath("//tbody/tr/td[@style='text-indent:{}em']".format(level))[i]

			#Recursive part starts now
			recursive_folder_traversal(level+1,os.path.join(new_directory,content_elements[i].text))

			content_elements[i] = driver.find_element_by_xpath("//tbody/tr/td[@style='text-indent:{}em']".format(level))[i]

			folder = driver.find_element_by_xpath(f'//body/tr/td[@style="text-indent:{level}em"]//a[@title="Close this folder"]')
			print('CLICKED' + folder.text)
			folder.click()

			element_loaded = EC.invisibility_of_element_located((By.XPATH,f"//td[@style='text-indent:{level}em']//a[@title='Close this folder']"))
			WebDriverWait(driver,20).until(element_loaded)

			continue
		# Coming down to individual files now.
		file = content_elements[i].find_elements_by_xpath('.//a')[1]
		file_link = file.get_attribute("href")
		file_name = os.path.join(new_directory, file.text)
		
		try:
			filedownloader(file, file_link,driver, ext="")
		except Exception as e:
			print(e)
			print(f"The file: {file_name} failed to download")
recursive_folder_traversal(new_directory=course_directory)
driver.switch_to.default_content()
