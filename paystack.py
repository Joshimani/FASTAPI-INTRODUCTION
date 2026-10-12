import httpx
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

SECRET_KEY = os.getenv("PAYSTACK_API_KEY")

base_url = "https://api.paystack.co"

headers = {
    "Authorization": f"Bearer {SECRET_KEY}",
    "Content-Type": "application/json"
}


async def initialize_payment(email: str, amount: float):

    data = {
        "email": email,
        "amount": int(amount * 100)  
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/transaction/initialize",
            json=data,
            headers=headers
        )

    response.raise_for_status()

    print(response.json())  # 👈 This will print Paystack's response

    return response.json()


async def verify_payment(reference: str):
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/transaction/verify/{reference}",
            headers=headers
        )

        response.raise_for_status()
        print(response.json())

        return response.json()


# async def test_payment():

#     result = await initialize_payment(
#         email="vincentjoy5002@gmail.com",
#         amount=5000
#     )

#     print("Initialization:", result)

#     reference = result["data"]["reference"]

#     verification = await verify_payment(reference)

#     print("Verification:", verification)


# asyncio.run(test_payment())

    