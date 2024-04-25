from aiocryptopay import AioCryptoPay, Networks
import asyncio

crypto = AioCryptoPay(token='161242:AAz3s8CZYeaK6rIydSiVNFqjakI2wBep33o', network=Networks.MAIN_NET)


async def main():
    profile = await crypto.get_me()
    currencies = await crypto.get_currencies()
    balance = await crypto.get_balance()
    rates = await crypto.get_exchange_rates()
    check = await crypto.create_check("USDT", 1)
    print(check)

    print(profile, currencies, balance, rates, sep='\n')


asyncio.run(main())
