import requests
import telebot
from telebot import types
from telebot.types import Message, CallbackQuery
from random import randint
from data import db_session
from data.users import User
from data.battles import Battles

TOKEN = ""

# url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
# key = "trnsl.1.1.20170208T075729Z.cdce3a3db4e5107e.64d6e22f16d94000532fc4f6ab51fe55704ea7b6"
# url = "https://fasttranslator.herokuapp.com/api/v1/text/to/text"
url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=ru&tl=en&dt=t&q="

bot = telebot.TeleBot(TOKEN)

BUTTONS = ["/rules", "/ДобавитьДрузей", "/СписокДрузей", "/ОдиночныйРежим", "/ОнлайнИгра"]

CURRENT_LANG = {"user_id": "rus"}
IS_PUSHED_BUTTON = set()

db_session.global_init("db/digital_war.db")


@bot.message_handler(commands=["start", "help", "home"])
def start(message: Message):
    print(message)
    bot.send_message(message.chat.id, "Привет, это DigitalWarGame! "
                                      "Игра, в которую можно поиграть с друзьями в свободное время!"
                                      "(ты же любишь стратегии😉)")

    _id = message.from_user.id

    db_sess = db_session.create_session()

    # con = sqlite3.connect(DB)
    # cur = con.cursor()

    # cur.execute(f"SELECT * FROM users WHERE ID = '{_id}'")
    # data = cur.fetchone()

    data  = db_sess.query(User).filter(User.id == f"{_id}").first()

    print(data)
    usrname = message.from_user.username
    if not usrname:
        bot.send_message(message.from_user.id, "У вас нет имени пользователя @username, создайте его "
                         "в настройках телеграмма и перезапустите бота")
        return
    if not data:
        user = User()
        user.id = f"{_id}"
        user.username = f"{message.from_user.username}"
        user.friends = "0"

        db_sess.add(user)
        db_sess.commit()

        # cur.execute(f"INSERT INTO users(ID, username, friends) VALUES ('{_id}', '{message.from_user.username}', '0')")

    # con.commit()
    # con.close()

    markup = types.ReplyKeyboardMarkup()
    butts = []
    texts = BUTTONS[:]
    for text in texts:
        butts.append(types.KeyboardButton(text))
    markup.add(*butts)

    global CURRENT_LANG
    CURRENT_LANG[_id] = "rus"

    bot.send_message(message.from_user.id, "Давай начнем", reply_markup=markup)


@bot.message_handler(commands=["rules"])
def rules(message: Message):
    with open("rules.txt", "r", encoding="UTF-8") as f:
        text = f.read()

    m = types.InlineKeyboardMarkup()
    butt = types.InlineKeyboardButton(text="Русский", callback_data=f"translate_rus")
    butt1 = types.InlineKeyboardButton(text="English", callback_data=f"translate_eng")
    m.add(butt)
    m.add(butt1)

    with open("rules.png", "rb") as file:
        data = file.read()

    bot.send_photo(message.from_user.id, photo=data)
    bot.send_message(message.from_user.id, text, reply_markup=m)


@bot.message_handler(commands=["ДобавитьДрузей"])
def add_friends(message: Message):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton("/home"))
    bot.send_message(message.chat.id, "Для добавления друга, необходимо ввести его @username, или нажмите кнопку Home", reply_markup=markup)
    with open("bot_info.png", "rb") as file:
        data = file.read()
    msg = bot.send_photo(message.from_user.id, photo=data)
    bot.register_next_step_handler(msg, take_username_friend)


def take_username_friend(message: Message):
    if "/home" in message.text:
        markup = types.ReplyKeyboardMarkup()
        butts = []
        texts = BUTTONS[:]
        for text in texts:
            butts.append(types.KeyboardButton(text))
        markup.add(*butts)

        bot.send_message(message.from_user.id, "Давай начнем", reply_markup=markup)
    elif message.text.startswith("@"):
        username_friend = message.text.strip().lstrip("@")

        db_sess = db_session.create_session()

        # con = sqlite3.connect(DB)
        # cur = con.cursor()

        # cur.execute(f"SELECT ID, username, friends FROM users WHERE username = '{username_friend}'")
        # data = cur.fetchone()

        data = db_sess.query(User).filter(User.username == f"{username_friend}").first()

        if not data:
            bot.send_message(message.from_user.id, "К сожалению такого пользователя нет в игре:(\nНо Вы можете добавить его по ссылке:")
            bot.send_message(message.from_user.id, "t.me/digital_war_game_bot")
        else:
            id_us, name, friends = data.id, data.username, data.friends

            current_us = message.from_user.username
            # data = cur.execute(f"SELECT friends, ID FROM users WHERE username = '{current_us}'").fetchone()[0]
            data = db_sess.query(User).filter(User.username == f"{current_us}").first()
            if username_friend not in data.friends:
                m = types.InlineKeyboardMarkup()
                butt = types.InlineKeyboardButton(text="Принять", callback_data=f"yes_{current_us}")
                butt1 = types.InlineKeyboardButton(text="Отклонить", callback_data=f"no_{current_us}")
                m.add(butt)
                m.add(butt1)
                bot.send_message(id_us, f"К Вам пришла заявка в друзья от: @{current_us}", reply_markup=m)



        # con.commit()
        # con.close()


@bot.callback_query_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    if call.data.startswith("yes_"):
        user = call.data[4:]

        db_sess = db_session.create_session()

        # con = sqlite3.connect(DB)
        # cur = con.cursor()

        # cur.execute(f"SELECT ID, username, friends FROM users WHERE username = '{call.from_user.username}'")
        # data = cur.fetchone()

        data = db_sess.query(User).filter(User.username == f"{call.from_user.username}").first()
        if data:
            id_us, name, friends = data.id, data.username, data.friends
            if user not in friends:
                friends += f";{user}"
            # cur.execute(f"UPDATE users SET friends='{friends}' WHERE ID='{id_us}'")
            data.friends = friends
            db_sess.commit()

        # cur.execute(f"SELECT ID, username, friends FROM users WHERE username = '{user}'")
        # data = cur.fetchone()

        data = db_sess.query(User).filter(User.username == f"{user}").first()
        if data:
            id_us, name, friends = data.id, data.username, data.friends
            if call.from_user.username not in friends:
                friends += f";{call.from_user.username}"
            # cur.execute(f"UPDATE users SET friends='{friends}' WHERE ID='{id_us}'")
            data.friends = friends
            db_sess.commit()

            bot.send_message(id_us, f"Пользователь @{call.from_user.username} добавил Вас в друзья!")


        # con.commit()
        # con.close()

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Done!', reply_markup=None)

    if call.data.startswith("del_"):
        user = call.data[4:]

        db_sess = db_session.create_session()

        # con = sqlite3.connect(DB)
        # cur = con.cursor()

        # cur.execute(f"SELECT ID, username, friends FROM users WHERE username = '{call.from_user.username}'")
        # data = cur.fetchone()
        data = db_sess.query(User).filter(User.username == f"{call.from_user.username}").first()
        k = False
        my_fr = []
        if data:
            id_us, name, friends = data.id, data.username, data.friends

            if user in friends:
                k = True
                fr = friends.split(";")
                del fr[fr.index(user)]
                friends = ";".join(fr)
                # cur.execute(f"UPDATE users SET friends='{friends}' WHERE ID='{id_us}'")
                data.friends = friends
                db_sess.commit()
            my_fr = friends[:]

        # cur.execute(f"SELECT ID, username, friends FROM users WHERE username = '{user}'")
        # data = cur.fetchone()
        data = db_sess.query(User).filter(User.username == f"{user}").first()
        if data:
            id_us, name, friends = data.id, data.username, data.friends

            if call.from_user.username in friends:
                k = True
                fr = friends.split(";")
                del fr[fr.index(call.from_user.username)]
                friends = ";".join(fr)
                # cur.execute(f"UPDATE users SET friends='{friends}' WHERE ID='{id_us}'")
                data.friends = friends
                db_sess.commit()
            if k:
                bot.send_message(id_us, f"Пользователь @{call.from_user.username} удалил Вас из друзей:(")

        # con.commit()
        # con.close()

        m = types.InlineKeyboardMarkup(row_width=2)
        for friend in my_fr.split(";")[1:]:
            butt = types.InlineKeyboardButton(text=f"{friend}", callback_data=f"None")
            butt1 = types.InlineKeyboardButton(text="❌", callback_data=f"del_{friend}")
            m.add(butt, butt1)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Done!', reply_markup=m)

    if call.data.startswith("invite_"):
        user = call.data[7:]
        db_sess = db_session.create_session()
        # con = sqlite3.connect(DB)
        # cur = con.cursor()

        # cur.execute(f"SELECT ID, player1, player2, id_board_1, id_board_2 FROM battles WHERE (player1 = '{call.from_user.username}' OR "
        #             f"player2 = '{call.from_user.username}') AND isPlaying = 1")
        # data = cur.fetchall()
        data = db_sess.query(Battles)\
            .filter((Battles.player1 == f'{call.from_user.username}') | (Battles.player2 == f'{call.from_user.username}'))\
            .filter(Battles.isPlaying == 1).all()
        for i in data:
            if i:
                idg, pl1, pl2, b1, b2 = i.id, i.player1, i.player2, i.id_board_1, i.id_board_2
                if pl1 == call.from_user.username:
                    plw = pl2
                    bw = b2
                    bl = b1
                else:
                    plw = pl1
                    bw = b1
                    bl = b1
                # cur.execute(f"UPDATE battles SET winner = '{plw}', isPlaying = 0 WHERE ID = {idg}")
                i.winner = f"{plw}"
                db_sess.commit()

                # id_plw = cur.execute(f"SELECT ID, username FROM users WHERE username = '{plw}'").fetchone()[0]
                id_plw = db_sess.query(User).filter(User.username == f'{plw}').first()
                bot.edit_message_text(chat_id=id_plw.id, message_id=bw, text='Соперник бежал!',
                                      reply_markup=None)
                bot.delete_message(chat_id=call.from_user.id, message_id=bl)


        # con.commit()

        m = types.InlineKeyboardMarkup()
        butt = types.InlineKeyboardButton(text="Принять", callback_data=f"inv_yes_{call.from_user.username}")
        butt1 = types.InlineKeyboardButton(text="Отклонить", callback_data=f"inv_no_{call.from_user.username}")
        m.add(butt)
        m.add(butt1)
        # idus = cur.execute(f"SELECT ID, username FROM users WHERE username = '{user}'").fetchone()[0]
        idus = db_sess.query(User).filter(User.username == f'{user}').first()
        bot.send_message(idus.id, f"К Вам пришел вызов от: @{call.from_user.username}", reply_markup=m)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Done!',
                              reply_markup=None)

        # con.close()

    if call.data.startswith("inv_yes_"):
        user = call.data[8:]

        db_sess = db_session.create_session()
        # con = sqlite3.connect(DB)
        # cur = con.cursor()

        # cur.execute(f"SELECT ID, username, friends FROM users WHERE username = '{call.from_user.username}'")
        # data = cur.fetchone()
        # if data:
        #     id_us, name, friends = data
        #     if user not in friends:
        #         friends += f";{user}"
        #     cur.execute(f"UPDATE users SET friends='{friends}' WHERE ID='{id_us}'")

        # cur.execute(f"SELECT ID, username, friends FROM users WHERE username = '{user}'")
        # data = cur.fetchone()
        # if data:
        #     id_us, name, friends = data
        #     if call.from_user.username not in friends:
        #         friends += f";{call.from_user.username}"
        #     cur.execute(f"UPDATE users SET friends='{friends}' WHERE ID='{id_us}'")
        #     bot.send_message(id_us, f"Пользователь @{call.from_user.username} добавил Вас в друзья!")

        board = [str(randint(0, 9)) for _ in range(randint(5, 20))]
        # cur.execute(f"INSERT INTO battles(player1, player2, id_board_1, id_board_2, position, step, winner, isPlaying) "
        #             f"VALUES ('{user}', '{call.from_user.username}', '', '', '{''.join(board)}', '{user}', '-1', 1)")

        battle = Battles()
        battle.player1 = f'{user}'
        battle.player2 = f'{call.from_user.username}'
        battle.position = f'{"".join(board)}'
        battle.step = f'{user}'
        battle.winner = '-1'
        battle.isPlaying = 1
        db_sess.add(battle)
        db_sess.commit()


        # id_game = cur.execute(f"SELECT ID, isPlaying FROM battles WHERE player1 = '{user}' AND "
        #                       f"player2 = '{call.from_user.username}' AND "
        #                       f"isPlaying = 1").fetchone()[0]
        id_game = db_sess.query(Battles).filter(Battles.player1 == f'{user}',
                                                Battles.player2 == f'{call.from_user.username}',
                                                Battles.isPlaying == 1).first()

        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton("/stop_game"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Done!',
                              reply_markup=None)
        bot.send_message(call.from_user.id, "Подключаю к противнику...", reply_markup=markup)

        m = types.InlineKeyboardMarkup(row_width=8)
        b_m = [types.InlineKeyboardButton(text=board[i], callback_data=f"step_{id_game.id}_{i}_{call.from_user.username}") for i in range(len(board))]
        m.add(*b_m)
        a = bot.send_message(call.from_user.id, f"Игра идет!\nХод: @{user}...", reply_markup=m)
        b2 = a.id

        # idus = cur.execute(f"SELECT ID, username FROM users WHERE username = '{user}'").fetchone()[0]
        idus = db_sess.query(User).filter(User.username == f'{user}').first().id
        m = types.InlineKeyboardMarkup(row_width=8)
        b_m = [types.InlineKeyboardButton(text=board[i], callback_data=f"step_{id_game.id}_{i}_{user}") for i in range(len(board))]
        m.add(*b_m)
        a1 = bot.send_message(idus, f"Игра идет!\nХод: @{user}...", reply_markup=m)
        b1 = a1.id

        # cur.execute(f"UPDATE battles SET id_board_1 = '{b1}', id_board_2 = '{b2}' WHERE ID = {id_game}")
        id_game.id_board_1 = f'{b1}'
        id_game.id_board_2 = f'{b2}'
        db_sess.commit()


        # con.commit()
        # con.close()

    if call.data.startswith("step_"):
        db_sess = db_session.create_session()
        # con = sqlite3.connect(DB)
        # cur = con.cursor()

        a = call.data.split("_")
        id_game = a[1]
        cell = int(a[2])
        player_step = "_".join(a[3:])

        # cur.execute(f"SELECT player1, player2, position, step, isPlaying, id_board_1, id_board_2 FROM battles WHERE ID = {id_game}")
        # data = cur.fetchone()
        data = db_sess.query(Battles).filter(Battles.id == id_game).first()
        if data:
            pl1, pl2, pos, step, isPl, b1, b2 = data.player1, data.player2, data.position, data.step, data.isPlaying, data.id_board_1, data.id_board_2
            if pl1 == call.from_user.username:
                opponent = pl2
                b_opp = b2
            else:
                opponent = pl1
                b_opp = b1

            # cur.execute(f"SELECT ID, username FROM users WHERE username = '{opponent}'")
            # id_opp = cur.fetchone()[0]

            id_opp = db_sess.query(User).filter(User.username == f'{opponent}').first()

            if isPl and call.from_user.username == step and call.from_user.id not in IS_PUSHED_BUTTON:
                board = list(pos)
                curr_cell = int(board[cell])
                if curr_cell == 0:
                    board = board[:cell]
                    if board:
                        # cur.execute(f"UPDATE battles SET position = '{''.join(board)}', step = '{opponent}' WHERE ID = {id_game}")
                        bat = db_sess.query(Battles).filter(Battles.id == id_game).first()
                        bat.position = f'{"".join(board)}'
                        bat.step = f'{opponent}'
                        db_sess.commit()

                        m = types.InlineKeyboardMarkup(row_width=8)
                        b_m = [types.InlineKeyboardButton(text=board[i],
                                                          callback_data=f"step_{id_game}_{i}_{call.from_user.username}")
                               for i in range(len(board))]
                        m.add(*b_m)
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text=f"Игра идет!\nХод: @{opponent}...",
                                              reply_markup=m)

                        m = types.InlineKeyboardMarkup(row_width=8)
                        b_m = [types.InlineKeyboardButton(text=board[i], callback_data=f"step_{id_game}_{i}_{opponent}") for
                               i in range(len(board))]
                        m.add(*b_m)
                        bot.edit_message_text(chat_id=id_opp.id, message_id=b_opp,
                                              text=f"Игра идет!\nХод: @{opponent}...",
                                              reply_markup=m)
                    else:
                        # cur.execute(f"UPDATE battles SET winner = '{opponent}', isPlaying = 0 WHERE ID = {id_game}")
                        bat = db_sess.query(Battles).filter(Battles.id == id_game).first()
                        bat.winner = f'{opponent}'
                        bat.isPlaying = 0
                        db_sess.commit()

                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text=f'К сожалению, Вы проиграли игроку @{opponent}:(',
                                              reply_markup=None)


                        bot.edit_message_text(chat_id=id_opp.id, message_id=b_opp,
                                              text=f'Поздравляю! Вы победили противника: @{call.from_user.username}',
                                              reply_markup=None)
                else:
                    nums = [str(i) for i in range(curr_cell)]

                    m = types.InlineKeyboardMarkup(row_width=8)
                    b_m = [types.InlineKeyboardButton(text=i, callback_data=f"editNum_{id_game}_{cell}_{i}_{call.from_user.username}") for
                           i in nums]
                    m.add(*b_m)

                    IS_PUSHED_BUTTON.add(call.from_user.id)

                    bot.send_message(call.from_user.id, f"Выберите число, которое хотите поставить вместо {curr_cell}:", reply_markup=m)

        # con.commit()
        # con.close()

    if call.data.startswith("editNum_"):
        if call.from_user.id in IS_PUSHED_BUTTON:
            IS_PUSHED_BUTTON.remove(call.from_user.id)

        db_sess = db_session.create_session()
        # con = sqlite3.connect(DB)
        # cur = con.cursor()

        a = call.data.split("_")
        id_game = a[1]
        cell = int(a[2])
        n = a[3]
        player_step = "_".join(a[4:])

        # cur.execute(
        #     f"SELECT player1, player2, position, step, isPlaying, id_board_1, id_board_2 FROM battles WHERE ID = {id_game}")
        # data = cur.fetchone()
        data = db_sess.query(Battles).filter(Battles.id == id_game).first()
        if data:
            pl1, pl2, pos, step, isPl, b1, b2 = data.player1, data.player2, data.position, data.step, data.isPlaying, data.id_board_1, data.id_board_2
            if pl1 == call.from_user.username:
                opponent = pl2
                b_opp = b2
                b_curr = b1
            else:
                opponent = pl1
                b_opp = b1
                b_curr = b2

            # cur.execute(f"SELECT ID, username FROM users WHERE username = '{opponent}'")
            # id_opp = cur.fetchone()[0]
            id_opp = db_sess.query(User).filter(User.username == f'{opponent}').first()

            if isPl and call.from_user.username == step:
                board = list(pos)
                board[cell] = n

                bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

                # cur.execute(
                #     f"UPDATE battles SET position = '{''.join(board)}', step = '{opponent}' WHERE ID = {id_game}")
                bat = db_sess.query(Battles).filter(Battles.id == id_game).first()
                bat.position = f'{"".join(board)}'
                bat.step = f'{opponent}'
                db_sess.commit()

                m = types.InlineKeyboardMarkup(row_width=8)
                b_m = [types.InlineKeyboardButton(text=board[i],
                                                  callback_data=f"step_{id_game}_{i}_{call.from_user.username}")
                       for i in range(len(board))]
                m.add(*b_m)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=b_curr,
                                      text=f"Игра идет!\nХод: @{opponent}...",
                                      reply_markup=m)

                m = types.InlineKeyboardMarkup(row_width=8)
                b_m = [types.InlineKeyboardButton(text=board[i], callback_data=f"step_{id_game}_{i}_{opponent}") for
                       i in range(len(board))]
                m.add(*b_m)
                bot.edit_message_text(chat_id=id_opp.id, message_id=b_opp,
                                      text=f"Игра идет!\nХод: @{opponent}...",
                                      reply_markup=m)

        # con.commit()
        # con.close()

    if call.data.startswith("translate_"):
        try:
            lang = call.data.split("_")[-1]

            m = types.InlineKeyboardMarkup()
            butt = types.InlineKeyboardButton(text="Русский", callback_data=f"translate_rus")
            butt1 = types.InlineKeyboardButton(text="English", callback_data=f"translate_eng")
            m.add(butt)
            m.add(butt1)
            global CURRENT_LANG

            if lang == "eng" and CURRENT_LANG[call.from_user.id] == "rus":
                CURRENT_LANG[call.from_user.id] = "eng"

                with open("rules.txt", "r", encoding="UTF-8") as f:
                    text = f.read()

                response = requests.post(url=url + text)
                print(response.json())
                q = response.json()
                tr_text = ""
                for i in range(len(q[0])):
                    tr_text += q[0][i][0]

                bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                      text=tr_text,
                                      reply_markup=m)
            elif lang == "rus" and CURRENT_LANG[call.from_user.id] == "eng":
                CURRENT_LANG[call.from_user.id] = "rus"

                with open("rules.txt", "r", encoding="UTF-8") as f:
                    text = f.read()

                bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                      text=text,
                                      reply_markup=m)
        except Exception as e:
            print(e)

    if call.data.startswith("statistic_"):
        friend = call.data[10:]

        db_sess = db_session.create_session()
        # con = sqlite3.connect(DB)
        # cur = con.cursor()

        # cur.execute(f"SELECT ID, winner FROM battles "
        #             f"WHERE player1 IN ('{friend}', '{call.from_user.username}') AND "
        #             f"player2 IN ('{friend}', '{call.from_user.username}') AND isPlaying = 0")
        #
        # data = cur.fetchall()

        data = db_sess.query(Battles).filter(Battles.player1.in_([f'{friend}', f'{call.from_user.username}']),
                                             Battles.player2.in_([f'{friend}', f'{call.from_user.username}']),
                                             Battles.isPlaying == 0).all()
        if data:
            us_k = sum(1 for i in data if i.winner == call.from_user.username)
            fr_k = sum(1 for i in data if i.winner == friend)

            text = f"Статистика игр:\n{call.from_user.username}: {us_k}\n{friend}: {fr_k}"
            bot.send_message(call.from_user.id, text)
        else:
            bot.send_message(call.from_user.id, "Вы пока не играли друг с другом, но это можно легко исправить")



@bot.message_handler(commands=["СписокДрузей"])
def list_friends(message: Message):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton("/home"))

    db_sess = db_session.create_session()
    # con = sqlite3.connect(DB)
    # cur = con.cursor()

    usrname = message.from_user.username
    # cur.execute(f"SELECT friends, ID FROM users WHERE username = '{usrname}'")
    # friends = cur.fetchone()[0].split(";")[1:]

    friends = db_sess.query(User).filter(User.username == f'{usrname}').first().friends.split(";")[1:]

    if len(friends) > 5:
        msg = "... Ого как у Вас много друзей"
    else:
        msg = "..."
    bot.send_message(message.chat.id, f"Открываю список{msg}", reply_markup=markup)

    m = types.InlineKeyboardMarkup(row_width=2)
    for friend in friends:
        butt = types.InlineKeyboardButton(text=f"{friend}", callback_data=f"statistic_{friend}")
        butt1 = types.InlineKeyboardButton(text="❌", callback_data=f"del_{friend}")
        m.add(butt, butt1)

    bot.send_message(message.chat.id, f"Друзья:", reply_markup=m)


@bot.message_handler(commands=["ОдиночныйРежим"])
def single_play(message: Message):
    idus = message.from_user.id

    # m = types.InlineKeyboardMarkup(row_width=20)
    # board = [types.InlineKeyboardButton(text=str(randint(0, 9)), callback_data=f"bla-bla") for _ in range(20)]
    # m.add(*board)
    # bot.send_message(idus, "test", reply_markup=m)

    bot.send_message(idus, "Данный режим находится в стадии разработки")


@bot.message_handler(commands=["ОнлайнИгра"])
def single_play(message: Message):
    idus = message.from_user.id
    if message.from_user.id in IS_PUSHED_BUTTON:
        IS_PUSHED_BUTTON.remove(message.from_user.id)

    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton("/stop_game"))
    bot.send_message(message.chat.id, "Для отправки другу вызова, необходимо выбрать его из списка друзей, или нажать кнопку stop_game",
                     reply_markup=markup)

    db_sess = db_session.create_session()
    # con = sqlite3.connect(DB)
    # cur = con.cursor()

    usrname = message.from_user.username
    # cur.execute(f"SELECT friends, ID FROM users WHERE username = '{usrname}'")
    # friends = cur.fetchone()[0].split(";")[1:]
    friends = db_sess.query(User).filter(User.username == f'{usrname}').first().friends.split(";")[1:]

    if len(friends) == 0:
        m = types.ReplyKeyboardMarkup()
        butts = []
        texts = BUTTONS[:]
        for text in texts:
            butts.append(types.KeyboardButton(text))
        m.add(*butts)

        bot.send_message(idus, "Упс, у Вас нет друзей, но вы можете сыграть в одиночную игру против меня", reply_markup=m)
    else:
        m = types.InlineKeyboardMarkup(row_width=1)
        for friend in friends:
            # cur.execute(f"SELECT ID, isPlaying FROM battles WHERE (player1 = '{friend}' OR player2 = '{friend}') AND isPlaying = 1")
            # check = cur.fetchone()
            check = db_sess.query(Battles).filter((Battles.player1 == f'{friend}') | (Battles.player2 == f'{friend}'))\
                .filter(Battles.isPlaying == 1).first()
            if check:
                continue
            butt = types.InlineKeyboardButton(text=f"@{friend}", callback_data=f"invite_{friend}")
            m.add(butt)

        bot.send_message(message.chat.id, f"Друзья(свободные):", reply_markup=m)


@bot.message_handler(commands=["stop_game"])
def stop_game(message: Message):
    usrname = message.from_user.username

    if message.from_user.id in IS_PUSHED_BUTTON:
        IS_PUSHED_BUTTON.remove(message.from_user.id)

    db_sess = db_session.create_session()
    # con = sqlite3.connect(DB)
    # cur = con.cursor()

    # cur.execute(
    #     f"SELECT ID, player1, player2, id_board_1, id_board_2 FROM battles WHERE (player1 = '{usrname}' OR "
    #     f"player2 = '{usrname}') AND isPlaying = 1")
    # data = cur.fetchall()

    data = db_sess.query(Battles).filter((Battles.player1 == f'{usrname}') | (Battles.player2 == f'{usrname}'))\
                .filter(Battles.isPlaying == 1).all()
    for i in data:
        if i:
            idg, pl1, pl2, b1, b2 = i.id, i.player1, i.player2, i.id_board_1, i.id_board_2
            if pl1 == usrname:
                plw = pl2
                bw = b2
                bl = b1
            else:
                plw = pl1
                bw = b1
                bl = b1
            # cur.execute(f"UPDATE battles SET winner = '{plw}', isPlaying = 0 WHERE ID = {idg}")
            i.winner = f'{plw}'
            i.isPlaying = 0
            db_sess.commit()

            # id_plw = cur.execute(f"SELECT ID, username FROM users WHERE username = '{plw}'").fetchone()[0]
            id_plw = db_sess.query(User).filter(User.username == f'{plw}').first()
            bot.edit_message_text(chat_id=id_plw.id, message_id=bw, text='Соперник бежал!',
                                  reply_markup=None)
            try:
                bot.delete_message(chat_id=message.from_user.id, message_id=bl)
            except Exception as e:
                print(e)


    # con.commit()
    # con.close()

    start(message)


@bot.message_handler(content_types=["text"])
def translate(message: Message):
    text = message.text
    print(message)
    # tr_text = requests.post(url=url, data={"key": key, "lang": lang[f'{message.from_user.id}'], "text": text}).json()["text"]
    # bot.reply_to(message=message, text=tr_text)


bot.polling()
