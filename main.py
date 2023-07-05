import random
import telebot
from telebot import types

hint_button = types.InlineKeyboardButton(text='Take a hint', callback_data="takehint")
markup_inline = types.InlineKeyboardMarkup()

hang_bot = telebot.TeleBot('TOKEN')
current_game = None
wordlist = ['удача', 'кілт', 'буран', 'будинок', 'розмарин','окуляри']


class HangmanGame:
    def __init__(self):
        self.word = random.choice(wordlist)
        self.masked_word = ''.join('*' for letter in self.word)
        self.attempts = 8
        self.guessed_letters = set()
        self.hint_taken = False

    def handle_guess(self, message):
        global current_game
        letter = message.text.lower()
        if letter in self.guessed_letters:
            hang_bot.send_message(message.chat.id,f'Ти вже відгадував цю літеру')
        else:
            self.guessed_letters.add(letter)
            self.masked_word = ''.join(char if char.lower() in self.guessed_letters else "*" for char in self.word)

            if self.masked_word == self.word:
                current_game = None
                hang_bot.send_message(message.chat.id, f'Молодець! Гру завершено!\nПравильне слово: {self.word}\nЯкщо хочеш зіграти ще, відправляй /play')
            elif letter in self.word:
                hang_bot.send_message(message.chat.id, f'Гарна здогадка! Тепер слово виглядає так:\n{self.masked_word}\nПродовжуй в тому ж дусі!')
            else:
                self.attempts -= 1
                if self.attempts == 0:
                    current_game = None
                    hang_bot.send_message(message.chat.id, f'Жаль, але ти програв. Правильне слово: {self.word}.\nЯкщо хочеш зіграти ще - відправляй /play')
                else:
                    hang_bot.send_message(message.chat.id, f'Такої літери немає в слові. Залишилось помилок - {self.attempts}')

    def receive_msg(self, message):
        if len(message.text) != 1 or not message.text.isalpha():
            hang_bot.send_message(message.chat.id, 'Будь ласка, введіть одну літеру')
        else:
            self.handle_guess(message)

@hang_bot.message_handler(commands=["start"])
def botgreeting(message):
    hang_bot.send_message(message.chat.id, '''Привіт!
Не хочеш зіграти в классичну гру "Hangman"(Шибениця)?
Правила дуже прості: Я загадую слово, твоя задача - вгадувати які літери можуть бути в цьому слові.
У тебе є право на 8 помилок перед тим, як гра закінчиться.
Коли будеш готовий, відправ /play''')

@hang_bot.message_handler(commands=["play"])
def play(message):
    global markup_inline
    global current_game
    markup_inline = types.InlineKeyboardMarkup()
    current_game = HangmanGame()
    markup_inline.add(hint_button)
    hang_bot.send_message(message.chat.id, f'Що ж, давай зіграємо!\nЯ загадав наступне слово:\n{current_game.masked_word}\nСпробуй відгадати!',reply_markup=markup_inline)

@hang_bot.message_handler(func= lambda message:True,)
def bot_reply(message):
    global current_game
    if current_game == None:
        hang_bot.send_message(message.chat.id, f'Якщо ти хочеш зіграти, відправляй /play')
    else:
        current_game.receive_msg(message)

@hang_bot.callback_query_handler(func=lambda call: call.data=="takehint")
def hint(call):
    global current_game
    if current_game.hint_taken:
        hang_bot.send_message(call.message.chat.id, f'Ти вже брав підказку!')
        return
    else:
        hint_letter = random.choice([x for x in current_game.word])
        while hint_letter in current_game.guessed_letters:
            hint_letter = random.choice([x for x in current_game.word])
        hang_bot.send_message(call.message.chat.id, f'В цьому слові є літера {hint_letter}')
        current_game.hint_taken = True
        return

hang_bot.infinity_polling()