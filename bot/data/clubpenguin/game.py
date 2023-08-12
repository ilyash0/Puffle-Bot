from bot.data import db_cp


class PenguinGameData(db_cp.Model):
    __tablename__ = 'penguin_game_data'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='RESTRICT', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    room_id = db_cp.Column(db_cp.ForeignKey('room.id', ondelete='RESTRICT', onupdate='CASCADE'), primary_key=True,
                           nullable=False, index=True)
    index = db_cp.Column(db_cp.Integer, primary_key=True, index=True)
    data = db_cp.Column(db_cp.Text, nullable=False, server_default=db_cp.text("''"))
