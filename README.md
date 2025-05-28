Weather Data Forecasting using Airflow

📌 Project Overview
This project demonstrates a simple yet powerful ETL (Extract, Transform, Load) pipeline that automates the process of fetching weather data from the Open-Meteo API, transforming it using Python, orchestrating the workflow via Apache Airflow, and loading the processed data into a PostgreSQL database running inside a Docker container. The stored data can then be visualized or queried using DBeaver.

🔄 ETL Flow Summary
1)Extract
Real-time weather data is fetched from the Open-Meteo API using a Python script.

2)Transform
The raw JSON data is processed and cleaned using pandas (or plain Python), ensuring it's in a tabular format suitable for database storage.

3)Load
The transformed data is inserted into a PostgreSQL database. Airflow manages this step to ensure automation, retries, and proper logging.

4)Orchestrate with Airflow
Apache Airflow manages the entire ETL pipeline using a DAG (Directed Acyclic Graph). Each step (Extract → Transform → Load) is a task that runs inside the Airflow environment.

5)Dockerized Environment
Both Airflow and PostgreSQL run inside Docker containers, ensuring easy setup and consistency across environments.

6)Visualize in DBeaver
The final weather data can be explored and analyzed using the DBeaver GUI, which connects directly to the Dockerized PostgreSQL instance.

