import requests
from typing import Dict

async def get_crypto_currency(name: str) -> Dict[str, str]:
    url = f"http://localhost:8095/coinmarketcap/api/crypto/{name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception("Error occurred while fetching data from the API")

async def format_value_data(data: Dict[str, str]) -> str:
    # Implement your formatting logic here based on the ValueDto class structure
    # Example formatting: symbol - price - volume_24h
    formatted_text = f"{data['symbol']} - {data['price']} - {data['volume_24h']}"
    return formatted_text