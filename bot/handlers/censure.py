from re import findall
from functools import lru_cache

from loguru import logger
from bot.data.clubpenguin.moderator import ChatFilterRuleCollection
from bot.events import event

TRANS_TAB = dict((ord(a), b) for a, b in zip(
    'a6bgreё3ukmho0npctyx4w',
    'абвдгеезикмноопрстухчш'
))
chat_filter_words: ChatFilterRuleCollection


@event.on("boot")
async def filter_load(server):
    global chat_filter_words
    chat_filter_words = await ChatFilterRuleCollection.get_collection()
    logger.info(f'Loaded {len(chat_filter_words)} filter words')


def simplify_message(message):
    if len(message) < 2:
        return message
    return ''.join(letter for i, letter in enumerate(message) if letter != message[i - 1])


def message_to_tokens(message):
    tokens_set = set()

    for token in set(findall(r'\w+', simplify_message(message.lower()))):
        tokens_set.add(token)
        tokens_set.add(simplify_message(token.translate(TRANS_TAB)))

    return tokens_set


@lru_cache(maxsize=None)
def is_message_valid(message):
    if not chat_filter_words:
        return False

    tokens = message_to_tokens(message)
    return not any(word in tokens for word in set(chat_filter_words.keys()))


@lru_cache(maxsize=None)
def get_consequence_from_message(message):
    if not chat_filter_words:
        return None

    tokens = message_to_tokens(message)
    return next((c for w, c in chat_filter_words.items() if w in tokens), None)
