# from celery.decorators import task
# from linkedin_scraper import Person, Company, actions
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


# options = Options()
# options.add_argument('--disable-gpu')
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument("--enable-automation")
# options.add_argument("--no-sandbox")
# driver = webdriver.Remote("http://crawler_chrome:4444/wd/hub", desired_capabilities=DesiredCapabilities.CHROME, options=options)
# driver.header_overrides = {
#     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
#     'AppleWebKit/537.11 (KHTML, like Gecko) '
#     'Chrome/23.0.1271.64 Safari/537.11',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#     'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
#     'Accept-Encoding': 'none',
#     'Accept-Language': 'en-US,en;q=0.8',
#     'Connection': 'keep-alive'
# }

# email = "mahsa.jafari2003@gmail.com"
# password = "mBGsgf9cuE7!s3W"
# actions.login(driver) # if email and password isnt given, it'll prompt in terminal
# # cmp = Company("https://ca.linkedin.com/company/google", driver=driver)
# # print(cmp)


from scrape_linkedin import ProfileScraper
with ProfileScraper(cookie='AQEDATXV0McAKSriAAABeo97_pQAAAF6s4iClE4ARvcdPTnchk3-lxcZQ0LSUIm694D1eDD_tRe8_HOxym2Z0uk13ft360RLh_GLEoVffKnlC2UkXdllyUuHRQAtO1PMLFBpy6_0Zqu_irWp8Pm8iSzh') as scraper:
    profile = scraper.scrape(user='austinoboyle')
print(profile.to_dict())