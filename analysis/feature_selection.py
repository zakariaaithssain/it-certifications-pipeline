import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.model_selection import cross_val_score
from tqdm import tqdm
from exploratory_data_analysis import EDA



#I am aiming to predict the missing levels (resp. domains) of certifications based on their Provider, Domain (resp. Level), Cost, and Duration.
#Logistic regression, is used to predict categorical outcome, linear is for numerical outcomes.

data = pd.read_csv(r'../data/pre_predictions_data.csv')
print(data.Domain.value_counts())
model = LogisticRegression(max_iter=10500)

lvl_training_data = data[(data['Cost (USD)'] > 0) & (data['Exam Duration (min)'] > 0) & (data['Domain'] != 'unknown') & (data['Level'] != 'unknown')]
#One-hot for domain and provider as ml models accept only numerical data
lvl_features = pd.get_dummies(lvl_training_data, columns= ['Domain', 'Provider']).drop(columns=['Level', 'Certification', 'Languages', 'Official Link', 'Description', 'Recommended Experience', ])
lvl_target = lvl_training_data.Level

domain_training_data = data[(data['Cost (USD)'] > 0) & (data['Exam Duration (min)'] > 0) & (data['Domain'] != 'unknown')]
#One-hot for level and provider as ml models accept only numerical data
domain_features = pd.get_dummies(domain_training_data, columns= ['Level', 'Provider']).drop(columns=['Domain', 'Certification', 'Languages', 'Official Link', 'Description', 'Recommended Experience', ])
domain_target = domain_training_data.Domain.map(lambda domain: 'data & other'
                                                if domain in ['it/business', 'devops', 'data']
                                                else domain) #to fix the problem of the cv.

#to choose between forward and backward selection, and the number of lvl_features to select, based on cross valuation
selector_direction = ['forward', 'backward']
lvl_best_selector, lvl_best_score = None, 0
domain_best_selector, domain_best_score = None, 0

for direction in selector_direction:
    print(f'evaluating {direction.capitalize()} features selection for Level prediction...')
    for n in tqdm(range(2, len(lvl_features.columns))):
        selector = SequentialFeatureSelector(estimator= model, n_features_to_select= n, direction= direction)
        selector.fit(lvl_features, lvl_target)
        score = cross_val_score(estimator= model, X=lvl_features[lvl_features.columns[selector.get_support()]], y=lvl_target, cv = 3).mean()
        if score > lvl_best_score:
            lvl_best_score = score
            lvl_best_selector = selector

    print(f'evaluating {direction.capitalize()} features selection for Domain prediction...')
    for n in tqdm(range(2, len(domain_features.columns))):
        selector = SequentialFeatureSelector(estimator= model, n_features_to_select= n, direction= direction, cv = 3)
        selector.fit(domain_features, domain_target)
        score = cross_val_score(estimator= model, X=domain_features[domain_features.columns[selector.get_support()]], y=domain_target, cv =3).mean()
        if score > domain_best_score:
            domain_best_selector = selector
            domain_best_score = score


lvl_optimal_features = lvl_features.columns[lvl_best_selector.get_support()].tolist()
print("Features to Keep According to The Optimal Selector for Level Prediction: ", lvl_optimal_features)
#training for lvl prediction:
lvl_X = lvl_features[lvl_optimal_features]
lvl_y = lvl_target
model.fit(lvl_X, lvl_y)
#predicting missing levels:
records_with_unknown_lvl = data[data['Level'] == 'unknown'].copy()
X_of_unknown_lvl = records_with_unknown_lvl[lvl_optimal_features]
predicted_lvl = model.predict(X_of_unknown_lvl)
# this sits the predicted levels in their places
data.loc[data['Level'] == 'unknown', 'Level'] = predicted_lvl

domain_optimal_features = domain_features.columns[domain_best_selector.get_support()].tolist()
print("Features to Keep According to The Optimal Selector for Domain Prediction: ", domain_optimal_features)
#training for domain prediction:
domain_X = domain_features[domain_optimal_features]
domain_y = domain_target
model.fit(domain_X, domain_y)
#predicting missing domains:
records_with_unknown_domain = pd.get_dummies(data = data, columns= ['Level', 'Provider'])[data['Domain'] == 'unknown']
X_of_unknown_domain = records_with_unknown_domain[domain_optimal_features]
predicted_domain = model.predict(X_of_unknown_domain)
# this sits the predicted domains in their places
data.loc[data['Domain'] == 'unknown', 'Domain'] = predicted_domain
data.to_csv(r'..\data\with_lvl_domain_predicted.csv', index= False)
