
from selenium import webdriver

from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver")

#select for filling in forms
from selenium.webdriver.support.ui import Select


def downloadCompanyOptions(aStock):

    # include stock in URL
    aURL = "http://www.barchart.com/stocks/quotes/" + aStock + "/options"

    # Get Page
    driver.get(aURL)

    #setup Options page
    theMoneyness = Select(driver.find_element_by_name('moneyness'))
    theView = Select(driver.find_element_by_name('view'))

    # Set Expiration Display
    #
    # theView =======================
    # Stacked           : stacked
    # Stacked OHLC      : stacked_ohl
    # Side-by-Side      : sbs
    # Side-by-Side OHLC : sbs_ohl
    theView.select_by_value('stacked')
    # theMoneyness =======================
    # Near-the-Money  :  inTheMoney
    # Show All        :  allRows
    theMoneyness.select_by_value('allRows')

    expiryText = driver.find_element_by_xpath("//div[@class='row bc-options-toolbar__second-row']").text
    print(expiryText)

    # Get Member Login popup
    aDriver = driver.find_element_by_css_selector("a.bc-user-block__button")  # .click()
    aDriver.click()
    # fill out Login and click
    driver.find_element_by_xpath('//*[@id="bc-login-form"]/div[1]/input').send_keys("barchartwork@gmail.com")
    driver.find_element_by_xpath('//*[@id="login-form-password"]').send_keys('mikeMike733223')
    driver.find_element_by_xpath('//*[@id="bc-login-form"]/div[4]/button').click()
    # wait a couple seconds then remove the popup and download the data
    driver.implicitly_wait(20)
    driver.find_element_by_xpath('/html/body/div[9]/div/div/div[1]/i').click()
    driver.find_element_by_xpath('//*[@id="main-content-column"]/div/div[3]/div[2]/div[2]/a').click()

    return driver
