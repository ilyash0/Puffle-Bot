from bot.data import AbstractDataCollection, db_cp


class Puffle(db_cp.Model):
    __tablename__ = 'puffle'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    parent_id = db_cp.Column(db_cp.ForeignKey('puffle.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    name = db_cp.Column(db_cp.String(50), nullable=False, server_default=db_cp.text("''::character varying"))
    cost = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    member = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    favourite_food = db_cp.Column(db_cp.ForeignKey('puffle_item.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    favourite_toy = db_cp.Column(db_cp.ForeignKey('puffle_item.id', ondelete='CASCADE', onupdate='CASCADE'))
    runaway_postcard = db_cp.Column(db_cp.ForeignKey('postcard.id', ondelete='CASCADE', onupdate='CASCADE'))


class PuffleItem(db_cp.Model):
    __tablename__ = 'puffle_item'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    parent_id = db_cp.Column(db_cp.ForeignKey('puffle_item.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    name = db_cp.Column(db_cp.String(50), nullable=False, server_default=db_cp.text("''::character varying"))
    type = db_cp.Column(db_cp.String(10), nullable=False, server_default=db_cp.text("'care'::character varying"))
    play_external = db_cp.Column(db_cp.String(10), nullable=False, server_default=db_cp.text("'none'::character varying"))
    cost = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    quantity = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))
    member = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    food_effect = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    rest_effect = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    play_effect = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    clean_effect = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))


class PuffleTreasureFurniture(db_cp.Model):
    __tablename__ = 'puffle_treasure_furniture'

    puffle_id = db_cp.Column(db_cp.ForeignKey('puffle.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                             nullable=False)
    furniture_id = db_cp.Column(db_cp.ForeignKey('furniture.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                                nullable=False)


class PuffleTreasureItem(db_cp.Model):
    __tablename__ = 'puffle_treasure_item'

    puffle_id = db_cp.Column(db_cp.ForeignKey('puffle.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                             nullable=False)
    item_id = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)


class PuffleTreasurePuffleItem(db_cp.Model):
    __tablename__ = 'puffle_treasure_puffle_item'

    puffle_id = db_cp.Column(db_cp.ForeignKey('puffle.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                             nullable=False)
    puffle_item_id = db_cp.Column(db_cp.ForeignKey('puffle_item.id', ondelete='CASCADE', onupdate='CASCADE'),
                                  primary_key=True, nullable=False)


class PenguinPuffle(db_cp.Model):
    __tablename__ = 'penguin_puffle'

    id = db_cp.Column(db_cp.Integer, primary_key=True,
                      server_default=db_cp.text("nextval('\"penguin_puffle_id_seq\"'::regclass)"))
    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    puffle_id = db_cp.Column(db_cp.ForeignKey('puffle.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    name = db_cp.Column(db_cp.String(16), nullable=False)
    adoption_date = db_cp.Column(db_cp.DateTime, nullable=False, server_default=db_cp.text("now()"))
    food = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("100"))
    play = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("100"))
    rest = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("100"))
    clean = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("100"))
    hat = db_cp.Column(db_cp.ForeignKey('puffle_item.id', ondelete='CASCADE', onupdate='CASCADE'))
    backyard = db_cp.Column(db_cp.Boolean, server_default=db_cp.text("false"))
    has_dug = db_cp.Column(db_cp.Boolean, server_default=db_cp.text("false"))


class PenguinPuffleItem(db_cp.Model):
    __tablename__ = 'penguin_puffle_item'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    item_id = db_cp.Column(db_cp.ForeignKey('puffle_item.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    quantity = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))


class PuffleCollection(AbstractDataCollection):
    __model__ = Puffle
    __indexby__ = 'id'
    __filterby__ = 'id'


class PenguinPuffleCollection(AbstractDataCollection):
    __model__ = PenguinPuffle
    __indexby__ = 'id'
    __filterby__ = 'penguin_id'


class PuffleItemCollection(AbstractDataCollection):
    __model__ = PuffleItem
    __indexby__ = 'id'
    __filterby__ = 'id'


class PenguinPuffleItemCollection(AbstractDataCollection):
    __model__ = PenguinPuffleItem
    __indexby__ = 'item_id'
    __filterby__ = 'penguin_id'
