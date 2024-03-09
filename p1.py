import aiohttp
import asyncio
import sys
import json
import datetime

class CurrencyFetcher:
    def __init__(self):
        self.base_url = "https://api.privatbank.ua/p24api/pubinfo"
        self.supported_currencies = ["EUR", "USD"]

    async def fetch_currency(self, currency, date):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}?json&exchange&coursid=5&date={date}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data:
                        if item['ccy'] == currency:
                            return {
                                'sale': float(item['sale']),
                                'purchase': float(item['buy'])
                            }
                else:
                    print(f"Не вдалося отримати курс {currency} за {date}.")
                    return None

    async def fetch_currencies_for_days(self, days):
        if days > 10:
            days = 10  # Обмеження на кількість днів
        tasks = []
        today = datetime.date.today()
        for i in range(days):
            date = today - datetime.timedelta(days=i)
            for currency in self.supported_currencies:
                tasks.append(self.fetch_currency(currency, date.strftime("%d.%m.%Y")))
        return await asyncio.gather(*tasks)

async def main():
    if len(sys.argv) < 2:
        print("Використання: python p1.py <кількість_днів>")
        return
    else:
        print("Для отримання курсу валют використовуйте наступну команду: python main.py <кількість_днів>")

    try:
        days = int(sys.argv[1])
        if days > 10:
            print("Помилка: Кількість днів не повинна перевищувати 10.")
            return
    except ValueError:
        print("Помилка: Некоректна кількість днів.")
        return

    currency_fetcher = CurrencyFetcher()
    currency_data = await currency_fetcher.fetch_currencies_for_days(days)
    result = []
    today = datetime.date.today()
    for i in range(days):
        date_data = {}
        for currency in currency_fetcher.supported_currencies:
            currency_data_item = currency_data[i * 2] if currency == "EUR" else currency_data[i * 2 + 1]
            date_data[currency] = currency_data_item
        date_key = (today - datetime.timedelta(days=i)).strftime("%d.%m.%Y")
        result.append({
            date_key: date_data
        })
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
