import telebot
import requests
from bs4 import BeautifulSoup
from telebot import types
from background import keep_alive, app
from dotenv import load_dotenv
import os
import pytesseract
from PIL import Image
from g4f.client import Client
from io import BytesIO


load_dotenv()
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
bot = telebot.TeleBot(os.getenv('TG_TOKEN'))
user_states = {}
client = Client()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_all_commands = types.KeyboardButton(text='/help')
    get_conf = types.KeyboardButton(text='/get_configuration')
    comp_reac = types.KeyboardButton(text='/complete_reaction')
    equal = types.KeyboardButton(text='/equalization')
    get_reac_ch = types.KeyboardButton(text='/get_reaction_chain')
    org_reacts = types.KeyboardButton(text='/organic_reactions')
    mol_mass = types.KeyboardButton(text='/molar_mass')
    gpt = types.KeyboardButton(text='/gpt')
    markup.add(button_all_commands, get_conf, comp_reac, equal, get_reac_ch, org_reacts, mol_mass, gpt)
    bot.send_message(message.chat.id, "Привет! Напишите /help и получите все команды.", reply_markup=markup)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Введи /get_configuration <элемент> для получения электронной конфигурации\n'
                                      '/complete_reaction <реакция> для дописывания реакции\n'
                                      '/equalization <реакция> для уравнивания реакции\n'
                                      '/get_reaction_chain <реакции через знак "="(равно)> для получения цепочки превращений\n'
                                      '/organic_reactions <реакцию(можно словами)> для получения органических реакций(фото)\n'
                                      '/molar_mass <вещество(реакцию)> для получения молярных масс веществ\n'
                                      '/gpt для диалога с chatgpt(умеет распознавать фото и работать с текстом)')


@bot.message_handler(commands=['gpt'])
def gpt_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_all_commands = types.KeyboardButton(text='/help')
    get_conf = types.KeyboardButton(text='/get_configuration')
    comp_reac = types.KeyboardButton(text='/complete_reaction')
    equal = types.KeyboardButton(text='/equalization')
    get_reac_ch = types.KeyboardButton(text='/get_reaction_chain')
    org_reacts = types.KeyboardButton(text='/organic_reactions')
    mol_mass = types.KeyboardButton(text='/molar_mass')
    gpt = types.KeyboardButton(text='/gpt')
    markup.add(button_all_commands, get_conf, comp_reac, equal, get_reac_ch, org_reacts, mol_mass, gpt)
    user_states[message.chat.id] = 'gpt'
    bot.send_message(message.chat.id, "Отправьте текст или фото для обработки GPT.", reply_markup=markup)


@bot.message_handler(content_types=['photo'], func=lambda message: user_states.get(message.chat.id) == 'gpt')
def handle_photo(message):
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_stream = BytesIO(downloaded_file)
        image = Image.open(image_stream)
        to_string = pytesseract.image_to_string(image, lang='rus+eng')

        if not to_string.strip():
            bot.reply_to(message, "Не удалось распознать текст на изображении.")
            return
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": to_string}],
            web_search=False
        )
        answer = response.choices[0].message.content

        bot.reply_to(message, f"Распознанный текст:\n{to_string}\n\nОтвет GPT:\n{answer}")

    except Exception as e:
        bot.reply_to(message, f"Ошибка при обработке изображения: {str(e)}")
    finally:
        if message.chat.id in user_states:
            del user_states[message.chat.id]


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'gpt')
def handle_gpt_text(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message.text}],
            web_search=False
        )
        answer = response.choices[0].message.content

        bot.reply_to(message, f"Ответ GPT:\n{answer}")

    except Exception as e:
        bot.reply_to(message, f"Ошибка при обработке запроса: {str(e)}")
    finally:
        if message.chat.id in user_states:
            del user_states[message.chat.id]


@bot.message_handler(commands=['get_configuration'])
def get_configuration(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_all_commands = types.KeyboardButton(text='/help')
    get_conf = types.KeyboardButton(text='/get_configuration')
    comp_reac = types.KeyboardButton(text='/complete_reaction')
    equal = types.KeyboardButton(text='/equalization')
    get_reac_ch = types.KeyboardButton(text='/get_reaction_chain')
    org_reacts = types.KeyboardButton(text='/organic_reactions')
    mol_mass = types.KeyboardButton(text='/molar_mass')
    gpt = types.KeyboardButton(text='/gpt')
    markup.add(button_all_commands, get_conf, comp_reac, equal, get_reac_ch, org_reacts, mol_mass, gpt)
    element = message.text.split(" ")
    if len(element) > 1:
        element = message.text.split(" ")[1]
        url = "https://chemistrypro.onrender.com/electronic_configuration"
        response = requests.post(url, data={'element': element})

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            texts = ''
            for tag in soup.find_all(['h5', 'p', 'pre']):
                texts += f'{tag.get_text(strip=True)}\n'
            max_length = 4096
            for i in range(0, len(texts), max_length):
                bot.send_message(message.chat.id, texts[i:i + max_length], reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f"Ошибка при запросе: {response.status_code}", reply_markup=markup)
    else:
        user_states[message.chat.id] = 'get_configuration'
        bot.send_message(message.chat.id, "Теперь отправьте элемент. Например: H")


@bot.message_handler(commands=['complete_reaction'])
def complete_reaction(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_all_commands = types.KeyboardButton(text='/help')
    get_conf = types.KeyboardButton(text='/get_configuration')
    comp_reac = types.KeyboardButton(text='/complete_reaction')
    equal = types.KeyboardButton(text='/equalization')
    get_reac_ch = types.KeyboardButton(text='/get_reaction_chain')
    org_reacts = types.KeyboardButton(text='/organic_reactions')
    mol_mass = types.KeyboardButton(text='/molar_mass')
    gpt = types.KeyboardButton(text='/gpt')
    markup.add(button_all_commands, get_conf, comp_reac, equal, get_reac_ch, org_reacts, mol_mass, gpt)
    element = message.text.split(" ")
    if len(element) > 1:
        element = message.text.split(" ")[1:]
        url = "https://chemistrypro.onrender.com/complete_reaction"
        response = requests.post(url, data={'chemical_formula': "".join(element)})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = ''
            final_reaction_header = soup.find('h5', text="Конечная реакция:")
            text += f'{final_reaction_header.get_text(strip=True)}\n'
            # Находим следующую за ним реакцию
            final_reaction = final_reaction_header.find_next('h5').get_text(strip=True)
            text += f'{final_reaction}\n'
            max_length = 4096
            for i in range(0, len(text), max_length):
                bot.send_message(message.chat.id, text[i:i + max_length], reply_markup=markup)
        else:
            print(response.status_code)
    else:
        user_states[message.chat.id] = 'complete_reaction'
        bot.send_message(message.chat.id, "Теперь отправьте реакцию. Например: H2SO4+KCl")



@bot.message_handler(commands=['equalization'])
def uravnivanie(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_all_commands = types.KeyboardButton(text='/help')
    get_conf = types.KeyboardButton(text='/get_configuration')
    comp_reac = types.KeyboardButton(text='/complete_reaction')
    equal = types.KeyboardButton(text='/equalization')
    get_reac_ch = types.KeyboardButton(text='/get_reaction_chain')
    org_reacts = types.KeyboardButton(text='/organic_reactions')
    mol_mass = types.KeyboardButton(text='/molar_mass')
    gpt = types.KeyboardButton(text='/gpt')
    markup.add(button_all_commands, get_conf, comp_reac, equal, get_reac_ch, org_reacts, mol_mass, gpt)
    element = message.text.split(" ")
    if len(element) > 1:
        element = message.text.split(" ")[1:]
        url = "https://chemistrypro.onrender.com/uravnivanie"
        response = requests.post(url, data={'chemical_formula': "".join(element)})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = ''
            final_reaction_header = soup.find('h5').get_text(strip=True)
            text += final_reaction_header
            max_length = 4096
            for i in range(0, len(text), max_length):
                bot.send_message(message.chat.id, text[i:i + max_length], reply_markup=markup)
        else:
            print(response.status_code)
    else:
        user_states[message.chat.id] = 'equalization'
        bot.send_message(message.chat.id, "Теперь отправьте реакцию. Например: H2+O2=H2O")



@bot.message_handler(commands=['get_reaction_chain'])
def get_reaction_chain(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_all_commands = types.KeyboardButton(text='/help')
    get_conf = types.KeyboardButton(text='/get_configuration')
    comp_reac = types.KeyboardButton(text='/complete_reaction')
    equal = types.KeyboardButton(text='/equalization')
    get_reac_ch = types.KeyboardButton(text='/get_reaction_chain')
    org_reacts = types.KeyboardButton(text='/organic_reactions')
    mol_mass = types.KeyboardButton(text='/molar_mass')
    gpt = types.KeyboardButton(text='/gpt')
    markup.add(button_all_commands, get_conf, comp_reac, equal, get_reac_ch, org_reacts, mol_mass, gpt)
    element = message.text.split(" ")
    if len(element) > 1:
        element = message.text.split(" ")[1:]
        url = "https://chemistrypro.onrender.com/get_reaction_chain"
        response = requests.post(url, data={'chemical_formula': "".join(element)})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            header_h4 = soup.find('h4')
            text = ''
            for el in header_h4.find_all_next(['h5', 'p']):
                if 'Как из' in el.get_text(strip=True):
                    text += f'**{el.get_text(strip=True)}**\n'
                elif 'Работает при помощи' not in el.get_text(strip=True):
                    text += f'{el.get_text(strip=True)}\n'
            max_length = 4096
            for i in range(0, len(text), max_length):
                bot.send_message(message.chat.id, text[i:i + max_length], reply_markup=markup)
        else:
            print(response.status_code)
    else:
        user_states[message.chat.id] = 'get_reaction_chain'
        bot.send_message(message.chat.id, "Теперь отправьте реакции через знак =(равно) для получения цепочки превращений. Например: Al=Al2O3=AlCl3")



@bot.message_handler(commands=['organic_reactions'])
def organic_reactions(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_all_commands = types.KeyboardButton(text='/help')
    get_conf = types.KeyboardButton(text='/get_configuration')
    comp_reac = types.KeyboardButton(text='/complete_reaction')
    equal = types.KeyboardButton(text='/equalization')
    get_reac_ch = types.KeyboardButton(text='/get_reaction_chain')
    org_reacts = types.KeyboardButton(text='/organic_reactions')
    mol_mass = types.KeyboardButton(text='/molar_mass')
    gpt = types.KeyboardButton(text='/gpt')
    markup.add(button_all_commands, get_conf, comp_reac, equal, get_reac_ch, org_reacts, mol_mass, gpt)
    element = message.text.split(" ")
    if len(element) > 1:
        element = message.text.split(" ")[1:]
        url = "https://chemistrypro.onrender.com/organic_reactions"
        response = requests.post(url, data={'chemical_formula': "".join(element)})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            images = soup.find_all('img')
            images_to_send = images[2:]

            for img in images_to_send:
                img_url = img.get('src')
                if img_url:
                    try:
                        bot.send_photo(message.chat.id, img_url, reply_markup=markup)
                    except Exception as e:
                        print(f"Произошла ошибка при отправке изображения: {e}")

        else:
            print(response.status_code)
    else:
        user_states[message.chat.id] = 'organic_reactions'
        bot.send_message(message.chat.id, "Теперь отправьте реакцию. Например: метан + br2")



@bot.message_handler(commands=['molar_mass'])
def molar_mass(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_all_commands = types.KeyboardButton(text='/help')
    get_conf = types.KeyboardButton(text='/get_configuration')
    comp_reac = types.KeyboardButton(text='/complete_reaction')
    equal = types.KeyboardButton(text='/equalization')
    get_reac_ch = types.KeyboardButton(text='/get_reaction_chain')
    org_reacts = types.KeyboardButton(text='/organic_reactions')
    mol_mass = types.KeyboardButton(text='/molar_mass')
    gpt = types.KeyboardButton(text='/gpt')
    markup.add(button_all_commands, get_conf, comp_reac, equal, get_reac_ch, org_reacts, mol_mass, gpt)
    element = message.text.split(" ")
    if len(element) > 1:
        element = message.text.split(" ")[1:]
        url = "https://chemistrypro.onrender.com/molyarnaya_massa"
        response = requests.post(url, data={'element': "".join(element)})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            answer = ''
            texts = soup.find_all('p')
            for text in texts[1:]:
                if 'Введите любую реакцию' not in text:
                    answer += f'{text.get_text(strip=True)}\n'
            max_length = 4096
            for i in range(0, len(answer), max_length):
                bot.send_message(message.chat.id, answer[i:i + max_length], reply_markup=markup)
        else:
            print(response.status_code)
    else:
        user_states[message.chat.id] = 'molar_mass'
        bot.send_message(message.chat.id, "Теперь отправьте вещество или элемент. Например: H2SO4")


@bot.message_handler(commands=['gpt'])
def gpt(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_all_commands = types.KeyboardButton(text='/help')
    get_conf = types.KeyboardButton(text='/get_configuration')
    comp_reac = types.KeyboardButton(text='/complete_reaction')
    equal = types.KeyboardButton(text='/equalization')
    get_reac_ch = types.KeyboardButton(text='/get_reaction_chain')
    org_reacts = types.KeyboardButton(text='/organic_reactions')
    mol_mass = types.KeyboardButton(text='/molar_mass')
    gpt = types.KeyboardButton(text='/gpt')
    markup.add(button_all_commands, get_conf, comp_reac, equal, get_reac_ch, org_reacts, mol_mass, gpt)
    user_states[message.chat.id] = 'gpt'
    bot.send_message(message.chat.id, "Теперь отправьте вещество или элемент. Например: H2SO4")



@bot.message_handler(func=lambda message: True)
def handle_reaction(message):
    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_all_commands = types.KeyboardButton(text='/help')
    get_conf = types.KeyboardButton(text='/get_configuration')
    comp_reac = types.KeyboardButton(text='/complete_reaction')
    equal = types.KeyboardButton(text='/equalization')
    get_reac_ch = types.KeyboardButton(text='/get_reaction_chain')
    org_reacts = types.KeyboardButton(text='/organic_reactions')
    mol_mass = types.KeyboardButton(text='/molar_mass')
    gpt = types.KeyboardButton(text='/gpt')
    markup.add(button_all_commands, get_conf, comp_reac, equal, get_reac_ch, org_reacts, mol_mass, gpt)
    if user_id in user_states:
        state = user_states[user_id]
        try:
            element = message.text.strip()
            if state == 'get_configuration':
                url = "https://chemistrypro.onrender.com/electronic_configuration"
                response = requests.post(url, data={'element': element})

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    texts = ''
                    for tag in soup.find_all(['h5', 'p', 'pre']):
                        texts += f'{tag.get_text(strip=True)}\n'
                    max_length = 4096
                    for i in range(0, len(texts), max_length):
                        bot.send_message(message.chat.id, texts[i:i + max_length], reply_markup=markup)
                else:
                    bot.send_message(message.chat.id, f"Ошибка при запросе: {response.status_code}",
                                     reply_markup=markup)

            elif state == 'complete_reaction':
                url = "https://chemistrypro.onrender.com/complete_reaction"
                response = requests.post(url, data={'chemical_formula': "".join(element)})
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = ''
                    final_reaction_header = soup.find('h5', text="Конечная реакция:")
                    text += f'{final_reaction_header.get_text(strip=True)}\n'
                    # Находим следующую за ним реакцию
                    final_reaction = final_reaction_header.find_next('h5').get_text(strip=True)
                    text += f'{final_reaction}\n'
                    max_length = 4096
                    for i in range(0, len(text), max_length):
                        bot.send_message(message.chat.id, text[i:i + max_length], reply_markup=markup)
                else:
                    print(response.status_code)

            elif state == 'equalization':
                url = "https://chemistrypro.onrender.com/uravnivanie"
                response = requests.post(url, data={'chemical_formula': "".join(element)})
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = ''
                    final_reaction_header = soup.find('h5').get_text(strip=True)
                    text += final_reaction_header
                    max_length = 4096
                    for i in range(0, len(text), max_length):
                        bot.send_message(message.chat.id, text[i:i + max_length], reply_markup=markup)
                else:
                    print(response.status_code)

            elif state == 'get_reaction_chain':
                url = "https://chemistrypro.onrender.com/get_reaction_chain"
                response = requests.post(url, data={'chemical_formula': "".join(element)})
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    header_h4 = soup.find('h4')
                    text = ''
                    for el in header_h4.find_all_next(['h5', 'p']):
                        if 'Как из' in el.get_text(strip=True):
                            text += f'**{el.get_text(strip=True)}**\n'
                        elif 'Работает при помощи' not in el.get_text(strip=True):
                            text += f'{el.get_text(strip=True)}\n'
                    max_length = 4096
                    for i in range(0, len(text), max_length):
                        bot.send_message(message.chat.id, text[i:i + max_length], reply_markup=markup)
                else:
                    print(response.status_code)

            elif state == 'organic_reactions':
                url = "https://chemistrypro.onrender.com/organic_reactions"
                response = requests.post(url, data={'chemical_formula': "".join(element)})
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    images = soup.find_all('img')
                    images_to_send = images[2:]

                    for img in images_to_send:
                        img_url = img.get('src')
                        if img_url:
                            try:
                                bot.send_photo(message.chat.id, img_url, reply_markup=markup)
                            except Exception as e:
                                print(f"Произошла ошибка при отправке изображения: {e}")

                else:
                    print(response.status_code)

            elif state == 'molar_mass':
                url = "https://chemistrypro.onrender.com/molyarnaya_massa"
                response = requests.post(url, data={'element': "".join(element)})
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    answer = ''
                    texts = soup.find_all('p')
                    for text in texts[1:]:
                        if 'Введите любую реакцию' not in text:
                            answer += f'{text.get_text(strip=True)}\n'
                    max_length = 4096
                    for i in range(0, len(answer), max_length):
                        bot.send_message(message.chat.id, answer[i:i + max_length], reply_markup=markup)
                else:
                    print(response.status_code)

        except Exception as e:
            bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")
        finally:
            del user_states[user_id]


keep_alive()
bot.polling()
