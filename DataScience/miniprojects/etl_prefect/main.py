from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from datetime import timedelta
import pandas as pd


# ---------------------
# TASKS
# ---------------------

@task(retries=2, retry_delay_seconds=5)
def extract_sales(path: str):
    logger = get_run_logger()
    logger.info('Extracting sales data...')
    df = pd.read_csv(path)
    logger.info(f'Extracted {len(df)} rows')
    return df


@task
def validate_schema(df: pd.DataFrame):
    logger = get_run_logger()
    required = ['order_id', 'country', 'product', 'qty', 'price_usd', 'category']
    missing = [c for c in required if c not in df.columns]

    if missing:
        logger.error(f'Missing required columns: {missing}')
        raise ValueError('Invalid schema')

    logger.info('Schema validation passed.')
    return df


@task
def transform_add_revenue(df: pd.DataFrame):
    logger = get_run_logger()
    logger.info('Calculating revenue column...')
    df['revenue'] = df['qty'] * df['price_usd']
    logger.info('Revenue column added.')
    return df


@task
def branch_by_country(df: pd.DataFrame):
    logger = get_run_logger()
    countries = df['country'].unique().tolist()
    logger.info(f'Detected countries: {countries}')
    return countries


@task
def transform_country_summary(df: pd.DataFrame, country: str):
    logger = get_run_logger()
    logger.info(f'Generating summary for country: {country}')
    d = df[df['country'] == country]
    summary = {
        'country': country,
        'orders': len(d),
        'total_revenue': float(d['revenue'].sum()),
        'top_category': d['category'].value_counts().idxmax()
    }
    logger.info(f'Summary for {country}: {summary}')
    return summary


@task
def load_output(summaries: list, output: str):
    logger = get_run_logger()
    df = pd.DataFrame(summaries)
    df = pd.DataFrame()
    if df.empty:
        logger.warning('No data to save')
    else:
        df.to_csv(output, index=False)
        logger.info(f'Output saved to {output}')
    return output


# ---------------------
# FLOW
# ---------------------

@flow(name='Sales Analytics ETL - Prefect Demo')
def sales_etl():
    logger = get_run_logger()
    logger.info('Starting Sales ETL pipeline...')

    df = extract_sales('data/sales_2024.csv')
    df = validate_schema(df)
    df = transform_add_revenue(df)

    countries = branch_by_country(df)

    summaries = []
    for c in countries:
        summary = transform_country_summary(df, c)
        summaries.append(summary)

    output = load_output(summaries, 'data/sales_summary.csv')

    logger.info(f'ETL Finished. Output file: {output}')
    return output


if __name__ == '__main__':
    sales_etl()
