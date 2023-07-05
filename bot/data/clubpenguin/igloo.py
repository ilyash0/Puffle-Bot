from functools import cached_property

from bot.data import AbstractDataCollection, db_cp


class Flooring(db_cp.Model):
    __tablename__ = 'flooring'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    name = db_cp.Column(db_cp.String(50))
    cost = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    patched = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    legacy_inventory = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    vanilla_inventory = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))


class Furniture(db_cp.Model):
    __tablename__ = 'furniture'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    name = db_cp.Column(db_cp.String(50), nullable=False)
    type = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))
    sort = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))
    cost = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    member = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    patched = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    legacy_inventory = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    vanilla_inventory = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    bait = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    max_quantity = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("100"))
    innocent = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))


class Igloo(db_cp.Model):
    __tablename__ = 'igloo'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    name = db_cp.Column(db_cp.String(50), nullable=False)
    cost = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    patched = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    legacy_inventory = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    vanilla_inventory = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))


class IglooFurniture(db_cp.Model):
    __tablename__ = 'igloo_furniture'

    igloo_id = db_cp.Column(db_cp.ForeignKey('penguin_igloo_room.id', ondelete='CASCADE', onupdate='CASCADE'),
                            primary_key=True, nullable=False, index=True)
    furniture_id = db_cp.Column(db_cp.ForeignKey('furniture.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                                nullable=False)
    x = db_cp.Column(db_cp.SmallInteger, primary_key=True, nullable=False, server_default=db_cp.text("0"))
    y = db_cp.Column(db_cp.SmallInteger, primary_key=True, nullable=False, server_default=db_cp.text("0"))
    frame = db_cp.Column(db_cp.SmallInteger, primary_key=True, nullable=False, server_default=db_cp.text("0"))
    rotation = db_cp.Column(db_cp.SmallInteger, primary_key=True, nullable=False, server_default=db_cp.text("0"))


class IglooLike(db_cp.Model):
    __tablename__ = 'igloo_like'

    igloo_id = db_cp.Column(db_cp.ForeignKey('penguin_igloo_room.id', ondelete='CASCADE', onupdate='CASCADE'),
                            primary_key=True, nullable=False)
    player_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                             nullable=False)
    count = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))
    date = db_cp.Column(db_cp.DateTime, nullable=False, server_default=db_cp.text("now()"))


class Location(db_cp.Model):
    __tablename__ = 'location'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    name = db_cp.Column(db_cp.String(50), nullable=False)
    cost = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    patched = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    legacy_inventory = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    vanilla_inventory = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))


class PenguinIgloo(db_cp.Model):
    __tablename__ = 'penguin_igloo'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    igloo_id = db_cp.Column(db_cp.ForeignKey('igloo.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                            nullable=False)


class PenguinLocation(db_cp.Model):
    __tablename__ = 'penguin_location'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    location_id = db_cp.Column(db_cp.ForeignKey('location.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                               nullable=False)


class PenguinFurniture(db_cp.Model):
    __tablename__ = 'penguin_furniture'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    furniture_id = db_cp.Column(db_cp.ForeignKey('furniture.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                                nullable=False)
    quantity = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))


class PenguinFlooring(db_cp.Model):
    __tablename__ = 'penguin_flooring'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    flooring_id = db_cp.Column(db_cp.ForeignKey('flooring.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                               nullable=False)


class IglooCollection(AbstractDataCollection):
    __model__ = Igloo
    __indexby__ = 'id'
    __filterby__ = 'id'

    @cached_property
    def legacy_inventory(self):
        return [item for item in self.values() if item.legacy_inventory]

    @cached_property
    def vanilla_inventory(self):
        return [item for item in self.values() if item.vanilla_inventory]


class PenguinIglooCollection(AbstractDataCollection):
    __model__ = PenguinIgloo
    __indexby__ = 'igloo_id'
    __filterby__ = 'penguin_id'


class LocationCollection(AbstractDataCollection):
    __model__ = Location
    __indexby__ = 'id'
    __filterby__ = 'id'

    @cached_property
    def legacy_inventory(self):
        return [item for item in self.values() if item.legacy_inventory]

    @cached_property
    def vanilla_inventory(self):
        return [item for item in self.values() if item.vanilla_inventory]


class PenguinLocationCollection(AbstractDataCollection):
    __model__ = PenguinLocation
    __indexby__ = 'location_id'
    __filterby__ = 'penguin_id'


class FurnitureCollection(AbstractDataCollection):
    __model__ = Furniture
    __indexby__ = 'id'
    __filterby__ = 'id'

    @cached_property
    def innocent(self):
        return [item for item in self.values() if item.innocent]

    @cached_property
    def legacy_inventory(self):
        return [item for item in self.values() if item.legacy_inventory]

    @cached_property
    def vanilla_inventory(self):
        return [item for item in self.values() if item.vanilla_inventory]


class PenguinFurnitureCollection(AbstractDataCollection):
    __model__ = PenguinFurniture
    __indexby__ = 'furniture_id'
    __filterby__ = 'penguin_id'


class FlooringCollection(AbstractDataCollection):
    __model__ = Flooring
    __indexby__ = 'id'
    __filterby__ = 'id'

    @cached_property
    def legacy_inventory(self):
        return [item for item in self.values() if item.legacy_inventory]

    @cached_property
    def vanilla_inventory(self):
        return [item for item in self.values() if item.vanilla_inventory]


class PenguinFlooringCollection(AbstractDataCollection):
    __model__ = PenguinFlooring
    __indexby__ = 'flooring_id'
    __filterby__ = 'penguin_id'
