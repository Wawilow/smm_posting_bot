jsn = {'user_id': 1587872539, 'user_token': '1534767c5e8badde5cb6def403683f8e1ef4946f5c555082ffbf393a1da5145c7d1d3590e95cfc12fea7e', 'group_id': '204098688'}
print(jsn['user_id'])
if 'user_id' in jsn.keys() and 'user_token' in jsn.keys() and 'group_id' in jsn.keys():
    print(jsn)
f = ([(True if i in jsn.keys() else False) for i in ['user_id', 'user_token', 'group_id']])
print(f)
print(all(f))
