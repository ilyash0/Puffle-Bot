from bot.data import db_cp


class Transactions(db_cp.Model):
    __tablename__ = 'transactions'

    id = db_cp.Column(db_cp.Integer, primary_key=True,
                      server_default=db_cp.text("nextval('\"login_id_seq\"'::regclass)"))
    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    time = db_cp.Column(db_cp.DateTime, nullable=False, server_default=db_cp.text("now()"))
    description = db_cp.Column(db_cp.CHAR(255), nullable=False)
    rub = db_cp.Column(db_cp.Numeric(15, 2), nullable=False, server_default=db_cp.text("0"))
