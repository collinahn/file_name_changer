
import os
import sqlite3
from sqlite3.dbapi2 import Connection

DB_FILE = './db/addr.db'
TXT_FILE = './db/entrc_incheon.txt'

def set_db():
    #파일이 없는 경우
    if os.path.exists(DB_FILE) == False:
        conn: Connection = None

        try:
            conn = sqlite3.connect(DB_FILE)
        except sqlite3.Error as e: 
            print(e)
        finally:
            if conn: 
                conn.close()

    query = """CREATE TABLE IF NOT EXISTS tMstSpecs ( \
                districtCode TEXT NOT NULL, \
                entranceCode TEXT NOT NULL, \
                lawCode TEXT NOT NULL, \
                siDoName TEXT NOT NULL, \
                siGunGuName TEXT NOT NULL, \
                eupMyenDongName TEXT NOT NULL, \
                roadAddrCode TEXT NOT NULL, \
                roadAddrName TEXT NOT NULL, \
                isBase TEXT, \
                buildingNo TEXT, \
                buildingSubNo TEXT, \
                buildingName TEXT, \
                addressCode TEXT NOT NULL, \
                buildingUsage TEXT, \
                buildingOption TEXT, \
                controllingDong TEXT, \
                xCoord REAL NOT NULL, \
                yCoord REAL NOT NULL \
                )"""

    try:
        conn = sqlite3.connect(DB_FILE, isolation_level=None) 
        curs: Connection = conn.cursor()

        #테이블 세팅
        curs.execute(query)

        print('table init')

    except sqlite3.Error as e: 
        print(e)
    finally:
        if conn: 
            conn.close()

def fill_data_from_txt():
    dataSplited2Lst: list[tuple] = []
    with open(TXT_FILE, 'r', encoding='UTF-8') as rows:
        for row in rows:
            dataSplited2Lst.append(_get_records(row))
            
    _insert_db(dataSplited2Lst)


def _get_records(string):
    emptyRecordsExcluded = string.replace('||', '|Null|')
    return tuple(emptyRecordsExcluded.split('|'))

def _insert_db(lst4executemany) -> bool:
    conn: Connection = None

    if not len(lst4executemany):
        return False

    # 데이터 Values() 개수 정함
    queryValue = '? ' * len(lst4executemany[0])
    queryValueStriped = queryValue.strip()
    queryValueComplete = queryValueStriped.replace(' ', ', ') # "?, ?, ?, ?, ?, ?"(들어오는 개수에 맞춰서)

    try:
        conn = sqlite3.connect(DB_FILE, isolation_level=None)
        conn.row_factory = sqlite3.Row
        curs = conn.cursor()
        query = "INSERT INTO tMstSpecs Values(" + queryValueComplete +");"
        curs.executemany(query, (lst4executemany))
        conn.close()

    except sqlite3.Error as e: 
        print(e)
        if conn:
            conn.close()
        return False
    
    return True


if __name__ == '__main__':
    set_db()
    fill_data_from_txt()