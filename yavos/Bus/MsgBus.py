import sys, asyncio, json, logging, websockets
from websockets.asyncio.server import ServerConnection as WebSocketServerProtocol

logger = logging.getLogger("MsgBus")
logging.basicConfig(level=logging.INFO)

class Server:
    """ simple websocket server """
    clients = {}
    identifiers = set()
    logger.info('Message Bus Starting Up ...')

    def __init__(self):
        logger.info('Message Bus Initialized')

    async def register(self, ws: WebSocketServerProtocol) -> None:
        identifier = ws.request.path[1:]
        if identifier in self.identifiers:
            logger.error("Error/Warning - duplicate identifiers. %s --- %s" % (identifier, self.identifiers))
            # return False here to deny duplicate bus identifiers
            #return False
 
        self.clients[ws] = identifier
        self.identifiers.add(identifier)
        logger.info(f'{ws.remote_address} Connected: {identifier}')
        return True

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        identifier = self.clients[ws]
        try:
            del self.clients[ws]
        except:
            pass

        try:
            self.identifiers.remove(identifier)
        except:
            pass

        logger.info(f'{ws.remote_address} Disconnected: {identifier}')

    async def find_client(self, target):
        for client in self.clients:
            if self.clients[client] == target:
                return client
        return None

    async def send_to_clients(self, message):
        # pseudo abstraction violation
        # should not really care about 
        # message structure at this level
        if self.clients:
            msg = json.loads(message)
            target = msg.get('target','')
            source = msg.get('source','')
            logger.debug("sending %s" % (msg,))
            if target == '' or source == '':
                logger.error("Error - Rejected ill formed message. source:%s, target:%s" % (source, target))
                return False

            if target == '*':
                # broadcast
                await asyncio.wait([client.send(message) for client in self.clients])
            else: 
                # directed
                client = await self.find_client(target)
                if client == None:
                    logger.warning("Target not found! %s, %s" % (target,msg))
                    return False

                await client.send(message)

                client2 = await self.find_client('system_monitor')
                if client2 == None:
                    logger.debug("Notice, system_monitor not found!")
                    return False
                await client2.send(message)

                return True
                        
    async def ws_handler(self, ws: WebSocketServerProtocol) -> None:
        if (await self.register(ws)):
            try:
                await self.distribute(ws)

            except:
                logger.error("Caught exception in ws_handler()")

            finally:
                await self.unregister(ws)
        else:
            logger.warning("Warning, can't register %s, dropping connection" % (ws.path,))

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        async for message in ws:
            await self.send_to_clients(message)


async def start_server(bus_host, bus_port):
    ws_server = Server()
    async with websockets.serve(ws_server.ws_handler, bus_host, bus_port) as server:
        # Keep the server running indefinitely
        await server.serve_forever()


if __name__ == "__main__":
    # we accept a port and if a port is present we also accept a host
    # if no port is specified we get port 4000, host = '0.0.0.0'
    # the default is public access unless private is specified as localhost
    bus_port = 4000
    bus_host = '0.0.0.0'
    if len(sys.argv) == 3:
        # we have both
        bus_port = sys.argv[1]
        bus_host = sys.argv[2]
    elif len(sys.argv) == 2:
        # we have a port
        bus_port = sys.argv[1]
    else:
        # we have neither
        pass
    bus_port = int(bus_port)
    logger.info(f"Host:{bus_host}:{bus_port}")
    asyncio.run(start_server(bus_host, bus_port))

