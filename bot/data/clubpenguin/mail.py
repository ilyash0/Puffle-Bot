from bot.data import AbstractDataCollection, db_cp


class Postcard(db_cp.Model):
    __tablename__ = 'postcard'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    name = db_cp.Column(db_cp.String(50), nullable=False)
    cost = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("10"))
    enabled = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))


class PenguinPostcard(db_cp.Model):
    __tablename__ = 'penguin_postcard'

    id = db_cp.Column(db_cp.Integer, primary_key=True,
                      server_default=db_cp.text("nextval('\"penguin_postcard_id_seq\"'::regclass)"))
    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                              index=True)
    sender_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    postcard_id = db_cp.Column(db_cp.ForeignKey('postcard.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    send_date = db_cp.Column(db_cp.DateTime, nullable=False, server_default=db_cp.text("now()"))
    details = db_cp.Column(db_cp.String(255), nullable=False, server_default=db_cp.text("''::character varying"))
    has_read = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))


class PostcardCollection(AbstractDataCollection):
    __model__ = Postcard
    __indexby__ = 'id'
    __filterby__ = 'id'
