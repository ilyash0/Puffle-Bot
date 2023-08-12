from bot.data import AbstractDataCollection, db_cp


class Stamp(db_cp.Model):
    __tablename__ = 'stamp'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    name = db_cp.Column(db_cp.String(50), nullable=False)
    group_id = db_cp.Column(db_cp.ForeignKey('stamp_group.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    member = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    rank = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))
    description = db_cp.Column(db_cp.String(255), nullable=False, server_default=db_cp.text("''::character varying"))


class StampGroup(db_cp.Model):
    __tablename__ = 'stamp_group'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    name = db_cp.Column(db_cp.String(50), nullable=False)
    parent_id = db_cp.Column(db_cp.ForeignKey('stamp_group.id', ondelete='CASCADE', onupdate='CASCADE'))


class CoverStamp(db_cp.Model):
    __tablename__ = 'cover_stamp'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    stamp_id = db_cp.Column(db_cp.ForeignKey('stamp.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                            nullable=False)
    x = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    y = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    rotation = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    depth = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))


class CoverItem(db_cp.Model):
    __tablename__ = 'cover_item'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    item_id = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    x = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    y = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    rotation = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    depth = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))


class PenguinStamp(db_cp.Model):
    __tablename__ = 'penguin_stamp'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    stamp_id = db_cp.Column(db_cp.ForeignKey('stamp.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                            nullable=False)
    recent = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("true"))


class StampCollection(AbstractDataCollection):
    __model__ = Stamp
    __indexby__ = 'id'
    __filterby__ = 'id'


class PenguinStampCollection(AbstractDataCollection):
    __model__ = PenguinStamp
    __indexby__ = 'stamp_id'
    __filterby__ = 'penguin_id'
