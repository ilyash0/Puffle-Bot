import json
from asyncio import CancelledError, IncompleteReadError, LimitOverrunError
from xml.etree.cElementTree import Element, SubElement, tostring

import defusedxml.cElementTree as Et
from loguru import logger

from bot.events import TagPacket, FrameworkPacket, event, XMLPacket


class AuthorityError(BaseException):
    pass


class Client:
    __slots__ = [
        "__reader",
        "__writer",
        "server",
        "logger",
        "peer_name",
        "received_packets",
        "joined_world",
        "client_type",
        "media_url",
        "event_num",
    ]

    def __init__(self, server, reader, writer):
        self.__reader = reader
        self.__writer = writer

        self.server = server

        self.peer_name = writer.get_extra_info("peername")

        self.joined_world = False
        self.client_type = None

        self.received_packets = set()

        super().__init__()

    async def send_tag(self, handler_id, *data):
        tag_data = "|".join(map(str, data))
        line = f"[{handler_id}]|{tag_data}|"
        await self.send_line(line, "\r\n")

    async def send_json(self, **data):
        await self.send_tag(
            "UI_CLIENTEVENT",
            self.event_num,
            "receivedJson",
            json.dumps(data, separators=(",", ":")),
        )

    async def send_xml(self, xml_dict):
        data_root = Element("msg")
        data_root.set("t", "sys")

        sub_element_parent = data_root
        for sub_element, sub_element_attribute in xml_dict.items():
            sub_element_object = SubElement(sub_element_parent, sub_element)

            if type(xml_dict[sub_element]) is dict:
                for sub_element_attribute_key, sub_element_attribute_value in xml_dict[
                    sub_element
                ].items():
                    sub_element_object.set(
                        sub_element_attribute_key, sub_element_attribute_value
                    )
            else:
                sub_element_object.text = xml_dict[sub_element]

            sub_element_parent = sub_element_object

        xml_data = tostring(data_root)
        await self.send_line(xml_data.decode("utf-8"))

    async def send_line(self, data, delimiter="\x00"):
        if not self.__writer.is_closing():
            logger.debug(f"Outgoing data: {data}")
            self.__writer.write((data + delimiter).encode("utf-8"))

    async def close(self):
        self.__writer.close()
        await self.__writer.wait_closed()
        await self._client_disconnected()

    async def __handle_tag_data(self, data):
        logger.debug(f"Received Tag data: {data}")
        parsed_data = data.split(" ")

        packet_id = parsed_data[0].strip()
        packet = TagPacket(packet_id)
        await event.emit(packet, self, *parsed_data[1:])

    async def __handle_framework_data(self, data):
        logger.debug(f"Received Framework data: {data}")
        parsed_data = json.loads(" ".join(data.split(" ")[1:]))

        packet_id = parsed_data["triggerName"]
        packet = FrameworkPacket(packet_id)

        await event.emit(packet, self, **parsed_data)

    async def __handle_xml_data(self, data):
        logger.debug(f"Received XML data: {data}")

        element_tree = Et.fromstring(data)

        if element_tree.tag == 'msg':
            try:
                body_tag = element_tree[0]
                action = body_tag.get('action')
                packet = XMLPacket(action)
                await event.emit(packet, self, **body_tag)
            except IndexError:
                self.logger.warn('Received invalid XML data (didn\'t contain a body tag)')
        else:
            logger.error("Received invalid XML data!")

    async def _client_connected(self):
        logger.info(f"Server {self.peer_name} connected")

        await event.emit("connected", self)

    async def _client_disconnected(self):
        logger.info(f"Server disconnected")

        await event.emit("disconnected", self)

    async def __data_received(self, data):
        data = data.decode()[:-1]
        try:
            if data.startswith("<"):
                await self.__handle_xml_data(data)
            elif data.startswith("#"):
                await self.__handle_framework_data(data[:-1])
            else:
                await self.__handle_tag_data(data[:-1])
        except AuthorityError:
            logger.debug(f"{self} tried to send game packet before authentication")

    async def run(self):
        await self._client_connected()
        while not self.__writer.is_closing():
            try:
                start_delimiter = await self.__reader.read(n=1)
                if start_delimiter.decode()[0:1] == "<":
                    data = await self.__reader.readuntil(separator=b"\x00")
                else:
                    data = await self.__reader.readuntil(separator=b"\r\n")

                if data:
                    await self.__data_received(start_delimiter + data)
                else:
                    logger.error("data not received")
                    await self.close()
                await self.__writer.drain()
            except IncompleteReadError:
                logger.error("IncompleteReadError")
                await self.close()
            except CancelledError:
                logger.error("CancelledError")
                await self.close()
            except ConnectionResetError:
                logger.error("ConnectionResetError")
                await self.close()
            except LimitOverrunError:
                logger.error("LimitOverrunError")
                await self.close()
            except BaseException as e:
                logger.exception(e.__traceback__)

        await self._client_disconnected()

    def __repr__(self):
        return f"<Server {self.peer_name}>"
