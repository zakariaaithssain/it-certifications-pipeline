from exploratory_data_analysis import EDA
import pandas as pd

data_before_predictions = pd.read_csv(r'../data/pre_predictions_data.csv')
data_after_predictions = pd.read_csv(r'../data/post_predictions_data.csv')

eda_before = EDA(data_before_predictions)
print('Saving Plots of Pre-Predictions Data...')
eda_before.plot_all(directory_path= r'EDA\eda_before_predictions')

eda_after = EDA(data_after_predictions)
print('Saving Plots of Post-Predictions Data...')
eda_after.plot_all(directory_path= r'EDA\eda_after_predictions')
