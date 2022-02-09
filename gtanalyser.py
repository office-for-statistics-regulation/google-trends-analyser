import os
import pandas as pd
import plotly.express as px
import time
from scripts.google_trends.baseline_finder import find_baseline_terms
from scripts.google_trends.baseline_normaliser import normalise_to_baseline
from scripts.google_trends.term_checker import check_term_viability
from scripts.google.front_page import get_front_page_results
import yaml


def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


save_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "outputs"))


def run(plot):
    config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "config", "config.yaml"))
    config = read_yaml(config_file)
    find_viability = config['RUN']['GOOGLETRENDS']['VIABILITY']['FIND']
    get_baseline = config['RUN']['GOOGLETRENDS']['BASELINE']['FIND']
    do_baseline = config['RUN']['GOOGLETRENDS']['BASELINE']['DO']
    get_front_page = config['RUN']['GOOGLE']['FRONTPAGE']['DO']

    if find_viability:
        print('Finding which interested terms are viable')
        check_term_viability(config)
    else:
        print('Term viability not checked, using all terms')

    if get_baseline:
        print('\nFinding the best baseline term based on the values in the config file')
        baseline_term = find_baseline_terms(config, plot=False)
    else:
        print('Using the baseline term specified in the config file')
        baseline_term = config['VARS']['GOOGLETRENDS']['BASELINE']['FORCE'][0]

    if do_baseline:
        if find_viability:
            df = pd.read_csv(f'{save_path}/google_trends/term_viability.csv')
            df_viable = df[df['viable'] == True]
            terms = df_viable['term'].tolist()
        else:
            terms = config['VARS']['GOOGLETRENDS']['VIABILITY']['TERMS']

        for term in terms:
            df_tmp = normalise_to_baseline(baseline=baseline_term, term=term, config=config)
            df_tmp = df_tmp.drop(columns=["isPartial"])
            if term == terms[0]:
                df = df_tmp
            else:
                df = df.merge(df_tmp, left_index=True, right_index=True, how="inner")

        df["time"] = df.index
        df = df.reset_index()
        df = pd.melt(df, id_vars=["time"], value_vars=terms)
        print(f"Saving file to {save_path}")
        df.to_csv(os.path.join(save_path, "google_trends/normalised_trends.csv"))
        if plot == True:
            fig = px.line(df, x="time", y="value", color="variable")
            fig.show()
            fig.write_image(os.path.join(save_path, "google_trends/normalised_trends.svg"))

    if get_front_page:
        interested_terms = config['VARS']['GOOGLE']['INTERESTED']
        trusted_urls = config['VARS']['GOOGLE']['TRUSTEDURLS']
        for interested_term in interested_terms:
            print({interested_term})
            df_tmp = get_front_page_results(term=interested_term,
                                            trusted_urls=trusted_urls)
            time.sleep(10)

            if interested_term == interested_terms[0]:
                df = df_tmp
            else:
                df = df.append(df_tmp)
                csv_path = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "outputs", "google", "front_page_analysis.csv"))
                df.to_csv(csv_path, index=False)


run(plot=True)
