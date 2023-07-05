from bot.data import AbstractDataCollection, db_cp


class Card(db_cp.Model):
    __tablename__ = 'card'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    name = db_cp.Column(db_cp.String(50), nullable=False)
    set_id = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))
    power_id = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    element = db_cp.Column(db_cp.CHAR(1), nullable=False, server_default=db_cp.text("'s'::bpchar"))
    color = db_cp.Column(db_cp.CHAR(1), nullable=False, server_default=db_cp.text("'b'::bpchar"))
    value = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("2"))
    description = db_cp.Column(db_cp.String(255), nullable=False, server_default=db_cp.text("''::character varying"))

    def get_string(self):
        return f'{self.id}|{self.element}|{self.value}|{self.color}|{self.power_id}'


class CardStarterDeck(db_cp.Model):
    __tablename__ = 'card_starter_deck'

    item_id = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False, index=True)
    card_id = db_cp.Column(db_cp.ForeignKey('card.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    quantity = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))


class PenguinCard(db_cp.Model):
    __tablename__ = 'penguin_card'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False, index=True)
    card_id = db_cp.Column(db_cp.ForeignKey('card.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    quantity = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))
    member_quantity = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))


class CardCollection(AbstractDataCollection):
    __model__ = Card
    __indexby__ = 'id'
    __filterby__ = 'id'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.starter_decks = {}

    def set_starter_decks(self, starter_deck_cards):
        for card in starter_deck_cards:
            starter_deck = self.starter_decks.get(card.item_id, [])
            starter_deck.append((self.get(card.card_id), card.quantity))
            self.starter_decks[card.item_id] = starter_deck

    @property
    def power_cards(self):
        return [card for card in self.values() if card.power_id > 0]


class PenguinCardCollection(AbstractDataCollection):
    __model__ = PenguinCard
    __indexby__ = 'card_id'
    __filterby__ = 'penguin_id'
