from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import time
import yaml


def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def get_front_page_results(term, trusted_urls):
    headers = {
        "User-agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
    }

    html = requests.get(f"https://www.google.com/search?q={term}",
                        headers=headers).text

    soup = BeautifulSoup(html, "lxml")

    heading_list = []
    link_list = []
    trusted_url_list = []

    for container in soup.findAll("div", class_="tF2Cxc"):
        heading = container.find("h3", class_="LC20lb DKV0Md").text
        link = container.find("a")["href"]

        heading_list.append(heading)
        link_list.append(link)
        if any(trusted_url in link for trusted_url in trusted_urls):
            trusted_url_list.append(True)
        else:
            trusted_url_list.append(False)

    front_page_results = pd.DataFrame(list(zip(heading_list, link_list, trusted_url_list)),
                                      columns=["heading", "link", "trusted_url"])
    front_page_results['term'] = term
    return front_page_results


if __name__ == "__main__":
    config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config", "config.yaml"))
    config = read_yaml(config_file)

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
            csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "google",
                                                    "front_page_analysis.csv"))
            df.to_csv(csv_path, index=False)
