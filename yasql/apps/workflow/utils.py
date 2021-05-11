# -*- coding:utf-8 -*-
# by pandonglin
import time
import hashlib


def gen_hook_signature(token):
    """
    gen hook token signature
    """
    timestamp = str(int(time.time()))
    tmp_str = timestamp + token
    md5_str = hashlib.md5(tmp_str.encode(encoding='utf-8')).hexdigest()
    return dict(signature=md5_str, timestamp=timestamp)