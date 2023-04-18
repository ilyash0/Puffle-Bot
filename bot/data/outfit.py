from bot.data import AbstractDataCollection, db


class Outfit(db.Model):
    __tablename__ = 'outfit'

    id = db.Column(db.Integer, primary_key=True, server_default=db.text("nextval('\"outfit_id_seq\"'::regclass)"))
    penguin_id = db.Column(db.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    photo = db.Column(db.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    flag = db.Column(db.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    color = db.Column(db.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    head = db.Column(db.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    face = db.Column(db.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    body = db.Column(db.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    neck = db.Column(db.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    hand = db.Column(db.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    feet = db.Column(db.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))


class OutfitCollection(AbstractDataCollection):
    __model__ = Outfit
    __indexby__ = 'id'
    __filterby__ = 'penguin_id'
