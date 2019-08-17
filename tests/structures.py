import random
import unittest

from server.aoprotocol import AOProtocol
from server.client_manager import ClientManager
from server.exceptions import TsuserverException
from server.tsuserver import TsuserverDR

class _Unittest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('\nTesting {}: '.format(cls.__name__), end=' ')
        if cls.__name__[0] == '_':
            cls.skipTest('', reason='')
        cls.server = _TestTsuserverDR()
        cls.clients = cls.server.client_list
        cls.area0 = cls.server.area_manager.get_area_by_id(0)
        cls.area1 = cls.server.area_manager.get_area_by_id(1)
        cls.area2 = cls.server.area_manager.get_area_by_id(2)
        cls.area3 = cls.server.area_manager.get_area_by_id(3)
        cls.area4 = cls.server.area_manager.get_area_by_id(4)
        cls.area5 = cls.server.area_manager.get_area_by_id(5)
        cls.area6 = cls.server.area_manager.get_area_by_id(6)
        cls.area7 = cls.server.area_manager.get_area_by_id(7)

        cls.a0_name = cls.area0.name
        cls.a1_name = cls.area1.name
        cls.a2_name = cls.area2.name
        cls.a3_name = cls.area3.name
        cls.a4_name = cls.area4.name
        cls.a5_name = cls.area5.name
        cls.a6_name = cls.area6.name
        cls.a7_name = cls.area7.name

    def list2reason(self, exc_list):
        if exc_list and exc_list[-1][0] is self:
            return exc_list[-1][1]

    def assert_property(self, yes, no, group, pred):
        if yes == 0:
            yes = set()
        if no == 0:
            no = set()

        if group == 'C':
            structure = self.server.client_manager.clients
        elif group == 'A':
            structure = self.server.area_manager.areas

        if yes == 1:
            yes = {x for x in structure if x not in no}
        if no == 1:
            no = {x for x in structure if x not in yes}

        for x in yes:
            self.assertTrue(pred(x), x)
        for x in no:
            self.assertFalse(pred(x), x)

    def tearDown(self):
        """
        Check if any packets were unaccounted for. Only do so if test passed.
        """

        # Test checker by hynekcer (2016): https://stackoverflow.com/a/39606065

        result = self.defaultTestResult()  # these 2 methods have no side effects
        self._feedErrorsToResult(result, self._outcome.errors)
        error = self.list2reason(result.errors)
        failure = self.list2reason(result.failures)

        if error or failure:
            return

        for c in self.clients:
            if c:
                c.assert_no_packets()
                c.assert_no_ooc()
                c.assert_no_ic()

    @classmethod
    def tearDownClass(cls):
        for (logger, handler) in cls.server.logger_handlers:
            handler.close()
            logger.removeHandler(handler)
        cls.server.disconnect_all()

class _TestSituation3(_Unittest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.server.make_clients(3)
        cls.c0 = cls.clients[0]
        cls.c1 = cls.clients[1]
        cls.c2 = cls.clients[2]
        cls.c0_cname = cls.c0.get_char_name() #'Kaede Akamatsu_HD'
        cls.c1_cname = cls.c1.get_char_name() #'Shuichi Saihara_HD'
        cls.c2_cname = cls.c2.get_char_name() #'Maki Harukawa_HD'

class _TestSituation4(_Unittest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.server.make_clients(4)
        cls.c0 = cls.clients[0]
        cls.c1 = cls.clients[1]
        cls.c2 = cls.clients[2]
        cls.c3 = cls.clients[3]
        cls.c0_cname = cls.c0.get_char_name() #'Kaede Akamatsu_HD'
        cls.c1_cname = cls.c1.get_char_name() #'Shuichi Saihara_HD'
        cls.c2_cname = cls.c2.get_char_name() #'Maki Harukawa_HD'
        cls.c3_cname = cls.c3.get_char_name() #'Monokuma_HD'

class _TestSituation5(_Unittest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.server.make_clients(5)
        cls.c0 = cls.clients[0]
        cls.c1 = cls.clients[1]
        cls.c2 = cls.clients[2]
        cls.c3 = cls.clients[3]
        cls.c4 = cls.clients[4]
        cls.c0_cname = cls.c0.get_char_name() #'Kaede Akamatsu_HD'
        cls.c1_cname = cls.c1.get_char_name() #'Shuichi Saihara_HD'
        cls.c2_cname = cls.c2.get_char_name() #'Maki Harukawa_HD'
        cls.c3_cname = cls.c3.get_char_name() #'Monokuma_HD'
        cls.c4_cname = cls.c4.get_char_name() #'SPECTATOR'

class _TestSituation4Mc12(_TestSituation4):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.c1.make_mod()
        cls.c2.make_mod()

class _TestSituation4Mc1Gc2(_TestSituation4):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.c1.make_mod()
        cls.c2.make_gm()

class _TestSituation5Mc1Gc2(_TestSituation5):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.c1.make_mod()
        cls.c2.make_gm()

class _TestClientManager(ClientManager):
    class _TestClient(ClientManager.Client):
        def __init__(self, *args, my_protocol=None):
            super().__init__(*args)
            self.received_packets = list()
            self.received_ooc = list()
            self.received_ic = list()
            self.my_protocol = my_protocol

        def disconnect(self):
            self.my_protocol.connection_lost(None, client=self)

        def send_command(self, command, *args):
            self.send_command_stc(command, *args)

        def send_command_stc(self, command_type, *args):
            if len(args) > 1 and isinstance(args[1], TsuserverException):
                new_args = [args[0], args[1].message]
                args = tuple(new_args)
            self.received_packets.append([command_type, args])
            self.receive_command_stc(command_type, *args)

        def send_command_cts(self, buffer):
            self.my_protocol.data_received(buffer.encode('utf-8'))

        def ooc(self, message, username=None):
            if username is None:
                username = self.name

            user = self.convert_symbol_to_word(username)
            message = self.convert_symbol_to_word(message)
            buffer = "CT#{}#{}#%".format(user, message)
            self.send_command_cts(buffer)

        @staticmethod
        def convert_symbol_to_word(mes):
            if mes is None:
                return None
            mes = mes.replace('#', '<num>')
            mes = mes.replace('$', '<dollar>')
            return mes

        @staticmethod
        def convert_word_to_symbol(mes):
            if mes is None:
                return None
            mes = mes.replace('<num>', '#')
            mes = mes.replace('<dollar>', '$')
            return mes

        def make_mod(self):
            if self.is_mod:
                return
            self.ooc('/login {}'.format(self.server.config['modpass']))
            self.assert_packet('FM', None)
            self.assert_ooc('Logged in as a moderator.', over=True)
            assert self.is_mod

        def make_cm(self):
            if self.is_cm:
                return
            self.ooc('/logincm {}'.format(self.server.config['cmpass']))
            self.assert_packet('FM', None)
            self.assert_ooc('Logged in as a community manager.', over=True)
            assert self.is_cm

        def make_gm(self):
            if self.is_gm:
                return
            self.ooc('/loginrp {}'.format(self.server.config['gmpass']))
            self.assert_packet('FM', None)
            self.assert_ooc('Logged in as a game master.', over=True)
            assert self.is_gm

        def make_normie(self):
            self.ooc('/logout')
            self.assert_ooc('You are no longer logged in.', ooc_over=True)
            self.assert_packet('FM', None, over=True)
            assert not (self.is_mod and self.is_cm and self.is_gm)

        def move_area(self, area_id, discard_packets=True, discard_trivial=False):
            as_command = random.randint(0, 1)
            area = self.server.area_manager.get_area_by_id(area_id)
            if as_command:
                self.ooc('/area {}'.format(area_id))
            else:
                name = area.name
                buffer = 'MC#{}-{}#0#%'.format(area_id, name)
                self.send_command_cts(buffer)

            assert self.area.id == area_id, (self.area.id, area_id, as_command)

            if discard_trivial:
                packets_to_discard = (
                                    ['HP', None],
                                    ['HP', None],
                                    ['BN', None],
                                    ['LE', None],
                                    ['FM', None]
                                    )
                for packet in packets_to_discard:
                    self.discard_packet(packet)

                _, x = self.search_match(['CT', ('<dollar>H', 'Changed area to')],
                                          self.received_packets, somewhere=True, remove_match=True,
                                          allow_partial_match=True)
                self.discard_ooc(x[1])

            elif discard_packets:
                self.discard_all()


        def check_match(self, exp_args, act_args, allow_partial_match=False):
            assert len(exp_args) == len(act_args), (len(exp_args), len(act_args))

            for exp_arg, act_arg in zip(exp_args, act_args):
                if exp_arg is None:
                    continue

                if isinstance(exp_arg, tuple):
                    assert len(exp_arg) == len(act_arg)

                    for i, param in enumerate(exp_arg):
                        if param is None:
                            continue
                        if allow_partial_match:
                            condition = act_arg[i].startswith(param)
                        else:
                            condition = param == act_arg[i]
                        assert condition, (i, param, act_arg[i])
                elif isinstance(act_arg, tuple):
                    assert exp_arg == act_arg[0], (exp_arg, act_arg[0])
                else:
                    assert exp_arg == act_arg, (exp_arg, act_arg)

        def search_match(self, exp_args, structure, somewhere=False, remove_match=True,
                         allow_partial_match=False):
            if not somewhere:
                to_look = structure[:1]
            else:
                to_look = structure

            for i, act_args in enumerate(to_look):
                try:
                    self.check_match(exp_args, act_args, allow_partial_match=allow_partial_match)
                except AssertionError:
                    continue
                else:
                    if remove_match:
                        structure.pop(i)
                    return i, act_args
            else:
                if somewhere:
                    connector = 'somewhere among'
                else:
                    connector = 'at the start of'
                err = 'Cannot find {} {} the packets of {}'.format(exp_args, connector, self)
                err += ('\r\nCurrent packets: {}'
                        .format('\r\n*'.join([str(x) for x in structure])))
                raise AssertionError(err)

        def assert_packet(self, command_type, args, over=False, ooc_over=False, ic_over=False,
                          somewhere=False):
            err = '{} expected packets, found none'.format(self)
            assert len(self.received_packets) > 0, err
            self.search_match([command_type, args], self.received_packets, somewhere=somewhere)

            if over:
                err = ('{} expected no more packets (did you accidentally put over=True?)'
                       .format(self))
                assert(len(self.received_packets) == 0), err
            elif ooc_over or ic_over:
                # Assumes actual over checks are done manually
                pass
            else:
                err = ('{} expected more packets (did you forget to put over=True?)'
                       .format(self))
                assert len(self.received_packets) != 0, err

        def assert_no_packets(self):
            err = ('{} expected no outstanding packets, found {}.'
                   .format(self, self.received_packets))
            assert len(self.received_packets) == 0, err

        def assert_not_packet(self, command_type, args, somewhere=True):
            try:
                self.search_match([command_type, args], self.received_packets,
                                  somewhere=somewhere, remove_match=False)
            except AssertionError:
                pass
            else:
                raise AssertionError('Found packet {} {} when expecting not to find it.'
                                     .format(command_type, args))

        def assert_ooc(self, message, username=None, over=False, ooc_over=False,
                       check_CT_packet=True, somewhere=False):
            if username is None:
                username = self.server.config['hostname']

            user = self.convert_symbol_to_word(username)
            message = self.convert_symbol_to_word(message)

            if check_CT_packet:
                self.assert_packet('CT', (user, message), over=over, ooc_over=ooc_over,
                                            somewhere=somewhere)

            assert(len(self.received_ooc) > 0)
            self.search_match([user, message], self.received_ooc, somewhere=somewhere)

            if over or ooc_over:
                err = 'Unhandled OOC messages for {}'.format(self)
                err += ('\r\nCurrent OOC: {}'
                        .format('\r\n*'.join([str(x) for x in self.received_ooc])))
                assert len(self.received_ooc) == 0, err
            else:
                assert(len(self.received_ooc) != 0)

        def assert_no_ooc(self):
            err = ('{} expected no more OOC messages, found {}'
                   .format(self, self.received_ooc))
            assert len(self.received_ooc) == 0, err

        def assert_not_ooc(self, message, username=None, somewhere=True):
            if username is None:
                username = self.server.config['hostname']

            user = self.convert_symbol_to_word(username)
            message = self.convert_symbol_to_word(message)

            self.assert_not_packet('CT', (user, message), somewhere=somewhere)

        def sic(self, message, msg_type=0, pre='-', folder=None, anim=None, pos=None, sfx=0,
                anim_type=0, cid=None, sfx_delay=0, button=0, evi=None, flip=0, ding=0, color=0,
                ignore_timelimit=True):
            if folder is None:
                folder = self.get_char_name()
            if anim is None:
                anim = 'happy'
            if pos is None:
                pos = self.pos if self.pos else 'def'
            if cid is None:
                cid = self.char_id
            if evi is None:
                evi = 0

            # 0 = msg_type
            # 1 = pre
            # 2 = folder
            # 3 = anim
            # 4 = msg
            # 5 = pos
            # 6 = sfx
            # 7 = anim_type
            # 8 = cid
            # 9 = sfx_delay
            # 10 = button
            # 11 = self.client.evi_list[evidence]
            # 12 = flip
            # 13 = ding
            # 14 = color

            buffer = ('MS#{}#{}#{}#{}#{}#{}#{}#{}#{}#{}#{}#{}#{}#{}#{}#%'
                      .format(msg_type, pre, folder, anim, message, pos, sfx, anim_type, cid,
                              sfx_delay, button, evi, flip, ding, color))
            if ignore_timelimit: # Time wasted here = 4 hours 8/10/19
                self.area.can_send_message = lambda: True
            self.send_command_cts(buffer)

        def assert_ic(self, message, over=False, ic_over=False, check_MS_packet=True, **kwargs):
            if check_MS_packet:
                self.assert_packet('MS', None, over=over, ic_over=ic_over)

            assert(len(self.received_ic) > 0)
            params = self.received_ic.pop(0)

            message = self.convert_word_to_symbol(message)

            param_ids = {'msg_type': 0,
                         'pre': 1,
                         'folder': 2,
                         'anim': 3,
                         'msg': 4,
                         'pos': 5,
                         'sfx': 6,
                         'anim_type': 7,
                         'cid': 8,
                         'sfx_delay': 9,
                         'button': 10,
                         'evi': 11,
                         'flip': 12,
                         'ding': 13,
                         'color': 14,
                         'showname': 15}

            if 'msg' not in kwargs:
                kwargs['msg'] = message

            for (item, val) in kwargs.items():
                err = ('Wrong IC parameter {}. Expected "{}", got "{}".'
                       .format(item, params[param_ids[item]], val))
                assert params[param_ids[item]] == val, err

            if over or ic_over:
                assert(len(self.received_ic) == 0)
            else:
                assert(len(self.received_ic) != 0)

        def assert_no_ic(self):
            err = ('{} expected no more IC messages, found {}'
                   .format(self, self.received_ic))
            assert len(self.received_ic) == 0, err

        def discard_packet(self, packet):
            try:
                self.search_match(packet, self.received_packets, somewhere=True, remove_match=True)
            except AssertionError:
                pass

        def discard_ooc(self, ooc):
            try:
                self.search_match(ooc, self.received_ooc, somewhere=True, remove_match=True)
            except AssertionError:
                pass

        def discard_all(self):
            self.received_packets = list()
            self.received_ooc = list()
            self.received_ic = list()

        def receive_command_stc(self, command_type, *args):
            buffer = ''
            if command_type == 'decryptor': # Hi
                buffer = 'HI#FAKEHDID#%'
            elif command_type == 'ID': # Server ID
                buffer = "ID#AO2#2.4.8#%"
                assert(args[0] == self.id)
            elif command_type == 'FL': # AO 2.2.5 configs
                pass
            elif command_type == 'PN': # Player count
                pass
            elif command_type == 'SI': # Counts for char/evi/music
                pass
            elif command_type == 'SC': # Character list
                pass
            elif command_type == 'SM': # First timer music/area list
                pass
            elif command_type == 'CharsCheck': # Available characters
                pass
            elif command_type == 'HP': # Def/pro bar
                pass
            elif command_type == 'BN': # Background file
                pass
            elif command_type == 'LE': # Evidence list
                pass
            elif command_type == 'MM': # ?????????????
                pass
            elif command_type == 'OPPASS': # Guard pass
                pass
            elif command_type == 'DONE': # Done setting up courtroom
                pass
            elif command_type == 'CT': # OOC message
                self.received_ooc.append((args[0], args[1]))
            elif command_type == 'FM': # Updated music/area list
                pass
            elif command_type == 'PV': # Current character
                pass
            elif command_type == 'MS': # IC message
                self.received_ic.append(args)
            elif command_type == 'ZZ': # Mod call
                pass
            else:
                raise KeyError('Unrecognized STC argument {} {}'.format(command_type, args))

            if buffer:
                self.send_command_cts(buffer)

    def __init__(self, server):
        super().__init__(server, client_obj=self._TestClient)

    def new_client(self, transport, ip=None, my_protocol=None):
        if ip is None:
            ip = self.server.get_ipid("127.0.0.1")
        c = super().new_client(transport, client_obj=self._TestClient, ip=ip,
                               my_protocol=my_protocol)
        return c

class _TestAOProtocol(AOProtocol):
    def connection_made(self, transport, my_protocol=None):
        """ Called upon a new client connecting

        :param transport: the transport object
        """
        self.client = None
        self.ping_timeout = None

        super().connection_made(transport, my_protocol=my_protocol)

    def connection_lost(self, exc, client=None):
        """ User disconnected

        :param exc: reason
        """
        if not self.client:
            self.client = client
        self.server.remove_client(self.client)

        if self.ping_timeout:
            self.ping_timeout.cancel()

    def data_received(self, data):
        super().data_received(data)

class _TestTsuserverDR(TsuserverDR):
    def __init__(self):
        super().__init__(client_manager=_TestClientManager, in_test=True)
        self.ao_protocol = _TestAOProtocol
        self.client_list = [None] * self.config['playerlimit']

    def create_client(self):
        new_ao_protocol = self.ao_protocol(self)
        new_ao_protocol.connection_made(None, my_protocol=new_ao_protocol)
        return new_ao_protocol.client

    def new_client(self, transport=None, my_protocol=None):
        c = self.client_manager.new_client(transport, my_protocol=my_protocol)
        if self.rp_mode:
            c.in_rp = True
        c.server = self
        c.area = self.area_manager.default_area()
        c.area.new_client(c)
        return c

    def make_client(self, char_id, hdid='FAKEHDID'):
        c = self.create_client()
        c.send_command_cts("askchaa#%")
        c.send_command_cts("RC#%")
        c.send_command_cts("RM#%")
        c.send_command_cts("RD#%")

        c.send_command_cts("CC#{}#{}#{}#%".format(c.id, char_id, hdid))
        exp = self.char_list[char_id] if char_id >= 0 else self.config['spectator_name']
        res = c.get_char_name()
        assert exp == res, (char_id, exp, res)
        c.discard_all()

        return c

    def make_clients(self, number, hdid_list=None, user_list=None):
        if hdid_list is None:
            hdid_list = ['FAKEHDID'] * number
        else:
            assert len(hdid_list) == number

        if user_list is None:
            user_list = ['user{}'.format(i) for i in range(number)]
        else:
            assert len(user_list) == number

        for i in range(number):
            area = self.area_manager.default_area()
            for j in range(len(self.char_list)):
                if area.is_char_available(j):
                    char_id = j
                    break
            else:
                char_id = -1

            client = self.make_client(char_id, hdid=hdid_list[i])
            client.name = user_list[i]

            for j, existing_client in enumerate(self.client_list):
                if existing_client is None:
                    self.client_list[j] = client
                    break
            else:
                j = -1
            assert j == client.id, (j, client.id)

    def disconnect_client(self, client_id, assert_no_outstanding=False):
        client = self.client_list[client_id]
        if not client:
            raise KeyError(client_id)

        client.disconnect()
        if assert_no_outstanding:
            client.assert_no_packets()
            client.assert_no_ooc()
        self.client_list[client_id] = None

    def disconnect_all(self, assert_no_outstanding=False):
        for (i, client) in enumerate(self.client_list):
            if client:
                client.disconnect()
                if assert_no_outstanding:
                    client.assert_no_packets()
                    client.assert_no_ooc()
                self.client_list[i] = None