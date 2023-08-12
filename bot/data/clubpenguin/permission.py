from bot.data import AbstractDataCollection, db_cp


class Permission(db_cp.Model):
    __tablename__ = 'permission'

    name = db_cp.Column(db_cp.String(50), nullable=False, primary_key=True)
    enabled = db_cp.Column(db_cp.Boolean, nullable=False, server_default=db_cp.text("true"))


class PenguinPermission(db_cp.Model):
    __tablename__ = 'penguin_permission'

    penguin_id = db_cp.Column(db_cp.ForeignKey(u'penguin.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), primary_key=True)
    permission_name = db_cp.Column(db_cp.ForeignKey(u'permission.name', ondelete=u'CASCADE', onupdate=u'CASCADE'),
                                   nullable=False, primary_key=True)


class PermissionCollection(AbstractDataCollection):
    __model__ = Permission
    __indexby__ = 'name'
    __filterby__ = 'name'

    async def register(self, permission_name):
        permission_parts = permission_name.split('.')
        for permission_index in range(1, len(permission_parts) + 1):
            permission_name = '.'.join(permission_parts[:permission_index])
            if permission_name not in self:
                await self.insert(name=permission_name)

    async def unregister(self, permission_name):
        for permission in self.values():
            if permission.name == permission_name or permission.name.startswith(permission_name):
                await self.delete(permission.name)


class PenguinPermissionCollection(AbstractDataCollection):
    __model__ = PenguinPermission
    __indexby__ = 'permission_name'
    __filterby__ = 'penguin_id'
