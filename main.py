import asyncio
import logging
import websockets
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
import aiohttp
import datetime
import aiofiles
from aiopath import AsyncPath

logging.basicConfig(level=logging.INFO)

class Server:
    clients = set()
    log_file = "exchange_logs.txt"

    async def register(self, ws: WebSocketServerProtocol):
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def log_exchange_command(self):
        async with aiofiles.open(self.log_file, mode='a') as file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await file.write(f"{timestamp}: 'exchange' command executed\n")

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.startswith('exchange'):
                command, *args = message.split(' ')
                if len(args) != 1 or not args[0].isdigit():
                    await ws.send("Invalid command. Usage: exchange N")
                    continue
                days = int(args[0])
                currency_data = await self.fetch_currency_data(days)
                await ws.send(currency_data)
                await self.log_exchange_command()  # Запис логу в файл
            else:
                await self.send_to_clients(f"{ws.remote_address}: {message}")

    async def fetch_currency_data(self, days: int):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5') as response:
                if response.status == 200:
                    data = await response.json()
                    history_data = data[-days:]
                    message = ""
                    for day_data in history_data:
                        message += f"{day_data['ccy']}: Buy - {day_data.get('buy', 'N/A')}, Sell - {day_data.get('sale', 'N/A')}\n"
                    return message
                else:
                    return "Failed to fetch currency data"

async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
