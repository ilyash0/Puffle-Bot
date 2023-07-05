from bot.data import AbstractDataCollection, db_cp


class BuddyList(db_cp.Model):
    __tablename__ = 'buddy_list'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    buddy_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                            nullable=False, index=True)
    best_buddy = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))


class BuddyRequest(db_cp.Model):
    __tablename__ = 'buddy_request'
    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    requester_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                                nullable=False)


class IgnoreList(db_cp.Model):
    __tablename__ = 'ignore_list'
    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    ignore_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                             nullable=False, index=True)


class Character(db_cp.Model):
    __tablename__ = 'character'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    name = db_cp.Column(db_cp.String(30), nullable=False)
    gift_id = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    stamp_id = db_cp.Column(db_cp.ForeignKey('stamp.id', ondelete='CASCADE', onupdate='CASCADE'))


class CharacterBuddy(db_cp.Model):
    __tablename__ = 'character_buddy'
    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    character_id = db_cp.Column(db_cp.ForeignKey('character.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                                nullable=False)
    best_buddy = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))


class BuddyListCollection(AbstractDataCollection):
    __model__ = BuddyList
    __filterby__ = 'penguin_id'
    __indexby__ = 'buddy_id'


class IgnoreListCollection(AbstractDataCollection):
    __model__ = IgnoreList
    __filterby__ = 'penguin_id'
    __indexby__ = 'ignore_id'


class BuddyRequestCollection(AbstractDataCollection):
    __model__ = BuddyRequest
    __filterby__ = 'penguin_id'
    __indexby__ = 'requester_id'


class CharacterCollection(AbstractDataCollection):
    __model__ = Character
    __filterby__ = 'id'
    __indexby__ = 'id'


class CharacterBuddyCollection(AbstractDataCollection):
    __model__ = CharacterBuddy
    __filterby__ = 'penguin_id'
    __indexby__ = 'character_id'
