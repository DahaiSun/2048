#!/usr/bin/env python3
"""
Generate scene-based wordbook JS files from Oxford 5000 CSV data.
Reads oxford_5000_cleaned.csv, maps words to scene categories,
and outputs registerWordbook() JS files for each scene.
"""

import csv
import os

# --- Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, 'oxford_5000_cleaned.csv')
AUDIO_DIR = os.path.join(SCRIPT_DIR, 'tts_delivery', 'audio')
WORDBOOKS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'wordbooks')

# --- Extra translations for words NOT in Oxford 5000 CSV ---
EXTRA_TRANSLATIONS = {
    'brochure': '手册',
    'excursion': '短途旅行',
    'safari': '狩猎旅行',
    'pilgrimage': '朝圣',
    'itinerary': '行程',
    'hostel': '旅社',
    'motel': '汽车旅馆',
    'inn': '旅馆',
    'paradise': '天堂',
    'postcard': '明信片',
    'sightseeing': '观光',
    'souvenir': '纪念品',
    'wander': '漫步',
    'visa': '签证',
    'baggage': '行李',
    'backpack': '背包',
    'landmark': '地标',
    'scenery': '风景',
    'voyage': '航行',
    'cereal': '谷物',
    'fridge': '冰箱',
    'garlic': '大蒜',
    'grill': '烧烤',
    'grocery': '杂货',
    'lettuce': '生菜',
    'microwave': '微波炉',
    'mushroom': '蘑菇',
    'olive': '橄榄',
    'organic': '有机的',
    'pasta': '意大利面',
    'peach': '桃子',
    'recipe': '食谱',
    'sausage': '香肠',
    'vinegar': '醋',
    'wheat': '小麦',
    'strawberry': '草莓',
    'snack': '零食',
    'toast': '吐司',
    'collar': '衣领',
    'costume': '服装',
    'elegant': '优雅的',
    'handbag': '手提包',
    'jumper': '毛衣',
    'purse': '钱包',
    'scarf': '围巾',
    'silk': '丝绸',
    'sleeve': '袖子',
    'stripe': '条纹',
    'sunglasses': '太阳镜',
    'underwear': '内衣',
    'vest': '背心',
    'wool': '羊毛',
    'zip': '拉链',
    'attic': '阁楼',
    'balcony': '阳台',
    'basement': '地下室',
    'chimney': '烟囱',
    'couch': '沙发',
    'cupboard': '橱柜',
    'curtain': '窗帘',
    'cushion': '垫子',
    'doorway': '门口',
    'drawer': '抽屉',
    'fireplace': '壁炉',
    'heater': '加热器',
    'landlord': '房东',
    'lawn': '草坪',
    'mat': '垫子',
    'pillow': '枕头',
    'plug': '插头',
    'rug': '地毯',
    'shelf': '架子',
    'shower': '淋浴',
    'sink': '水槽',
    'sofa': '沙发',
    'stairs': '楼梯',
    'tap': '水龙头',
    'terrace': '露台',
    'vacuum': '吸尘器',
    'wardrobe': '衣柜',
    'yard': '院子',
    'accelerate': '加速',
    'brake': '刹车',
    'cab': '出租车',
    'carriage': '车厢',
    'commute': '通勤',
    'crossing': '人行横道',
    'diesel': '柴油',
    'fare': '车费',
    'ferry': '渡轮',
    'gear': '齿轮',
    'harbour': '港口',
    'helicopter': '直升机',
    'highway': '高速公路',
    'junction': '交叉路口',
    'lorry': '卡车',
    'motorway': '高速公路',
    'petrol': '汽油',
    'platform': '站台',
    'rail': '铁轨',
    'runway': '跑道',
    'steer': '驾驶',
    'subway': '地铁',
    'terminal': '航站楼',
    'tire': '轮胎',
    'tunnel': '隧道',
    'van': '货车',
    'vehicle': '车辆',
    'ache': '疼痛',
    'allergy': '过敏',
    'ambulance': '救护车',
    'ankle': '脚踝',
    'bandage': '绷带',
    'chin': '下巴',
    'clinic': '诊所',
    'deaf': '聋的',
    'dentist': '牙医',
    'diabetes': '糖尿病',
    'dizzy': '头晕的',
    'dose': '剂量',
    'elbow': '肘',
    'forehead': '额头',
    'gym': '健身房',
    'headache': '头痛',
    'immune': '免疫的',
    'infection': '感染',
    'injection': '注射',
    'jaw': '下巴',
    'joint': '关节',
    'kidney': '肾脏',
    'liver': '肝脏',
    'lung': '肺',
    'nail': '指甲',
    'nerve': '神经',
    'pharmacy': '药房',
    'pill': '药片',
    'poison': '毒药',
    'pregnant': '怀孕的',
    'prescription': '处方',
    'rib': '肋骨',
    'spine': '脊柱',
    'surgeon': '外科医生',
    'swallow': '吞咽',
    'symptom': '症状',
    'throat': '喉咙',
    'thumb': '拇指',
    'toe': '脚趾',
    'tongue': '舌头',
    'vaccine': '疫苗',
    'virus': '病毒',
    'vitamin': '维生素',
    'waist': '腰',
    'ward': '病房',
    'wheelchair': '轮椅',
    'wound': '伤口',
    'wrist': '手腕',
    'coupon': '优惠券',
    'merchant': '商人',
    'wholesale': '批发',
    'penny': '便士',
    'refund': '退款',
    'retail': '零售',
    'bargain': '讨价还价',
    'receipt': '收据',
    'algebra': '代数',
    'arithmetic': '算术',
    'blackboard': '黑板',
    'encyclopedia': '百科全书',
    'handwriting': '笔迹',
    'headmaster': '校长',
    'notebook': '笔记本',
    'textbook': '课本',
    'undergraduate': '本科生',
    'affection': '感情',
    'awkward': '尴尬的',
    'empathy': '同理心',
    'enthusiasm': '热情',
    'envy': '嫉妒',
    'frustrate': '挫败',
    'grief': '悲伤',
    'irritate': '激怒',
    'jealous': '嫉妒的',
    'quarrel': '争吵',
    'sorrow': '悲伤',
    'tease': '取笑',
    'temper': '脾气',
    'rehearsal': '排练',
    'rhythm': '节奏',
    'sculpture': '雕塑',
    'ballet': '芭蕾',
    'volleyball': '排球',
    'yoga': '瑜伽',
    'recreation': '娱乐',
    'chess': '国际象棋',
    'check-in': '登记入住',
    'accommodation': '住宿',
    'heritage': '遗产',
    'hiking': '远足',
    'resort': '度假胜地',
    'tourism': '旅游业',
    # --- Additional missing translations ---
    # food
    'berry': '浆果',
    'candy': '糖果',
    'cherry': '樱桃',
    'cookie': '饼干',
    'corn': '玉米',
    'dessert': '甜点',
    'dine': '用餐',
    'grape': '葡萄',
    'honey': '蜂蜜',
    'kettle': '水壶',
    'lamb': '羊肉',
    'pea': '豌豆',
    'pie': '馅饼',
    'pizza': '比萨',
    'pork': '猪肉',
    'roast': '烤',
    'steak': '牛排',
    'supper': '晚餐',
    'tomato': '番茄',
    # clothing
    'shorts': '短裤',
    'stain': '污渍',
    'wallet': '钱包',
    # home
    'lock': '锁',
    'tile': '瓷砖',
    # health
    'cough': '咳嗽',
    'teeth': '牙齿',
    # shopping
    'cheque': '支票',
    'mall': '购物中心',
    'supply': '供应',
    # nature
    'breeze': '微风',
    'butterfly': '蝴蝶',
    'deer': '鹿',
    'dolphin': '海豚',
    'ecology': '生态学',
    'eruption': '喷发',
    'fog': '雾',
    'frost': '霜',
    'goat': '山羊',
    'jungle': '丛林',
    'mammal': '哺乳动物',
    'rabbit': '兔子',
    'rainbow': '彩虹',
    'reef': '礁石',
    'shark': '鲨鱼',
    'sunshine': '阳光',
    'thunder': '雷',
    'tiger': '老虎',
    'volcano': '火山',
    'whale': '鲸鱼',
    'wolf': '狼',
    # entertainment
    'athletics': '田径',
    'surf': '冲浪',
    # travel
    'customs': '海关',
    'luggage': '行李',
    'suitcase': '手提箱',
    # work
    'intern': '实习生',
    'overtime': '加班',
    # school
    'diploma': '文凭',
    'graduation': '毕业',
    'grammar': '语法',
    'quiz': '测验',
    'semester': '学期',
    'tutor': '家教',
    'vocabulary': '词汇',
    # social
    'bore': '使厌烦',
    'compliment': '赞美',
    'confuse': '使困惑',
    'hug': '拥抱',
    'thankful': '感激的',
}

# --- Scene categories ---
SCENE_CATEGORIES = {
    'food': {
        'name': '食物饮料',
        'emoji': '\U0001f354',
        'description': '食物、饮料、烹饪相关词汇',
        'words': [
            'apple', 'banana', 'bean', 'beef', 'beer', 'berry', 'biscuit', 'bite', 'boil',
            'bottle', 'bowl', 'bread', 'breakfast', 'butter', 'cafe', 'cake', 'candy',
            'carrot', 'cereal', 'cheese', 'chef', 'cherry', 'chicken', 'chip', 'chocolate',
            'chop', 'coffee', 'cook', 'cookie', 'corn', 'cream', 'cup', 'dairy', 'delicious',
            'dessert', 'diet', 'dine', 'dinner', 'dish', 'drink', 'eat', 'egg', 'fat',
            'feed', 'fish', 'flavour', 'flour', 'food', 'fork', 'fresh', 'fridge', 'fruit',
            'fry', 'garlic', 'glass', 'grain', 'grape', 'grill', 'grocery', 'honey', 'hungry',
            'ingredient', 'jam', 'juice', 'kettle', 'kitchen', 'knife', 'lamb', 'lemon',
            'lettuce', 'lunch', 'meal', 'meat', 'menu', 'microwave', 'milk', 'mix',
            'mushroom', 'nut', 'oil', 'olive', 'onion', 'orange', 'organic', 'oven',
            'pan', 'pasta', 'pea', 'peach', 'pepper', 'pie', 'pizza', 'plate', 'pork',
            'pot', 'potato', 'pour', 'protein', 'raw', 'recipe', 'restaurant', 'rice',
            'roast', 'salad', 'salt', 'sandwich', 'sauce', 'sausage', 'slice', 'snack',
            'soup', 'spice', 'spoon', 'steak', 'stir', 'stomach', 'strawberry', 'sugar',
            'supper', 'sweet', 'taste', 'tea', 'toast', 'tomato', 'vegetable', 'vinegar',
            'water', 'wheat', 'wine',
        ]
    },
    'clothing': {
        'name': '服饰穿着',
        'emoji': '\U0001f455',
        'description': '衣服、鞋帽、配饰相关词汇',
        'words': [
            'belt', 'boot', 'button', 'cap', 'clothes', 'clothing', 'coat', 'collar',
            'comfortable', 'cotton', 'costume', 'designer', 'dress', 'elegant', 'fabric',
            'fashion', 'fit', 'formal', 'glove', 'handbag', 'hat', 'heel', 'jacket',
            'jeans', 'jewellery', 'jumper', 'label', 'leather', 'material', 'outfit',
            'pair', 'pants', 'pattern', 'pocket', 'purse', 'ring', 'scarf', 'shirt',
            'shoe', 'shop', 'shorts', 'silk', 'size', 'skirt', 'sleeve', 'sock',
            'stain', 'stripe', 'style', 'suit', 'sunglasses', 'sweater', 'tie', 'tight',
            'top', 'towel', 'trousers', 'underwear', 'uniform', 'vest', 'wallet', 'wear',
            'wool', 'zip',
        ]
    },
    'home': {
        'name': '家居房屋',
        'emoji': '\U0001f3e0',
        'description': '房屋、家具、家电相关词汇',
        'words': [
            'apartment', 'attic', 'balcony', 'basement', 'bathroom', 'bed', 'bedroom',
            'blanket', 'blind', 'brick', 'brush', 'build', 'carpet', 'ceiling', 'chair',
            'chimney', 'clean', 'clock', 'corridor', 'couch', 'cupboard', 'curtain',
            'cushion', 'decoration', 'desk', 'door', 'doorway', 'drawer', 'dust',
            'electricity', 'entrance', 'estate', 'fence', 'fireplace', 'flat', 'floor',
            'furniture', 'garage', 'garden', 'gate', 'hall', 'heater', 'home', 'house',
            'household', 'housing', 'iron', 'key', 'kitchen', 'lamp', 'landlord',
            'lawn', 'light', 'living', 'lock', 'mat', 'mirror', 'mortgage', 'neighbour',
            'oven', 'paint', 'path', 'pillow', 'pipe', 'plug', 'property', 'rent',
            'repair', 'roof', 'room', 'rug', 'shelf', 'shower', 'sink', 'sofa', 'stairs',
            'tap', 'tenant', 'terrace', 'tile', 'toilet', 'vacuum', 'wall', 'wardrobe',
            'wash', 'window', 'yard',
        ]
    },
    'transport': {
        'name': '交通出行',
        'emoji': '\U0001f697',
        'description': '交通工具、道路、出行相关词汇',
        'words': [
            'accelerate', 'accident', 'airline', 'airport', 'bicycle', 'bike', 'board',
            'brake', 'bridge', 'bus', 'cab', 'car', 'cargo', 'carriage', 'coach',
            'commute', 'crash', 'cross', 'crossing', 'cruise', 'cycle', 'delay',
            'deliver', 'departure', 'destination', 'diesel', 'direction', 'distance',
            'drive', 'driver', 'engine', 'exit', 'fare', 'ferry', 'flight', 'fuel',
            'garage', 'gear', 'harbour', 'helicopter', 'highway', 'jam', 'journey',
            'junction', 'lane', 'lorry', 'map', 'motorway', 'park', 'parking',
            'passenger', 'path', 'petrol', 'platform', 'port', 'rail', 'railway',
            'ride', 'road', 'route', 'runway', 'sail', 'seat', 'ship', 'signal',
            'speed', 'station', 'steer', 'stop', 'street', 'subway', 'taxi', 'terminal',
            'ticket', 'tire', 'traffic', 'train', 'transport', 'trip', 'truck', 'tunnel',
            'turn', 'van', 'vehicle', 'wheel',
        ]
    },
    'health': {
        'name': '健康身体',
        'emoji': '\U0001f3e5',
        'description': '身体、疾病、医疗、健身相关词汇',
        'words': [
            'ache', 'allergy', 'ambulance', 'ankle', 'appointment', 'arm', 'back',
            'bandage', 'blood', 'body', 'bone', 'brain', 'breath', 'breathe', 'burn',
            'cancer', 'chest', 'chin', 'clinic', 'cold', 'cough', 'cure', 'deaf',
            'dentist', 'depression', 'diabetes', 'diagnosis', 'diet', 'disability',
            'disease', 'dizzy', 'doctor', 'dose', 'drug', 'ear', 'elbow', 'emergency',
            'examine', 'exercise', 'eye', 'face', 'fat', 'fever', 'finger', 'fitness',
            'flu', 'foot', 'forehead', 'gym', 'hair', 'hand', 'head', 'headache',
            'heal', 'health', 'healthy', 'hear', 'heart', 'heel', 'hip', 'hospital',
            'hurt', 'ill', 'illness', 'immune', 'infection', 'injection', 'injury',
            'jaw', 'joint', 'kidney', 'knee', 'leg', 'lip', 'liver', 'lung', 'medicine',
            'mental', 'mouth', 'muscle', 'nail', 'neck', 'nerve', 'nose', 'nurse',
            'operate', 'operation', 'organ', 'pain', 'painful', 'patient', 'pharmacy',
            'physical', 'pill', 'poison', 'pregnant', 'prescription', 'pulse', 'recover',
            'recovery', 'relax', 'rib', 'shoulder', 'sick', 'skin', 'sleep', 'spine',
            'stomach', 'stress', 'stroke', 'surgeon', 'surgery', 'swallow', 'symptom',
            'teeth', 'therapy', 'throat', 'thumb', 'toe', 'tongue', 'tooth', 'treatment',
            'vaccine', 'virus', 'vitamin', 'waist', 'ward', 'weight', 'wheelchair',
            'wound', 'wrist',
        ]
    },
    'shopping': {
        'name': '购物消费',
        'emoji': '\U0001f6d2',
        'description': '购物、消费、金钱相关词汇',
        'words': [
            'account', 'afford', 'bargain', 'bill', 'brand', 'budget', 'buy', 'cash',
            'cent', 'change', 'charge', 'cheap', 'cheque', 'coin', 'consumer', 'cost',
            'coupon', 'credit', 'currency', 'customer', 'deal', 'debt', 'deliver',
            'delivery', 'demand', 'department', 'deposit', 'discount', 'dollar', 'earn',
            'exchange', 'expensive', 'export', 'fee', 'goods', 'guarantee', 'import',
            'income', 'insurance', 'invest', 'investment', 'item', 'loan', 'luxury',
            'mall', 'market', 'merchant', 'offer', 'online', 'order', 'owe', 'own',
            'package', 'pay', 'payment', 'penny', 'pound', 'price', 'produce', 'product',
            'profit', 'purchase', 'quality', 'quantity', 'receipt', 'refund', 'retail',
            'sale', 'save', 'sell', 'service', 'shelf', 'shop', 'shopping', 'spend',
            'store', 'supply', 'tax', 'trade', 'value', 'wallet', 'wholesale', 'worth',
        ]
    },
    'nature': {
        'name': '天气自然',
        'emoji': '\U0001f324\ufe0f',
        'description': '天气、动植物、环境相关词汇',
        'words': [
            'air', 'animal', 'atmosphere', 'autumn', 'bay', 'beach', 'bear', 'bee',
            'bird', 'blow', 'branch', 'breeze', 'butterfly', 'cat', 'cattle', 'cave',
            'chicken', 'climate', 'cloud', 'coast', 'cold', 'continent', 'cow',
            'creature', 'crop', 'deer', 'desert', 'dog', 'dolphin', 'drought',
            'dust', 'earth', 'earthquake', 'ecology', 'elephant', 'emission',
            'environment', 'eruption', 'evolution', 'farm', 'feather', 'field',
            'fish', 'flood', 'flower', 'fly', 'fog', 'forest', 'freeze', 'frost',
            'garden', 'globe', 'goat', 'grass', 'harvest', 'heat', 'hill', 'horse',
            'hurricane', 'ice', 'insect', 'island', 'jungle', 'lake', 'landscape',
            'leaf', 'lion', 'mammal', 'monkey', 'moon', 'mountain', 'mud', 'nature',
            'ocean', 'pet', 'pig', 'planet', 'plant', 'pollution', 'pond', 'rabbit',
            'rain', 'rainbow', 'recycle', 'reef', 'river', 'rock', 'root', 'sand',
            'sea', 'season', 'seed', 'shark', 'sheep', 'shell', 'shore', 'sky',
            'snake', 'snow', 'soil', 'species', 'spring', 'star', 'storm', 'stream',
            'summer', 'sun', 'sunshine', 'temperature', 'thunder', 'tide', 'tiger',
            'tree', 'tropical', 'valley', 'volcano', 'warm', 'waste', 'wave', 'weather',
            'whale', 'wildlife', 'wind', 'winter', 'wolf', 'wood', 'worm',
        ]
    },
    'entertainment': {
        'name': '娱乐爱好',
        'emoji': '\U0001f3ad',
        'description': '音乐、体育、艺术、游戏相关词汇',
        'words': [
            'act', 'action', 'actor', 'actress', 'adventure', 'album', 'art', 'artist',
            'athletics', 'audience', 'ballet', 'band', 'baseball', 'basketball', 'beat',
            'camera', 'camp', 'captain', 'celebrate', 'champion', 'channel', 'chess',
            'cinema', 'climb', 'club', 'coach', 'comedy', 'compete', 'competition',
            'concert', 'contest', 'creative', 'dance', 'director', 'drama', 'draw',
            'drawing', 'entertainment', 'episode', 'exhibition', 'fan', 'fiction',
            'film', 'football', 'fun', 'gallery', 'game', 'goal', 'golf', 'guitar',
            'hero', 'hobby', 'holiday', 'instrument', 'jazz', 'joke', 'kick', 'league',
            'leisure', 'match', 'medal', 'media', 'movie', 'museum', 'music', 'musical',
            'novel', 'opera', 'orchestra', 'outdoor', 'paint', 'painting', 'party',
            'perform', 'performance', 'photo', 'photograph', 'photography', 'piano',
            'play', 'player', 'plot', 'poem', 'poet', 'poetry', 'pool', 'race',
            'recreation', 'record', 'rehearsal', 'relax', 'rhythm', 'rock', 'role',
            'run', 'scene', 'score', 'screen', 'sculpture', 'series', 'show', 'sing',
            'singer', 'ski', 'soccer', 'song', 'sport', 'stadium', 'stage', 'star',
            'studio', 'surf', 'swim', 'team', 'tennis', 'theatre', 'tour', 'tournament',
            'video', 'volleyball', 'yoga',
        ]
    },
    'travel': {
        'name': '旅行酒店',
        'emoji': '\u2708\ufe0f',
        'description': '旅游、住宿、观光相关词汇',
        'words': [
            'abroad', 'accommodation', 'adventure', 'airline', 'airport', 'arrival',
            'attraction', 'backpack', 'baggage', 'beach', 'board', 'book', 'border',
            'brochure', 'cabin', 'camera', 'camp', 'cancel', 'check-in', 'coast',
            'confirm', 'cruise', 'culture', 'currency', 'customs', 'delay', 'depart',
            'departure', 'destination', 'embassy', 'excursion', 'explore', 'fare',
            'ferry', 'flight', 'foreign', 'guide', 'harbour', 'heritage', 'hiking',
            'holiday', 'hostel', 'hotel', 'inn', 'island', 'itinerary', 'journey',
            'landmark', 'language', 'leisure', 'local', 'luggage', 'map', 'monument',
            'motel', 'museum', 'overseas', 'pack', 'palace', 'paradise', 'passenger',
            'passport', 'photo', 'pilgrimage', 'port', 'postcard', 'reception',
            'reservation', 'resort', 'return', 'route', 'ruin', 'safari', 'scenery',
            'sightseeing', 'souvenir', 'suitcase', 'temple', 'terminal', 'ticket',
            'tour', 'tourism', 'tourist', 'translate', 'trip', 'vacation', 'visa',
            'visit', 'voyage', 'wander',
        ]
    },
    'work': {
        'name': '工作职场',
        'emoji': '\U0001f4bc',
        'description': '职业、办公、商务相关词汇',
        'words': [
            'accountant', 'agency', 'agenda', 'ambition', 'applicant', 'application',
            'apply', 'appoint', 'appointment', 'assistant', 'authority', 'boss',
            'brand', 'business', 'candidate', 'career', 'chairman', 'client',
            'colleague', 'commission', 'committee', 'company', 'conference', 'consultant',
            'contract', 'cooperate', 'corporate', 'corporation', 'deal', 'deadline',
            'demand', 'department', 'deputy', 'director', 'dismiss', 'document',
            'duty', 'earn', 'economy', 'efficiency', 'employ', 'employee', 'employer',
            'employment', 'enterprise', 'entrepreneur', 'executive', 'experience',
            'export', 'factory', 'firm', 'hire', 'human', 'import', 'income',
            'industry', 'intern', 'interview', 'invest', 'investment', 'job', 'labour',
            'lead', 'leadership', 'manage', 'management', 'manager', 'manufacture',
            'marketing', 'meeting', 'negotiate', 'network', 'occupation', 'office',
            'operate', 'organization', 'overtime', 'partner', 'partnership', 'pension',
            'position', 'profession', 'professional', 'profit', 'project', 'promote',
            'promotion', 'proposal', 'qualify', 'recruit', 'reference', 'resign',
            'responsibility', 'resume', 'retire', 'retirement', 'role', 'salary',
            'schedule', 'sector', 'shift', 'skill', 'staff', 'strategy', 'succeed',
            'success', 'supervisor', 'task', 'team', 'trade', 'training', 'union',
            'volunteer', 'wage', 'work', 'worker', 'workplace',
        ]
    },
    'school': {
        'name': '学校教育',
        'emoji': '\U0001f3eb',
        'description': '学校、学习、考试相关词汇',
        'words': [
            'academic', 'academy', 'algebra', 'arithmetic', 'assignment', 'biology',
            'blackboard', 'book', 'campus', 'certificate', 'chapter', 'chemistry',
            'class', 'classroom', 'college', 'composition', 'concentrate', 'course',
            'curriculum', 'debate', 'degree', 'dictionary', 'diploma', 'discipline',
            'education', 'elementary', 'encyclopedia', 'engineering', 'essay', 'exam',
            'examination', 'exercise', 'experiment', 'faculty', 'fail', 'geography',
            'grade', 'graduate', 'graduation', 'grammar', 'handwriting', 'headmaster',
            'history', 'homework', 'instruction', 'knowledge', 'language', 'learn',
            'lecture', 'lesson', 'level', 'library', 'literature', 'major', 'mark',
            'master', 'mathematics', 'memory', 'minor', 'note', 'notebook', 'paragraph',
            'pass', 'pen', 'pencil', 'philosophy', 'physics', 'practice', 'primary',
            'principal', 'professor', 'program', 'progress', 'project', 'pupil',
            'qualification', 'quiz', 'read', 'reading', 'register', 'research',
            'result', 'review', 'revision', 'scholar', 'scholarship', 'school',
            'science', 'secondary', 'semester', 'skill', 'student', 'study', 'subject',
            'teach', 'teacher', 'term', 'test', 'textbook', 'theory', 'tutor',
            'undergraduate', 'university', 'vocabulary', 'write', 'writing',
        ]
    },
    'social': {
        'name': '社交情感',
        'emoji': '\U0001f4ac',
        'description': '情感、社交、人际关系相关词汇',
        'words': [
            'admire', 'affection', 'afraid', 'agree', 'alone', 'anger', 'angry',
            'annoy', 'anxious', 'apologize', 'argue', 'argument', 'ashamed',
            'attitude', 'attract', 'awkward', 'blame', 'bore', 'bother', 'brave',
            'calm', 'care', 'celebrate', 'cheer', 'comfort', 'communicate',
            'communication', 'community', 'companion', 'complain', 'compliment',
            'concern', 'confidence', 'confident', 'confuse', 'congratulate',
            'conversation', 'cry', 'culture', 'curious', 'date', 'delight',
            'depressed', 'desire', 'disappoint', 'emotion', 'emotional', 'empathy',
            'encourage', 'enthusiasm', 'envy', 'excuse', 'family', 'fear', 'feel',
            'feeling', 'forgive', 'friend', 'friendly', 'friendship', 'frustrate',
            'generous', 'gentle', 'grateful', 'greet', 'grief', 'guilt', 'happiness',
            'happy', 'hate', 'honest', 'hope', 'hug', 'humour', 'impress', 'inspire',
            'introduce', 'invite', 'irritate', 'jealous', 'joy', 'kind', 'kiss',
            'laugh', 'lonely', 'love', 'marry', 'mood', 'neighbour', 'nervous',
            'offend', 'opinion', 'passion', 'patient', 'personality', 'pity', 'pleased',
            'polite', 'praise', 'pride', 'promise', 'proud', 'quarrel', 'regret',
            'reject', 'relationship', 'relief', 'respect', 'romance', 'romantic',
            'rude', 'sad', 'satisfy', 'shame', 'share', 'shock', 'shy', 'sincere',
            'smile', 'social', 'sorrow', 'sorry', 'sympathy', 'tease', 'temper',
            'tender', 'thankful', 'trust', 'upset', 'welcome', 'wish', 'worry',
        ]
    },
}


def load_csv_translations(csv_path):
    """Load term -> translation mapping from oxford_5000_cleaned.csv"""
    translations = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            term = row['term'].strip().lower()
            translation = row['translation'].strip()
            # Keep the first occurrence (some words may appear multiple times with different CEFR)
            if term not in translations:
                translations[term] = translation
    return translations


def check_audio(word, audio_dir):
    """Check if audio file exists for a word, return filename or None."""
    filename = f"{word}.wav"
    filepath = os.path.join(audio_dir, filename)
    if os.path.isfile(filepath):
        return filename
    return None


def escape_js_string(s):
    """Escape a string for use inside JS double-quoted string."""
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def generate_wordbook_js(scene_id, scene_data, translations, audio_dir):
    """Generate JS file content for a single scene wordbook."""
    words_js_lines = []
    missing_words = []
    audio_found = 0
    audio_missing = 0

    for word in scene_data['words']:
        word_lower = word.strip().lower()

        # Look up translation: first CSV, then EXTRA_TRANSLATIONS
        meaning = translations.get(word_lower)
        if meaning is None:
            meaning = EXTRA_TRANSLATIONS.get(word_lower)
        if meaning is None:
            meaning = EXTRA_TRANSLATIONS.get(word)
        if meaning is None:
            missing_words.append(word)
            meaning = word  # fallback: use the word itself

        # Check audio
        audio_file = check_audio(word_lower, audio_dir)
        # Also try with the original casing / hyphenated form
        if audio_file is None and word != word_lower:
            audio_file = check_audio(word, audio_dir)

        audio_str = f'"{escape_js_string(audio_file)}"' if audio_file else 'null'

        if audio_file:
            audio_found += 1
        else:
            audio_missing += 1

        word_escaped = escape_js_string(word_lower)
        meaning_escaped = escape_js_string(meaning)

        words_js_lines.append(
            f'                {{ word: "{word_escaped}", meaning: "{meaning_escaped}", audio: {audio_str} }}'
        )

    # Build the full JS content
    name_escaped = escape_js_string(scene_data['name'])
    emoji_escaped = escape_js_string(scene_data['emoji'])
    desc_escaped = escape_js_string(scene_data['description'])

    words_block = ',\n'.join(words_js_lines)

    js_content = f"""registerWordbook('scene_{scene_id}', {{
    name: "{name_escaped}",
    emoji: "{emoji_escaped}",
    group: 'scene',
    description: "{desc_escaped}",
    levels: {{
        all: {{
            name: "{emoji_escaped} \u5168\u90e8",
            words: [
{words_block}
            ]
        }}
    }}
}});
"""
    return js_content, missing_words, audio_found, audio_missing


def main():
    # Load CSV translations
    print(f"Loading CSV from: {CSV_PATH}")
    translations = load_csv_translations(CSV_PATH)
    print(f"Loaded {len(translations)} terms from CSV.")

    # Ensure output directory exists
    os.makedirs(WORDBOOKS_DIR, exist_ok=True)
    print(f"Output directory: {WORDBOOKS_DIR}")
    print(f"Audio directory: {AUDIO_DIR}")
    print()

    total_words = 0
    total_audio_found = 0
    total_audio_missing = 0
    all_missing = {}

    for scene_id, scene_data in SCENE_CATEGORIES.items():
        js_content, missing_words, audio_found, audio_missing = generate_wordbook_js(
            scene_id, scene_data, translations, AUDIO_DIR
        )

        output_path = os.path.join(WORDBOOKS_DIR, f'scene_{scene_id}.js')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(js_content)

        word_count = len(scene_data['words'])
        total_words += word_count
        total_audio_found += audio_found
        total_audio_missing += audio_missing

        status = f"  scene_{scene_id}.js  =>  {word_count:>3} words  |  audio: {audio_found} found, {audio_missing} missing"
        if missing_words:
            status += f"  |  NO TRANSLATION: {missing_words}"
            all_missing[scene_id] = missing_words
        print(status)

    print()
    print(f"{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total scenes generated:  {len(SCENE_CATEGORIES)}")
    print(f"Total words across all:  {total_words}")
    print(f"Total audio found:       {total_audio_found}")
    print(f"Total audio missing:     {total_audio_missing}")

    if all_missing:
        print()
        print(f"Words with NO translation (using word as fallback):")
        for sid, words in all_missing.items():
            print(f"  {sid}: {words}")

    print()
    print("Done! All scene wordbook files generated.")


if __name__ == '__main__':
    main()
