from data.markets import get_market_data
from config.assets import COMMODITIES


def get_commodity_data():

    return get_market_data(COMMODITIES)