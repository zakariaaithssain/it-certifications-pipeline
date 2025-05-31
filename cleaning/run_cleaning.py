from cleaning.cleaners import ComptiaCleaner, AWSCleaner, MicrosoftCleaner, FinalDataCleaner
import pandas as pd
import time as t
def run_cleaning(state=None, progress=None): #those are st related arguments
    try:
        cleaners = [ComptiaCleaner(r'C:\Users\zakar\OneDrive\Bureau\PFA\it_certifications_project\data\raw\raw_CompTIA_certifications.json'), AWSCleaner(r'C:\Users\zakar\OneDrive\Bureau\PFA\it_certifications_project\data\raw\raw_AWS_certifications.json'),
                    MicrosoftCleaner(r'C:\Users\zakar\OneDrive\Bureau\PFA\it_certifications_project\data\raw\raw_Microsoft_certifications.json')]
        certifs = []
        step = 1
        for cleaner in cleaners:
            state.text(f"Standardizing {cleaner.provider} columns...")
            cleaner.standardize_columns_names()
            t.sleep(1)
            progress.progress(step/9)
            step+=1
            state.text(f"Adding Provider column for {cleaner.provider}...")
            cleaner.add_provider_column()
            t.sleep(1)
            progress.progress(step/9)
            step+=1
            state.text(f"Saving {cleaner.provider} cleaned data...")
            data = cleaner.get_data()
            certifs.append(data)
            t.sleep(1)
            progress.progress(step/ 9)
            step +=1

        state.text("Concatenating cleaned data...")
        raw_final = pd.concat(certifs, ignore_index= True, join= 'outer') # shape = (114,22)
        raw_final.to_json(r'C:\Users\zakar\OneDrive\Bureau\PFA\it_certifications_project\data\raw\raw_final_data.json', orient = 'records', indent = 2)
        print('Before cleaning: ', raw_final.shape)

        state.text("Calling the final cleaner...")
        final_cleaner = FinalDataCleaner(r'C:\Users\zakar\OneDrive\Bureau\PFA\it_certifications_project\data\raw\raw_final_data.json')
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

        final_data.to_csv(r'C:\Users\zakar\OneDrive\Bureau\PFA\it_certifications_project\data\pre_predictions_data.csv', index= False)
        print(final_data.shape)
        state.empty()
        return True
    except Exception as e:
        print(f'error {e}')
        state.error("An error has occured while cleaning: {e}. Please try again!")
        return False
















