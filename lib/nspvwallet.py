import platform
import os
import re
import slickrpc


class CustomProxy(slickrpc.Proxy):
    def __init__(self,
                 service_url=None,
                 service_port=None,
                 conf_file=None,
                 timeout=3000):
        config = dict()
        if conf_file:
            config = slickrpc.ConfigObj(conf_file)
        if service_url:
            config.update(self.url_to_conf(service_url))
        if service_port:
            config.update(rpcport=service_port)
        elif not config.get('rpcport'):
            config['rpcport'] = 7771
        self.conn = self.prepare_connection(config, timeout=timeout)


def def_credentials(chain):
    rpcport = ''
    ac_dir = ''
    operating_system = platform.system()
    if operating_system == 'Darwin':
        ac_dir = os.environ['HOME'] + '/Library/Application Support/Komodo'
    elif operating_system == 'Linux':
        ac_dir = os.environ['HOME'] + '/.komodo'
    elif operating_system == 'Win64' or operating_system == 'Windows':
        ac_dir = '%s/komodo/' % os.environ['APPDATA']
    if chain == 'KMD':
        coin_config_file = str(ac_dir + '/komodo.conf')
    else:
        coin_config_file = str(ac_dir + '/' + chain + '/' + chain + '.conf')
    with open(coin_config_file, 'r') as f:
        for line in f:
            l = line.rstrip()
            if re.search('rpcuser', l):
                rpcuser = l.replace('rpcuser=', '')
            elif re.search('rpcpassword', l):
                rpcpassword = l.replace('rpcpassword=', '')
            elif re.search('rpcport', l):
                rpcport = l.replace('rpcport=', '')
    if len(rpcport) == 0:
        if chain == 'KMD':
            rpcport = 7771
        else:
            print("rpcport not in conf file, exiting")
            print("check "+coin_config_file)
            exit(1)

    return CustomProxy("http://%s:%s@127.0.0.1:%d" % (rpcuser, rpcpassword, int(rpcport)))
