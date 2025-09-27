import time
import asyncio
import aiohttp  # para peticiones asíncronas
import pandas as pd
import io  # <<--- para StringIO

# -------------------
# Función normal (def)
# -------------------
def get_dataset_sync(urls):
    '''Descarga datasets de forma secuencial'''
    datasets = []
    for url in urls:
        print(f'Descargando (sync): {url}')
        df = pd.read_csv(url)  # espera a que termine
        datasets.append(df)
    return datasets

# ----------------------
# Función asíncrona (async)
# ----------------------
async def fetch_dataset(session, url):
    '''Descarga un dataset de forma asíncrona'''
    print(f'Descargando (async): {url}')
    async with session.get(url) as response:
        content = await response.read()
        return pd.read_csv(io.StringIO(content.decode()))

async def get_dataset_async(urls):
    '''Descarga datasets de forma concurrente'''
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_dataset(session, url) for url in urls]
        datasets = await asyncio.gather(*tasks)
    return datasets


# ----------------------
# Ejemplo de uso
# ----------------------
urls = [
    'https://people.sc.fsu.edu/~jburkardt/data/csv/airtravel.csv',
    'https://people.sc.fsu.edu/~jburkardt/data/csv/hw_200.csv',
    'https://people.sc.fsu.edu/~jburkardt/data/csv/grades.csv'
]

# Con funciones normales
start = time.time()
datasets_sync = get_dataset_sync(urls)
print(f'Tiempo sync: {time.time()-start:.2f} seg')

# Con funciones asíncronas
start = time.time()
datasets_async = asyncio.run(get_dataset_async(urls))
print(f'Tiempo async: {time.time()-start:.2f} seg')

# Procesar ejemplo: ver tamaños de cada dataset
for i, df in enumerate(datasets_async, 1):
    print(f'Dataset {i} tiene {df.shape[0]} filas y {df.shape[1]} columnas')
