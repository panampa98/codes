import os
import pandas as pd
import pyodbc
from tqdm import tqdm

class SQLServerLoader:
    '''
    SQLServerLoader automatically:
    - Reads one CSV file or all CSVs inside a folder.
    - Uses the CSV filename as the SQL Server table name.
    - Detects SQL types based on pandas dtypes.
    - Auto-creates the SQL Server table.
    '''

    def __init__(self, server: str, database: str, source_path: str):
        self.server = server
        self.database = database
        self.source_path = source_path

        self.conn = self.connect_sql_server()
        self.cursor = self.conn.cursor()

        self.files = self.collect_csv_files()
        self.process_files()

    # 1. SQL Server connection
    def connect_sql_server(self):
        conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            'Trusted_Connection=yes;'
        )
        print('Connecting to SQL Server...')
        return pyodbc.connect(conn_str, autocommit=True)

    # 2. Detect CSVs
    def collect_csv_files(self):
        if os.path.isfile(self.source_path):
            return [self.source_path]

        elif os.path.isdir(self.source_path):
            return [
                os.path.join(self.source_path, f)
                for f in os.listdir(self.source_path)
                if f.lower().endswith('.csv')
            ]

        raise ValueError('source_path must be a CSV file or a folder containing CSV files.')

    # 3. Process files
    def process_files(self):
        for file_path in self.files:
            print(f'\n➡ Processing file: {file_path}')

            table_name = os.path.splitext(os.path.basename(file_path))[0]
            print(f'   → Using table name: {table_name}')

            df = self.load_dataframe(file_path)
            self.create_table(table_name, df)
            self.insert_data(table_name, df)

    # 4. Load CSV
    def load_dataframe(self, file_path):
        df = pd.read_csv(file_path)

        for col in df.select_dtypes(include=['object']).columns:
            try:
                df[col] = pd.to_datetime(df[col], format='mixed').dt.tz_localize(None)
            except Exception:
                pass

        return df

    # 5. Map pandas dtype → SQL type
    def map_dtype_to_sql(self, dtype):
        dtype = str(dtype)

        if 'int' in dtype:
            return 'INT'
        if 'float' in dtype:
            return 'FLOAT'
        if 'datetime' in dtype:
            return 'DATETIME'
        if 'bool' in dtype:
            return 'BIT'

        return 'VARCHAR(255)'

    # 6. Create SQL table
    def create_table(self, table_name, df):
        print(f"   → Creating table '{table_name}'...")

        col_defs = []

        for col, dtype in df.dtypes.items():
            sql_type = self.map_dtype_to_sql(dtype)
            col_defs.append(f'[{col}] {sql_type}')

        create_sql = f'''
        IF NOT EXISTS (
            SELECT * FROM sysobjects
            WHERE name = '{table_name}' AND xtype = 'U'
        )
        CREATE TABLE [{table_name}] (
            {', '.join(col_defs)}
        );
        '''

        self.cursor.execute(create_sql)
        print(f"   ✔ Table '{table_name}' created or already exists.")

    # 7. Insert data
    def insert_data(self, table_name, df, chunk_size=5000):
        print(f"   → Inserting data into '{table_name}'...")

        # Enable optimized batch insertion
        self.cursor.fast_executemany = True

        # Convert datetime columns
        for col in df.columns:
            if 'datetime' in str(df[col].dtype):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Replace NaN with None
        df = df.where(pd.notnull(df), None)

        # Prepare SQL INSERT
        columns = df.columns.tolist()
        sql_cols = ', '.join(f'[{c}]' for c in columns)
        placeholders = ', '.join(['?'] * len(columns))

        insert_sql = f"""
        INSERT INTO [{table_name}] ({sql_cols})
        VALUES ({placeholders})
        """

        records = df.values.tolist()
        total_rows = len(records)

        print(f"   → Total rows to insert: {total_rows:,}")

        # Insert using chunks with progress bar
        for i in tqdm(range(0, total_rows, chunk_size), desc="   → Progress"):
            chunk = records[i:i+chunk_size]
            self.cursor.executemany(insert_sql, chunk)

        print(f"   ✔ Inserted {total_rows:,} rows successfully.")

    # 8. Close
    def close(self):
        self.conn.close()
        print('\nConnection closed.')


if __name__ == '__main__':
    loader = SQLServerLoader(
        server='DESKTOP-21KF01T',
        database='LogisticsOps2022_2024',
        source_path=r'D:\DevPold\Kaggle\logistics-operations-database'
    )
    loader.close()
