from datetime import datetime
from functools import cached_property

from bot.data import db_cp


class Penguin(db_cp.Model):
    __tablename__ = 'penguin'

    id = db_cp.Column(db_cp.Integer, primary_key=True, server_default=db_cp.text("nextval('\"penguin_id_seq\"'::regclass)"))
    username = db_cp.Column(db_cp.String(14), nullable=False, unique=True)
    nickname = db_cp.Column(db_cp.String(30), nullable=False)
    password = db_cp.Column(db_cp.CHAR(60), nullable=False)
    email = db_cp.Column(db_cp.String(255), nullable=False, index=True)
    registration_date = db_cp.Column(db_cp.DateTime, nullable=False, server_default=db_cp.text("now()"))
    active = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    safe_chat = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    last_paycheck = db_cp.Column(db_cp.DateTime, nullable=False, server_default=db_cp.text("now()"))
    minutes_played = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    moderator = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    stealth_moderator = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    character = db_cp.Column(db_cp.ForeignKey('character.id', ondelete='CASCADE', onupdate='CASCADE'))
    igloo = db_cp.Column(db_cp.ForeignKey('penguin_igloo_room.id', ondelete='CASCADE', onupdate='CASCADE'))
    coins = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("500"))
    color = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    head = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    face = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    neck = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    body = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    hand = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    feet = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    photo = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    flag = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    permaban = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    book_modified = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    book_color = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))
    book_highlight = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))
    book_pattern = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    book_icon = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))
    agent_status = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    field_op_status = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    career_medals = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    agent_medals = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    last_field_op = db_cp.Column(db_cp.DateTime, nullable=False, server_default=db_cp.text("now()"))
    com_message_read_date = db_cp.Column(db_cp.DateTime, nullable=False, server_default=db_cp.text("now()"))
    ninja_rank = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    ninja_progress = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    fire_ninja_rank = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    fire_ninja_progress = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    water_ninja_rank = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    water_ninja_progress = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    ninja_matches_won = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    fire_matches_won = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    water_matches_won = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    rainbow_adoptability = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    has_dug = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    puffle_handler = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    nuggets = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    walking = db_cp.Column(db_cp.ForeignKey('penguin_puffle.id', ondelete='CASCADE', onupdate='CASCADE'))
    opened_playercard = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    special_wave = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    special_dance = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    special_snowball = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    map_category = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    status_field = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))
    timer_active = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    timer_start = db_cp.Column(db_cp.Time, nullable=False, server_default=db_cp.text("'00:00:00'::time without time zone"))
    timer_end = db_cp.Column(db_cp.Time, nullable=False, server_default=db_cp.text("'23:59:59'::time without time zone"))
    timer_total = db_cp.Column(db_cp.Interval, nullable=False, server_default=db_cp.text("'01:00:00'::interval"))
    grounded = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    approval_en = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    approval_pt = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    approval_fr = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    approval_es = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    approval_de = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    approval_ru = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    rejection_en = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    rejection_pt = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    rejection_fr = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    rejection_es = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    rejection_de = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    rejection_ru = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
    ip = db_cp.Column(db_cp.String(15), nullable=False)
    snow_ninja_progress = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))
    snow_ninja_rank = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("0"))

    def __init__(self, *args, **kwargs):
        self.inventory = None
        self.permissions = None
        self.attributes = None
        self.igloos = None
        self.igloo_rooms = None
        self.furniture = None
        self.flooring = None
        self.locations = None
        self.stamps = None
        self.cards = None
        self.puffles = None
        self.puffle_items = None
        self.buddies = None
        self.buddy_requests = None
        self.character_buddies = None
        self.ignore = None

        super().__init__(*args, **kwargs)

    def safe_nickname(self):
        return self.nickname if self.approval else "P" + str(self.id)

    async def status_field_set(self, field_bitmask):
        if (self.status_field & field_bitmask) == 0:
            await self.update(status_field=self.status_field ^ field_bitmask).apply()

    def status_field_get(self, field_bitmask):
        return (self.status_field & field_bitmask) != 0

    @cached_property
    def age(self):
        return (datetime.now() - self.registration_date).days

    @cached_property
    def approval(self):
        return int(f'{self.approval_ru * 1}{self.approval_de * 1}0{self.approval_es * 1}'
                   f'{self.approval_fr * 1}{self.approval_pt * 1}{self.approval_en * 1}', 2)

    @cached_property
    def rejection(self):
        return int(f'{self.rejection_ru * 1}{self.rejection_de * 1}0{self.rejection_es * 1}'
                   f'{self.rejection_fr * 1}{self.rejection_pt * 1}{self.rejection_en * 1}', 2)


class ActivationKey(db_cp.Model):
    __tablename__ = 'activation_key'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    activation_key = db_cp.Column(db_cp.CHAR(255), primary_key=True, nullable=False)


class PenguinMembership(db_cp.Model):
    __tablename__ = 'penguin_membership'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    start = db_cp.Column(db_cp.DateTime, primary_key=True, nullable=False)
    expires = db_cp.Column(db_cp.DateTime)
    start_aware = db_cp.Column(db_cp.Boolean, server_default=db_cp.text("false"))
    expires_aware = db_cp.Column(db_cp.Boolean, server_default=db_cp.text("false"))
    expired_aware = db_cp.Column(db_cp.Boolean, server_default=db_cp.text("false"))


class Login(db_cp.Model):
    __tablename__ = 'login'

    id = db_cp.Column(db_cp.Integer, primary_key=True, server_default=db_cp.text("nextval('\"login_id_seq\"'::regclass)"))
    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    date = db_cp.Column(db_cp.DateTime, nullable=False, server_default=db_cp.text("now()"))
    ip_hash = db_cp.Column(db_cp.CHAR(255), nullable=False)
    minutes_played = db_cp.Column(db_cp.Integer, nullable=False, server_default=db_cp.text("0"))


class EpfComMessage(db_cp.Model):
    __tablename__ = 'epf_com_message'

    message = db_cp.Column(db_cp.Text, nullable=False)
    character_id = db_cp.Column(db_cp.ForeignKey('character.id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    date = db_cp.Column(db_cp.DateTime, nullable=False, server_default=db_cp.text("now()"))


class CfcDonation(db_cp.Model):
    __tablename__ = 'cfc_donation'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    coins = db_cp.Column(db_cp.Integer, nullable=False)
    charity = db_cp.Column(db_cp.Integer, nullable=False)
    date = db_cp.Column(db_cp.DateTime, nullable=False, server_default=db_cp.text("now()"))
