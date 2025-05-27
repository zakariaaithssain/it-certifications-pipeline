from cleaners import ComptiaCleaner, AWSCleaner, MicrosoftCleaner, FinalDataCleaner
import pandas as pd

cleaners = [ComptiaCleaner(r'..\data\raw\raw_CompTIA_certifications.json'), AWSCleaner(r'..\data\raw\raw_AWS_certifications.json'),
            MicrosoftCleaner(r'..\data\raw\raw_Microsoft_certifications.json')]
certifs = []
for cleaner in cleaners:
    cleaner.standardize_columns_names()
    cleaner.add_provider_column()
    data = cleaner.get_data()
    certifs.append(data)

raw_final = pd.concat(certifs, ignore_index= True, join= 'outer') # shape = (114,22)
raw_final.to_json(r'..\data\raw\raw_final_data.json', orient = 'records', indent = 2)
print('Before cleaning: ', raw_final.shape)

final_cleaner = FinalDataCleaner(r'..\data\raw\raw_final_data.json')
final_data = (final_cleaner
              .drop_missing_name_rows()
              .drop_duplicate_certifications()
              .reorder_columns()
              .drop_empty_columns()
              .clean_duration()
              .clean_cost()
              .clean_certification_name()
              .standardize_columns_names()
              .standardize_languages_column()
              .standardize_Level_column()
              .standardize_Domain_column()
              .final_touches()
              .get_data())

final_data.to_csv(r'..\data\pre_predictions_data.csv', index= False)

print('After cleaning :', final_data.shape)














