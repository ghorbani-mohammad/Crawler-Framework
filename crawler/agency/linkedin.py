from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from linkedin_scraper import Person, actions, Company

options = Options()
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--enable-javascript")
driver = webdriver.Remote("http://crawler_chrome:4444/wd/hub",
                                desired_capabilities=DesiredCapabilities.CHROME,
                                options=options)

email = "mahsa.jafari2003@gmail.com"
password = "mBGsgf9cuE7!s3W"
actions.login(driver, email, password) # if email and password isnt given, it'll prompt in terminal
person = Person("https://www.linkedin.com/in/gh-m/", driver=driver)
# print(person)
print('******** name:')
print(person.name)
print('******** about:')
print(person.about)
print('******** experiences')
print(person.experiences)
print('******** educations')
print(person.educations)
print('******** company')
print(person.company)
print('******** job_title')
print(person.job_title)


company = Company("https://www.linkedin.com/company/lockheed-martin/")
print(company)