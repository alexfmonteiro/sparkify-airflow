from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 postgres_conn_id,
                 table,
                 mode,
                 sql,
                 *args, **kwargs):
        
        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.postgres_conn_id=postgres_conn_id
        self.table=table
        self.mode=mode
        self.sql=sql

    def execute(self, context):
        if self.mode not in ['append-only','delete-load']:
            raise ValueError(f"Mode parameter should be 'append-only' or 'delete-load'.")
        
        self.log.info(f"LoadDimensionOperator: Loading {self.table} data")

        pg_hook  = PostgresHook(postgres_conn_id=self.postgres_conn_id)

        t_sql = ''
        if self.mode == 'delete-load':
            t_sql = f'TRUNCATE TABLE public.{self.table}; '

        i_sql = f"INSERT INTO public.{self.table} ({self.sql});"
        f_sql = t_sql + i_sql 
        pg_hook.run(f_sql)
        
        self.log.info(f"LoadDimensionOperator: {self.table} data loaded")
