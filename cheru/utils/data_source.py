import sqlite3
import os
from nonebot.log import logger

DB_DIR = os.path.expanduser('~/.cheru/data/')


class sqlite:
    def __init__(self, db_name: str, table_name: str, column_name: list):
        '''
        初始化数据库

        param: db_name 数据库名称

        param: table_name 表名

        param: column_name 列名

        '''
        self.dir_name = DB_DIR + db_name + '.db'
        os.makedirs(os.path.dirname(self.dir_name), exist_ok=True)
        self.conn = None
        self.cursor = None
        self._create_table(table_name, column_name)

    def _connect(self):
        self.conn = sqlite3.connect(self.dir_name)
        self.cursor = self.conn.cursor()

    def _create_table(self, table, colunm):
        try:
            colunm_name = ''
            for item in colunm:
                colunm_name += f'{item} VARCHAR(4000) NOT NULL,'
            colunm_name = colunm_name[:-1]
            self._connect()
            self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table}
            (GID INTEGER PRIMARY KEY AUTOINCREMENT,
            {colunm_name}
            );''')
            self.conn.commit()
        except Exception as e:
            logger.error(e)

    def insertOrUpdate(self, table: str, colunm: list, data):
        '''
        插入/更新

        param: table 表名

        param: colunm 列名

        param: data 对应列的值

        用法：

        table = 'table1'

        colunm = ['colunm1', 'colunm2']

        data = ('1', '2')

        insertOrUpdate(table, colunm, data)
        '''
        try:
            colunm_name = ','
            colunm_name = colunm_name.join([item for item in colunm])
            vallen = len(colunm)
            values = ','
            values = values.join(['?' for item in range(vallen)])
            sql = f'INSERT OR REPLACE INTO {table}({colunm_name}) VALUES({values})'
            self.cursor.execute(sql, data)
            self.conn.commit()
        except Exception as e:
            logger.error(e)
            self.conn.rollback()

    def select(self, table: str, colunm: str, data) -> list:
        '''
        查询数据

        param: table 表名

        param: colunm 列名

        param: data 对应列的值

        用法：

        table = 'table1'

        colunm = 'colunm1'

        data = '1'

        data_list = select(table, colunm, data)
        '''
        try:
            sql = f'SELECT * FROM {table} WHERE {colunm}=?'
            result = self.cursor.execute(sql, [data]).fetchall()
            if len(result) == 0:
                return []
            return result
        except Exception as e:
            logger.error(e)

    def delete(self, table: str, colunm: str, data):
        '''
        删除数据

        param: table 表名

        param: colunm 列名

        param: data 对应列的值

        用法：

        table = 'table1'

        colunm = 'colunm1'

        data = '1'

        delete(table, colunm, data)
        '''
        try:
            sql = f'DELETE FROM {table} WHERE {colunm}=?'
            self.cursor.execute(sql, data)
            self.conn.commit()
        except Exception as e:
            logger.error(e)
            self.conn.rollback()

    def delete_all(self, table: str):
        '''
        删除所有数据

        param: table 表名

        param: colunm 列名

        用法：

        table = 'table1'

        colunm = 'colunm1'

        delete_all(table, colunm)
        '''
        try:
            sql = f'DELETE FROM {table}'
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            logger.error(e)
            self.conn.rollback()
