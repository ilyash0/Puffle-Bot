from bot.data import db_pb


class Users(db_pb.Model):
    __tablename__ = 'users'

    id = db_pb.Column(db_pb.BigInteger, primary_key=True, nullable=False)
    penguin_id = db_pb.Column(db_pb.BigInteger, nullable=False)
    language = db_pb.Column(db_pb.String(2), nullable=False, server_default=db_pb.text("ru"))


class PenguinIntegrations(db_pb.Model):
    __tablename__ = 'penguin_integrations'

    discord_id = db_pb.Column(db_pb.BigInteger, primary_key=True, nullable=False)
    penguin_id = db_pb.Column(db_pb.BigInteger, primary_key=True, nullable=False,
                              server_default=db_pb.text("nextval('penguin_integrations_discord_id_seq'::regclass)"))
