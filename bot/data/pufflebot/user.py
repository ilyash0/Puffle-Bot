from bot.data import db_pb


class User(db_pb.Model):
    __tablename__ = 'user'

    id = db_pb.Column(db_pb.BigInteger, primary_key=True, nullable=False)
    penguin_id = db_pb.Column(db_pb.BigInteger, nullable=False)
    language = db_pb.Column(db_pb.String(5), nullable=False, server_default=db_pb.text("en-GB"))
    enabled_notify = db_pb.Column(db_pb.Boolean, nullable=False, server_default=db_pb.text("true"))
    enabled_coins_notify = db_pb.Column(db_pb.Boolean, nullable=False, server_default=db_pb.text("true"))
    enabled_membership_notify = db_pb.Column(db_pb.Boolean, nullable=False, server_default=db_pb.text("true"))


class PenguinIntegrations(db_pb.Model):
    __tablename__ = 'penguin_integrations'

    discord_id = db_pb.Column(db_pb.BigInteger, primary_key=True, nullable=False)
    penguin_id = db_pb.Column(db_pb.BigInteger, primary_key=True, nullable=False,
                              server_default=db_pb.text("nextval('penguin_integrations_discord_id_seq'::regclass)"))
