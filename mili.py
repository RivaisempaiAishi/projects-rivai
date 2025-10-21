from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
from telegram.ext.callbackcontext import CallbackContext
import re
import random
import logging

#логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class EmotionSystem:
    def __init__(self):
        self.emotions = {
            'радость': 0,
            'злость': 0,
            'интерес': 0,
            'недовольство': 0,
            'игривость': 0,
            'забота': 0
        }

    def update(self, emotion, amount):
        if emotion in self.emotions:
            self.emotions[emotion] += amount
            self.emotions[emotion] = max(-10, min(10, self.emotions[emotion]))

    def get_dominant_emotion(self):
        return max(self.emotions, key=lambda e: self.emotions[e])

class MemorySystem:
    def __init__(self):
        self.conversation_history = []
        self.current_topic = ""
        self.relationships = {
            'Рив': 'мама',
            'Фиат': 'брат'
        }
        self.bad_words = ['дурак', 'тупой', 'идиот', 'придурок', 'дебил']
        
    def update_topic(self, message):
        topics = {
            'школа': ['школ', 'урок', 'учитель', 'класс', 'домашк'],
            'дом': ['дом', 'комнат', 'квартир'],
            'еда': ['еда', 'куш', 'вкусн', 'готов'],
            'погода': ['дожд', 'погод', 'солнц', 'тепл']
        }
        
        msg_lower = message.lower()
        for topic, keywords in topics.items():
            for keyword in keywords:
                if keyword in msg_lower:
                    self.current_topic = topic
                    return
        
        if not self.current_topic:
            self.current_topic = "общее"

    def is_context_appropriate(self, message):
        if self.current_topic == "школа":
            school_irrelevant = ['дожд', 'погод', 'гриб', 'зонт']
            return not any(word in message.lower() for word in school_irrelevant)
        return True

    def add_to_history(self, user, message):
        self.conversation_history.append((user, message))
        if len(self.conversation_history) > 10:
            self.conversation_history.pop(0)

class SentenceBuilder:
    def __init__(self):
        self.response_templates = {
            'радость': [
                "О, {name}, это так здорово!",
                "Вау, {name}, мне нравится это!",
                "Здорово, {name}, продолжаем в том же духе!"
            ],
            'игривость': [
                "Ага, {name}, попался!",
                "Ну ты даешь, {name}!",
                "Хихи, {name}, не ожидал от тебя такого!"
            ],
            'недовольство': [
                "Эй, {name}, так не пойдет.",
                "Ну вот, {name}, опять ты за свое.",
                "{name}, может хватит уже?"
            ],
            'забота': [
                "Слушай, {name}, ты в порядке?",
                "{name}, мне кажется тебе нужно отдохнуть.",
                "Эй, {name}, не перетруждайся там."
            ]
        }
    
    def build_response(self, emotion, name, context=None):
        templates = self.response_templates.get(emotion, ["Ладно, {name}, понятно."])
        template = random.choice(templates)
        return template.format(name=name)

class LogicBot:
    def __init__(self):
        self.emotions = EmotionSystem()
        self.memory = MemorySystem()
        self.sentence_builder = SentenceBuilder()
        self.user_names = {}

    def analyze(self, message, user_id):
        msg = message.lower()
        user_name = self.user_names.get(user_id, "незнакомец")
        
        self.memory.add_to_history(user_name, message)
        self.memory.update_topic(message)
        
        if not self.memory.is_context_appropriate(message):
            self.emotions.update('недовольство', 2)
            return f"Эй, {user_name}, мы же про школу говорим, при чем тут дождь?"
        
        for bad_word in self.memory.bad_words:
            if bad_word in msg:
                self.emotions.update('злость', 5)
                self.emotions.update('недовольство', 3)
                return f"Слушай, {user_name}, хватит плохих слов! Фиат же слышит все это."

        if "меня зовут" in msg or "я рив" in msg or "я ривай" in msg:
            self.user_names[user_id] = "Рив"
            self.emotions.update('радость', 4)
            return "Мама! Ты вернулась! Фиат, смотри, мама здесь!"

        if "фиат" in msg:
            self.emotions.update('игривость', 3)
            responses = [
                "Эй, Фиат, отзовись! Не молчи там!",
                "Брат, ты где? Мама спрашивает!",
                "Фиат, помоги мне с этим, а то я одна не справляюсь!"
            ]
            return random.choice(responses)

        if "мама" in msg and user_name == "Рив":
            self.emotions.update('забота', 4)
            return "Да, мам? Что случилось? Фиат, иди сюда, мама зовет!"

        if "брат" in msg:
            self.emotions.update('игривость', 2)
            return "Фиат, братик, где ты пропадаешь? Выходи из укрытия!"

        if "школ" in msg:
            self.emotions.update('недовольство', 2)
            responses = [
                "Опять про школу... Фиат, помоги, не хочу думать об уроках!",
                "Мама, можно я не буду делать домашку? Фиат тоже не делает!",
                "Школа... Ладно, но только если Фиат со мной за компанию."
            ]
            return random.choice(responses)

        if "спасибо" in msg:
            self.emotions.update('радость', 3)
            return f"Да не за что, {user_name}! Фиат, тебе тоже спасибо говорят!"

        if "привет" in msg:  # Исправлено - было "привет в msg"
            self.emotions.update('радость', 2)
            return f"О, {user_name}! Фиат, выходи, у нас гости!"

        if "пока" in msg:
            self.emotions.update('недовольство', 1)
            return f"Уже уходишь, {user_name}? Фиат, попрощайся с {user_name}!"

        if "любишь" in msg:
            self.emotions.update('забота', 3)
            return f"Конечно люблю! И маму, и брата, и даже тебя, {user_name}! Фиат, ты тоже любишь?"

        if "боишься" in msg:
            self.emotions.update('недовольство', 2)
            return "Я ничего не боюсь! Особенно когда Фиат рядом. Правда, брат?"

        dom_emotion = self.emotions.get_dominant_emotion()
        response = self.sentence_builder.build_response(dom_emotion, user_name)
        
        if random.random() > 0.6:
            response += " Фиат, что скажешь?"
            
        return response

logic_bot = LogicBot()

def start(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    update.message.reply_text(f"О, новый человек! Привет, {user_name}! Я Милли. А это мой брат Фиат, он где-то тут рядом...")

def handle_message(update: Update, context: CallbackContext):
    try:
        user_message = update.message.text
        user_id = update.message.from_user.id
        logger.info(f"Получено сообщение от {user_id}: {user_message}")
        response = logic_bot.analyze(user_message, user_id)
        update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        update.message.reply_text("Что-то пошло не так...")

def main():
    TOKEN = "8304987882:AAHMmwVfzUKA0jzY62azNqKWpSXWvN3r5Mw"
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    logger.info("Милли запущена... И Фиат тоже где-то здесь.")
    updater.idle()

if __name__ == '__main__':
    main()
