from bot.data import AbstractDataCollection, db_cp


class Ban(db_cp.Model):
    __tablename__ = 'ban'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    issued = db_cp.Column(db_cp.DateTime, primary_key=True, nullable=False, server_default=db_cp.text("now()"))
    expires = db_cp.Column(db_cp.DateTime, primary_key=True, nullable=False, server_default=db_cp.text("now()"))
    moderator_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    reason = db_cp.Column(db_cp.SmallInteger, nullable=False)
    comment = db_cp.Column(db_cp.Text)
    message = db_cp.Column(db_cp.Text)
    
    
class Mute(db_cp.Model):
    __tablename__ = 'mute'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    issued = db_cp.Column(db_cp.DateTime, primary_key=True, nullable=False, server_default=db_cp.text("now()"))
    expires = db_cp.Column(db_cp.DateTime, primary_key=True, nullable=False, server_default=db_cp.text("now()"))
    moderator_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    message = db_cp.Column(db_cp.Text)


class Warning(db_cp.Model):
    __tablename__ = 'warning'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    expires = db_cp.Column(db_cp.DateTime, primary_key=True, nullable=False)
    issued = db_cp.Column(db_cp.DateTime, primary_key=True, nullable=False)


class Report(db_cp.Model):
    __tablename__ = 'report'

    id = db_cp.Column(db_cp.Integer, primary_key=True, server_default=db_cp.text("nextval('\"report_ID_seq\"'::regclass)"))
    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    reporter_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    report_type = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    date = db_cp.Column(db_cp.DateTime, nullable=False, server_default=db_cp.text("now()"))
    server_id = db_cp.Column(db_cp.Integer, nullable=False)
    room_id = db_cp.Column(db_cp.ForeignKey('room.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    
    
class Logs(db_cp.Model):
    __tablename__ = 'logs'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    date = db_cp.Column(db_cp.DateTime, primary_key=True, nullable=False, server_default=db_cp.text("now()"))
    type = db_cp.Column(db_cp.Integer, nullable=False)
    text = db_cp.Column(db_cp.Text)
    room_id = db_cp.Column(db_cp.ForeignKey('room.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    server_id = db_cp.Column(db_cp.Integer, nullable=False)


class ChatFilterRule(db_cp.Model):
    __tablename__ = 'chat_filter_rule'

    word = db_cp.Column(db_cp.Text, primary_key=True)
    filter = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    warn = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    ban = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))


class ChatFilterRuleCollection(AbstractDataCollection):
    __model__ = ChatFilterRule
    __filterby__ = 'word'
    __indexby__ = 'word'