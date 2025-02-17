import sqlite3
import pandas as pd
import os

class SQLiteLoader:
    def __init__(self, db_name: str, table_name: str, file_path: str):
        self.db_name = db_name
        self.table_name = table_name
        self.file_path = file_path

        db_folder = 'databases'

        # Si la carpeta no existe, la crea
        if not os.path.exists(db_folder):
            os.makedirs(db_folder)
            
        self.conn = sqlite3.connect(os.path.join(db_folder, 'data.db'))
        self.cursor = self.conn.cursor()

    def load_data(self):
        '''Carga el dataset a dataframe'''
        self.df = pd.read_csv(self.file_path, index_col=0).head(100)
        print('Datos cargados desde el CSV.')

    def create_table(self):
        '''Crea la tabla si no existe, detectando los tipos de datos desde el DataFrame'''
        columns_types = []
        for col, dtype in self.df.dtypes.items():
            if 'int' in str(dtype):
                col_type = 'INTEGER'
            elif 'float' in str(dtype):
                col_type = 'REAL'
            else:
                col_type = 'TEXT'
            columns_types.append(f'{col} {col_type}')
        create_query = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({', '.join(columns_types)})"
        
        self.cursor.execute(create_query)
        self.conn.commit()
        print('Tabla creada o ya existente.')

    def insert_data(self):
        '''Inserta los datos en la tabla'''
        placeholders = ', '.join(['?' for _ in self.df.columns])
        insert_query = f'INSERT INTO {self.table_name} VALUES ({placeholders})'
        self.cursor.executemany(insert_query, self.df.values.tolist())
        self.conn.commit()
        print('Datos insertados en la base de datos.')

    def close_connection(self):
        '''Cierra la conexión con la base de datos'''
        self.conn.close()
        print('Conexión cerrada.')

# Uso del código
db_loader = SQLiteLoader('data.db', 'dataset', 'DataScience/datasets/wine-reviews/winemag-data_first150k.csv')
db_loader.load_data()
db_loader.create_table()
db_loader.insert_data()
db_loader.close_connection()
