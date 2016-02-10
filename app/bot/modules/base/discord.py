from os import getenv

class EMOTES:
    LirikH = '<:lirikH:141625927871365130>'
    LirikFeels = '<:lirikFEELS:141625906534809600>'
    LirikNot = '<:lirikNOT:141625908594343936>'

master_id = getenv('MASTER_ID')
master = '<@{id}>'.format(id=master_id)
