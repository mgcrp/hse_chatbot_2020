from time import sleep
import sqlalchemy as sa


pg_conn_string = 'postgresql+psycopg2://chatbot_user:chatbot_password@localhost:5432/chatbot'


def execute_sql_safe(query, engine, query_name, tries=1, sleep_seconds=10):
    cnt = 0
    sql_flag = False

    while not sql_flag:
        try:
            print(f'Начинаю execute {query_name}')
            engine.execution_options(autocommit=True).execute(query)
            print(f'Закончил execute {query_name}')
            sql_flag = True
            engine.dispose()
        except sa.exc.SQLAlchemyError:
            engine.dispose()
            sql_flag = False
            cnt += 1
            if cnt >= tries:
                print(f"Выполнение sql запроса выполнено с ошибкой. Попытки закончились, rais'им ошибку")
                raise
            else:
                print(f'Выполнение sql запроса выполнено с ошибкой. жду {sleep_seconds} сек. и пробую снова')
                sleep(sleep_seconds)
        except Exception:
            engine.dispose()
            raise
