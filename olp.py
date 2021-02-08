import requests as rq

base = {"OLP": {"OLP12": {"url": "192.168.220.112", "group1": "pt=8", 'group2': "pt=10"}}}
print(base['OLP']['OLP12']['url'])

olp = input('OLP?:')
group = input(f'OLP:{olp} номер в группе?:')
action = input(f'OLP:{olp}.{group} ON/OFF?:')

ip = base['OLP'][f'OLP{olp}']['url']
print(ip)
grp = base['OLP'][f'OLP{olp}'][f'group{group}']
print(grp)

if action == "ON" or action == "on":
    do_it = '1'
    resq = f'http://{ip}/sec/?{grp}&cmd={grp[3:]}:{do_it}'
    print(resq)
    res = rq.get(resq)

    print(res)
elif action == "OFF" or action == "off":
    do_it = '0'
    resq = f'http://{ip}/sec/?{grp}&cmd={grp[3:]}:{do_it}'
    print(resq)
    res = rq.get(resq)
    print(res)
else:
    print('wrong request')


