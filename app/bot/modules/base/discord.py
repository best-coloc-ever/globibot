from os import getenv

class EMOTES:
    LirikH = '<:lirikH:141625927871365130>'
    LirikFeels = '<:lirikFEELS:141625906534809600>'
    LirikNot = '<:lirikNOT:141625908594343936>'
    LirikGood = '<:lirikGOOD:141625902118338560>'
    LirikDj = '<:lirikDJ:141625905805131776>'
    LirikChamp = '<:lirikCHAMP:141625908011204608>'
    LirikF = '<:lirikF:141625910460809216>'

master_id = getenv('MASTER_ID')
master = '<@{id}>'.format(id=master_id)
