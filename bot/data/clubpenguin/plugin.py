from bot.data import AbstractDataCollection, db_cp


class PluginAttribute(db_cp.Model):
    __tablename__ = 'plugin_attribute'

    plugin_name = db_cp.Column(db_cp.Text, primary_key=True, nullable=False)
    name = db_cp.Column(db_cp.Text, primary_key=True, nullable=False)
    value = db_cp.Column(db_cp.Text)


class PenguinAttribute(db_cp.Model):
    __tablename__ = 'penguin_attribute'

    penguin_id = db_cp.Column(db_cp.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                              nullable=False)
    name = db_cp.Column(db_cp.Text, primary_key=True, nullable=False)
    value = db_cp.Column(db_cp.Text)


class PenguinAttributeCollection(AbstractDataCollection):
    __model__ = PenguinAttribute
    __indexby__ = 'name'
    __filterby__ = 'penguin_id'


class PluginAttributeCollection(AbstractDataCollection):
    __model__ = PluginAttribute
    __indexby__ = 'name'
    __filterby__ = 'plugin_name'
