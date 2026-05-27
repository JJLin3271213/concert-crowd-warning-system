import requests, time
API = 'https://secure-achievement-production-a328.up.railway.app'

birdnest = {
    'name': '国家体育场（鸟巢）', 'address': '北京市朝阳区国家体育场南路1号', 'total_capacity': 91000,
    'zones': [
        ('西南入口', 0, 0), ('东南入口', 0, 0), ('东北入口', 0, 0), ('西北入口', 0, 0), ('出口', 0, 1),
        ('一层看台A区', 5000, 0), ('一层看台B区', 5000, 0), ('一层看台C区', 6000, 0), ('一层看台D区', 6000, 0),
        ('一层看台E区', 6000, 0), ('一层看台F区', 5000, 0), ('一层看台G区', 5000, 0), ('一层看台H区', 5000, 0),
        ('一层看台J区', 5000, 0), ('一层看台K区', 5000, 0), ('一层看台L区', 5000, 0),
        ('二层看台', 15000, 0), ('三层看台', 12000, 0),
        ('内场VIP区', 3000, 0), ('内场普通A区', 2000, 0), ('内场普通B区', 2000, 0),
    ],
    'roads': [
        ('西南入口','一层看台A区'), ('西南入口','一层看台B区'), ('东南入口','一层看台C区'), ('东南入口','一层看台D区'),
        ('东北入口','一层看台E区'), ('东北入口','一层看台F区'), ('西北入口','一层看台G区'), ('西北入口','一层看台H区'),
        ('一层看台A区','一层看台B区'), ('一层看台B区','一层看台A区'), ('一层看台B区','一层看台C区'), ('一层看台C区','一层看台B区'),
        ('一层看台C区','一层看台D区'), ('一层看台D区','一层看台C区'), ('一层看台D区','一层看台E区'), ('一层看台E区','一层看台D区'),
        ('一层看台E区','一层看台F区'), ('一层看台F区','一层看台E区'), ('一层看台F区','一层看台G区'), ('一层看台G区','一层看台F区'),
        ('一层看台G区','一层看台H区'), ('一层看台H区','一层看台G区'), ('一层看台H区','一层看台J区'), ('一层看台J区','一层看台H区'),
        ('一层看台J区','一层看台K区'), ('一层看台K区','一层看台J区'), ('一层看台K区','一层看台L区'), ('一层看台L区','一层看台K区'),
        ('一层看台A区','二层看台'), ('一层看台B区','二层看台'), ('二层看台','三层看台'), ('三层看台','二层看台'),
        ('一层看台A区','内场VIP区'), ('一层看台C区','内场VIP区'), ('一层看台E区','内场普通A区'), ('一层看台G区','内场普通B区'),
        ('内场VIP区','内场普通A区'), ('内场普通A区','内场VIP区'), ('内场普通A区','内场普通B区'), ('内场普通B区','内场普通A区'),
        ('三层看台','出口'), ('内场普通B区','出口'), ('一层看台L区','出口'),
    ]
}

zhengzhou = {
    'name': '郑州奥林匹克体育中心', 'address': '河南省郑州市中原区丹水大道与长椿路交叉口', 'total_capacity': 60000,
    'zones': [
        ('主入口', 0, 0), ('出口', 0, 1),
        ('一层看台A区', 4000, 0), ('一层看台B区', 4000, 0), ('一层看台C区', 3500, 0), ('一层看台D区', 3500, 0),
        ('二层看台A区', 5000, 0), ('二层看台B区', 5000, 0), ('二层看台C区', 4000, 0), ('二层看台D区', 4000, 0),
        ('三层看台', 12000, 0), ('内场VIP区', 2000, 0), ('内场A区', 3000, 0), ('内场B区', 3000, 0),
    ],
    'roads': [
        ('主入口','一层看台A区'), ('主入口','一层看台B区'),
        ('一层看台A区','一层看台B区'), ('一层看台B区','一层看台A区'),
        ('一层看台A区','一层看台C区'), ('一层看台C区','一层看台A区'),
        ('一层看台B区','一层看台D区'), ('一层看台D区','一层看台B区'),
        ('一层看台C区','一层看台D区'), ('一层看台D区','一层看台C区'),
        ('一层看台A区','二层看台A区'), ('一层看台B区','二层看台B区'),
        ('一层看台C区','二层看台C区'), ('一层看台D区','二层看台D区'),
        ('二层看台A区','二层看台B区'), ('二层看台B区','二层看台A区'),
        ('二层看台A区','二层看台C区'), ('二层看台C区','二层看台A区'),
        ('二层看台B区','二层看台D区'), ('二层看台D区','二层看台B区'),
        ('二层看台A区','三层看台'), ('二层看台B区','三层看台'),
        ('一层看台A区','内场VIP区'), ('一层看台B区','内场VIP区'),
        ('内场VIP区','内场A区'), ('内场A区','内场VIP区'),
        ('内场A区','内场B区'), ('内场B区','内场A区'),
        ('三层看台','出口'), ('内场B区','出口'), ('一层看台D区','出口'),
    ]
}

def add_venue(data):
    print(f'Creating: {data["name"]}')
    # Create venue
    r = requests.post(f'{API}/api/venues', params={
        'name': data['name'], 'address': data['address'], 'total_capacity': data['total_capacity']
    })
    venue = r.json()
    venue_id = venue['id']
    print(f'  Venue ID: {venue_id}')

    # Create zones
    zone_map = {}
    for name, cap, is_exit in data['zones']:
        r = requests.post(f'{API}/api/zones', params={
            'venue_id': venue_id, 'name': name, 'capacity': cap, 'is_exit': is_exit
        })
        zone_map[name] = r.json()['id']
    print(f'  Zones: {len(zone_map)}')

    # Create roads
    road_count = 0
    for from_name, to_name in data['roads']:
        if from_name in zone_map and to_name in zone_map:
            r = requests.post(f'{API}/api/road_network', params={
                'from_zone_id': zone_map[from_name], 'to_zone_id': zone_map[to_name],
                'venue_id': venue_id, 'distance': 1
            })
            if r.status_code == 200:
                road_count += 1
        time.sleep(0.3)
    print(f'  Roads: {road_count}')
    time.sleep(2)

print('=== Bird Nest ===')
add_venue(birdnest)
print()
print('=== Zhengzhou Olympic ===')
add_venue(zhengzhou)
print()
print('Done!')
