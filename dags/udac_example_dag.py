from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators import (
    StageToRedshiftOperator,
    LoadFactOperator,
    LoadDimensionOperator,
    DataQualityOperator,
)
from helpers import SqlQueries
import create_tables

CREATE_TABLE_SQLS = [
    "staging_events_table",
    "staging_songs_table",
    "songplays_table",
    "artists_table",
    "songs_table",
    "time_table",
    "users_table",
]

DIM_TABLES = ["songs", "artists", "users", "time"]

default_args = {
    "owner": "udacity",
    "start_date": datetime(2021, 5, 1),
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "catchup": False,
    "email_on_retry": False,
}

dag = DAG(
    "udac_example_dag",
    default_args=default_args,
    description="Load and transform data in Redshift with Airflow",
    schedule_interval=None #'@hourly',
)

start_task = DummyOperator(task_id="begin_execution", dag=dag)

tables_created_task = DummyOperator(task_id="tables_created", dag=dag)

# dynamically create tasks to create the tables
for create_table_sql in CREATE_TABLE_SQLS:
    create_task = PostgresOperator(
        task_id=f"create_{create_table_sql}",
        dag=dag,
        postgres_conn_id="redshift_conn",
        sql=eval("create_tables.{0}".format(create_table_sql)),
    )

    start_task >> create_task >> tables_created_task


stage_events_task = StageToRedshiftOperator(
    task_id="stage_events",
    dag=dag,
    db_conn_id="redshift_conn",
    db_table="staging_events",
    aws_conn_id="aws_conn",
    s3_bucket="udacity-dend",
    s3_key="log_data",
    db_extra="FORMAT AS JSON 's3://udacity-dend/log_json_path.json' \
                                                      IGNOREHEADER 1",
)

stage_songs_task = StageToRedshiftOperator(
    task_id="stage_songs",
    dag=dag,
    db_conn_id="redshift_conn",
    db_table="staging_songs",
    aws_conn_id="aws_conn",
    s3_bucket="udacity-dend",
    s3_key="song_data",
    db_extra="JSON 'auto'",
)

load_songplays_task = LoadFactOperator(
    task_id="load_songplays_fact_table",
    dag=dag,
    postgres_conn_id="redshift_conn",
    sql=f"INSERT INTO public.songplays ({SqlQueries.songplay_table_insert});"
)

tables_loaded_task = DummyOperator(task_id="tables_loaded", dag=dag)

# dinamically create tasks to load dimension tables
for table in DIM_TABLES:
    load_dim_table = LoadDimensionOperator(
        task_id=f"load_{table}_dim_table",
        dag=dag,
        postgres_conn_id="redshift_conn",
        table=table,
        mode="delete-load",
        sql=eval('SqlQueries.{0}_table_insert'.format(table))
    )

    load_songplays_task >> load_dim_table >> tables_loaded_task

run_quality_checks = DataQualityOperator(
    task_id="run_data_quality_checks", 
    dag=dag,
    db_conn_id = "redshift_conn",
    tables=["songplays","songs", "artists", "users", "time"]
)

end_task = DummyOperator(task_id="stop_execution", dag=dag)

tables_created_task >> stage_events_task >> load_songplays_task
tables_created_task >> stage_songs_task >> load_songplays_task
tables_loaded_task >> run_quality_checks >> end_task
