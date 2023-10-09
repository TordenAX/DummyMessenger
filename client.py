import aiohttp
import asyncio
import random
import time

SERVERS = ['http://localhost:8000', 'http://localhost:8001']  # Список адресов серверов
NAMES = ['Alice', 'Bob', 'Charlie', 'David', 'Emma', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack']
NUM_REQUESTS = 5000  # Количество запросов
CONCURRENT_REQUESTS = 50  # Количество одновременно запущенных корутин


async def send_message(session, url, sender, text, start_time):
    async with session.post(url, json={'sender': sender, 'text': text}) as response:
        response_data = await response.json()
        request_time = time.time() - start_time
        print(f"Response: {response_data}, Request Time: {request_time}")


async def run_requests(session, semaphore):
    for _ in range(NUM_REQUESTS):
        async with semaphore:
            server_url = random.choice(SERVERS)
            sender = random.choice(NAMES)
            text = f"Message {random.randint(1, 100)}"
            request_start_time = time.time()
            await send_message(session, server_url, sender, text, request_start_time)


async def main():
    sem = asyncio.Semaphore(CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(CONCURRENT_REQUESTS):
            tasks.append(run_requests(session, sem))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    program_start_time = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    program_end_time = time.time()
    total_time = program_end_time - program_start_time
    request_time_per_request = total_time / NUM_REQUESTS
    throughput = NUM_REQUESTS / total_time
    print(f"Total Time: {total_time} seconds")
    print(f"Request Time per Request: {request_time_per_request} seconds")
    print(f"Throughput: {throughput} requests per second")
