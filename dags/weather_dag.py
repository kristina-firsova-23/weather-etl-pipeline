from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Импортируем нашу ETL функцию
import sys
from pathlib import Path

# Добавляем путь к корню проекта, чтобы найти etl_weather.py
sys.path.append(str(Path(__file__).parent.parent))

from etl_weather import run_etl

# Аргументы по умолчанию для DAG
default_args = {
    'owner': 'me',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Создаем DAG, который будет выполняться каждый день в 09:00
with DAG(
    'weather_etl_petropavlovsk',
    default_args=default_args,
    description='ETL for Petropavlovsk-Kamchatsky weather',
    schedule_interval='0 9 * * *',  # каждый день в 9 утра
    catchup=False,
) as dag:

    # Задача на выполнение ETL
    run_etl_task = PythonOperator(
        task_id='run_etl_script',
        python_callable=run_etl  # Это имя функции должно быть в etl_weather.py
    )

    # Задача на успешное завершение
    notify_task = BashOperator(
        task_id='print_success',
        bash_command='echo "ETL pipeline finished successfully at $(date)"'
    )

    run_etl_task >> notify_task  # Зависимости: сначала ETL, потом уведомление
