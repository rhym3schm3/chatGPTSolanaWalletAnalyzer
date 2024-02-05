from openai import OpenAI
import os
import requests
from typing import List, Dict, Any

client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY")
)
class Tokens:
    def __init__(self, items: List[Any]):
        self.items = items

# Function to fetch tokens for a given wallet address
def fetch_tokens(wallet_address: str) -> Tokens:
    api_key = os.environ.get("HELIUS_API_KEY")
    url = f'https://mainnet.helius-rpc.com/?api-key={api_key}'
    print(f'Starting search for tokens for wallet address: {wallet_address}')
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "jsonrpc": "2.0",
        "id": "my-id",
        "method": "searchAssets",
        "params": {
            "ownerAddress": wallet_address,
            "tokenType": "all",
            "displayOptions": {
                "showCollectionMetadata": True,
            },
        },
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses
        
        data = response.json()
        
        if not data.get('result'):
            raise ValueError('No data found or an error occurred')
        
        return Tokens(items=data.get('result', []))
    
    except requests.HTTPError as http_err:
        print(f"HTTP error! {http_err}")
        return Tokens(items=[])
    except Exception as err:
        print(f"Error fetching tokens: {err}")
        return Tokens(items=[])

def wallet_analyses(json_payload):
    print(f'Starting chat with ChatGPT')
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Your role is to analyze JSON data about the tokens and NFTs a Solana wallet holds, including using the decimal place value for tokens to calculate the accurate quantity and providing the total price for fungible tokens. For NFTs, output the name of the NFTs and the collection they are part of. For fungible tokens, give the name, quantity (correctly calculated using the decimal place value), price per token, and the total price. Present the data in a clear, concise manner, avoiding speculation on the value or potential of any assets. Ensure accuracy and privacy in handling the data, and clarify any ambiguities by asking questions to ensure correct interpretation of the data."
            },
            {
                "role": "user",
                "content": json_payload
            }
        ]
    )
    print(f'ChatGPT response: {response.choices[0].message.content}')
    return response.choices[0].message.content

def main():
    wallet_address = input("Enter a wallet address to fetch tokens: ")
    try:
        tokens = fetch_tokens(wallet_address)
        wallet_analyses(str(tokens.items))
    except Exception as e:
        print('Error fetching tokens:', str(e))

if __name__ == "__main__":
    main()


