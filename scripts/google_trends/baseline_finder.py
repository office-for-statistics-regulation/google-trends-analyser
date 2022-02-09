from pytrends.request import TrendReq
import pandas as pd
from tqdm import tqdm
import plotly.express as px
import numpy as np
import os
import random
import yaml


def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


# Normalise function to be used later to find the best performing baseline term
def normalize(df):
    result = df.copy()
    for feature_name in df.columns:
        max_value = abs(df[feature_name].max())
        min_value = abs(df[feature_name].min())
        abs_max_value = max([max_value, min_value])
        result[feature_name] = df[feature_name] / abs_max_value
    return result


def find_baseline_terms(config, plot=True):
    pytrend = TrendReq(hl="en-GB", tz=360)

    interested_terms = config['VARS']['GOOGLETRENDS']['VIABILITY']['TERMS']
    regions = config['VARS']['GOOGLETRENDS']['BASELINE']['REGION']
    random_terms = config['VARS']['GOOGLETRENDS']['BASELINE']['RANDOM']

    timeframe = config['VARS']['TIMEFRAME']

    if timeframe == "7D":
        var_tf = "now 7-d"
    elif timeframe == "30D":
        var_tf = "today -m"
    elif timeframe == "90D":
        var_tf = "today 3-m"
    elif timeframe == "90D":
        var_tf = "today 12-m"
    elif timeframe == "5Y":
        var_tf = "today 5-y"
    elif timeframe == "ALL":
        var_tf = "all"
    else:
        var_tf = "today 12-m"

    # Subsample 5 interested terms at random
    interested_terms = random.sample(interested_terms, 5)

    # used for tqdm progress bar. It's the total number of iterations called
    n = len(regions) * len(random_terms) * len(interested_terms)

    # reads in pre-saved csv that has been compiling, in case of error
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "google_trends",
                                            "baseline_analysis.csv"))
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["term", "baseline", "variance", "dist_between_means", "std"])

    # Iterates through comparison words, and creates baseline random pairs
    with tqdm(total=n) as pbar:
        for interested_term in interested_terms:
            for region in regions:
                for random_term in random_terms:

                    df_check = df["term"] + " " + df["baseline"]

                    # Checks if the interested_term has already been made so doesn't waste an API call
                    if f"{interested_term} {region} {random_term}" not in df_check.to_list():
                        pytrend.build_payload(kw_list=[interested_term, f"{region} {random_term}"],
                                              cat=0,
                                              timeframe=var_tf,
                                              geo="GB")

                        data = pytrend.interest_over_time()
                        variance = data.var()[1]
                        dist_between_means = data.mean()[0] - data.mean()[1]
                        std = data.std()[1]
                        baseline = f"{region} {random_term}"
                        term = interested_term

                        df_tmp = pd.DataFrame([{"term": term, "baseline": baseline, "variance": variance,
                                                "dist_between_means": dist_between_means, "std": std}])
                        df = df.append(df_tmp)

                    # Updates CSV as it goes incase of errors
                    df.to_csv(csv_path, index=False)
                    pbar.update(1)

    # Some basic plots
    if plot:
        # Plots distance between means and variance for all
        fig = px.scatter(df, x="dist_between_means",
                         y="variance",
                         color="term",
                         hover_name="baseline",
                         hover_data=["dist_between_means", "variance", "std"],
                         labels={
                             "dist_between_means": "Distance between means",
                             "variance": "Variance",
                             "std": "Standard deviation"
                         }
                         )
        fig.show()

    # Groups finds and plots
    df_best_grouped_baseline_terms = df.groupby(["baseline"]).mean()

    # normalise terms to find the best one
    df_best_grouped_baseline_terms_norm = df_best_grouped_baseline_terms.copy()
    df_best_grouped_baseline_terms_norm = normalize(df_best_grouped_baseline_terms_norm)

    # Finds the distance to the origin (0,0) which denotes the best performing baseline term overall
    df_best_grouped_baseline_terms_norm["dist_to_origin"] = np.sqrt(
        (df_best_grouped_baseline_terms_norm["dist_between_means"] - 0) ** 2
        + (df_best_grouped_baseline_terms_norm["variance"] - 0) ** 2)

    # Adds this to origin dataframe for colour purposes on plot
    df_best_grouped_baseline_terms["dist_to_origin"] = df_best_grouped_baseline_terms_norm["dist_to_origin"]

    # Finds the best for each column: distance to mean, variance, std, and distance to origin
    best_grouped_baseline_terms = df_best_grouped_baseline_terms_norm.abs().idxmin().to_list()

    if plot:
        # Produces a plot for grouped means and labels the three best performing baseline terms
        fig = px.scatter(df_best_grouped_baseline_terms,
                         x="dist_between_means",
                         y="variance",
                         color="dist_to_origin",
                         color_continuous_scale="viridis",
                         hover_name=df_best_grouped_baseline_terms.index,
                         labels={
                             "dist_between_means": "Distance between means",
                             "variance": "Variance",
                             "dist_to_origin": "Distance to origin",
                             "std": "Standard deviation"
                         }
                         )
        fig.add_annotation(x=df_best_grouped_baseline_terms[df_best_grouped_baseline_terms.index ==
                                                            best_grouped_baseline_terms[0]][
            "dist_between_means"].values[0],
                           y=df_best_grouped_baseline_terms[df_best_grouped_baseline_terms.index ==
                                                            best_grouped_baseline_terms[0]]["variance"].values[0],
                           text=best_grouped_baseline_terms[0],
                           showarrow=False,
                           arrowhead=1)
        fig.add_annotation(x=df_best_grouped_baseline_terms[df_best_grouped_baseline_terms.index ==
                                                            best_grouped_baseline_terms[1]][
            "dist_between_means"].values[0],
                           y=df_best_grouped_baseline_terms[df_best_grouped_baseline_terms.index ==
                                                            best_grouped_baseline_terms[1]]["variance"].values[0],
                           text=best_grouped_baseline_terms[1],
                           showarrow=False,
                           arrowhead=1)
        fig.add_annotation(x=df_best_grouped_baseline_terms[df_best_grouped_baseline_terms.index ==
                                                            best_grouped_baseline_terms[3]][
            "dist_between_means"].values[0],
                           y=df_best_grouped_baseline_terms[df_best_grouped_baseline_terms.index ==
                                                            best_grouped_baseline_terms[3]]["variance"].values[0],
                           text=best_grouped_baseline_terms[3],
                           showarrow=False,
                           arrowhead=1)
        fig.show()

    print(f"The baseline term with the smallest distance between means is {best_grouped_baseline_terms[0]}")
    print(f"The baseline term with the smallest variance is {best_grouped_baseline_terms[1]}")
    print(f"The baseline term with the combined performance score is {best_grouped_baseline_terms[2]}")

    if plot:
        # Plots the best baseline terms
        new_terms = interested_terms[0:2] + best_grouped_baseline_terms
        new_terms = list(dict.fromkeys(new_terms))
        # Checks if the interested_term  has already been made so doesn't waste an API call
        pytrend.build_payload(kw_list=new_terms[0:5],
                              cat=0,
                              timeframe=var_tf,
                              geo="GB")

        data = pytrend.interest_over_time()
        data["time"] = data.index
        data = pd.melt(data, id_vars=["time"], value_vars=new_terms)

        fig = px.line(data,
                      x="time",
                      y="value",
                      color="variable",
                      labels={
                          "value": "Count",
                          "variable": "Term",
                          "time": "Date"}
                      )
        fig.show()

    return best_grouped_baseline_terms[2]
