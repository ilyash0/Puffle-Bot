from bot.data import AbstractDataCollection, db_cp


class Outfit(db_cp.Model):
    __tablename__ = 'outfit'

    id = db_cp.Column(db_cp.Integer, primary_key=True, server_default=db_cp.text("nextval('\"outfit_id_seq\"'::regclass)"))
    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    photo = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    flag = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    color = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    head = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    face = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    body = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    neck = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    hand = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    feet = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))


class OutfitCollection(AbstractDataCollection):
    __model__ = Outfit
    __indexby__ = 'id'
    __filterby__ = 'penguin_id'
