from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
import logging
import pendulum  # ✅ use pendulum instead of days_ago

# Constants
LATITUDE = '18.641156'
LONGITUDE = '73.682952'
POSTGRES_CONN_ID = 'postgres_default'
API_CONN_ID = 'open_meteo_api'

default_args = {
    'owner': 'airflow',
    'start_date': pendulum.today("UTC").subtract(days=1),  # ✅ updated here
    'retries': 2,
}

# DAG definition
with DAG(
    dag_id='weather_etl_pipeline',
    default_args=default_args,
    schedule='* * * * *',  # ✅ Airflow 2.9+ uses 'schedule'
    catchup=False,
    description='ETL pipeline to fetch weather data and load into PostgreSQL'
) as dag:

    @task()
    def extract_weather_data():
        logging.info("Starting weather data extraction...")
        http_hook = HttpHook(http_conn_id=API_CONN_ID, method='GET')
        endpoint = f'/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true'
        response = http_hook.run(endpoint)

        if response.status_code == 200:
            logging.info("Weather data extraction successful.")
            return response.json()
        else:
            logging.error(f"Failed to fetch weather data: {response.status_code}")
            raise Exception(f"Failed to fetch weather data: {response.status_code}")

    @task()
    def transform_weather_data(weather_data):
        logging.info("Transforming weather data...")
        current_weather = weather_data['current_weather']
        transformed_data = {
            'latitude': float(LATITUDE),
            'longitude': float(LONGITUDE),
            'temperature': current_weather['temperature'],
            'windspeed': current_weather['windspeed'],
            'winddirection': current_weather['winddirection'],
            'weathercode': current_weather['weathercode']
        }
        logging.info(f"Transformed data: {transformed_data}")
        return transformed_data

    @task()
    def load_weather_data(transformed_data):
        logging.info("Loading weather data into PostgreSQL...")
        try:
            pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
            conn = pg_hook.get_conn()
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_data (
                latitude FLOAT,
                longitude FLOAT,
                temperature FLOAT,
                windspeed FLOAT,
                winddirection FLOAT,
                weathercode INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cursor.execute("""
            INSERT INTO weather_data (latitude, longitude, temperature, windspeed, winddirection, weathercode)
            VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                transformed_data['latitude'],
                transformed_data['longitude'],
                transformed_data['temperature'],
                transformed_data['windspeed'],
                transformed_data['winddirection'],
                transformed_data['weathercode']
            ))

            conn.commit()
            cursor.close()
            logging.info("Weather data successfully loaded into PostgreSQL.")
        except Exception as e:
            logging.error(f"Error loading data into PostgreSQL: {str(e)}")
            raise

    # ETL Workflow
    weather_data = extract_weather_data()
    transformed_data = transform_weather_data(weather_data)
    load_weather_data(transformed_data)
