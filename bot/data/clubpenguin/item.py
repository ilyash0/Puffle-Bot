from functools import cached_property

from bot.data import AbstractDataCollection, db_cp


class Item(db_cp.Model):
    __tablename__ = 'item'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    name = db_cp.Column(db_cp.String(50))
    type = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))
    cost = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    member = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    bait = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    patched = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    legacy_inventory = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    vanilla_inventory = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    epf = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    tour = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    release_date = db_cp.Column(db_cp.Date, nullable=False, server_default=db_cp.text("now()"))
    treasure = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    innocent = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))

    def is_color(self):
        return self.type == 1

    def is_head(self):
        return self.type == 2

    def is_face(self):
        return self.type == 3

    def is_neck(self):
        return self.type == 4

    def is_body(self):
        return self.type == 5

    def is_hand(self):
        return self.type == 6

    def is_feet(self):
        return self.type == 7

    def is_flag(self):
        return self.type == 8

    def is_photo(self):
        return self.type == 9

    def is_award(self):
        return self.type == 10


class PenguinItem(db_cp.Model):
    __tablename__ = 'penguin_item'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'),
                              primary_key=True, nullable=False)
    item_id = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'),
                           primary_key=True, nullable=False)


class ItemCollection(AbstractDataCollection):
    __model__ = Item
    __indexby__ = 'id'
    __filterby__ = 'id'

    @cached_property
    def treasure(self):
        return { item for item in self.values() if item.treasure }

    @cached_property
    def innocent(self):
        return { item for item in self.values() if item.innocent }

    @cached_property
    def legacy_inventory(self):
        return { item for item in self.values() if item.legacy_inventory }

    @cached_property
    def vanilla_inventory(self):
        return { item for item in self.values() if item.vanilla_inventory }


class PenguinItemCollection(AbstractDataCollection):
    __model__ = PenguinItem
    __indexby__ = 'item_id'
    __filterby__ = 'penguin_id'
