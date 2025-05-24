
import pandas as pd
import re

class DataCleaner():
    def __init__(self, raw_data_file, provider = None):
        self.data = pd.read_json(raw_data_file, orient='records').copy()
        self.provider = provider

    def drop_empty_columns(self, tolerance = 0.5):
        missing_ratio = self.data.isna().mean()
        to_drop = missing_ratio[missing_ratio > tolerance].index
        self.data.drop(columns= to_drop, inplace= True)
        return self

    def drop_missing_name_rows(self):
        self.data.dropna(subset = ['Certification'], inplace = True, ignore_index = True)
        return self

    def add_provider_column(self):
        self.data['Provider'] = self.provider
        return self

    def reorder_columns(self): #for the final cleaner
        prior = ['Certification', 'Provider', 'Domain', 'Level', 'Languages', 'Cost (USD)', 'Official Link', 'Description', 'Recommended Experience', 'Exam Code', 'Exam Duration (min)', ]
        columns = prior + [col for col in self.data.columns if col not in prior]
        self.data = self.data[columns]
        return self

    def clean_cost(self):
        self.data['Cost (USD)'] = self.data['Cost (USD)'].map(self._find_cost)
        return self

    def _find_cost(self, string):
        if isinstance(string, str):
            match = re.search(r'\d+', string) #\d+ means one or more digits.
            return float(match.group()) if match else 0.
        return 0.

    def clean_duration(self):
        self.data['Exam Duration (min)'] = self.data['Exam Duration (min)'].map(self._find_cost)
        return self

    def clean_certification_name(self):
        self.data['Certification'] = self.data['Certification'].map(self._unwanted_string)
        return self

    def _unwanted_string(self, cert_name):
        unwanted = ['CompTIA', 'AWS', 'Microsoft', ':', '- Associate', '- Professional', '- Specialty', 'Associate', 'Professional', 'Speciality', 'Expert']
        for word in unwanted:
            cert_name = cert_name.replace(word, '')
        return cert_name.strip()



    def standardize_columns_names(self):
        united_names = {'Exam duration' : 'Exam Duration (min)' , 'Length of Test': 'Exam Duration (min)', 'Exam Duration' : 'Exam Duration (min)', 'Exam Description' : 'Description', 'URL' : 'Official Link',
 'Requirements' : 'Recommended Experience', 'Intended candidate' : 'Recommended Experience', 'Category' : 'Level',
  'Exam Codes' : 'Exam Code', 'Price' : 'Cost (USD)', 'Cost' : 'Cost (USD)', 'Exam format' : 'Type of Questions', 'Languages offered' : 'Languages',
'Candidate role examples' : 'Domain'}
        self.data.rename(columns = united_names, errors = 'ignore', inplace= True)
        return self

    def drop_duplicate_certifications(self):
        # Create helper normalized columns
        self.data['_cert_norm'] = self.data['Certification'].str.lower().str.strip()
        self.data['_provider_norm'] = self.data['Provider'].str.lower().str.strip()
        self.data['_level_norm'] = self.data['Level'].fillna('').str.lower().str.strip()

        self.data = self.data.drop_duplicates(subset = ['_cert_norm', '_provider_norm', '_level_norm'], keep = 'first' )
        # Drop helper columns
        self.data.drop(columns=['_cert_norm', '_provider_norm', '_level_norm'], inplace=True)
        return self

    def get_data(self):
        return self.data

class ComptiaCleaner(DataCleaner):
    def __init__(self, raw_data_file):
        super().__init__(raw_data_file, 'CompTIA')

    def standardize_columns_names(self):  #just to fix duplicated column name after renaming
        col1 = self.data['Exam Codes'].map(lambda value : '' if value == None else str(value))
        col2 = self.data['Exam Code'].map(lambda value: '' if value == None else str(value))
        self.data['Exam Code'] = col1 + col2
        self.data.drop(columns = ['Exam Codes'], inplace= True)
        return super().standardize_columns_names()


class AWSCleaner(DataCleaner):
    def __init__(self, raw_data_file):
        super().__init__(raw_data_file, 'AWS')



class MicrosoftCleaner(DataCleaner):
    def __init__(self, raw_data_file):
        super().__init__(raw_data_file, 'Microsoft')
        self.data['Requirements'] = self.data['Requirements'].map(lambda row: re.sub(r'\s+', ' ', row.strip()) if isinstance(row, str) else 'Not Specified')

    def standardize_columns_names(self):  #just to fix duplicated columns names after renaming
        self.data['Domain'] = self.data['Domain'].str.cat(self.data['Targeted Role'], sep = ': ')
        self.data.drop(columns = ['Targeted Role'], inplace= True)
        return super().standardize_columns_names()



class FinalDataCleaner(DataCleaner):
    def __init__(self, raw_data_file):
        super().__init__(raw_data_file)

    def standardize_languages_column(self):
        self.data['Languages'] = self.data['Languages'].apply(
            lambda x: re.sub(r'[\n\t]+', ', ', x).strip().strip(' , ') if isinstance(x, str) else 'Not Specified')

        self.data['Languages'] = self.data['Languages'].map(self._iso639mapping)

        self.data['Languages'] = self.data['Languages'].map(
            lambda x: x.replace('(at launch)', '').replace('(at later date)', '')
            .replace(' and', '').replace('to follow', '').replace('in 2025', '')
            .replace(' with', ',').strip() if isinstance(x, str) else 'Not Specified')
        return self

    def _iso639mapping(self, row):
        iso639 = {
            'en': 'English',
            'fr': 'French',
            'es': 'Spanish',
            'de': 'German',
            'it': 'Italian',
            'pt-br': 'Portuguese (Brazil)',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'zh-cn': 'Chinese (Simplified)',
            'zh-tw': 'Chinese (Traditional)',
            'ko': 'Korean',
            'ar-sa': 'Arabic (Saudi Arabia)',
            'id-id': 'Indonesian (Indonesia)',
            'id': 'Indonesian',
            'vi': 'Vietnamese (Vietnam)',
            'vi-vn': 'Vietnamese (Vietnam)',
            'nl': 'Dutch',
            'pl': 'Polish',
            'el-gr': 'Greek (Greece)',
            'hu': 'Hungarian',
            'ro': 'Romanian',
            'uk': 'Ukrainian',
            'bg': 'Bulgarian (Bulgaria)',
            'th': 'Thai',
            'tr': 'Turkish',
            'ms': 'Malay',
            'en-my': 'English (Malaysia)'
        }
        if pd.isna(row) or row == 'TBD':
            return 'Not Specified'

        split_row = str(row).split(',')
        new_row =[]
        fixed = False
        for lang in split_row:
            for key in iso639:
                if key == lang.strip():
                    new_row.append(iso639[key])
                    fixed = True
        if not fixed: new_row = row #which means that the column is good already
        else: new_row = ', '.join(new_row)

        return new_row

    def standardize_Level_column(self):
        level_map = {
            'beginner': 'Beginner',
            'foundational': 'Beginner',
            'intermediate': 'Intermediate',
            'associate': 'Intermediate',
            'advanced': 'Advanced',
            'professional': 'Advanced',
            'speciality': 'Specialized',
            'specialty': 'Specialized'
        }

        self.data['Level'] = self.data['Level'].str.lower().map(level_map)
        return self

    def standardize_Domain_column(self):
        domain_map = {
            'microsoft 365: administrator': 'productivity',
            'office 365: administrator': 'productivity',
            'business analyst, it support, marketing professional, product or project manager, line-of-business or it manager, sales professional': 'it/business',

            'azure: administrator': 'cloud',
            'azure: ai engineer': 'cloud',
            'azure: developer': 'cloud',
            'azure: data engineer': 'data',
            'azure: data scientist': 'data',
            'azure: database administrator': 'cloud',
            'azure: solution architect': 'cloud',
            'azure: network engineer': 'cloud',
            'azure: security engineer': 'security',
            'azure: devops engineer': 'devops',
            'azure: security operations analyst': 'security',

            'microsoft defender: administrator': 'security',
            'microsoft entra: administrator': 'security',

            'dynamics 365: business analyst': 'business apps',
            'dynamics 365: functional consultant': 'business apps',
            'dynamics: business analyst': 'business apps',
            'dynamics 365: developer': 'business apps',
            'dynamics 365: business owner': 'business apps',

            'windows: business user': 'productivity',
            'word: business user': 'productivity',
            'powerpoint: business user': 'productivity',
            'office: business user': 'productivity',
            'access: business user': 'productivity',
            'excel: business user': 'productivity',
            'outlook: business user': 'productivity',

            'microsoft fabric: data engineer': 'data',

            'backend software developer, devops engineer, data engineer, mlops engineer, and data scientist': 'devops',

            'microsoft power platform: developer': 'automation',
            'microsoft power platform: data analyst': 'automation',
            'microsoft power platform: functional consultant': 'automation',
            'microsoft power platform: app maker': 'automation',
        }
        self.data.Domain = self.data.Domain.str.lower().map(domain_map)
        return self

    def final_touches(self):
        self.data['Description'] = self.data['Description'].fillna('Not Specified')
        self.data['Recommended Experience'] = self.data['Recommended Experience'].fillna('Not Specified')
        self.data['Level'] = self.data['Level'].fillna('Unknown')
        self.data['Domain'] = self.data['Domain'].fillna('Unknown')

        for column in self.data.columns.tolist():
            if column not in ['Cost (USD)', 'Exam Duration (min)']:
                self.data[column] = self.data[column].astype(str)
                self.data[column] = self.data[column].str.lower()

        self.data['Exam Duration (min)'] = self.data['Exam Duration (min)'].astype(int)
        self.data['Cost (USD)'] = self.data['Cost (USD)'].astype(int)
        self.data.sort_values('Certification', inplace=True, ignore_index=True)
        return self




















