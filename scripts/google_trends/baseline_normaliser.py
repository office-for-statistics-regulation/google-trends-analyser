from pytrends.request import TrendReq
import yaml


def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def normalise_to_baseline(baseline, term, config):

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

    pytrend = TrendReq(hl='en-GB', tz=360)

    pytrend.build_payload(kw_list=[baseline, term],
                          cat=0,
                          timeframe=var_tf,
                          geo='GB')

    data = pytrend.interest_over_time()
    data[term] = data[term] - data[baseline]
    normalised_data = data.drop(columns=baseline)

    return normalised_data
