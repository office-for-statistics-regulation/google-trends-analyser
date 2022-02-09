# google-trends-analyser

Python code to analyse terms on Google Trends. Built on the [pytrends](https://github.com/GeneralMills/pytrends) package.
Functions have been created to: 1) check the viability of terms (is data present? are there gaps?), 2) find a baseline
term to compare results against, 3) run normalisation against this baseline term, 4) check whether the results from
Google are from trusted websites.

### Getting

To clone locally use:

`git clone https://github.com/office-for-statistics-regulation/google-trends-analyser`

### Setting

To install requirements `cd` to the cloned folder and use:

`pip install -r requirements.txt`

### Configuration

Please update the `config.yaml` file with your requirements, including whether you want the `gtanalyser.py` script to
check term viability, find a baseline, whether you want terms to be normalised to a baseline, and whether you want
to check Google.

### Using

To run:

`python gtanalyser.py`

This will call functions in `/scripts/`
This will save the tweets to the `/outputs/` folder.

### Acknowledgements

This code uses the [pytrends](https://github.com/GeneralMills/pytrends) package.