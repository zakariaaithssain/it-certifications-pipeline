from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
from io import StringIO
from tqdm import tqdm

import requests as rq
import pandas as pd

#I adapted the AWS scraper after they changed the layout. Now CompTIA changed the layout too.
class BaseScraper:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.data = None

    def _init_driver(self):
        options = webdriver.ChromeOptions()
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-lvl_features=AutomationControlled')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36')
        options.add_argument('--headless=new')
        return webdriver.Chrome(options=options)

    def scraper(self):
        raise NotImplementedError('Each Site Should Implement Its Own Scraper')

    def save_to_json(self, filename):
        if self.data is not None:
            print(filename)
            self.data.to_json(filename, orient = 'records', indent = 2) #records saves each row as a dictionary.

    def get_data(self):
        return self.data



class CompTIA(BaseScraper):
    def __init__(self):
        super().__init__('CompTIA', 'https://www.comptia.org/certifications')

    def scraper(self):
        comptia_certifs = pd.DataFrame()
        certif_urls = self._certifs_urls().items()
        print(len(certif_urls))
        for certif_name, certif_url in tqdm(certif_urls):
            certif_data = self._certif_data(certif_name, certif_url)
            comptia_certifs = pd.concat([comptia_certifs, certif_data.to_frame().T], ignore_index=True)
        self.data = comptia_certifs

    def _certifs_urls(self):
        try:
            response = rq.get(self.url)
        except rq.exceptions.RequestException:
            print("An Error Has Occured While Requesting CompTIA.")
            return {}

        bs = BeautifulSoup(response.text, 'html.parser')
        cert_boxes = bs.find_all('a', {'class': 'featured-certification_box w-inline-block'})

        certifs_urls = {}
        for box in cert_boxes:
            name_tag = box.find('div', {'class': 'featured-certification_name'})
            if name_tag:
                cert_name = name_tag.text.strip()
                if box.has_attr('href'):
                    cert_url = "https://www.comptia.org" + box['href']
                    certifs_urls[cert_name] = cert_url
        return certifs_urls

    def _certif_data(self, certif_name, certif_url):
        try:
            response = rq.get(certif_url)
        except rq.exceptions.RequestException:
            print("An Error Has Occurred While Requesting The URL of This Certification.")
            return pd.Series(name=certif_name)

        bs = BeautifulSoup(response.text, 'html.parser')
        table = bs.find('table', {'class': 'basictablenotresonsive'})

        if not table: return pd.Series(name=certif_name)
        try:
            df = pd.read_html(StringIO(str(table)))[0]  # it returns a list of dataframes, thus the need of indexing.
        except ValueError:
            return pd.Series(name=certif_name)

        if df.shape[1] == 2:
            df.columns = ['Field', 'Value']
            certif_data = pd.Series(data=df['Value'].values, index=df['Field'].values, name=certif_name)
            certif_data = pd.concat([pd.Series(data=[certif_name, certif_url], index=['Certification', 'URL']), certif_data])
            return certif_data
        elif df.shape[1] == 3:
            df.columns = ['Field', 'whatever', 'Value']
            certif_data = pd.Series(data=df['Value'].values, index=df['Field'].values, name=certif_name)
            certif_data = pd.concat([pd.Series(data=[certif_name, certif_url], index=['Certification', 'URL']), certif_data])
            return certif_data
        else:
            return pd.Series(name=certif_name)



class AWS(BaseScraper):     #STILL TRYING TO FIGURE OUT HOW TO GET THE DATA FROM THE NEW LAYOUT.
    def __init__(self):
        super().__init__('AWS', 'https://aws.amazon.com/certification/')

    def scraper(self):
        driver = self._init_driver()
        certif_urls = self._certifs_urls(driver)
        aws_certifs = pd.DataFrame()
        for url in tqdm(certif_urls):
            certif_data = self._certif_data(url, driver)
            aws_certifs = pd.concat([aws_certifs, certif_data.to_frame().T], ignore_index=True)
        self.data = aws_certifs
        driver.quit()

    def _certifs_urls(self, driver):
        
        try:
            driver.get(self.url)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="amsinteractive-card-verticalpattern-data"]/div/div/div/div/div/div/a')))

        except TimeoutException as e:
            print(f"Driver Was Enable To Get AWS URL, Error: ", str(e))

        certifs_fig = driver.find_elements(By.XPATH, '//*[@id="amsinteractive-card-verticalpattern-data"]/div/div/div/div/div/div/a')
        if len(certifs_fig) < 12: print(f"Warning: The driver seems to not get all the certifications. Certifications found: {len(certifs_fig)}")
        certif_urls = []  # certifs names are in images thus I can't use a dictionary as in comptia_scraper.
        for fig in certifs_fig:
            certif_url = fig.get_attribute("href")
            certif_urls.append(certif_url)
        return certif_urls

    def _certif_data(self, certif_url, driver):
        try:
            driver.get(certif_url)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        except Exception as e:
            print(f'Driver Was Enable To Get The URL {certif_url}, Error: ', str(e))
        
        #for the new layout
        try: WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Exam-overview"]/div/div[3]/div[2]/button')))
        except TimeoutException:
            pass
        #for the old layout that contains a table.
        try: WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'table')))
        except TimeoutException:
            pass            

        bs = BeautifulSoup(driver.page_source, 'lxml')

        table = bs.find('table')
        show_more_button = driver.find_element(By.XPATH, '//*[@id="Exam-overview"]/div/div[3]/div[2]/button')

        #for the old layout
        if table: 
            certif_name = bs.find('h1').text
            try:
                df = pd.read_html(StringIO(str(table)))[0]
            except ValueError:
                return pd.Series({'Certification': certif_name})

            if df.shape[1] >= 2:
                df.columns = ['Field', 'Value']
                certif_data = pd.Series(data=df['Value'].values, index=df['Field'].values, name=certif_name)
                certif_data = pd.concat([pd.Series({'Certification' : certif_name, 'Official Link' : certif_url}), certif_data])
            else:
                return pd.Series({'Certification': certif_name})
            return certif_data
        
        #for the new layout
        elif show_more_button: 
            certif_data = {}
            driver.execute_script("arguments[0].click();", show_more_button)

            certif_name = bs.find("h1", {"data-rg-n" : "HeadingText"}).text
            certif_data["Certification"] = certif_name

            certif_description = driver.find_element(By.CSS_SELECTOR, 'div.col_module_col__8176fa0f.col_module_colXs12__8176fa0f.col_module_colS12__8176fa0f.col_module_colM6__8176fa0f.col_module_colL6__8176fa0f.col_module_colXl6__8176fa0f.col_module_colXxl6__8176fa0f.textmediacontent_module_textContainer__a8f07c10 > div.basetext_module_text__34d4534b.bodytext_module_body__cc74e5ca.bodytext_module_size1__cc74e5ca').text
            certif_data["Description"] = certif_description

            details = driver.find_elements(By.XPATH, '//*[@id="Exam-overview"]/div/div/div/div/div/div')
            for elt in details:
                column = elt.find_element(By.TAG_NAME, "h3").text
                value = elt.find_element(By.TAG_NAME, "p").text
                certif_data[column] = value
            
            return pd.Series(data = certif_data)
        
        else: print("Neither the new layout nor the old one is working,\nAWS might have changed the layout again!")
            




class Microsoft(BaseScraper):
    def __init__(self):
        super().__init__("Microsoft", 'https://learn.microsoft.com/en-us/credentials/browse/?credential_types=certification')

    def scraper(self):
        driver = self._init_driver()
        try:
            driver.get(self.url)
        except Exception as e:
            print(f"Driver Was Enable To Get This URL {self.url}, Error: ", str(e))
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'card-template')))
        except TimeoutException:
            pass
        bs = BeautifulSoup(driver.page_source, 'html.parser')
        main_data = self._all_pages_certifs(driver)
        enriched_rows = []
        for certif_idx in tqdm(main_data.index):
            certif_row = main_data.iloc[certif_idx]
            certif_url = certif_row['URL']
            certif_extra_data = self._certif_extra_data(driver, certif_url)
            full_data_row = pd.concat(
                [certif_row.to_frame().T.reset_index(drop=True), certif_extra_data.reset_index(drop=True)], axis=1)
            enriched_rows.append(full_data_row)

        final_data = pd.concat(enriched_rows, ignore_index=True)
        self.data = final_data
        driver.quit()

    def _all_pages_certifs(self, driver):
        page1 = self._one_page_certifs(driver)
        for index in range(2, 4):
            try: WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'button.pagination-link[data-page="{index}"]')))
            except TimeoutException:
                pass
            button = driver.find_element(By.CSS_SELECTOR, f'button.pagination-link[data-page="{index}"]')
            button.click()
            this_page = self._one_page_certifs(driver)
            page1 = pd.concat([page1, this_page], ignore_index=True)

        return page1

    def _one_page_certifs(self, driver):
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'card-template')))
        bs = BeautifulSoup(driver.page_source, 'html.parser')
        certifs_cards = bs.find_all('div', {'class': 'card-template'})
        data = {}
        for card in certifs_cards:
            title_url_tag = card.find('a', {'class': 'card-title'})

            if title_url_tag:
                certif_title = title_url_tag.text.strip()
                data[certif_title] = []
                certif_url = "https://learn.microsoft.com" + title_url_tag['href']
                data[certif_title].append(certif_url)

                code_tag = card.find('span', {'class': 'is-comma-delimited'})
                if code_tag:
                    certif_exam_code = code_tag.text.strip()
                    data[certif_title].append(certif_exam_code)
                else:
                    data[certif_title].append(
                        None)  # I noticed that the exam code is often absent, which gives an error

                metadata_tag = card.find('ul', {'class': 'metadata page-metadata font-size-xs'})
                if len(metadata_tag) >= 3:
                    certif_domaine = metadata_tag.li
                    data[certif_title].append(certif_domaine.text.strip())
                    certif_target_role = certif_domaine.find_next_sibling('li')
                    data[certif_title].append(certif_target_role.text.strip())
                    certif_lvl = certif_target_role.find_next_sibling('li')
                    data[certif_title].append(certif_lvl.text.strip())

        data = pd.DataFrame(data).T
        data.columns = ['URL', 'Exam Code', 'Domain', 'Targeted Role', 'Level']
        data.index.name = 'Certification'
        data.reset_index(inplace=True)
        return data

    def _certif_extra_data(self, driver, certif_url):
        try:
            driver.get(certif_url)
        except Exception as e:
            print(f'Driver Was Enable To Get This URL {certif_url}, Error: ', str(e))

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'li')))
        except TimeoutException:
            pass
        bs = BeautifulSoup(driver.page_source, 'html.parser')
        return self._v2_layout(driver, certif_url, bs) if bs.find('div', {'id': 'at-a-glance'}) else self._v1_layout(driver, certif_url, bs)

    def _v1_layout(self, driver, certif_url, bs):
        try:
            certif_description = bs.find('p').text.strip()
        except AttributeError:
            certif_description = None

        try:
            certif_prerequisites = ""
            prerequisites_tags = bs.find_all('ul')
            if len(prerequisites_tags) == 2:
                prerequisites_tags = prerequisites_tags[1]
                for elt in prerequisites_tags:
                    certif_prerequisites += elt.text.strip() + '\n'
            elif len(prerequisites_tags) == 1:
                prerequisites_tags = prerequisites_tags[0]
                for elt in prerequisites_tags:
                    certif_prerequisites += elt.text.strip() + '\n'
        except AttributeError:
            certif_prerequisites = None

        try:
            country_button = driver.find_element(By.CSS_SELECTOR, 'select.exam-countries')
            select = Select(country_button)
            select.select_by_visible_text('Morocco')  # the pricing depends on the country.
        except:
            pass

        try:
            certif_price = bs.find('div', {'class': 'exam-amount'}).text.strip()
        except AttributeError:
            certif_price = None

        try:
            certif_languages = bs.find('p', {'class': 'font-size-sm margin-top-none'}).find('span', {
                'class': 'is-comma-delimited'}).text.replace('\\n', ', ')
        except AttributeError:
            certif_languages = None

        return pd.Series(data=[certif_description, certif_languages, certif_prerequisites, certif_price, None],
                         index=['Description', 'Languages', 'Requirements', 'Price', 'Exam Duration']).to_frame().T

    def _v2_layout(self, driver, certif_url, bs):
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'at-a-glance')))
        except TimeoutException:
            pass

        try:
            certif_description = bs.find('div', {'class': 'content margin-bottom-lg'}).find('p').text.strip()
        except AttributeError:
            certif_description = None

        try:
            certif_prerequisites = ""
            prerequisites_tags = bs.find('div', {'class': 'content margin-bottom-lg'}).ul.find_next_sibling('ul')
            for elt in prerequisites_tags: certif_prerequisites += elt.text.strip() + "\n"
        except (AttributeError, TypeError):
            certif_prerequisites = None

        try:
            exam_duration = bs.find('section', {'id': 'certification-take-the-exam'}).find('span', {
                'class': 'font-weight-semibold'}).text.strip()
        except AttributeError:
            exam_duration = None

        try:
            country_button = driver.find_element(By.CSS_SELECTOR, 'select.exam-countries')
            select = Select(country_button)
            select.select_by_visible_text('Morocco')  # the pricing depends on the country.
        except:
            pass

        try:
            certif_price = bs.find('p', {'class': 'exam-amount'}).text.strip()
        except AttributeError:
            certif_price = None

        try:
            languages_class = bs.find('span', {'class': 'docon-localize-language'}).find_parent('div',
                                                                                                {'class': 'media-left'})
            certif_languages = languages_class.find_next_sibling('div', {'class': 'media-content'}).p.find_next_sibling(
                'p').text.replace('\\n', ', ')
        except AttributeError:
            certif_languages = None

        return pd.Series(data=[certif_description, certif_languages, certif_prerequisites, certif_price, exam_duration],
                         index=['Description', 'Languages', 'Requirements', 'Price', 'Exam Duration']).to_frame().T


