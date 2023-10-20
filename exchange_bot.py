import aiohttp
import asyncio
import argparse
import datetime

class ExchangeRateFetcher:
    def __init__(self):
        self.session = None

    async def fetch(self, session, date):
        url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"
        async with session.get(url) as response:
            data = await response.json()
            return data

class ExchangeRateService:
    def __init__(self):
        self.fetcher = ExchangeRateFetcher()

    async def get_exchange_rates(self, days):
        exchange_rates = []
        today = datetime.date.today()

        async with aiohttp.ClientSession() as session:
            for i in range(days):
                date = today - datetime.timedelta(days=i)
                formatted_date = date.strftime("%d.%m.%Y")
                data = await self.fetcher.fetch(session, formatted_date)
                eur_rate = None
                usd_rate = None

                if "exchangeRate" in data:
                    for rate in data["exchangeRate"]:
                        if rate["currency"] == "EUR":
                            eur_rate = {"sale": rate["saleRate"], "purchase": rate["purchaseRate"]}
                        elif rate["currency"] == "USD":
                            usd_rate = {"sale": rate["saleRate"], "purchase": rate["purchaseRate"]}

                exchange_rates.append({
                    formatted_date: {
                        'EUR': eur_rate,
                        'USD': usd_rate
                    }
                })

        return exchange_rates

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch exchange rates for EUR and USD from PrivatBank.")
    parser.add_argument("days", type=int, help="Number of days to fetch exchange rates for (up to 10 days)")
    args = parser.parse_args()

    if args.days > 10:
        print("Error: You can fetch exchange rates for up to 10 days only.")
        exit(1)

    loop = asyncio.get_event_loop()
    service = ExchangeRateService()
    exchange_rates = loop.run_until_complete(service.get_exchange_rates(args.days))

    print(exchange_rates)
