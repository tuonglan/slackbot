# -*- coding: utf-8 -*-

import unittest, os, sys
sys.path.insert(0, '../')
from papago_trans import PapagoTranslator


if __name__ == '__main__':
    client_id = os.environ.get('PAPAGO_CLIENT_ID')
    client_secret = os.environ.get('PAPAGO_CLIENT_SECRET')
    trans = PapagoTranslator(client_id, client_secret)

    rt = trans.translate('앗; 이제 봤네요. 저희 도동집 왔는데 지금 음식이 나왔습니')
    print "Translated text: \"%s\"" % rt

    rt = trans.translate('This is definitely English')
    print rt
