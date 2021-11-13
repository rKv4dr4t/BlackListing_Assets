# BlackListing_Crypto
Put in white list every crypto in your Binance account that won't to automatically sell. Any other crypto isn't in white list, will sell it returning USDT

## Setup
- Install [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- Generate API keys in Binance and put them in `config.py`
- Change crypto to white listing and fee, in `app.py` (r. 18-19)
- Change optionally value in USDT to overcome for black listing, in `app.py` (r. 26)
- Go to the current folder and run project: `python app.py`
- Go to `127.0.0.1:80` in your browser
