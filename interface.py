import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os

from scraping.run_scraping import run_scraping
from cleaning.run_cleaning import run_cleaning
from pruning.run_predicting import run_predicting
from analysis.exploratory_data_analysis import EDA


if 'show_raw_data' not in st.session_state: st.session_state.show_raw_data = False
if 'clean_raw_data' not in st.session_state: st.session_state.clean_raw_data = False
if 'show_clean_data' not in st.session_state: st.session_state.show_clean_data = False
if 'predict' not in st.session_state: st.session_state.predict = False
if 'show_predicted_data' not in st.session_state: st.session_state.show_predicted_data = False
if 'eda' not in st.session_state: st.session_state.eda = False
if 'eda_options' not in st.session_state: st.session_state.eda_options = False


st.title("IT Certifications Pipeline Dashboard")
st.write("Scrape, clean, and analyze metadata of IT certifications from providers: AWS, Microsoft, and CompTIA.")

st.title("Scrape the metadata")
scraping_button = st.button('Run Scraping')

if scraping_button:
    waiting_text = st.text('Scraping might take a while, please be patient!')
    state = st.empty()
    progress = st.progress(0)
    scraper_feedback = run_scraping(state= state, progress=progress)

    if scraper_feedback: st.success(f"Metadata has been scraped successfully!")
    else: st.error(f"Scraping failed, please try again!")

    st.session_state.show_raw_data = True
    state.empty()
    waiting_text.empty()

if st.session_state.get('show_raw_data', False):
    show_raw_button = st.button("Show Scraped Data")
    if show_raw_button:
        for raw_file in ["CompTIA", "AWS", "Microsoft"]:
            file_path = os.path.join(fr'C:\Users\zakar\OneDrive\Bureau\PFA\it_certifications_project\data\raw\raw_{raw_file}_certifications.json')
            try:
                df = pd.read_json(file_path)
                st.markdown(f"### {raw_file}: ###")
                st.write(df)
                st.session_state.clean_raw_data = True
            except Exception as e:
                st.error(f"Failed to load data for {raw_file}: {e}")


if st.session_state.get('clean_raw_data', False):
    st.title("Clean the metadata")
    clean_raw_button = st.button(" Clean & Concatenate Scraped Data")
    if clean_raw_button:
        state = st.empty()
        progress = st.progress(0)
        if run_cleaning(state= state, progress=progress):
            st.success("Metadata cleaned successfully!")
            st.session_state.show_clean_data = True


if st.session_state.get('show_clean_data', False):
    show_clean_button = st.button("Show Cleaned Data")
    if show_clean_button:
        try:
            df = pd.read_csv(r'C:\Users\zakar\OneDrive\Bureau\PFA\it_certifications_project\data\pre_predictions_data.csv')
            st.markdown("### Cleaned Data: ###")
            st.write(df)
            st.session_state.predict = True
        except Exception as e:
            st.error(f"Failed to load cleaned data: {e}")

if st.session_state.get('predict', False):
    st.title("Predict the missing values")
    predict_button = st.button(" Predict Missing Values")
    if predict_button:
        state = st.empty()
        progress = st.progress(0)
        waiting_text = st.text('Predicting might take a while, please be patient!')
        run_predicting(state = state, progress= progress)
        waiting_text.empty()
        st.session_state.show_predicted_data = True

if st.session_state.get('show_predicted_data', False):
    show_predicted_button = st.button("Show Final Data")
    if show_predicted_button:
        try:
            df = pd.read_csv(r'C:\Users\zakar\OneDrive\Bureau\PFA\it_certifications_project\data\post_predictions_data.csv')
            st.markdown("### Final Data: ###")
            st.write(df)
            st.session_state.eda = True
        except Exception as e:
            st.error(f"Failed to load final data: {e}")

if st.session_state.get('eda', False):
    eda_button = st.button("Explore")
    st.session_state.eda_options = True

if st.session_state.get('eda_options', False):
    options = ['Certifications per Level and Provider',
               'Avg Cost per Level and Provider',
               'Avg Duration per Level and Provider',
               'Top Five Languages',
               'Cost distribution (USD)',
               'Duration distribution (min)',
               'Cost boxplot (USD)',
               'Duration boxplot (min)',
               'Certifications per Domain'
               ]
    select_button = st.selectbox(label= 'Select plot type:', options=options)
    fig, axe = plt.subplots()
    post = pd.read_csv(r'C:\Users\zakar\OneDrive\Bureau\PFA\it_certifications_project\data\post_predictions_data.csv')
    post_eda = EDA(post)
    plot_functions = {
        'Certifications per Level and Provider':
        post_eda.nbre_certification_per_lvl_and_provider,
        'Avg Cost per Level and Provider': post_eda.avg_cost_per_lvl_and_provider,
        'Avg Duration per Level and Provider': post_eda.avg_duration_per_lvl_and_provider,
        'Top Five Languages': post_eda.top_five_languages,
        'Cost distribution (USD)': post_eda.cost_distribution,
        'Duration distribution (min)': post_eda.duration_distribution,
        'Cost boxplot (USD)': post_eda.cost_boxplot,
        'Duration boxplot (min)': post_eda.cost_boxplot,
        'Certifications per Domain': post_eda.nbre_certification_per_domain
    }
    plot_functions[select_button](axe=axe, st=True)










