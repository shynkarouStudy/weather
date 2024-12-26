from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import csv
import aiohttp
import asyncio

app = FastAPI()
templates = Jinja2Templates(directory='templates')

cities = {}

def load_cities(filename):
    global cities
    with open(filename, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cities[row["capital"]] = {
                'country': row['country'],
                'lat': float(row['latitude']),
                'lon': float(row['longitude']),
                'weather': 'N/A'
            }
    return cities

load_cities('europe.csv')

@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.get('/update')
async def fetch_weather():
    global cities

    async def fetch_city_weather(city_name):
        city = cities[city_name]
        url =  f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current_weather=true"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Error fetching weather data")
                data = await response.json()
                city['weather'] = f"{data['current_weather']['temperature']:.1f}"

    tasks = [fetch_city_weather(city) for city in cities]
    await asyncio.gather(*tasks)

    return cities
