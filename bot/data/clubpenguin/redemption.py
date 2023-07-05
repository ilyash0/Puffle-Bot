from bot.data import db_cp


class RedemptionCode(db_cp.Model):
    __tablename__ = 'redemption_code'

    id = db_cp.Column(db_cp.Integer, primary_key=True,
                      server_default=db_cp.text("nextval('\"redemption_code_id_seq\"'::regclass)"))
    code = db_cp.Column(db_cp.String(16), nullable=False, unique=True)
    type = db_cp.Column(db_cp.String(8), nullable=False, server_default=db_cp.text("'BLANKET'::character varying"))
    coins = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    expires = db_cp.Column(db_cp.DateTime)
    uses = db_cp.Column(db_cp.Integer)
    party_coins = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cards = set()
        self._flooring = set()
        self._furniture = set()
        self._igloos = set()
        self._items = set()
        self._locations = set()
        self._puffles = set()
        self._puffle_items = set()

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, child):
        if isinstance(child, RedemptionAwardCard):
            self._cards.add(child)

    @property
    def flooring(self):
        return self._flooring

    @flooring.setter
    def flooring(self, child):
        if isinstance(child, RedemptionAwardFlooring):
            self._flooring.add(child)

    @property
    def furniture(self):
        return self._furniture

    @furniture.setter
    def furniture(self, child):
        if isinstance(child, RedemptionAwardFurniture):
            self._furniture.add(child)

    @property
    def igloos(self):
        return self._igloos

    @igloos.setter
    def igloos(self, child):
        if isinstance(child, RedemptionAwardIgloo):
            self._igloos.add(child)

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, child):
        if isinstance(child, RedemptionAwardItem):
            self._items.add(child)

    @property
    def locations(self):
        return self._locations

    @locations.setter
    def locations(self, child):
        if isinstance(child, RedemptionAwardLocation):
            self._locations.add(child)

    @property
    def puffles(self):
        return self._puffles

    @puffles.setter
    def puffles(self, child):
        if isinstance(child, RedemptionAwardPuffle):
            self._puffles.add(child)

    @property
    def puffle_items(self):
        return self._puffle_items

    @puffle_items.setter
    def puffle_items(self, child):
        if isinstance(child, RedemptionAwardPuffleItem):
            self._puffle_items.add(child)


class RedemptionBook(db_cp.Model):
    __tablename__ = 'redemption_book'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    name = db_cp.Column(db_cp.String(255), nullable=False)


class RedemptionBookWord(db_cp.Model):
    __tablename__ = 'redemption_book_word'

    question_id = db_cp.Column(db_cp.Integer, primary_key=True, server_default=db_cp.text("nextval('\"redemption_book_word_question_id_seq\"'::regclass)"))
    book_id = db_cp.Column(db_cp.ForeignKey('redemption_book.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    page = db_cp.Column(db_cp.SmallInteger, primary_key=True, nullable=False, server_default=db_cp.text("1"))
    line = db_cp.Column(db_cp.SmallInteger, primary_key=True, nullable=False, server_default=db_cp.text("1"))
    word_number = db_cp.Column(db_cp.SmallInteger, primary_key=True, nullable=False, server_default=db_cp.text("1"))
    answer = db_cp.Column(db_cp.String(20), nullable=False)


class RedemptionAwardCard(db_cp.Model):
    __tablename__ = 'redemption_award_card'
    code_id = db_cp.Column(db_cp.ForeignKey('redemption_code.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    card_id = db_cp.Column(db_cp.ForeignKey('card.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)


class RedemptionAwardFlooring(db_cp.Model):
    __tablename__ = 'redemption_award_flooring'
    code_id = db_cp.Column(db_cp.ForeignKey('redemption_code.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    flooring_id = db_cp.Column(db_cp.ForeignKey('flooring.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                               nullable=False)


class RedemptionAwardFurniture(db_cp.Model):
    __tablename__ = 'redemption_award_furniture'
    code_id = db_cp.Column(db_cp.ForeignKey('redemption_code.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    furniture_id = db_cp.Column(db_cp.ForeignKey('furniture.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                                nullable=False)


class RedemptionAwardIgloo(db_cp.Model):
    __tablename__ = 'redemption_award_igloo'
    code_id = db_cp.Column(db_cp.ForeignKey('redemption_code.id', ondelete='CASCADE', onupdate='CASCADE'),
                           primary_key=True, nullable=False)
    igloo_id = db_cp.Column(db_cp.ForeignKey('igloo.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                            nullable=False)


class RedemptionAwardItem(db_cp.Model):
    __tablename__ = 'redemption_award_item'
    code_id = db_cp.Column(db_cp.ForeignKey('redemption_code.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    item_id = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)


class RedemptionAwardLocation(db_cp.Model):
    __tablename__ = 'redemption_award_location'
    code_id = db_cp.Column(db_cp.ForeignKey('redemption_code.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    location_id = db_cp.Column(db_cp.ForeignKey('location.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                               nullable=False)


class RedemptionAwardPuffle(db_cp.Model):
    __tablename__ = 'redemption_award_puffle'
    code_id = db_cp.Column(db_cp.ForeignKey('redemption_code.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    puffle_id = db_cp.Column(db_cp.ForeignKey('puffle.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                             nullable=False)


class RedemptionAwardPuffleItem(db_cp.Model):
    __tablename__ = 'redemption_award_puffle_item'
    code_id = db_cp.Column(db_cp.ForeignKey('redemption_code.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    puffle_item_id = db_cp.Column(db_cp.ForeignKey('puffle_item.id', ondelete='CASCADE', onupdate='CASCADE'),
                                  primary_key=True, nullable=False)


class PenguinRedemptionCode(db_cp.Model):
    __tablename__ = 'penguin_redemption_code'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    code_id = db_cp.Column(db_cp.ForeignKey('redemption_code.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False, index=True)


class PenguinRedemptionBook(db_cp.Model):
    __tablename__ = 'penguin_redemption_book'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    book_id = db_cp.Column(db_cp.ForeignKey('redemption_book.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False, index=True)
