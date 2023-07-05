from bot.data import db_cp


class Quest(db_cp.Model):
    __tablename__ = 'quest'

    id = db_cp.Column(db_cp.Integer, primary_key=True, server_default=db_cp.text("nextval('\"quest_id_seq\"'::regclass)"))
    name = db_cp.Column(db_cp.String(50), nullable=False, unique=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tasks = set()

        self._items = set()
        self._furniture = set()
        self._pet = set()

        self._complete = set()
        self._in_progress = set()

    @property
    def items(self):
        return self._items

    @property
    def furniture(self):
        return self._furniture

    @property
    def pet(self):
        return self._pet

    @property
    def complete(self):
        return self._complete

    @property
    def in_progress(self):
        return self._in_progress

    @property
    def awards(self):
        return self._items.union(self._furniture.union(self._pet))

    @property
    def tasks(self):
        return self._tasks

    @items.setter
    def items(self, child):
        if isinstance(child, QuestAwardItem):
            self._items.add(child)

    @furniture.setter
    def furniture(self, child):
        if isinstance(child, QuestAwardFurniture):
            self._furniture.add(child)

    @pet.setter
    def pet(self, child):
        if isinstance(child, QuestAwardPuffleItem):
            self._pet.add(child)

    @tasks.setter
    def tasks(self, child):
        if isinstance(child, QuestTask):
            self._tasks.add(child)

    @complete.setter
    def complete(self, child):
        if isinstance(child, PenguinQuestTask):
            if child.complete:
                self._complete.add(child.task_id)
            else:
                self._in_progress.add(child.task_id)

class GameQuest(db_cp.Model):
    __tablename__ = 'game_quest'

    id = db_cp.Column(db_cp.Integer(), nullable=False, primary_key=True, server_default=db_cp.text("nextval('\"game_quest_id_seq\"'::regclass)"))
    type_id = db_cp.Column(db_cp.Integer(), nullable=False, server_default='0')
    coins = db_cp.Column(db_cp.Integer(), nullable=False, server_default='500')
    item = db_cp.Column(db_cp.Integer(), nullable=False, server_default='0')
    furniture = db_cp.Column(db_cp.Integer(), nullable=False, server_default='0')


class PenguinQuest(db_cp.Model):
    __tablename__ = 'penguin_quest'

    id = db_cp.Column(db_cp.Integer(), nullable=False, primary_key=True, server_default=db_cp.text("nextval('\"game_quest_id_seq\"'::regclass)"))
    penguin_id = db_cp.Column(db_cp.Integer(), nullable=False, server_default='0')
    quest_id = db_cp.Column(db_cp.Integer(), nullable=False, server_default='500')
    argv1 = db_cp.Column(db_cp.Integer(), nullable=False, server_default='0')
    argv2 = db_cp.Column(db_cp.Integer(), nullable=False, server_default='0')
    status = db_cp.Column(db_cp.Integer(), nullable=False, server_default='0')
    expires = db_cp.Column(db_cp.DateTime, nullable=False, server_default=db_cp.text("(now() + '23:59:59'::interval)"))


class QuestAwardItem(db_cp.Model):
    __tablename__ = 'quest_award_item'

    quest_id = db_cp.Column(db_cp.ForeignKey('quest.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                            nullable=False)
    item_id = db_cp.Column(db_cp.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)


class QuestAwardFurniture(db_cp.Model):
    __tablename__ = 'quest_award_furniture'

    quest_id = db_cp.Column(db_cp.ForeignKey('quest.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                            nullable=False)
    furniture_id = db_cp.Column(db_cp.ForeignKey('furniture.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                                nullable=False)
    quantity = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))


class QuestAwardPuffleItem(db_cp.Model):
    __tablename__ = 'quest_award_puffle_item'

    quest_id = db_cp.Column(db_cp.ForeignKey('quest.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                            nullable=False)
    puffle_item_id = db_cp.Column(db_cp.ForeignKey('puffle_item.id', ondelete='CASCADE', onupdate='CASCADE'),
                                  primary_key=True, nullable=False)
    quantity = db_cp.Column(db_cp.SmallInteger, nullable=False, server_default=db_cp.text("1"))


class QuestTask(db_cp.Model):
    __tablename__ = 'quest_task'

    id = db_cp.Column(db_cp.Integer, primary_key=True, server_default=db_cp.text("nextval('\"quest_id_seq\"'::regclass)"))
    quest_id = db_cp.Column(db_cp.ForeignKey('quest.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    description = db_cp.Column(db_cp.String(50), nullable=False)
    room_id = db_cp.Column(db_cp.ForeignKey('room.id', ondelete='CASCADE', onupdate='CASCADE'))
    data = db_cp.Column(db_cp.String(50))


class PenguinQuestTask(db_cp.Model):
    __tablename__ = 'penguin_quest_task'

    task_id = db_cp.Column(db_cp.ForeignKey('quest_task.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                           primary_key=True)
    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                              primary_key=True)
    complete = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("false"))
