
from selenium import webdriver

import pandas as pd
#get pandas HTML table support
from pandas.io.html import read_html

# this makes the "driver" global and will initiate at startup...
# move to jupyter and pass driver between methods if needed.
#driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver")

#select for filling in forms
from selenium.webdriver.support.ui import Select


def downloadCompanyOptions(driver, aStock="AAPL"):
# added driver to parameters to accomadate moving out of global variable
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

def scrapeCompanyOptionData(driver, aStock, theExpiryDateText ):

    # include stock in URL
    aURL = "http://www.barchart.com/stocks/quotes/" + aStock + "/options"

    # Get Page
    driver.get(aURL)

    #setup Options page
    theMoneyness = Select(driver.find_element_by_name('moneyness'))
    theView = Select(driver.find_element_by_name('view'))
    theExpiry = Select(driver.find_element_by_xpath('//*[@id="main-content-column"]/div/div[3]/div[1]/div/div[2]/select'))

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
    theExpiry.select_by_value(theExpiryDateText)

    # get the text to show days to expiry and IV
    expiryText = driver.find_element_by_xpath("//div[@class='row bc-options-toolbar__second-row']").text
    expiryText = expiryText.replace('\n', ' -- ')

    optionsTables = read_html(driver.page_source)

    # close the browser
    # driver.close()
    # I am now returning driver to the calling program
    # Because for multiple calls i was getting the invalid session ID error
    #   That is a WebDriver error that occurs when the server does not
    #   recognize the unique session identifier.
    #   this happens if the session has been deleted or if the session ID is invalid.

    callOptions = optionsTables[0]
    putOptions = optionsTables[1]

    callOptions = callOptions.iloc[:, :-2]
    putOptions = putOptions.iloc[:, :-2]
    thePuts = putOptions.set_axis(['Strike', 'Last', '% From Last', 'Bid', 'Midpoint', 'Ask', 'Change',
                                   '% Chg', 'IV', 'Volume', 'Open Int', 'Time'],axis=1, inplace=False)
    theCalls = callOptions.set_axis(['Strike', 'Last', '% From Last', 'Bid', 'Midpoint', 'Ask', 'Change',
                                   '% Chg', 'IV', 'Volume', 'Open Int', 'Time'],axis=1, inplace=False)
    # callOptions.rename(columns={'Strike', 'Last', '%FromLast', 'Bid', 'Midpoint', 'Ask', 'Change', '%Chg', 'IV', 'Volume', 'OpenInt', 'Time'}, inplace=True)

    return theCalls, thePuts, expiryText, driver


def XXXXscrapeCompanyOptionData(driver, aStock, theExpiryDateText ):

    # include stock in URL
    aURL = "http://www.barchart.com/stocks/quotes/" + aStock + "/options"

    # Get Page
    driver.get(aURL)

    #setup Options page
    theMoneyness = Select(driver.find_element_by_name('moneyness'))
    theView = Select(driver.find_element_by_name('view'))
    theExpiry = Select(driver.find_element_by_xpath('//*[@id="main-content-column"]/div/div[3]/div[1]/div/div[2]/select'))

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
    theExpiry.select_by_value(theExpiryDateText)

    # get the text to show days to expiry and IV
    expiryText = driver.find_element_by_xpath("//div[@class='row bc-options-toolbar__second-row']").text
    expiryText = expiryText.replace('\n', ' -- ')

    optionsTables = read_html(driver.page_source)

    # close the browser
    # driver.close()
    # I am now returning driver to the calling program
    # Because for multiple calls i was getting the invalid session ID error
    #   That is a WebDriver error that occurs when the server does not
    #   recognize the unique session identifier.
    #   this happens if the session has been deleted or if the session ID is invalid.

    callOptions = optionsTables[0]
    putOptions = optionsTables[1]

    callOptions = callOptions.iloc[:, :-2]
    putOptions = putOptions.iloc[:, :-2]
    thePuts = putOptions.set_axis(['Strike', 'Last', '% From Last', 'Bid', 'Midpoint', 'Ask', 'Change',
                                   '% Chg', 'IV', 'Volume', 'Open Int', 'Time'],axis=1, inplace=False)
    theCalls = callOptions.set_axis(['Strike', 'Last', '% From Last', 'Bid', 'Midpoint', 'Ask', 'Change',
                                   '% Chg', 'IV', 'Volume', 'Open Int', 'Time'],axis=1, inplace=False)
    # callOptions.rename(columns={'Strike', 'Last', '%FromLast', 'Bid', 'Midpoint', 'Ask', 'Change', '%Chg', 'IV', 'Volume', 'OpenInt', 'Time'}, inplace=True)

    return theCalls, thePuts, expiryText, driver
