import pandas as pd
#this is use just to determine the unique and different names of all the certifications
comptia = pd.read_json(r'raw\raw_CompTIA_certifications.json')
comptia_columns = set(comptia.columns)
aws = pd.read_json(r'raw\raw_AWS_certifications.json')
aws_columns = set(aws.columns)
micro = pd.read_json(r'raw\raw_Microsoft_certifications.json')
micro_columns = set(micro.columns)
unique_names = comptia_columns | aws_columns | micro_columns
mapping = {'Length of Test': 'Exam Duration', 'Exam Description' : 'Description', 'Targeted Role' : 'Domain', 'URL' : 'Official Link',
 'Requirements' : 'Recommended Experience', 'Intended candidate' : 'Recommended Experience', 'Category' : 'Level',
  'Exam Codes' : 'Exam Code', 'Price' : 'Cost', 'Exam format' : 'Type of Questions', 'Languages offered' : 'Languages',
'Candidate role examples' : 'Domain', 'Exam Details' : 'Description'}

