from pytrends.request import TrendReq
import pandas as pd
from tqdm import tqdm
import numpy as np
import os
import yaml


def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def check_term_viability(config):
    pytrend = TrendReq(hl="en-GB", tz=360)

    interested_terms = config['VARS']['GOOGLETRENDS']['VIABILITY']['TERMS']
    zero_counts = config['VARS']['GOOGLETRENDS']['VIABILITY']['ZEROCOUNT']
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
    # 7D, 30D, 90D, 12M, 5Y, ALL

    # used for the tqdm progress bar. It's the total number of iterations called
    n = len(interested_terms)

    # reads in pre-saved csv that has compiled, in case of errors
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "google_trends",
                                            "term_viability.csv"))
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["term", "data_present", "data_gaps", "viable", "comments"])

    # Iterates through interested_terms from config file
    with tqdm(total=n) as pbar:
        for interested_term in interested_terms:
            # Checks if the interested_term has already been made so doesn't waste an API call
            if f"{interested_term}" not in df["term"].to_list():
                pytrend.build_payload(kw_list=[interested_term],
                                      cat=0,
                                      timeframe=var_tf,
                                      geo="GB")

                data = pytrend.interest_over_time()

                # Conditional statements for checking data viability as set in config file
                if len(data) == 0:
                    data_present = False
                    data_gaps = False
                    viable = False
                    comments = 'No data'
                elif np.where(data.iloc[:, 0].values == 0)[0].size >= zero_counts['ALMOSTNONE']:
                    data_present = True
                    data_gaps = True
                    viable = False
                    comments = 'Almost no usable data'
                elif zero_counts['MANY'] <= np.where(data.iloc[:, 0].values == 0)[0].size < zero_counts['ALMOSTNONE']:
                    data_present = True
                    data_gaps = True
                    viable = False
                    comments = 'Many data gaps'
                elif zero_counts['FEW'] <= np.where(data.iloc[:, 0].values == 0)[0].size < zero_counts['MANY']:
                    data_present = True
                    data_gaps = True
                    viable = False
                    comments = 'Some data gaps'
                elif zero_counts['VIABLE'] <= np.where(data.iloc[:, 0].values == 0)[0].size < zero_counts['FEW']:
                    data_present = True
                    data_gaps = True
                    viable = False
                    comments = 'Few data gaps'
                else:
                    data_present = True
                    data_gaps = False
                    viable = True
                    comments = ''

                df_tmp = pd.DataFrame([{"term": interested_term, "data_present": data_present,
                                        "data_gaps": data_gaps, "viable": viable, "comments": comments}])
                df = df.append(df_tmp)

            # Updates CSV as it goes incase of errors
            df.to_csv(csv_path, index=False)
            pbar.update(1)
