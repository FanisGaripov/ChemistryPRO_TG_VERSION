Eng: This is a telegram bot created as a mini-port of a website on flask. It makes it easier to work with website functions, while spending less internet traffic. The bot is written in pyTelegramBotApi using requests. The bot sends requests to the server with the user's parameters (reaction, substance) and receives a response (it turned out to be a kind of REST API project), which is then sent to the user. There are 6 main site functions available: 
1. Molar masses of substances (/molar_mass)
2. Adding chemical reactions (/complete_reaction)
3. Equalization of chemical reactions (/equalization)
4. Organic reactions (/organic_reactions)
5. Transformation chains (/get_reaction_chain)
6. Electronic configurations (/get_configuration)

The bot is embedded on render.com and that's why he needs a flask server to which uptimerobot will send requests(uptimerobot.com ), so that the bot does not shut down.

Рус: Это телеграм-бот, созданный в качестве мини-порта сайта на flask. Он упрощает работу с функциями сайта, тратя при этом меньше трафика интернета. Бот написан на pyTelegramBotApi, используя requests. Бот отправляет запросы на сервер с параметрами пользователя(реакцией, веществом) и получает ответ(получился своего рода REST API - проект), который в дальнейшем высылается пользователю. Доступно 6 функций основного сайта: 
1. Молярные массы веществ (/molar_mass)
2. Дописывание химических реакций (/complete_reaction)
3. Уравнивание химических реакций (/equalization)
4. Органические реакции (/organic_reactions)
5. Цепочки превращений (/get_reaction_chain)
6. Электронные конфигурации (/get_configuration)

Бот задеплоен на render.com и поэтому ему нужен flask-сервер, на который будет отправлять запросы uptimerobot(uptimerobot.com), чтобы бот работал на постоянной основе.
