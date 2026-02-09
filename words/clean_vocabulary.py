"""
Oxford 5000 CSV Cleaner & Vocabulary JS Generator
Fixes:
1. Split merged/concatenated rows (e.g. "cut v.dad" -> "cut" + "dad")
2. Strip POS markers (adj., n., v., det./pron., modal, number, etc.)
3. Remove sense disambiguators (close 1, live1, can2)
4. Fix broken words (reven ge -> revenge)
5. Fix non-ASCII chars (non-breaking spaces, curly quotes)
6. Remove standalone POS abbreviations
7. Fill missing Chinese translations
8. Regenerate oxford_vocabulary.js
"""
import csv
import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, 'oxford_5000_merged_total_translated.csv')
MANIFEST_PATH = os.path.join(SCRIPT_DIR, 'tts_delivery', 'words_manifest.json')
AUDIO_DIR = os.path.join(SCRIPT_DIR, 'tts_delivery', 'audio')
OUTPUT_CSV = os.path.join(SCRIPT_DIR, 'oxford_5000_cleaned.csv')
OUTPUT_JS = os.path.join(os.path.dirname(SCRIPT_DIR), 'oxford_vocabulary.js')

# POS patterns to strip from terms
POS_TAGS = [
    r'\s+adj\./adv\.',
    r'\s+det\./pron\./adv\.',
    r'\s+det\./pron\.',
    r'\s+det\./number',
    r'\s+conj\./prep\.',
    r'\s+conj\./adv\.',
    r'\s+prep\./adv\.',
    r'\s+pron\./det\.',
    r'\s+adj\./pron\.',
    r'\s+adv\./prep\.',
    r'\s+exclam\./n\.',
    r'\s+number/det\.',
    r'\s+n\./v\.',
    r'\s+indefinite\s+article',
    r'\s+definite\s+article',
    r'\s+infinitive\s+marker',
    r'\s+modal\s+v\.',
    r'\s+modal',
    r'\s+auxiliary',
    r'\s+number',
    r'\s+adj\.',
    r'\s+adv\s*\.',
    r'\s+adv\.',
    r'\s+det\.',
    r'\s+pron\.',
    r'\s+prep\.',
    r'\s+conj\.',
    r'\s+exclam\.',
    r'\s+n\.',
    r'\s+v\s*\.',
    r'\s+v\.',
]

# Standalone POS abbreviations (entire term is just a POS marker)
SKIP_TERMS = {
    'adj.', 'adv.', 'n.', 'v.', 'conj.', 'det.', 'prep.', 'pron.', 'exclam.',
    'adj./adv.', 'det./pron.', 'n./v.', 'n.place', 'n.who', 'n.ethical',
    'n.treasure', 'n.neighbouring', 'infinitive marker', 'auxiliary',
}

# Regex to detect merged entries: word + POS_MARKER + nextword
# e.g. "cut v.dad", "sandwich n.Saturday", "bright adj.brilliant"
MERGE_PATTERN = re.compile(
    r'(\S+?)\s+'
    r'(?:adj\./adv\.|det\./pron\./adv\.|det\./pron\.|det\./number|'
    r'conj\./prep\.|conj\./adv\.|prep\./adv\.|pron\./det\.|'
    r'adj\./pron\.|adv\./prep\.|exclam\./n\.|number/det\.|n\./v\.|'
    r'indefinite\s+article|definite\s+article|infinitive\s+marker|'
    r'modal\s+v\.|modal|auxiliary|number|'
    r'adj\.|adv\s*\.|det\.|pron\.|prep\.|conj\.|exclam\.|n\.|v\s*\.)'
    r'\s*(\S.*)?'
)

# Known broken words to fix
BROKEN_WORDS = {
    'reven ge': 'revenge',
    'allright': 'all right',
    'second 1 det./': 'second',
    'recount 1': 'recount',
}

# Translation dictionary for common English words missing translations
# This covers the ~250 words at the end of the CSV that lack translations
TRANSLATIONS = {
    # Common C1 words - providing Chinese translations
    'abolish': '废除', 'abortion': '堕胎', 'absence': '缺席', 'absent': '缺席的',
    'absolute': '绝对的', 'absorb': '吸收', 'abstract': '抽象的', 'absurd': '荒谬的',
    'abundance': '丰富', 'abuse': '滥用', 'academy': '学院', 'accelerate': '加速',
    'accent': '口音', 'acceptable': '可接受的', 'acceptance': '接受', 'accessible': '可接近的',
    'accommodate': '容纳', 'accommodation': '住宿', 'accomplish': '完成', 'accomplishment': '成就',
    'accountability': '责任', 'accumulate': '积累', 'accuracy': '准确性', 'accusation': '指控',
    'acid': '酸', 'acknowledge': '承认', 'acquisition': '获取', 'activation': '激活',
    'activist': '活动家', 'adaptation': '适应', 'addiction': '成瘾', 'addition': '加法',
    'adequate': '充分的', 'administrator': '管理者', 'admiration': '钦佩', 'adoption': '采用',
    'advent': '出现', 'adversary': '对手', 'adverse': '不利的', 'advocate': '提倡',
    'aesthetic': '审美的', 'affection': '感情', 'aftermath': '后果', 'aggression': '侵略',
    'agony': '痛苦', 'aid': '援助', 'aids': '艾滋病', 'aka': '又称',
    'alien': '外星人', 'alignment': '对齐', 'allegation': '指控', 'allege': '宣称',
    'allegedly': '据称', 'alliance': '联盟', 'allocate': '分配', 'allocation': '分配',
    'allowance': '津贴', 'ally': '盟友', 'alongside': '在旁边', 'altar': '祭坛',
    'alternate': '交替', 'altogether': '完全', 'ambassador': '大使', 'ambiguity': '歧义',
    'ambiguous': '模棱两可的', 'amid': '在...之中', 'ammunition': '弹药', 'analogy': '类比',
    'anchor': '锚', 'angel': '天使', 'anger': '愤怒', 'angle': '角度',
    'animation': '动画', 'anonymous': '匿名的', 'anthropology': '人类学',
    'antibody': '抗体', 'anticipate': '预期', 'anxiety': '焦虑',
    'apparatus': '装置', 'appealing': '有吸引力的', 'appetite': '食欲',
    'appliance': '器具', 'applicable': '适用的', 'appreciation': '欣赏',
    'arbitrary': '任意的', 'arch': '拱门', 'arena': '竞技场',
    'arguably': '可以说', 'array': '数组', 'arrow': '箭头',
    'articulate': '清晰表达', 'artwork': '艺术品', 'assault': '攻击',
    'assert': '断言', 'assertion': '断言', 'asset': '资产',
    'asylum': '庇护', 'atom': '原子', 'atrocity': '暴行',
    'attachment': '附件', 'attain': '达到', 'autobiography': '自传',
    'autonomy': '自治', 'avid': '热心的', 'awareness': '意识',
    'backdrop': '背景', 'backing': '支持', 'bail': '保释',
    'ballot': '选票', 'ban': '禁止', 'banner': '横幅',
    'bare': '赤裸的', 'bargain': '交易', 'barrel': '桶',
    'baseline': '基线', 'bass': '低音', 'bat': '球棒',
    'batch': '批次', 'bay': '海湾', 'beacon': '灯塔',
    'beam': '光束', 'beast': '野兽', 'bee': '蜜蜂',
    'belly': '肚子', 'beloved': '心爱的', 'benchmark': '基准',
    'beneficial': '有益的', 'betray': '背叛', 'bias': '偏见',
    'bind': '绑定', 'biography': '传记', 'bishop': '主教',
    'blade': '刀片', 'blast': '爆炸', 'bleed': '流血',
    'blend': '混合', 'blessing': '祝福', 'bloom': '开花',
    'blueprint': '蓝图', 'bold': '大胆的', 'bolt': '螺栓',
    'bond': '债券', 'bonus': '奖金', 'boom': '繁荣',
    'boost': '促进', 'bounce': '弹跳', 'bound': '必然的',
    'boundary': '边界', 'bow': '弓', 'breach': '违反',
    'breakdown': '故障', 'breakthrough': '突破', 'breed': '品种',
    'bride': '新娘', 'brigade': '旅', 'broker': '经纪人',
    'brutal': '残忍的', 'buddy': '伙伴', 'bulk': '大量',
    'bulletin': '公告', 'bully': '欺负', 'bureau': '局',
    'bureaucracy': '官僚主义', 'burst': '爆发',
    'cage': '笼子', 'calendar': '日历', 'calling': '召唤',
    'cannon': '大炮', 'capitalism': '资本主义', 'capitalist': '资本家',
    'cargo': '货物', 'carpet': '地毯', 'carriage': '马车',
    'casualty': '伤亡', 'catalogue': '目录', 'cater': '迎合',
    'caution': '谨慎', 'ceasefire': '停火', 'census': '人口普查',
    'certainty': '确定性', 'certification': '认证', 'chancellor': '总理',
    'chaos': '混乱', 'characterize': '描述', 'charm': '魅力',
    'chart': '图表', 'chase': '追逐', 'check': '检查',
    'chef': '厨师', 'chief': '首领', 'chorus': '合唱',
    'chronic': '慢性的', 'chunk': '块', 'circuit': '电路',
    'circulate': '循环', 'citizenship': '公民身份', 'civic': '公民的',
    'civilian': '平民', 'civilization': '文明', 'clarify': '澄清',
    'clash': '冲突', 'classification': '分类', 'clause': '条款',
    'clergy': '神职人员', 'cliff': '悬崖', 'cling': '紧抓',
    'clip': '剪辑', 'closure': '关闭', 'cluster': '群',
    'coalition': '联盟', 'coastal': '沿海的', 'cocktail': '鸡尾酒',
    'cognitive': '认知的', 'coincide': '巧合', 'coincidence': '巧合',
    'collaboration': '合作', 'collaborative': '协作的', 'collar': '衣领',
    'colonial': '殖民的', 'colony': '殖民地', 'combat': '战斗',
    'comic': '漫画', 'commander': '指挥官', 'commence': '开始',
    'commentary': '评论', 'commentator': '评论员', 'commerce': '商业',
    'commissioner': '专员', 'commodity': '商品', 'commune': '公社',
    'communist': '共产主义者', 'companion': '同伴', 'comparable': '可比的',
    'compassion': '同情', 'compel': '强迫', 'compensate': '补偿',
    'compensation': '补偿', 'competence': '能力', 'competent': '胜任的',
    'compile': '编译', 'complement': '补充', 'completion': '完成',
    'complexity': '复杂性', 'compliance': '合规', 'complication': '并发症',
    'compliment': '赞美', 'comply': '遵守', 'compose': '组成',
    'composer': '作曲家', 'composition': '作曲', 'compromise': '妥协',
    'compulsory': '强制的', 'conceal': '隐藏', 'concede': '承认',
    'conceive': '构想', 'conception': '概念', 'concession': '让步',
    'condemn': '谴责', 'configuration': '配置', 'confine': '限制',
    'confirmation': '确认', 'confront': '面对', 'confrontation': '对抗',
    'congregation': '会众', 'conscience': '良心', 'consciousness': '意识',
    'consensus': '共识', 'consent': '同意', 'consequence': '后果',
    'consequently': '因此', 'conservation': '保护', 'conserve': '节约',
    'consistency': '一致性', 'consolidate': '巩固', 'conspiracy': '阴谋',
    'constituent': '成分', 'constitution': '宪法', 'constitutional': '宪法的',
    'constrain': '约束', 'constraint': '约束', 'consultant': '顾问',
    'consultation': '咨询', 'consumption': '消费', 'container': '容器',
    'contemplate': '沉思', 'contempt': '蔑视', 'contend': '竞争',
    'contender': '竞争者', 'contest': '竞赛', 'continent': '大陆',
    'contractor': '承包商', 'contradiction': '矛盾', 'controversial': '有争议的',
    'controversy': '争论', 'convention': '惯例', 'conversion': '转换',
    'conviction': '定罪', 'copyright': '版权', 'cord': '绳索',
    'cornerstone': '基石', 'coronary': '冠状的', 'corporate': '企业的',
    'correction': '纠正', 'correlation': '相关性', 'correspondent': '记者',
    'corresponding': '相应的', 'corruption': '腐败', 'costly': '昂贵的',
    'council': '委员会', 'counselling': '咨询', 'counsellor': '顾问',
    'counterpart': '对应物', 'countless': '无数的', 'coup': '政变',
    'courtesy': '礼貌', 'craft': '工艺', 'crawl': '爬行',
    'creativity': '创造力', 'credibility': '可信度', 'crew': '船员',
    'critique': '批评', 'crown': '王冠', 'crude': '粗糙的',
    'crush': '粉碎', 'crystal': '水晶', 'cultivation': '种植',
    'curiosity': '好奇心', 'curriculum': '课程', 'custody': '监护',
    'custom': '自定义', 'cyber': '网络的',
    'dawn': '黎明', 'deadly': '致命的', 'dealer': '经销商',
    'dean': '院长', 'debris': '碎片', 'debut': '首次亮相',
    'decay': '衰落', 'declaration': '声明', 'dedication': '奉献',
    'deem': '认为', 'default': '默认', 'defect': '缺陷',
    'deficit': '赤字', 'defy': '违抗', 'delegate': '代表',
    'delegation': '代表团', 'deliberate': '故意的', 'deliberately': '故意地',
    'delicate': '精致的', 'denial': '否认', 'denounce': '谴责',
    'dense': '密集的', 'deployment': '部署', 'deposit': '存款',
    'depression': '抑郁', 'deprive': '剥夺', 'deputy': '副',
    'derive': '导出', 'descendant': '后代', 'descent': '下降',
    'designate': '指定', 'desirable': '理想的', 'desktop': '桌面',
    'despair': '绝望', 'desperate': '绝望的', 'detention': '拘留',
    'deteriorate': '恶化', 'devastate': '摧毁', 'devil': '魔鬼',
    'devise': '设计', 'devote': '致力于', 'diagnosis': '诊断',
    'dialogue': '对话', 'dictate': '支配', 'dignity': '尊严',
    'dilemma': '困境', 'dimension': '维度', 'diplomacy': '外交',
    'diplomat': '外交官', 'directive': '指令', 'disability': '残疾',
    'discard': '丢弃', 'discharge': '排放', 'discipline': '纪律',
    'disclosure': '披露', 'discourse': '话语', 'discretion': '自由裁量权',
    'discrimination': '歧视', 'displace': '取代', 'disposal': '处置',
    'dispose': '处理', 'dispute': '争端', 'disrupt': '扰乱',
    'disruption': '中断', 'dissolve': '溶解', 'distant': '遥远的',
    'distinct': '独特的', 'distinction': '区别', 'distinctive': '独特的',
    'distort': '扭曲', 'distress': '困扰', 'distribution': '分配',
    'disturb': '打扰', 'diversity': '多样性', 'divine': '神圣的',
    'doctrine': '教义', 'documentation': '文档', 'domain': '领域',
    'domestic': '国内的', 'dominance': '支配', 'donation': '捐赠',
    'donor': '捐赠者', 'dose': '剂量', 'draft': '草案',
    'drain': '排水', 'dramatically': '戏剧性地', 'drift': '漂移',
    'drought': '干旱', 'dual': '双重的', 'dub': '配音',
    'dump': '倾倒', 'duration': '持续时间', 'dust': '灰尘',
    'dwell': '居住', 'dynamic': '动态的', 'dynasty': '王朝',
    'ease': '缓解', 'echo': '回声', 'ecological': '生态的',
    'ecology': '生态', 'economist': '经济学家', 'editorial': '社论',
    'ego': '自我', 'elaborate': '精心的', 'elder': '长者',
    'electoral': '选举的', 'eligible': '合格的', 'elite': '精英',
    'embed': '嵌入', 'embody': '体现', 'embrace': '拥抱',
    'emergence': '出现', 'emission': '排放', 'emperor': '皇帝',
    'empire': '帝国', 'empower': '赋权', 'enact': '制定',
    'encompass': '包含', 'encounter': '遇到', 'endeavour': '努力',
    'endless': '无尽的', 'endorse': '支持', 'endure': '忍受',
    'enforcement': '执行', 'engagement': '参与', 'enterprise': '企业',
    'enthusiasm': '热情', 'entity': '实体', 'entrepreneur': '企业家',
    'epidemic': '流行病', 'equality': '平等', 'equation': '方程',
    'equilibrium': '平衡', 'equity': '公平', 'equivalent': '等价的',
    'erode': '侵蚀', 'escalate': '升级', 'essence': '本质',
    'eternal': '永恒的', 'evacuation': '疏散', 'evaluate': '评估',
    'evaluation': '评估', 'evident': '明显的', 'evil': '邪恶',
    'evolution': '进化', 'evolve': '进化', 'excavation': '挖掘',
    'exception': '例外', 'excess': '过量', 'exclusive': '独家的',
    'exclusively': '独家地', 'execution': '执行', 'executive': '高管',
    'exemption': '豁免', 'exile': '流放', 'expansion': '扩张',
    'expedition': '远征', 'expertise': '专业知识', 'expiry': '到期',
    'explicit': '明确的', 'exploitation': '剥削', 'explosion': '爆炸',
    'explosive': '爆炸性的', 'exponent': '指数', 'export': '出口',
    'extract': '提取', 'extraction': '提取', 'extreme': '极端的',
    'eyebrow': '眉毛', 'fabric': '织物', 'facade': '外观',
    'facilitate': '促进', 'faction': '派系', 'fairy': '仙女',
    'fame': '名声', 'famine': '饥荒', 'fantasy': '幻想',
    'fare': '票价', 'fascinate': '迷住', 'fate': '命运',
    'fatigue': '疲劳', 'feat': '壮举', 'federation': '联邦',
    'feminist': '女权主义者', 'fibre': '纤维', 'fierce': '激烈的',
    'firearm': '枪支', 'fixture': '固定装置', 'flag': '标志',
    'flair': '天赋', 'flame': '火焰', 'flaw': '缺陷',
    'flee': '逃离', 'fleet': '舰队', 'flesh': '肉',
    'flexibility': '灵活性', 'flip': '翻转', 'float': '漂浮',
    'flood': '洪水', 'flourish': '繁荣', 'fluid': '液体',
    'flush': '冲洗', 'folk': '民间的', 'footage': '镜头',
    'forecast': '预测', 'forge': '锻造', 'format': '格式',
    'formation': '形成', 'formula': '公式', 'forth': '向前',
    'fortune': '财富', 'forum': '论坛', 'fossil': '化石',
    'foster': '培养', 'fraction': '分数', 'fragment': '碎片',
    'franchise': '特许经营', 'fraud': '欺诈', 'freely': '自由地',
    'frequency': '频率', 'frontier': '边境', 'frustrate': '挫败',
    'frustration': '挫折', 'fulfil': '实现', 'full-time': '全职',
    'funeral': '葬礼', 'furnish': '装备', 'fury': '愤怒',
    'fusion': '融合', 'galaxy': '银河', 'gang': '帮派',
    'gaze': '凝视', 'gear': '齿轮', 'genocide': '种族灭绝',
    'genuine': '真正的', 'gesture': '手势', 'glance': '一瞥',
    'globe': '地球', 'glory': '荣耀', 'gorgeous': '华丽的',
    'govern': '统治', 'governance': '治理', 'grace': '优雅',
    'grain': '谷物', 'graphic': '图形的', 'grasp': '抓住',
    'grave': '坟墓', 'gravity': '重力', 'greenhouse': '温室',
    'greet': '问候', 'grief': '悲伤', 'grin': '咧嘴笑',
    'grip': '紧握', 'gross': '总的', 'groundwork': '基础',
    'guardian': '监护人', 'guerrilla': '游击队', 'guilt': '内疚',
    'gut': '直觉',
    'habitat': '栖息地', 'halt': '停止', 'hamper': '阻碍',
    'handful': '少数', 'harassment': '骚扰', 'hardware': '硬件',
    'harmful': '有害的', 'harmony': '和谐', 'harsh': '严酷的',
    'harvest': '收获', 'hatred': '仇恨', 'haunt': '萦绕',
    'hazard': '危险', 'heal': '治愈', 'heap': '堆',
    'hearing': '听证会', 'hedge': '树篱', 'heir': '继承人',
    'hemisphere': '半球', 'heritage': '遗产', 'hierarchy': '等级制度',
    'high-profile': '高调的', 'highland': '高地', 'highlight': '突出',
    'hilarious': '搞笑的', 'hip': '臀部', 'historian': '历史学家',
    'homeland': '祖国', 'hopeful': '有希望的', 'horizon': '地平线',
    'hormone': '激素', 'horn': '角', 'hostage': '人质',
    'hostile': '敌对的', 'household': '家庭', 'humanitarian': '人道主义的',
    'humble': '谦逊的', 'humidity': '湿度', 'hunger': '饥饿',
    'hunt': '狩猎', 'hurricane': '飓风', 'hydrogen': '氢',
    'hypothesis': '假设',
    'icon': '图标', 'identical': '相同的', 'identification': '识别',
    'ideology': '意识形态', 'ignorance': '无知', 'illusion': '幻觉',
    'illustration': '插图', 'imagery': '意象', 'immigration': '移民',
    'imminent': '迫在眉睫的', 'immune': '免疫的', 'implement': '实施',
    'implementation': '实施', 'implication': '含义', 'implicit': '隐含的',
    'impose': '强加', 'imprisonment': '监禁', 'impulse': '冲动',
    'inability': '无能', 'inadequate': '不充分的', 'inappropriate': '不适当的',
    'incidence': '发生率', 'inclusion': '包含', 'incorporate': '合并',
    'incur': '招致', 'independence': '独立', 'indicator': '指标',
    'indictment': '起诉书', 'indigenous': '本土的', 'induce': '诱导',
    'inequality': '不平等', 'inevitable': '不可避免的', 'infant': '婴儿',
    'infection': '感染', 'inflation': '通货膨胀', 'influential': '有影响力的',
    'infrastructure': '基础设施', 'ingredient': '成分', 'inherent': '固有的',
    'inherit': '继承', 'inhibit': '抑制', 'initiate': '发起',
    'initiative': '倡议', 'inject': '注入', 'injection': '注射',
    'innovation': '创新', 'innovative': '创新的', 'input': '输入',
    'inquiry': '调查', 'inscription': '铭文', 'insert': '插入',
    'insider': '内部人员', 'inspection': '检查', 'inspector': '检查员',
    'installation': '安装', 'instance': '实例', 'instant': '即时的',
    'institutional': '制度的', 'instinct': '本能', 'instrumental': '有帮助的',
    'intake': '摄入', 'integral': '不可缺少的', 'integrate': '整合',
    'integration': '整合', 'integrity': '完整性', 'intellectual': '智力的',
    'intensify': '加强', 'intensity': '强度', 'intensive': '密集的',
    'intent': '意图', 'interact': '互动', 'interference': '干扰',
    'interior': '内部', 'intermediate': '中间的', 'interpretation': '解释',
    'intervene': '干预', 'intervention': '干预', 'intimate': '亲密的',
    'invasion': '入侵', 'investigator': '调查员', 'invisible': '看不见的',
    'invoke': '调用', 'irony': '讽刺', 'isolation': '隔离',
    'jaw': '下巴', 'journalism': '新闻', 'judicial': '司法的',
    'junction': '交叉口', 'jurisdiction': '管辖权', 'jury': '陪审团',
    'justification': '理由', 'justify': '证明',
    'keen': '热衷的', 'kidnap': '绑架', 'kingdom': '王国',
    'kit': '工具包', 'knee': '膝盖', 'knit': '编织',
    'label': '标签', 'ladder': '梯子', 'landlord': '房东',
    'landmark': '地标', 'landscape': '风景', 'lane': '车道',
    'laser': '激光', 'lateral': '侧面的', 'latitude': '纬度',
    'latter': '后者', 'launch': '发射', 'lawsuit': '诉讼',
    'layout': '布局', 'league': '联盟', 'lean': '倾斜',
    'leap': '跳跃', 'leave': '离开', 'legacy': '遗产',
    'legend': '传说', 'legislation': '立法', 'legislature': '立法机构',
    'legitimate': '合法的', 'leisure': '休闲', 'lend': '借出',
    'lesbian': '女同性恋', 'level': '水平', 'lever': '杠杆',
    'liberal': '自由的', 'liberation': '解放', 'liberty': '自由',
    'licence': '许可证', 'likelihood': '可能性', 'limb': '四肢',
    'limitation': '限制', 'lineup': '阵容', 'linger': '逗留',
    'linkage': '联系', 'literacy': '识字', 'literal': '字面的',
    'literary': '文学的', 'litre': '升', 'litter': '垃圾',
    'livestock': '牲畜', 'lobby': '游说', 'log': '日志',
    'logic': '逻辑', 'lone': '孤独的', 'longtime': '长期的',
    'loop': '循环', 'lord': '勋爵', 'loyalty': '忠诚',
    'lump': '块',
    'machinery': '机器', 'magical': '神奇的', 'magistrate': '地方法官',
    'magnificent': '壮丽的', 'magnitude': '量级', 'mainstream': '主流',
    'maintenance': '维护', 'mandate': '授权', 'manifest': '清单',
    'manipulate': '操纵', 'manipulation': '操纵', 'manuscript': '手稿',
    'marathon': '马拉松', 'march': '行军', 'margin': '边距',
    'marker': '标记', 'marketplace': '市场', 'massacre': '屠杀',
    'mate': '伙伴', 'mechanism': '机制', 'medal': '奖牌',
    'meditation': '冥想', 'membrane': '膜', 'memoir': '回忆录',
    'memorial': '纪念的', 'merchant': '商人', 'mercy': '怜悯',
    'mere': '仅仅的', 'merely': '仅仅', 'merge': '合并',
    'merger': '合并', 'merit': '优点', 'metaphor': '隐喻',
    'methodology': '方法论', 'midst': '中间', 'migration': '迁移',
    'militant': '激进的', 'militia': '民兵', 'mineral': '矿物',
    'minister': '部长', 'ministry': '部门', 'miracle': '奇迹',
    'misery': '痛苦', 'misleading': '误导的', 'missile': '导弹',
    'missionary': '传教士', 'mob': '暴民', 'mobility': '流动性',
    'mobilize': '动员', 'moderate': '适度的', 'modification': '修改',
    'momentum': '势头', 'monarch': '君主', 'monastery': '修道院',
    'monetary': '货币的', 'monopoly': '垄断', 'monument': '纪念碑',
    'morale': '士气', 'mortality': '死亡率', 'mortgage': '抵押贷款',
    'motif': '主题', 'motion': '运动', 'mount': '安装',
    'mould': '模具', 'multilateral': '多边的', 'municipal': '市政的',
    'mutual': '相互的', 'myth': '神话', 'mythology': '神话学',
    'nail': '钉子', 'naive': '天真的', 'narrative': '叙事',
    'nationwide': '全国性的', 'naval': '海军的', 'necessity': '必要性',
    'neglect': '忽视', 'negotiate': '谈判', 'negotiation': '谈判',
    'nerve': '神经', 'networking': '社交', 'neutral': '中立的',
    'newcomer': '新来者', 'newsletter': '通讯', 'niche': '利基',
    'noble': '高贵的', 'nominate': '提名', 'nomination': '提名',
    'nonetheless': '尽管如此', 'nonsense': '胡说', 'norm': '规范',
    'notable': '显著的', 'notably': '尤其', 'notify': '通知',
    'notion': '概念', 'notorious': '臭名昭著的', 'novel': '小说',
    'nucleus': '核', 'nuisance': '麻烦', 'nursing': '护理',
    'nutrition': '营养',
    'obesity': '肥胖', 'oblige': '迫使', 'obscure': '模糊的',
    'observation': '观察', 'obsess': '着迷', 'obstacle': '障碍',
    'occurrence': '发生', 'odds': '几率', 'offence': '犯罪',
    'offspring': '后代', 'ongoing': '持续的', 'onset': '开始',
    'operational': '运营的', 'operator': '运营商', 'opt': '选择',
    'optical': '光学的', 'optimism': '乐观', 'optimistic': '乐观的',
    'orbit': '轨道', 'organ': '器官', 'organism': '有机体',
    'orientation': '方向', 'origin': '起源', 'outbreak': '爆发',
    'outfit': '装备', 'output': '输出', 'outrage': '愤怒',
    'outsider': '局外人', 'outstanding': '杰出的', 'overcome': '克服',
    'overlap': '重叠', 'overlook': '忽视', 'oversee': '监督',
    'overtime': '加班', 'overview': '概述', 'overwhelm': '压倒',
    'ownership': '所有权', 'oxygen': '氧气',
    'pace': '步伐', 'pack': '包', 'pact': '协定',
    'pan': '平底锅', 'pandemic': '大流行', 'panel': '面板',
    'parade': '游行', 'paradox': '悖论', 'paragraph': '段落',
    'parallel': '平行的', 'parameter': '参数', 'parish': '教区',
    'parliament': '议会', 'part-time': '兼职', 'partial': '部分的',
    'participant': '参与者', 'participation': '参与', 'partnership': '伙伴关系',
    'passion': '激情', 'passionate': '热情的', 'passive': '被动的',
    'patent': '专利', 'patience': '耐心', 'patriot': '爱国者',
    'patrol': '巡逻', 'patron': '赞助人', 'peak': '巅峰',
    'peasant': '农民', 'peculiar': '奇特的', 'peer': '同行',
    'penalty': '罚款', 'penetrate': '渗透', 'pension': '养老金',
    'perceive': '感知', 'perception': '感知', 'persistent': '持久的',
    'personnel': '人员', 'petition': '请愿', 'pharmaceutical': '制药的',
    'phase': '阶段', 'phenomenon': '现象', 'philosopher': '哲学家',
    'photography': '摄影', 'phrase': '短语', 'physician': '医生',
    'pier': '码头', 'pilgrim': '朝圣者', 'pine': '松树',
    'pioneer': '先驱', 'pipeline': '管道', 'pit': '坑',
    'pitch': '音高', 'plague': '瘟疫', 'plea': '恳求',
    'plead': '辩护', 'pledge': '承诺', 'plot': '情节',
    'plug': '插头', 'plunge': '跳入', 'pole': '极',
    'poll': '投票', 'pond': '池塘', 'portfolio': '投资组合',
    'portray': '描绘', 'pose': '构成', 'possession': '拥有',
    'poster': '海报', 'postpone': '推迟', 'pot': '锅',
    'pottery': '陶器', 'poultry': '家禽', 'poverty': '贫困',
    'practitioner': '从业者', 'prayer': '祈祷', 'precede': '先于',
    'precedent': '先例', 'precious': '珍贵的', 'precisely': '精确地',
    'precision': '精确', 'predator': '掠食者', 'predecessor': '前任',
    'predominantly': '主要地', 'prejudice': '偏见', 'premise': '前提',
    'premium': '溢价', 'presidency': '总统任期', 'presidential': '总统的',
    'prestige': '声望', 'presumably': '大概', 'presume': '假设',
    'prevalence': '流行', 'prevention': '预防', 'prey': '猎物',
    'pride': '骄傲', 'priest': '牧师', 'primarily': '主要地',
    'primitive': '原始的', 'princess': '公主', 'principal': '主要的',
    'principally': '主要地', 'privilege': '特权', 'probe': '探测',
    'proceeding': '诉讼程序', 'proceeds': '收益', 'proclaim': '宣告',
    'procurement': '采购', 'productivity': '生产力', 'profession': '职业',
    'profound': '深刻的', 'projection': '预测', 'prominent': '突出的',
    'pronounced': '明显的', 'propaganda': '宣传', 'propel': '推进',
    'prophet': '先知', 'proportion': '比例', 'proposition': '命题',
    'prosecute': '起诉', 'prosecution': '检察', 'prosecutor': '检察官',
    'prosperity': '繁荣', 'protective': '保护的', 'protocol': '协议',
    'province': '省', 'provincial': '省的', 'provision': '规定',
    'provoke': '挑衅', 'psychiatric': '精神病学的', 'pulse': '脉搏',
    'pump': '泵', 'punch': '拳打', 'pursue': '追求',
    'query': '查询', 'quest': '探索', 'quota': '配额',
    'radar': '雷达', 'radical': '激进的', 'rage': '愤怒',
    'raid': '突袭', 'rally': '集会', 'ranking': '排名',
    'rape': '强奸', 'ratio': '比率', 'rational': '理性的',
    'ray': '射线', 'readily': '容易地', 'realization': '实现',
    'realm': '领域', 'rear': '后部', 'reasoning': '推理',
    'reassure': '安慰', 'rebel': '反叛者', 'rebellion': '叛乱',
    'recipient': '接收者', 'reconstruction': '重建', 'recount': '叙述',
    'referendum': '公投', 'reflection': '反思', 'reform': '改革',
    'refuge': '避难', 'refusal': '拒绝', 'regain': '恢复',
    'regardless': '不管', 'regime': '政权', 'regulator': '监管机构',
    'regulatory': '监管的', 'rehabilitation': '康复', 'reign': '统治',
    'rejection': '拒绝', 'relevance': '相关性', 'reliability': '可靠性',
    'reluctant': '不情愿的', 'remainder': '剩余', 'remains': '遗迹',
    'remedy': '补救', 'reminder': '提醒', 'removal': '移除',
    'render': '渲染', 'renew': '更新', 'renowned': '著名的',
    'rental': '租赁', 'replacement': '替换', 'reportedly': '据报道',
    'representation': '代表', 'reproduce': '繁殖', 'reproduction': '繁殖',
    'republic': '共和国', 'resemble': '相似', 'reside': '居住',
    'residence': '住所', 'residential': '住宅的', 'residue': '残留',
    'resignation': '辞职', 'resistance': '抵抗', 'respective': '各自的',
    'respectively': '分别', 'restoration': '恢复', 'restraint': '克制',
    'resume': '恢复', 'retreat': '撤退', 'retrieve': '检索',
    'revelation': '启示', 'revenge': '报复', 'reverse': '反转',
    'revival': '复兴', 'revive': '复活', 'revolutionary': '革命的',
    'rhetoric': '修辞', 'rib': '肋骨', 'ribbon': '丝带',
    'rigid': '刚性的', 'riot': '暴乱', 'rip': '撕裂',
    'ritual': '仪式', 'rival': '对手', 'robust': '强健的',
    'rod': '杆', 'romance': '浪漫', 'rope': '绳子',
    'rotation': '旋转', 'royal': '皇家的', 'ruin': '毁灭',
    'ruling': '裁定', 'rumour': '谣言', 'rural': '农村的',
    'sacred': '神圣的', 'sacrifice': '牺牲', 'saint': '圣人',
    'sake': '缘故', 'sanction': '制裁', 'satellite': '卫星',
    'savage': '野蛮的', 'scandal': '丑闻', 'scatter': '散布',
    'scenario': '场景', 'scope': '范围', 'scream': '尖叫',
    'sculpture': '雕塑', 'seal': '密封', 'secular': '世俗的',
    'segment': '段', 'seize': '抓住', 'sensation': '感觉',
    'sentiment': '情感', 'separation': '分离', 'sequence': '序列',
    'sergeant': '中士', 'serial': '连续的', 'settlement': '和解',
    'settler': '定居者', 'severe': '严重的', 'sexuality': '性',
    'shade': '阴影', 'shadow': '影子', 'shall': '将',
    'shallow': '浅的', 'shame': '羞耻', 'shatter': '粉碎',
    'shed': '小屋', 'sheer': '纯粹的', 'shelter': '庇护所',
    'shield': '盾牌', 'shipping': '航运', 'shore': '海岸',
    'shortage': '短缺', 'shrink': '收缩', 'siege': '围攻',
    'sigh': '叹息', 'simultaneously': '同时', 'sin': '罪',
    'situated': '坐落于', 'sketch': '素描', 'skip': '跳过',
    'slam': '猛关', 'slap': '掌击', 'slash': '削减',
    'slavery': '奴隶制', 'slot': '槽', 'smash': '粉碎',
    'snap': '折断', 'soak': '浸泡', 'soar': '飙升',
    'socialist': '社会主义者', 'sole': '唯一的', 'solely': '仅仅',
    'solicitor': '律师', 'solidarity': '团结', 'solo': '独奏',
    'sound': '健全的', 'sovereignty': '主权', 'spam': '垃圾邮件',
    'span': '跨度', 'spare': '备用的', 'spark': '火花',
    'specialized': '专业的', 'specification': '规格', 'specimen': '标本',
    'spectacle': '景象', 'spectrum': '光谱', 'spell': '拼写',
    'sphere': '球体', 'spin': '旋转', 'spine': '脊柱',
    'spotlight': '聚光灯', 'spouse': '配偶', 'spy': '间谍',
    'squad': '小队', 'squeeze': '挤压', 'stab': '刺',
    'stability': '稳定性', 'stabilize': '稳定', 'stake': '利害关系',
    'standing': '常设的', 'stark': '鲜明的', 'statistical': '统计的',
    'steer': '引导', 'stem': '茎', 'stereotype': '刻板印象',
    'stimulus': '刺激', 'stir': '搅拌', 'storage': '存储',
    'straightforward': '简单的', 'strain': '压力', 'strand': '线',
    'strategic': '战略的', 'striking': '显著的', 'strip': '剥夺',
    'strive': '奋斗', 'structural': '结构的', 'stumble': '绊倒',
    'stun': '使震惊', 'submission': '提交', 'subscriber': '订阅者',
    'subscription': '订阅', 'subsidy': '补贴', 'substantial': '大量的',
    'substantially': '大量地', 'substitute': '替代', 'substitution': '替换',
    'subtle': '微妙的', 'suburban': '郊区的', 'succession': '继承',
    'successive': '连续的', 'successor': '继任者', 'suck': '吸',
    'sue': '起诉', 'suicide': '自杀', 'suite': '套房',
    'summit': '峰会', 'superb': '极好的', 'superior': '优越的',
    'supervise': '监督', 'supervision': '监督', 'supervisor': '主管',
    'supplement': '补充', 'supportive': '支持的', 'supposedly': '据称',
    'suppress': '压制', 'supreme': '最高的', 'surge': '激增',
    'surgical': '外科的', 'surplus': '过剩', 'surrender': '投降',
    'surveillance': '监视', 'suspension': '暂停', 'suspicion': '怀疑',
    'suspicious': '可疑的', 'sustain': '维持', 'swing': '摇摆',
    'sword': '剑', 'symbolic': '象征的', 'syndrome': '综合症',
    'synthesis': '合成', 'systematic': '系统的', 'tackle': '处理',
    'tactic': '策略', 'tactical': '战术的', 'taxpayer': '纳税人',
    'tempt': '诱惑', 'tenant': '租户', 'tender': '温柔的',
    'tenure': '任期', 'terminal': '终端', 'terminate': '终止',
    'terrain': '地形', 'terrific': '极好的', 'testify': '作证',
    'testimony': '证词', 'texture': '质地', 'thankfully': '幸运地',
    'theatrical': '戏剧的', 'theology': '神学', 'theoretical': '理论的',
    'thereafter': '此后', 'thereby': '因此', 'thoughtful': '体贴的',
    'thought-provoking': '发人深省的', 'thread': '线程', 'threshold': '门槛',
    'thrilled': '兴奋的', 'thrive': '茁壮成长', 'tide': '潮汐',
    'tighten': '收紧', 'timber': '木材', 'timely': '及时的',
    'tobacco': '烟草', 'tolerance': '容忍', 'tolerate': '忍受',
    'toll': '通行费', 'torture': '酷刑', 'toxic': '有毒的',
    'trace': '痕迹', 'trademark': '商标', 'trail': '小径',
    'trait': '特征', 'transaction': '交易', 'transcript': '成绩单',
    'transformation': '转变', 'transit': '过境', 'transition': '过渡',
    'transmission': '传输', 'transparency': '透明度', 'transportation': '交通',
    'trauma': '创伤', 'treaty': '条约', 'tremendous': '巨大的',
    'tribunal': '法庭', 'tribute': '致敬', 'trigger': '触发',
    'trillion': '万亿', 'trio': '三人组', 'triumph': '胜利',
    'troop': '军队', 'trophy': '奖杯', 'troubled': '困扰的',
    'trustee': '受托人', 'tumour': '肿瘤', 'tunnel': '隧道',
    'twist': '扭曲',
    'unconstitutional': '违宪的', 'undercover': '秘密的', 'underestimate': '低估',
    'undermine': '破坏', 'undertake': '承担', 'unemployment': '失业',
    'unfair': '不公平的', 'unfold': '展开', 'unified': '统一的',
    'unity': '统一', 'unprecedented': '史无前例的', 'uprising': '起义',
    'upside': '上面', 'usage': '用法', 'utility': '效用',
    'utmost': '极度的',
    'vacuum': '真空', 'valid': '有效的', 'validity': '有效性',
    'vanish': '消失', 'variable': '变量', 'variant': '变体',
    'variation': '变化', 'vegetation': '植被', 'vein': '静脉',
    'venture': '冒险', 'verdict': '裁决', 'verse': '诗句',
    'veteran': '老兵', 'viable': '可行的', 'vibrant': '充满活力的',
    'vicious': '恶性的', 'violation': '违反', 'virtual': '虚拟的',
    'virtue': '美德', 'visa': '签证', 'visibility': '能见度',
    'visible': '可见的', 'vocal': '声音的', 'volatile': '不稳定的',
    'voluntary': '自愿的', 'vulnerability': '脆弱性', 'vulnerable': '脆弱的',
    'wage': '工资', 'warfare': '战争', 'warrant': '逮捕令',
    'weaken': '削弱', 'weave': '编织', 'weird': '奇怪的',
    'welfare': '福利', 'whatsoever': '任何', 'wheat': '小麦',
    'whereby': '借此', 'whisper': '低语', 'wholly': '完全',
    'widen': '拓宽', 'widow': '寡妇', 'wilderness': '荒野',
    'wit': '智慧', 'withdrawal': '撤回', 'witness': '目击者',
    'workforce': '劳动力', 'worship': '崇拜', 'worthwhile': '值得的',
    'worthy': '值得的', 'wrist': '手腕', 'yield': '产量',
    'zone': '区域',
    # Common A1/A2/B1 words that lost translations due to row merging
    'bath': '洗澡', 'bathroom': '浴室', 'cut': '切割', 'dad': '爸爸',
    'from': '从', 'front': '前面', 'ice': '冰', 'lunch': '午餐',
    'machine': '机器', 'sandwich': '三明治', 'Saturday': '星期六',
    'start': '开始', 'statement': '声明', 'anybody': '任何人',
    'bright': '明亮的', 'brilliant': '出色的', 'easily': '容易地',
    'education': '教育', 'flu': '流感', 'image': '图像',
    'immediately': '立即', 'onto': '到...上', 'opportunity': '机会',
    'program': '程序', 'progress': '进步', 'sadly': '悲伤地',
    'safe': '安全的', 'towards': '朝向', 'towel': '毛巾',
    'absolutely': '绝对地', 'academic': '学术的', 'bite': '咬',
    'due': '由于', 'fitness': '健身', 'fixed': '固定的',
    'imaginary': '想象的', 'immediate': '立即的', 'percentage': '百分比',
    'perfectly': '完美地', 'qualify': '有资格', 'queue': '队列',
    'seed': '种子', 'sensible': '明智的', 'value': '价值',
    'various': '各种的', 'spice': '香料', 'spill': '溢出',
    'therapy': '治疗', 'better': '更好的', 'leave': '离开',
    'level': '水平', 'litre': '升', 'litter': '垃圾',
    'term': '术语', 'shade': '阴影', 'shadow': '影子',
    'activation': '激活', 'activist': '活动家',
    'chart': '图表', 'chief': '首领', 'concede': '承认',
    'conceive': '构想', 'consequently': '因此', 'conservation': '保护',
    'distant': '遥远的', 'distinct': '独特的', 'harmful': '有害的',
    'hearing': '听证会', 'hilarious': '搞笑的', 'hip': '臀部',
    'outstanding': '杰出的', 'overcome': '克服', 'pursue': '追求',
    'range': '范围', 'persist': '坚持', 'personnel': '人员',
    'petition': '请愿', 'capitalist': '资本家', 'cargo': '货物',
    'craft': '工艺', 'crawl': '爬行', 'endeavour': '努力',
    'endless': '无尽的', 'fleet': '舰队', 'flesh': '肉',
    'hopeful': '有希望的', 'horizon': '地平线', 'machinery': '机器',
    'magical': '神奇的', 'sin': '罪', 'situated': '坐落于',
    'trophy': '奖杯', 'troubled': '困扰的', 'vein': '静脉',
    'venture': '冒险', 'weaken': '削弱', 'weave': '编织',
    # C1 words missing translations (second batch)
    'philosophical': '哲学的', 'pirate': '海盗', 'post-war': '战后的',
    'preach': '说教', 'pregnancy': '怀孕', 'preliminary': '初步的',
    'premier': '总理', 'prescribe': '开处方', 'prescription': '处方',
    'presently': '目前', 'preservation': '保存', 'preside': '主持',
    'prestigious': '有声望的', 'prevail': '盛行', 'privatization': '私有化',
    'problematic': '有问题的', 'proceedings': '诉讼程序', 'processing': '处理',
    'processor': '处理器', 'productive': '有成效的', 'profitable': '有利可图的',
    'rifle': '步枪', 'rotate': '旋转', 'sack': '解雇',
    'scattered': '分散的', 'sceptical': '怀疑的', 'screw': '螺丝',
    'scrutiny': '审查', 'seemingly': '看似', 'seldom': '很少',
    'selective': '选择性的', 'senator': '参议员', 'sensitivity': '敏感性',
    'set-up': '设置', 'shareholder': '股东', 'shrug': '耸肩',
    'simulate': '模拟', 'simulation': '模拟', 'toss': '投掷',
    'trailer': '拖车', 'transparent': '透明的', 'tribal': '部落的',
    'tuition': '学费', 'turnout': '出席人数', 'turnover': '营业额',
    'undergraduate': '本科生', 'underlying': '根本的', 'undoubtedly': '毫无疑问',
    'unify': '统一', 'unveil': '揭开', 'uphold': '维护',
    'uranium': '铀', 'urgent': '紧急的', 'utilize': '利用',
    'vacancy': '空缺', 'vague': '模糊的', 'vow': '发誓',
    'waist': '腰', 'warehouse': '仓库', 'warrior': '战士',
    'weed': '杂草', 'wheelchair': '轮椅', 'whilst': '当...时',
    'widespread': '广泛的', 'wing': '翅膀', 'wire': '电线',
    'witch': '女巫', 'wrap': '包裹', 'youngster': '年轻人',
    # C1 words missing translations (final batch)
    'upcoming': '即将到来的', 'upgrade': '升级', 'utterly': '完全地',
    'varied': '各种各样的', 'verbal': '口头的', 'verify': '验证',
    'versus': '对', 'vessel': '船只', 'vice': '副',
    'villager': '村民', 'violate': '违反', 'ward': '病房',
    'well-being': '幸福', 'whip': '鞭子', 'width': '宽度',
    'willingness': '意愿', 'wipe': '擦', 'workout': '锻炼',
    'yell': '叫喊',
    # Additional common words
    'FALSE': None,  # skip
    'TRUE': None,  # skip
    'a': '一个', 'the': '这个', 'an': '一个', 'and': '和',
    'I': '我', 'we': '我们', 'you': '你', 'he': '他',
    'she': '她', 'it': '它', 'they': '他们', 'this': '这个',
    'that': '那个', 'what': '什么', 'which': '哪个', 'who': '谁',
    'whose': '谁的', 'will': '将', 'would': '会', 'could': '能',
    'should': '应该', 'must': '必须', 'may': '可以', 'might': '可能',
    'shall': '将', 'can': '能', 'cannot': '不能', 'need': '需要',
    'ought': '应当', 'have': '有', 'used': '习惯于',
    'each': '每个', 'both': '两个', 'few': '少数', 'many': '许多',
    'more': '更多', 'most': '最多', 'much': '很多', 'another': '另一个',
    'any': '任何', 'some': '一些', 'all': '全部', 'other': '其他',
    'own': '自己的', 'out': '外面', 'several': '几个', 'such': '这样的',
    'neither': '两者都不', 'either': '两者之一', 'whatever': '无论什么',
    'hello': '你好', 'goodbye': '再见', 'least': '最少', 'less': '更少',
    'till': '直到', 'until': '直到', 'throughout': '贯穿', 'nor': '也不',
    'first': '第一', 'second': '第二', 'third': '第三', 'fourth': '第四',
    'fifth': '第五', 'one': '一', 'two': '二', 'three': '三',
    'four': '四', 'five': '五', 'six': '六', 'seven': '七',
    'eight': '八', 'nine': '九', 'ten': '十', 'eleven': '十一',
    'twelve': '十二', 'thirteen': '十三', 'fourteen': '十四', 'fifteen': '十五',
    'sixteen': '十六', 'seventeen': '十七', 'eighteen': '十八', 'nineteen': '十九',
    'twenty': '二十', 'thirty': '三十', 'forty': '四十', 'fifty': '五十',
    'sixty': '六十', 'seventy': '七十', 'eighty': '八十', 'ninety': '九十',
    'hundred': '百', 'thousand': '千', 'million': '百万', 'billion': '十亿',
    'trillion': '万亿', 'zero': '零',
    'all right': '好的', 'alone': '独自', 'full-time': '全职', 'part-time': '兼职',
}


def normalize_text(text):
    """Fix non-ASCII characters"""
    text = text.replace('\u00a0', ' ')  # Non-breaking space -> regular space
    text = text.replace('\u2019', "'")  # Right single quotation mark -> apostrophe
    text = text.replace('\u2018', "'")  # Left single quotation mark -> apostrophe
    text = text.replace('\u201c', '"')  # Left double quotation mark
    text = text.replace('\u201d', '"')  # Right double quotation mark
    return text


def split_merged_terms(term, cefr):
    """Split a merged term like 'cut v.dad' into individual words"""
    term = normalize_text(term.strip())

    # Fix known broken words
    if term in BROKEN_WORDS:
        term = BROKEN_WORDS[term]

    # Skip standalone POS abbreviations
    if term in SKIP_TERMS:
        return []

    # Try to detect and split merged entries
    results = []
    remaining = term

    while remaining:
        remaining = remaining.strip()
        if not remaining:
            break

        m = MERGE_PATTERN.match(remaining)
        if m:
            word = m.group(1).strip()
            rest = m.group(2) or ''
            if word and word not in SKIP_TERMS:
                results.append(clean_single_term(word))
            remaining = rest.strip()
        else:
            # No more merges detected, clean the remaining term
            cleaned = clean_single_term(remaining)
            if cleaned:
                results.append(cleaned)
            break

    return [r for r in results if r]


def clean_single_term(term):
    """Clean a single term: remove POS markers, sense numbers, etc."""
    term = term.strip()

    if not term:
        return None

    if term in SKIP_TERMS:
        return None

    # Remove sense disambiguator numbers (e.g. "close 1", "live1", "can2")
    term = re.sub(r'\s*\d+\s*$', '', term)  # "close 1" -> "close"
    term = re.sub(r'(\D)\d+$', r'\1', term)  # "live1" -> "live", "can2" -> "can"

    # Strip trailing POS markers
    for pattern in POS_TAGS:
        term = re.sub(pattern + r'\s*$', '', term).strip()

    # Remove trailing dots that are POS remnants (but keep real abbreviations like "o'clock")
    if term.endswith('.') and not term.endswith("o'clock"):
        # Check if it's a POS abbreviation
        if re.match(r'^(adj|adv|n|v|det|pron|prep|conj|exclam)\.?$', term):
            return None

    term = term.strip()

    # Skip if result is empty or just punctuation
    if not term or not any(c.isalpha() for c in term):
        return None

    # Skip remaining POS fragments (e.g. "/adj.", "adj", "/adv.")
    if re.match(r'^/?(?:adj|adv|n|v|det|pron|prep|conj|exclam)\.?/?\.?$', term):
        return None

    # Skip all-uppercase non-words (FALSE, TRUE, etc.) unless they're acronyms
    if term.isupper() and len(term) > 2:
        return None

    return term


def clean_translation(translation):
    """Remove POS markers and other junk from translation text"""
    if not translation:
        return ''
    t = translation.strip()
    # Remove POS markers from translations
    # e.g. "每个 det./pron./adv." -> "每个"
    # e.g. "好吧，adj./adv." -> "好吧"
    # e.g. "单独 adj./adv." -> "单独"
    # e.g. "谁的det./pron。" -> "谁的"
    # e.g. "much det./代词。" -> "much"  (this is a bad translation, will be overridden)
    t = re.sub(r'\s*(?:adj\.|adv\.|det\.|pron\.|prep\.|conj\.|exclam\.|n\.|v\.)'
               r'(?:/(?:adj\.|adv\.|det\.|pron\.|prep\.|conj\.|exclam\.|n\.|v\.))*\s*$', '', t)
    # Also catch Chinese-punctuated versions (e.g. "谁的det./pron。")
    t = re.sub(r'\s*(?:adj|adv|det|pron|prep|conj|exclam)\.'
               r'(?:/(?:adj|adv|det|pron|prep|conj|exclam)\.?)*[。]?\s*$', '', t)
    # Catch "much det./代词。" pattern (POS marker + Chinese POS)
    t = re.sub(r'\s*(?:adj|adv|det|pron|prep|conj|exclam)\.'
               r'(?:/[^\s]+)*[。.]?\s*$', '', t)
    # Remove sense numbers from translations (e.g. "第二个 1 检测/" -> "第二个")
    t = re.sub(r'\s*\d+\s*(?:检测|det)/?\.?\s*$', '', t)
    t = re.sub(r'[，,]\s*$', '', t)  # Remove trailing comma
    # Remove sense numbers from end of translation (e.g. "关闭 1" -> "关闭", "做1" -> "做")
    t = re.sub(r'\s*\d+\s*$', '', t)
    return t.strip()


def main():
    # 1. Read the original CSV
    print("Reading CSV...")
    raw_rows = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_rows.append(row)
    print(f"  Read {len(raw_rows)} rows")

    # 2. Read audio manifest
    manifest_map = {}
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        manifest_map = {e['word']: e['filename'] for e in manifest}
        print(f"  Loaded manifest: {len(manifest_map)} audio entries")

    # 3. Also build a map of actual audio files on disk
    audio_files = set()
    if os.path.exists(AUDIO_DIR):
        for f in os.listdir(AUDIO_DIR):
            if f.endswith('.wav'):
                # Map word name (without .wav) to filename
                audio_files.add(f)
        print(f"  Found {len(audio_files)} audio files on disk")

    # 4. Process each row: split merged terms, clean, deduplicate
    cleaned = []
    seen_words = set()

    for row in raw_rows:
        term = row['term'].strip()
        cefr = row['cefr'].strip()
        translation = row.get('translation', '').strip()

        # Split merged terms
        words = split_merged_terms(term, cefr)

        for word in words:
            if not word:
                continue

            word_lower = word.lower()

            # Deduplicate
            if word_lower in seen_words:
                continue
            seen_words.add(word_lower)

            # Find translation
            meaning = ''
            if translation and len(words) == 1:
                # Only use the original translation if there was exactly one word in the row
                meaning = clean_translation(normalize_text(translation))

            # If no translation, or translation is the English word itself, look up in our dictionary
            if not meaning or meaning.lower() == word_lower:
                lookup = TRANSLATIONS.get(word, TRANSLATIONS.get(word_lower, ''))
                if lookup is None:  # Explicitly marked for skip
                    continue
                meaning = lookup or meaning or ''

            # Find audio file
            audio = ''
            # Try exact match in manifest
            if word in manifest_map:
                audio = manifest_map[word]
            elif word_lower in manifest_map:
                audio = manifest_map[word_lower]
            # Try finding audio file on disk
            elif f"{word_lower}.wav" in audio_files:
                audio = f"{word_lower}.wav"
            elif f"{word}.wav" in audio_files:
                audio = f"{word}.wav"

            cleaned.append({
                'term': word,
                'cefr': cefr,
                'translation': meaning,
                'audio': audio,
            })

    print(f"\n  Cleaned: {len(cleaned)} unique words (from {len(raw_rows)} raw rows)")

    # 5. Write cleaned CSV
    print(f"\nWriting cleaned CSV to {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['term', 'cefr', 'translation'])
        writer.writeheader()
        for entry in cleaned:
            writer.writerow({
                'term': entry['term'],
                'cefr': entry['cefr'],
                'translation': entry['translation'],
            })

    # 6. Generate JS file
    print(f"Generating {OUTPUT_JS}...")
    levels = ['A1', 'A2', 'B1', 'B2', 'C1']
    vocab = {level: [] for level in levels}

    for entry in cleaned:
        cefr = entry['cefr']
        if cefr not in vocab:
            continue

        js_entry = {
            'word': entry['term'],
            'meaning': entry['translation'],
        }
        if entry['audio']:
            js_entry['audio'] = entry['audio']

        vocab[cefr].append(js_entry)

    total = sum(len(v) for v in vocab.values())
    no_translation = sum(1 for e in cleaned if not e['translation'])
    no_audio = sum(1 for e in cleaned if not e['audio'])

    lines = []
    lines.append('// Oxford 5000 词汇数据 (自动生成)')
    lines.append(f'// 总词数: {total}')
    lines.append('')
    lines.append('const OXFORD_VOCABULARY = {')

    for level in levels:
        words = vocab[level]
        lines.append(f'  "{level}": [')
        for w in words:
            word_esc = w['word'].replace('\\', '\\\\').replace('"', '\\"')
            meaning_esc = w['meaning'].replace('\\', '\\\\').replace('"', '\\"')
            if 'audio' in w:
                audio_esc = w['audio'].replace('\\', '\\\\').replace('"', '\\"')
                lines.append(f'    {{ word: "{word_esc}", meaning: "{meaning_esc}", audio: "{audio_esc}" }},')
            else:
                lines.append(f'    {{ word: "{word_esc}", meaning: "{meaning_esc}" }},')
        lines.append(f'  ],  // {level}: {len(words)} words')
        lines.append('')

    lines.append('};')

    with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    # 7. Report
    print(f"\n{'='*50}")
    print(f"RESULTS")
    print(f"{'='*50}")
    print(f"Total unique words: {total}")
    for level in levels:
        with_audio = sum(1 for w in vocab[level] if 'audio' in w)
        with_meaning = sum(1 for w in vocab[level] if w['meaning'])
        print(f"  {level}: {len(vocab[level]):>5} words  ({with_audio} with audio, {with_meaning} with translation)")
    print(f"\nWords without translation: {no_translation}")
    print(f"Words without audio: {no_audio}")

    if no_translation > 0:
        missing = [e['term'] for e in cleaned if not e['translation']]
        print(f"\nMissing translations ({len(missing)}):")
        for w in missing[:50]:
            print(f"  - {w}")
        if len(missing) > 50:
            print(f"  ... and {len(missing) - 50} more")


if __name__ == '__main__':
    main()
