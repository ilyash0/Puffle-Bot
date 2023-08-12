from bot.data import db_cp


class PenguinTrack(db_cp.Model):
    __tablename__ = 'penguin_track'

    id = db_cp.Column(db_cp.Integer, primary_key=True,
                      server_default=db_cp.text("nextval('\"penguin_track_id_seq\"'::regclass)"))
    name = db_cp.Column(db_cp.String(12), nullable=False, server_default=db_cp.text("''::character varying"))
    owner_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    sharing = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    pattern = db_cp.Column(db_cp.Text, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._likes = 0

    @property
    def likes(self):
        return self._likes

    @likes.setter
    def likes(self, like_count):
        self._likes = like_count


class TrackLike(db_cp.Model):
    __tablename__ = 'track_like'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    track_id = db_cp.Column(db_cp.ForeignKey('penguin_track.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                            nullable=False, index=True)
    date = db_cp.Column(db_cp.DateTime, primary_key=True, nullable=False, server_default=db_cp.text("now()"))
