from datetime import datetime
from decimal import Decimal
from typing import Dict

import requests


async def get_crypto_currency(access_token: str, name: str) -> Dict[str, str]:
    url = f"http://localhost:8095/coinmarketcap/api/crypto/{name}"
    # Include the access token as a bearer token in the Authorization header
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception("Error occurred while fetching data from the API")


async def format_value_data(dto: Dict[str, str]) -> str:
    formatted_str = f"Symbol: {dto['symbol']}\n"
    formatted_str += f"Price: {format_decimal(dto['price'])}\n"
    formatted_str += f"24h Volume: {format_decimal(dto['volume_24h'])}\n"
    formatted_str += f"24h Volume Change: {format_decimal(dto['volume_change_24h'])}%\n"
    formatted_str += f"1h Percent Change: {format_decimal(dto['percent_change_1h'])}%\n"
    formatted_str += f"24h Percent Change: {format_decimal(dto['percent_change_24h'])}%\n"
    formatted_str += f"7d Percent Change: {format_decimal(dto['percent_change_7d'])}%\n"
    formatted_str += f"30d Percent Change: {format_decimal(dto['percent_change_30d'])}%\n"
    formatted_str += f"60d Percent Change: {format_decimal(dto['percent_change_60d'])}%\n"
    formatted_str += f"90d Percent Change: {format_decimal(dto['percent_change_90d'])}%\n"
    formatted_str += f"Market Cap: {format_decimal(dto['market_cap'])}\n"
    formatted_str += f"Market Cap Dominance: {format_decimal(dto['market_cap_dominance'])}%\n"
    formatted_str += f"Fully Diluted Market Cap: {format_decimal(dto['fully_diluted_market_cap'])}\n"
    # formatted_str += f"TVL: {dto['tvl']}\n"
    formatted_str += f"Last Updated: {format_datetime(dto['last_updated'])}"

    return formatted_str


def format_decimal(value: str) -> str:
    if value is not None:
        try:
            decimal_value = Decimal(value)
            return "{:,.2f}".format(decimal_value)
        except ValueError:
            return "N/A"
    else:
        return "N/A"


def format_datetime(value: str) -> str:
    if value is not None:
        try:
            timestamp = int(value)
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return "Invalid Timestamp"
    else:
        return "N/A"
