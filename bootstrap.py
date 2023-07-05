import argparse
import asyncio
from loguru import logger

from bot.core.server import Server

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Boot a server for Discord bot')
    parser.add_argument('-id', action='store', default=8000, type=int, help='Discord bot server ID')
    parser.add_argument('-n', '--name', action='store', help='Discord bot server name')
    parser.add_argument('-a', '--address', action='store', default='0.0.0.0',
                        help='Discord bot server address')
    parser.add_argument('-p', '--port', action='store', help='Discord bot server port', default=8000, type=int)
    # parser.add_argument('-l', '--lang', action='store', default='en', help='Discord bot language',
    #                     choices=['en', 'fr', 'pt', 'es', 'de', 'ru'])
    parser.add_argument('-t', '--token', action='store', help='Token for Discord bot')

    database_group = parser.add_argument_group('database')
    database_group.add_argument('-da', '--database-address', action='store',
                                dest='database_address',
                                default='localhost',
                                help='Postgresql database address')
    database_group.add_argument('-du', '--database-username', action='store',
                                dest='database_username',
                                default='postgres',
                                help='Postgresql database username')
    database_group.add_argument('-dp', '--database-password', action='store',
                                dest='database_password',
                                default='password',
                                help='Postgresql database password')
    database_group.add_argument('-dn', '--database-name', action='store',
                                dest='database_name_cp',
                                default='postgres',
                                help='Postgresql database name for club penguin')
    database_group.add_argument('-dn2', '--database-name2', action='store',
                                dest='database_name_pb',
                                default='pufflebot',
                                help='Postgresql database name for puffle bot')

    args = parser.parse_args()

    factory_instance = Server(args)
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(factory_instance.start())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info('Shutting down...')
