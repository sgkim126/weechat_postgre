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


def msg_cb(command, buf, date, tags, displayed, hilight, username, msg):
    servername = weechat.buffer_get_string(buf, 'localvar_server')
    channelname = weechat.buffer_get_string(buf, 'short_name')
    insert_log(servername, channelname, username, msg, hilight, command, date)
    return weechat.WEECHAT_RC_OK


def log_cb(command, buf, date, tags, displayed, hilight, prefix, msg):
    servername = weechat.buffer_get_string(buf, 'localvar_server')
    channelname = weechat.buffer_get_string(buf, 'short_name')
    username = msg.split()[0]
    insert_log(servername, channelname, username, msg, hilight, command, date)
    return weechat.WEECHAT_RC_OK


def insert_log(servername, channelname, username, message, hilight,
               command, time):
    cursor = connect.cursor()
    try:
        query = ("INSERT INTO"
                 "  weechat_message (username, servername, channelname,"
                 "    message, hilight, command, time)"
                 "  VALUES ('%s', '%s', '%s', '%s', %s, '%s',"
                 "    to_timestamp(%s))")
        cursor.execute(query %
                       (username, servername, channelname,
                        message, hilight, command, time))
        connect.commit()
    except Exception as ex:
        weechat.prnt('', "Exception in insert_message: %s" % ex.message)
        raise ex
    finally:
        cursor.close()


def main():
    global connect
    connect = psycopg2.connect(dbname='weechat', user='weechat')
    if not check_table_exists():
        create_table()
    weechat.hook_print('', 'irc_privmsg', '', 1, 'msg_cb', 'PRIVMSG')
    weechat.hook_print('', 'irc_join', '', 1, 'log_cb', 'JOIN')
    weechat.hook_print('', 'irc_part', '', 1, 'log_cb', 'PART')


def shutdown_cb():
    global connect
    if connect:
        connect.close()


if __name__ == '__main__':
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
                        SCRIPT_LICENCE, SCRIPT_DESC, 'shutdown_cb', ''):
        main()
