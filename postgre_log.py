import psycopg2
import traceback
import weechat


SCRIPT_NAME = "postgre_log"
SCRIPT_AUTHOR = "Seulgi Kim <dev@seulgik.im>"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENCE = "GPL3"
SCRIPT_DESC = "Save messages in PostgreSQL"


_connection = None
_msg_hook = None
_part_hook = None
_join_hook = None


def is_table_exists():
    global _connection
    cursor = _connection.cursor()
    try:
        query = ("SELECT *"
                 "  FROM information_schema.tables"
                 "  WHERE table_name='weechat_message'")
        cursor.execute(query)
        return cursor.rowcount == 1
    finally:
        cursor.close()


def create_table_if_not_exists():
    global _connection
    if is_table_exists():
        return
    cursor = _connection.cursor()
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
        _connection.commit()
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
    global _connection
    cursor = _connection.cursor()
    try:
        query = ("INSERT INTO"
                 "  weechat_message (username, servername, channelname,"
                 "    message, hilight, command, time)"
                 "  VALUES (%s, %s, %s, %s, %s, %s,"
                 "    to_timestamp(%s))")
        cursor.execute(query, [username, servername, channelname, message,
                               hilight, command, time])
        _connection.commit()
    finally:
        cursor.close()


def postgre_log_enable_cb(data, buffer, args):
    global _connection
    global _msg_hook
    global _join_hook
    global _part_hook

    try:
        _connection = psycopg2.connect(args)
    except psycopg2.OperationalError as ex:
        weechat.prnt('', 'Valid connection string is required.')
        return weechat.WEECHAT_RC_ERROR

    create_table_if_not_exists()
    _msg_hook = weechat.hook_print('', 'irc_privmsg', '', 1, 'msg_cb',
                                   'PRIVMSG')
    _join_hook = weechat.hook_print('', 'irc_join', '', 1, 'log_cb', 'JOIN')
    _part_hook = weechat.hook_print('', 'irc_part', '', 1, 'log_cb', 'PART')
    return weechat.WEECHAT_RC_OK


def postgre_log_disable_cb(data=None, buffer=None, args=None):
    global _connection
    global _msg_hook
    global _join_hook
    global _part_hook
    if _connection is None:
        weechat.prnt('', "postgre_log is already disabled.")
        return weechat.WEECHAT_RC_OK
    _connection.close()
    _connection = None
    if _msg_hook:
        weechat.unhook(_msg_hook)
        _msg_hook = None
    if _join_hook:
        weechat.unhook(_join_hook)
        _join_hook = None
    if _part_hook:
        weechat.unhook(_part_hook)
        _part_hook = None
    return weechat.WEECHAT_RC_OK


def shutdown_cb():
    return postgre_log_disable_cb()


if __name__ == '__main__':
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
                        SCRIPT_LICENCE, SCRIPT_DESC, 'shutdown_cb', ''):
        weechat.hook_command('postgre_log_enable', "Enable the postgre log.",
                             'connection_string', '', '',
                             'postgre_log_enable_cb', '')
        weechat.hook_command('postgre_log_disable', "Disable the postgre log.",
                             '', '', '', 'postgre_log_disable_cb', '')
