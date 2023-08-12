from bot.data import AbstractDataCollection, db_cp


class DanceSong(db_cp.Model):
    __tablename__ = 'dance_song'

    id = db_cp.Column(db_cp.Integer, primary_key=True)
    name = db_cp.Column(db_cp.String(30), nullable=False)
    song_length_millis = db_cp.Column(db_cp.Integer, nullable=False)
    song_length = db_cp.Column(db_cp.Integer, nullable=False)
    millis_per_bar = db_cp.Column(db_cp.Integer, nullable=False)


class DanceSongCollection(AbstractDataCollection):
    __model__ = DanceSong
    __indexby__ = 'id'
    __filterby__ = 'id'
