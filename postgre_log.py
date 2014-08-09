import psycopg2
import weechat


SCRIPT_NAME = "postgre_log"
SCRIPT_AUTHOR = "Seulgi Kim <dev@seulgik.im>"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENCE = "GPL3"
SCRIPT_DESC = "Save messages in PostgreSQL"


connect = None


def check_table_exists():
    cursor = connect.cursor()
    try:
        query = ("SELECT *"
                 "  FROM information_schema.tables"
                 "  WHERE table_name='weechat_message'")
        cursor.execute(query)
        return cursor.rowcount == 1
    except Exception as ex:
        weechat.prnt('', "Exception in check_tabke_exists: %s" % ex.message)
        raise ex
    finally:
        cursor.close()


def create_table():
    cursor = connect.cursor()
    try:
        query = ("CREATE TABLE weechat_message ("
                 "  id SERIAL PRIMARY KEY,"
                 "  username CHAR(16) NOT NULL,"
                 "  servername VARCHAR(64) NOT NULL,"
                 "  channelname VARCHAR(50) NOT NULL,"
                 "  message VARCHAR(512) NOT NULL,"
                 "  hilight CHAR(1) NOT NULL,"
                 "  command VARCHAR(16) NOT NULL,"
                 "  time TIMESTAMP WITH TIME ZONE NOT NULL)")
        cursor.execute(query)
        connect.commit()
    except Exception as ex:
        weechat.prnt('', "Exception in create_table: %s" % ex.message)
        raise ex
    finally:
        cursor.close()


def main():
    global connect
    connect = psycopg2.connect(dbname='weechat', user='weechat')
    if not check_table_exists():
        create_table()


def shutdown_cb():
    if connect:
        connect.close()


if __name__ == '__main__':
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
                        SCRIPT_LICENCE, SCRIPT_DESC, 'shutdown_cb', ''):
        main()
