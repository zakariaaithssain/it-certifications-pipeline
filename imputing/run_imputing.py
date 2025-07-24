from imputing.imputer import MissingColumnsPredictor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier

import pandas as pd

df = pd.read_csv(r"C:\Users\zakar\OneDrive\Bureau\PFA\it_certifications_project\data\post_predictions_data.csv")
print(df.describe())
print(df.info())
print(df.columns)
#we should predict the missing domains and levels first and save them to the dataframe, before predicting the cost and duration.
def run_predicting(state = None, progress = None): #those are st related arguments.
    try:
        data = pd.read_csv(r'C:\Users\zakar\OneDrive\Bureau\PFA\it_certifications_project\data\pre_predictions_data.csv')
        useful_columns = data.loc[: , ['Provider', 'Domain', 'Level', 'Cost (USD)', 'Exam Duration (min)']]
        #########################################Level Prediction####################################################
        print('Predicting Missing Levels with DTC...')
        if state is not None: state.text("Predicting missing levels using DTC...")
        level_training_data = pd.get_dummies(data=useful_columns, columns=['Provider','Domain'])[(data['Cost (USD)'] > 0)
                                                                                                 & (data['Exam Duration (min)'] > 0)
                                                                                                 &(data['Domain'] != 'unknown')
                                                                                                 &(data['Level']!= 'unknown')]
        level_model = DecisionTreeClassifier(random_state=37, class_weight='balanced')
        level_predictor = MissingColumnsPredictor(name='Level', model=level_model, training_data=level_training_data, n_splits=5, model_type='classifier')
        level_features = level_predictor.get_optimal_features(progressor=progress)
        level_predictor.train()

        level_input = pd.get_dummies(data=useful_columns, columns=['Provider', 'Domain']).loc[data['Level'] =='unknown', level_features]
        predicted_level = level_predictor.predict(X=level_input)
        data.loc[data['Level'] == 'unknown', 'Level'] = predicted_level

        #########################################Domain Prediction####################################################
        print('Predicting Missing Domains with DTC...')
        if state is not None: state.text("Predicting missing domains using DTC...")
        domain_training_data = pd.get_dummies(data=useful_columns, columns=['Provider','Level']).map(lambda domain: 'business apps'
                                                                            if domain=='it/business'
                                                                            else ('data & other'if domain in ['devops', 'data', 'security']
                                                                            else domain))[(data['Cost (USD)'] > 0)
                                                                                                 & (data['Exam Duration (min)'] > 0)
                                                                                                 &(data['Domain'] != 'unknown')
                                                                                                 &(data['Level']!= 'unknown')]
        domain_model = DecisionTreeClassifier (random_state=37, class_weight='balanced')
        domain_predictor = MissingColumnsPredictor(name='Domain', model=domain_model, training_data=domain_training_data, n_splits=5, model_type='classifier')
        domain_features = domain_predictor.get_optimal_features(progressor=progress)
        domain_predictor.train()

        domain_input = pd.get_dummies(data=useful_columns, columns=['Provider', 'Level']).loc[data['Domain'] =='unknown', domain_features]
        predicted_domain = domain_predictor.predict(X=domain_input)
        data.loc[data['Domain'] == 'unknown', 'Domain'] = predicted_domain


        #########################################Cost Prediction####################################################
        training_data = pd.get_dummies(data=useful_columns, columns=['Provider', 'Domain', 'Level'])[(data['Cost (USD)'] > 0) & (data['Exam Duration (min)'] > 0)]
        print('Predicting Missing Costs with DTR...')
        if state is not None: state.text("Predicting missing costs with DTR...")
        cost_model = DecisionTreeRegressor(random_state=37)
        cost_predictor = MissingColumnsPredictor(name='Cost (USD)', model=cost_model, training_data=training_data, n_splits=5)
        cost_features = cost_predictor.get_optimal_features(progressor=progress)
        cost_predictor.train()

        cost_input = pd.get_dummies(data=useful_columns, columns=['Provider', 'Domain', 'Level']).loc[data['Cost (USD)'] ==0, cost_features]
        predicted_cost = cost_predictor.predict(X=cost_input)
        data.loc[data['Cost (USD)'] == 0, 'Cost (USD)'] = predicted_cost.astype('int64')

        #####################################Duration Prediction#################################################
        print('Predicting Missing Durations with RFR...')
        if state is not None: state.text("Predicting missing durations with RFR...")
        duration_model = RandomForestRegressor(random_state=37)
        duration_predictor = MissingColumnsPredictor(name='Exam Duration (min)', model=duration_model, training_data=training_data, n_splits=5)
        duration_features = duration_predictor.get_optimal_features(progressor=progress)
        duration_predictor.train()

        duration_input = pd.get_dummies(data=useful_columns, columns=['Provider', 'Domain', 'Level']).loc[data['Exam Duration (min)'] ==0, duration_features]
        predicted_duration = duration_predictor.predict(X=duration_input)
        data.loc[data['Exam Duration (min)'] == 0, 'Exam Duration (min)'] = predicted_duration.astype('int64')

        #this is the final data, at least with the provider, domain, level, cost, and duration with no missing values.
        data.to_csv(r'C:\Users\zakar\OneDrive\Bureau\PFA\it_certifications_project\data/post_predictions_data.csv', index= False)
        if state is not None: state.success("Missing values predicted successfully!")
    except Exception as e:
        if state is not None: state.error(f"An error has occured while predicting: {e}. Please try again!")
