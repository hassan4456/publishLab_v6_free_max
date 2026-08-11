import datetime
def get_seasonal():
    m=datetime.datetime.now().month
    s={8:['back to school anxiety','first day school'],10:['halloween fear dark','courage brave'],12:['christmas kindness','winter bedtime'],1:['new year goals']}
    return s.get(m,['anger management'])
