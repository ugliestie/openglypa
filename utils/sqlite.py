import sqlite3 as sq

db = sq.connect('./groups_settings.db')
cur = db.cursor()


async def db_start():
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS group_commands_settings (
                        group_id TEXT PRIMARY KEY,
                        text BOOLEAN DEFAULT 1,
                        topor BOOLEAN DEFAULT 1,
                        demotivators BOOLEAN DEFAULT 1,
                        memes BOOLEAN DEFAULT 1,
                        polls BOOLEAN DEFAULT 1
                    )
                ''')
    cur.execute('''
                    CREATE TABLE IF NOT EXISTS group_automatic_settings (
                        group_id TEXT PRIMARY KEY,
                        lazyness INTEGER DEFAULT 95,
                        text BOOLEAN DEFAULT 1,
                        topor BOOLEAN DEFAULT 1,
                        demotivators BOOLEAN DEFAULT 1,
                        memes BOOLEAN DEFAULT 1,
                        polls BOOLEAN DEFAULT 1
                    )
                ''')
    db.commit()

async def check_group(group_id):
    user = cur.execute("SELECT * FROM group_commands_settings WHERE group_id == {key}".format(key=group_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO group_commands_settings (group_id) VALUES ({key})".format(key=group_id))
        cur.execute("INSERT INTO group_automatic_settings (group_id) VALUES ({key})".format(key=group_id))
        db.commit()

async def get_commands_settings(group_id):
    row = cur.execute('SELECT text, topor, demotivators, memes, polls FROM group_commands_settings WHERE group_id = ?', (group_id,)).fetchone()
    if row is None:
        await check_group(group_id)
        return (1, 1, 1, 1, 1)
    return row

async def get_automatic_settings(group_id):
    row = cur.execute('SELECT text, topor, demotivators, memes, polls FROM group_automatic_settings WHERE group_id = ?', (group_id,)).fetchone()
    if row is None:
        await check_group(group_id)
        return (1, 1, 1, 1, 1)
    return row

async def set_setting(type_setting, kind_setting, setting, group_id):
    if type_setting == "commands":
        if kind_setting == "text":
            cur.execute('UPDATE group_commands_settings SET text = ? WHERE group_id = ?', (setting, group_id))
        elif kind_setting == "topor":
            cur.execute('UPDATE group_commands_settings SET topor = ? WHERE group_id = ?', (setting, group_id))
        elif kind_setting == "demotivators":
            cur.execute('UPDATE group_commands_settings SET demotivators = ? WHERE group_id = ?', (setting, group_id))
        elif kind_setting == "memes":
            cur.execute('UPDATE group_commands_settings SET memes = ? WHERE group_id = ?', (setting, group_id))
        elif kind_setting == "polls":
            cur.execute('UPDATE group_commands_settings SET polls = ? WHERE group_id = ?', (setting, group_id))
    elif type_setting == "automatic":
        if kind_setting == "text":
            cur.execute('UPDATE group_automatic_settings SET text = ? WHERE group_id = ?', (setting, group_id))
        elif kind_setting == "topor":
            cur.execute('UPDATE group_automatic_settings SET topor = ? WHERE group_id = ?', (setting, group_id))
        elif kind_setting == "demotivators":
            cur.execute('UPDATE group_automatic_settings SET demotivators = ? WHERE group_id = ?', (setting, group_id))
        elif kind_setting == "memes":
            cur.execute('UPDATE group_automatic_settings SET memes = ? WHERE group_id = ?', (setting, group_id))
        elif kind_setting == "polls":
            cur.execute('UPDATE group_automatic_settings SET polls = ? WHERE group_id = ?', (setting, group_id))
    db.commit()

async def get_automatic_generations(group_id):
    row = cur.execute('SELECT lazyness, text, topor, demotivators, memes, polls FROM group_automatic_settings WHERE group_id = ?', (group_id,)).fetchone()
    if row is None:
        await check_group(group_id)
        return (95, 1, 1, 1, 1, 1)
    return row

async def update_lazyness(lazyness, group_id):
    cur.execute('UPDATE group_automatic_settings SET lazyness = ? WHERE group_id = ?', (lazyness, group_id))
    db.commit()