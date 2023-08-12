from bot.data import db_pb


class Fundraising(db_pb.Model):
    __tablename__ = 'fundraising'

    server_id = db_pb.Column(db_pb.BigInteger, primary_key=True, nullable=False)
    channel_id = db_pb.Column(db_pb.BigInteger, primary_key=True, nullable=False)
    message_id = db_pb.Column(db_pb.BigInteger, primary_key=True, nullable=False)
    penguin_id = db_pb.Column(db_pb.BigInteger, nullable=False)
    raised = db_pb.Column(db_pb.Integer, nullable=False, server_default=db_pb.text("0"))
    goal = db_pb.Column(db_pb.Integer)


class FundraisingBackers(db_pb.Model):
    __tablename__ = 'fundraising_backers'

    message_id = db_pb.Column(db_pb.BigInteger, primary_key=True, nullable=False)
    receiver_penguin_id = db_pb.Column(db_pb.BigInteger, nullable=False)
    backer_penguin_id = db_pb.Column(db_pb.BigInteger, primary_key=True, nullable=False)
