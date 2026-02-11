#!/usr/bin/env python3
"""
Generate CET-4 and CET-6 vocabulary wordbook JS files.

Architecture:
1. Read oxford_5000_cleaned.csv to reuse translations
2. Check if audio file exists in tts_delivery/audio/{word}.wav
3. Use hardcoded CET-4 and CET-6 word lists
4. For words in Oxford CSV -> reuse translation; otherwise -> use CET_TRANSLATIONS dict
5. Split CET-4 into high-freq (top 40%) and core (remaining 60%)
6. Split CET-6 into high-freq (top 40%) and core (remaining 60%)
7. Output: wordbooks/cet4_vocabulary.js and cet6_vocabulary.js
"""

import csv
import os
import json

# === Paths ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OXFORD_CSV = os.path.join(SCRIPT_DIR, 'oxford_5000_cleaned.csv')
AUDIO_DIR = os.path.join(SCRIPT_DIR, 'tts_delivery', 'audio')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'wordbooks')

# === CET-4 Word List (~800 high-frequency words) ===
CET4_WORDS = [
    'abandon', 'aboard', 'absolute', 'absorb', 'abstract', 'abundant', 'abuse',
    'academic', 'accelerate', 'accent', 'acceptable', 'access', 'accident',
    'accommodation', 'accompany', 'accomplish', 'account', 'accountant', 'accumulate',
    'accurate', 'accuse', 'accustom', 'ache', 'achieve', 'achievement', 'acid',
    'acknowledge', 'acquire', 'adapt', 'addition', 'additional', 'address', 'adequate',
    'adjust', 'administration', 'admire', 'admission', 'admit', 'adolescent', 'adopt',
    'advance', 'advanced', 'advantage', 'adventure', 'advertise', 'advertisement',
    'affect', 'affection', 'afford', 'aggressive', 'agriculture', 'aid', 'alarm',
    'alcohol', 'alert', 'alien', 'allocate', 'allowance', 'alter', 'alternative',
    'ambition', 'ambitious', 'amend', 'amount', 'ample', 'amuse', 'analyse',
    'ancestor', 'anchor', 'annual', 'anticipate', 'anxiety', 'anxious', 'apart',
    'apparent', 'appeal', 'appetite', 'appliance', 'applicable', 'application',
    'appoint', 'appointment', 'appreciate', 'approach', 'appropriate', 'approval',
    'approve', 'approximate', 'arise', 'arouse', 'arrange', 'arrangement', 'arrest',
    'artificial', 'aspect', 'assemble', 'assess', 'assessment', 'asset', 'assign',
    'assist', 'assistance', 'associate', 'association', 'assume', 'assumption',
    'assure', 'astonish', 'atmosphere', 'attach', 'attain', 'attempt', 'attend',
    'attitude', 'attribute', 'audience', 'authority', 'automatic', 'available',
    'avenue', 'avoid', 'awake', 'award', 'aware', 'awareness',
    'bachelor', 'backward', 'bacteria', 'balance', 'ban', 'band', 'bargain',
    'barrier', 'basis', 'battery', 'behalf', 'behave', 'behaviour', 'belief',
    'belong', 'beneath', 'beneficial', 'benefit', 'besides', 'betray', 'beyond',
    'bias', 'bid', 'billion', 'bind', 'blame', 'blank', 'blast', 'bleed', 'blend',
    'bless', 'blind', 'block', 'bloom', 'blow', 'boast', 'bold', 'bond', 'boom',
    'boost', 'border', 'bore', 'bound', 'boundary', 'bow', 'brand', 'brave',
    'breakdown', 'breed', 'brief', 'brilliant', 'broad', 'broadcast', 'brochure',
    'budget', 'burden', 'bureau', 'burst',
    'calculate', 'campaign', 'cancel', 'candidate', 'capable', 'capacity', 'capture',
    'carbon', 'career', 'casual', 'catalogue', 'category', 'cattle', 'caution',
    'celebrate', 'ceremony', 'certificate', 'chain', 'challenge', 'champion',
    'channel', 'chapter', 'characteristic', 'charge', 'charity', 'charm', 'chart',
    'chase', 'cheat', 'cherish', 'chief', 'chip', 'circumstance', 'cite', 'citizen',
    'civil', 'claim', 'clarify', 'classify', 'client', 'climate', 'cling', 'clue',
    'coach', 'code', 'collapse', 'colleague', 'column', 'combat', 'combine',
    'command', 'comment', 'commercial', 'commission', 'commit', 'committee',
    'communicate', 'community', 'companion', 'comparable', 'comparison', 'compel',
    'compensate', 'compete', 'competent', 'complaint', 'complement', 'complex',
    'complicated', 'component', 'compose', 'comprehensive', 'compromise', 'compulsory',
    'concentrate', 'concept', 'concern', 'conclude', 'concrete', 'condemn', 'conduct',
    'conference', 'confess', 'confidence', 'confident', 'confine', 'confirm',
    'conflict', 'confront', 'confuse', 'congress', 'connect', 'conscience',
    'conscious', 'consensus', 'consent', 'consequence', 'conservative', 'consider',
    'considerable', 'consist', 'consistent', 'constant', 'constitute', 'construct',
    'consult', 'consultant', 'consume', 'consumer', 'contact', 'contemporary',
    'content', 'contest', 'context', 'contract', 'contradict', 'contrast',
    'contribute', 'controversial', 'convention', 'conventional', 'conversation',
    'convert', 'convey', 'convince', 'cooperate', 'cope', 'corporate', 'correct',
    'correspond', 'cost', 'council', 'counsel', 'counter', 'course', 'crash',
    'create', 'creative', 'creature', 'credit', 'crime', 'criminal', 'crisis',
    'criterion', 'critical', 'criticism', 'criticize', 'crop', 'crucial', 'crush',
    'cultivate', 'culture', 'cure', 'curiosity', 'curious', 'current', 'curriculum',
    'custom', 'cycle',
    'danger', 'deadline', 'deal', 'debate', 'decade', 'decay', 'decline', 'decorate',
    'decrease', 'dedicate', 'defeat', 'defend', 'deficit', 'define', 'definite',
    'definition', 'delay', 'delegate', 'deliberate', 'delicate', 'deliver', 'demand',
    'democracy', 'demonstrate', 'denial', 'dense', 'deny', 'depart', 'departure',
    'depend', 'deposit', 'depress', 'deprive', 'derive', 'describe', 'deserve',
    'designate', 'desire', 'desperate', 'despite', 'destination', 'destroy',
    'destruction', 'detect', 'determine', 'device', 'devote', 'diagnose', 'diet',
    'differ', 'digital', 'dilemma', 'dimension', 'diminish', 'diplomatic', 'direct',
    'directory', 'disability', 'disaster', 'discipline', 'discount', 'discourage',
    'discover', 'discovery', 'discrimination', 'discuss', 'disease', 'disguise',
    'dismiss', 'disorder', 'display', 'dispose', 'dispute', 'dissolve', 'distant',
    'distinct', 'distinction', 'distinguish', 'distribute', 'district', 'disturb',
    'diverse', 'divide', 'division', 'domestic', 'dominant', 'dominate', 'donate',
    'doom', 'doubt', 'draft', 'drain', 'drama', 'dramatic', 'drift', 'drive',
    'drought', 'due', 'dull', 'dump', 'durable', 'duration', 'duty', 'dynamic',
    'earn', 'economy', 'edition', 'editor', 'efficient', 'elaborate', 'elderly',
    'elect', 'election', 'electronic', 'element', 'eliminate', 'embrace', 'emerge',
    'emergency', 'emission', 'emotion', 'emphasis', 'emphasize', 'employ', 'employee',
    'employer', 'enable', 'encounter', 'encourage', 'endure', 'energy', 'enforce',
    'engage', 'engine', 'enhance', 'enormous', 'enquiry', 'ensure', 'enterprise',
    'enthusiasm', 'entire', 'entitle', 'entity', 'environment', 'episode', 'equal',
    'equipment', 'equivalent', 'era', 'error', 'escape', 'especially', 'essential',
    'establish', 'estate', 'estimate', 'evaluate', 'eventually', 'evidence', 'evil',
    'evolution', 'evolve', 'exaggerate', 'examine', 'exceed', 'excellent', 'except',
    'exception', 'excess', 'exchange', 'excite', 'exclude', 'exclusive', 'execute',
    'exercise', 'exhaust', 'exhibit', 'exhibition', 'exist', 'existence', 'expand',
    'expansion', 'expect', 'expense', 'experiment', 'expert', 'exploit', 'explore',
    'explosion', 'export', 'expose', 'exposure', 'extend', 'extension', 'extensive',
    'extent', 'external', 'extra', 'extraordinary', 'extreme',
]

# === CET-6 Word List (~600 additional words NOT in CET-4) ===
CET6_WORDS = [
    'abolish', 'abrupt', 'absurd', 'accessible', 'acclaim', 'accountable',
    'acknowledge', 'acute', 'adequate', 'adhere', 'adjacent', 'adolescence',
    'advent', 'adverse', 'advocate', 'aesthetic', 'affiliate', 'afflict',
    'aggregate', 'agitate', 'agonize', 'allegation', 'allege', 'alleviate',
    'alliance', 'allot', 'ally', 'ambiguous', 'ample', 'analogy', 'anonymous',
    'apparatus', 'applaud', 'apprentice', 'arbitrary', 'arrogant', 'aspiration',
    'assault', 'assert', 'assimilate', 'asylum', 'atrocity', 'audit',
    'authentic', 'authorize', 'autonomy', 'aversion', 'avid',
    'backlash', 'baffle', 'bankrupt', 'barren', 'batter', 'bewilder',
    'blaze', 'bleak', 'blight', 'bliss', 'blunder', 'blur', 'bolster',
    'bombard', 'boycott', 'breach', 'brink', 'brittle', 'brutal', 'bulletin',
    'bureaucracy', 'burnout',
    'calibrate', 'camouflage', 'canopy', 'capsule', 'captive', 'cascade',
    'catalyst', 'cater', 'caution', 'ceasefire', 'census', 'centralize',
    'chronic', 'chunk', 'circulate', 'civic', 'clamp', 'clause', 'cleanse',
    'clergy', 'clinical', 'coalition', 'coerce', 'cognitive', 'coherent',
    'coincide', 'collaborate', 'commodity', 'communal', 'compact', 'compassion',
    'compile', 'complacent', 'complexion', 'comply', 'conceive', 'condemn',
    'confiscate', 'congregation', 'conscientious', 'consecutive', 'consolidate',
    'conspicuous', 'conspiracy', 'constrain', 'contaminate', 'contemplate',
    'contempt', 'contend', 'contingent', 'contradict', 'controversy',
    'converse', 'conviction', 'coordinate', 'cordial', 'corrode', 'corrupt',
    'cosmic', 'counsel', 'counterfeit', 'courtesy', 'covert', 'crack',
    'creed', 'cripple', 'criteria', 'crude', 'cuisine', 'culminate',
    'cumulative', 'curb', 'custody',
    'dazzle', 'debris', 'deceased', 'deceive', 'decree', 'deem', 'default',
    'defect', 'defer', 'deficiency', 'defy', 'degenerate', 'degradation',
    'delegate', 'deliberate', 'demographic', 'demolish', 'denounce', 'depict',
    'deploy', 'depreciate', 'deprive', 'deputy', 'derived', 'designate',
    'deteriorate', 'detrimental', 'devastate', 'deviate', 'devise', 'diagnose',
    'diffuse', 'diligent', 'dilute', 'diminish', 'dire', 'discard', 'discern',
    'disclose', 'discourse', 'discreet', 'discrepancy', 'discretion', 'dispatch',
    'disperse', 'displace', 'disposition', 'disproportionate', 'disrupt',
    'dissent', 'dissolve', 'distort', 'distract', 'diverse', 'divert',
    'doctrine', 'domain', 'donate', 'doom', 'dose', 'downfall', 'drastic',
    'dread', 'dubious', 'dwarf', 'dwell', 'dynamic',
    'eccentric', 'eclipse', 'edifice', 'elapse', 'elaborate', 'eligible',
    'elite', 'eloquent', 'embed', 'embody', 'eminent', 'empirical', 'empower',
    'encompass', 'endorse', 'enlighten', 'enrich', 'ensue', 'entail',
    'envision', 'epidemic', 'equate', 'equity', 'erode', 'erratic', 'essence',
    'eternal', 'ethic', 'evacuate', 'evade', 'evoke', 'exacerbate', 'excerpt',
    'exile', 'exotic', 'expedite', 'explicit', 'extinguish', 'extract',
    'extravagant',
    'fabricate', 'facet', 'facilitate', 'faction', 'fallacy', 'famine',
    'fatigue', 'feasible', 'feat', 'feeble', 'ferocious', 'fertile',
    'fidelity', 'fiscal', 'flaw', 'flee', 'flicker', 'flock', 'flourish',
    'fluctuate', 'foe', 'folklore', 'formidable', 'foster', 'fragment',
    'franchise', 'fraud', 'frenzy', 'friction', 'fringe', 'fruitful',
    'fulfill', 'furnish', 'fury', 'futile',
    'gauge', 'gazette', 'genocide', 'genuine', 'germ', 'gigantic', 'glacier',
    'glamour', 'glare', 'glitter', 'gloom', 'gorgeous', 'grace', 'graft',
    'grasp', 'gratitude', 'graze', 'grieve', 'grim', 'groan', 'gross',
    'grotesque', 'grudge', 'gulf',
    'habitat', 'halt', 'hamper', 'harass', 'harmony', 'harsh', 'haste',
    'haunt', 'hazard', 'heed', 'heighten', 'heritage', 'hierarchy', 'hinder',
    'hoist', 'homogeneous', 'horizon', 'hostile', 'hover', 'huddle', 'humble',
    'hybrid', 'hygiene', 'hysterical',
    'identical', 'illuminate', 'illusion', 'immense', 'immerse', 'immune',
    'impair', 'impartial', 'imperative', 'imperial', 'impetus', 'implement',
    'implicate', 'implicit', 'impose', 'impulse', 'inaugurate', 'incidence',
    'incline', 'incorporate', 'increment', 'incur', 'indigenous', 'indignant',
    'indispensable', 'induce', 'infer', 'inferior', 'inflate', 'inflict',
    'ingenious', 'inherent', 'inhibit', 'initiate', 'inject', 'innovative',
    'inquiry', 'inscribe', 'instigate', 'institute', 'intact', 'integral',
    'integrate', 'integrity', 'intellect', 'intercept', 'interim', 'intricate',
    'intrinsic', 'intuition', 'invade', 'invoke', 'ironic', 'irrigation',
    'isolate', 'ivory',
]

# === CET Translations for words NOT in Oxford 5000 ===
CET_TRANSLATIONS = {
    'abolish': '\u5e9f\u9664', 'abrupt': '\u7a81\u7136\u7684', 'absurd': '\u8352\u8c2c\u7684', 'accessible': '\u53ef\u8fdb\u5165\u7684',
    'acclaim': '\u6b22\u547c', 'accountable': '\u8d1f\u6709\u8d23\u4efb\u7684', 'accumulate': '\u79ef\u7d2f', 'accustom': '\u4f7f\u4e60\u60ef',
    'acute': '\u6025\u6027\u7684', 'adhere': '\u575a\u6301', 'adjacent': '\u90bb\u8fd1\u7684', 'adolescence': '\u9752\u6625\u671f',
    'adolescent': '\u9752\u5c11\u5e74', 'advent': '\u5230\u6765', 'adverse': '\u4e0d\u5229\u7684', 'advocate': '\u63d0\u5021',
    'aesthetic': '\u7f8e\u5b66\u7684', 'affiliate': '\u9644\u5c5e', 'afflict': '\u6298\u78e8', 'aggregate': '\u603b\u8ba1',
    'agitate': '\u6405\u52a8', 'agonize': '\u82e6\u607c', 'allegation': '\u6307\u63a7', 'allege': '\u58f0\u79f0',
    'alleviate': '\u7f13\u89e3', 'alliance': '\u8054\u76df', 'allot': '\u5206\u914d', 'ally': '\u76df\u53cb',
    'ambiguous': '\u6a21\u7cca\u7684', 'analogy': '\u7c7b\u6bd4', 'anonymous': '\u533f\u540d\u7684', 'apparatus': '\u8bbe\u5907',
    'applaud': '\u9f13\u638c', 'apprentice': '\u5b66\u5f92', 'arbitrary': '\u4efb\u610f\u7684', 'arrogant': '\u50b2\u6162\u7684',
    'aspiration': '\u62b1\u8d1f', 'assault': '\u653b\u51fb', 'assert': '\u65ad\u8a00', 'assimilate': '\u5438\u6536',
    'asylum': '\u907f\u96be\u6240', 'atrocity': '\u66b4\u884c', 'audit': '\u5ba1\u8ba1', 'authentic': '\u771f\u5b9e\u7684',
    'authorize': '\u6388\u6743', 'autonomy': '\u81ea\u6cbb', 'aversion': '\u538c\u6076', 'avid': '\u6e34\u671b\u7684',
    'backlash': '\u53cd\u5f39', 'baffle': '\u56f0\u60d1', 'bankrupt': '\u7834\u4ea7', 'barren': '\u8d2b\u7620\u7684',
    'batter': '\u51fb\u6253', 'bewilder': '\u8ff7\u60d1', 'blaze': '\u706b\u7130', 'bleak': '\u8352\u51c9\u7684',
    'blight': '\u67af\u840e', 'bliss': '\u5e78\u798f', 'blunder': '\u5931\u8bef', 'blur': '\u6a21\u7cca',
    'bolster': '\u652f\u6491', 'bombard': '\u8f70\u70b8', 'boycott': '\u62b5\u5236', 'breach': '\u8fdd\u53cd',
    'brink': '\u8fb9\u7f18', 'brittle': '\u8106\u5f31\u7684', 'brutal': '\u6b8b\u5fcd\u7684', 'bulletin': '\u516c\u62a5',
    'bureaucracy': '\u5b98\u50da\u4e3b\u4e49', 'burnout': '\u5026\u6020',
    'calibrate': '\u6821\u51c6', 'camouflage': '\u4f2a\u88c5', 'canopy': '\u5929\u7bf7', 'capsule': '\u80f6\u56ca',
    'captive': '\u4fc6\u864f', 'cascade': '\u7011\u5e03', 'catalyst': '\u50ac\u5316\u5242', 'cater': '\u8fce\u5408',
    'ceasefire': '\u505c\u706b', 'census': '\u4eba\u53e3\u666e\u67e5', 'centralize': '\u96c6\u4e2d', 'chronic': '\u6162\u6027\u7684',
    'chunk': '\u5927\u5757', 'circulate': '\u6d41\u901a', 'civic': '\u516c\u6c11\u7684', 'clamp': '\u5939\u7d27',
    'clause': '\u6761\u6b3e', 'cleanse': '\u6e05\u6d17', 'clergy': '\u795e\u804c\u4eba\u5458', 'clinical': '\u4e34\u5e8a\u7684',
    'coalition': '\u8054\u76df', 'coerce': '\u5f3a\u8feb', 'cognitive': '\u8ba4\u77e5\u7684', 'coherent': '\u8fde\u8d2f\u7684',
    'coincide': '\u5de7\u5408', 'collaborate': '\u5408\u4f5c', 'commodity': '\u5546\u54c1', 'communal': '\u516c\u5171\u7684',
    'compact': '\u7d27\u51d1\u7684', 'compassion': '\u540c\u60c5', 'compile': '\u7f16\u8f91', 'complacent': '\u81ea\u6ee1\u7684',
    'complexion': '\u80a4\u8272', 'comply': '\u9075\u5b88', 'confiscate': '\u6ca1\u6536', 'congregation': '\u96c6\u4f1a',
    'conscientious': '\u8ba4\u771f\u7684', 'consecutive': '\u8fde\u7eed\u7684', 'consolidate': '\u5de9\u56fa',
    'conspicuous': '\u663e\u773c\u7684', 'conspiracy': '\u9634\u8c0b', 'constrain': '\u7ea6\u675f',
    'contaminate': '\u6c61\u67d3', 'contemplate': '\u6c89\u601d', 'contempt': '\u8511\u89c6', 'contend': '\u7ade\u4e89',
    'contingent': '\u4f9d\u60c5\u51b5\u800c\u5b9a\u7684', 'controversy': '\u4e89\u8bae', 'converse': '\u4ea4\u8c08',
    'conviction': '\u5b9a\u7f6a', 'coordinate': '\u534f\u8c03', 'cordial': '\u70ed\u60c5\u7684', 'corrode': '\u8150\u8680',
    'corrupt': '\u8150\u8d25\u7684', 'cosmic': '\u5b87\u5b99\u7684', 'counterfeit': '\u4f2a\u9020\u7684', 'courtesy': '\u793c\u8c8c',
    'covert': '\u79d8\u5bc6\u7684', 'creed': '\u4fe1\u6761', 'cripple': '\u6b8b\u75be', 'crude': '\u7c97\u7cd9\u7684',
    'cuisine': '\u70f9\u996a', 'culminate': '\u8fbe\u5230\u9ad8\u6f6e', 'cumulative': '\u7d2f\u79ef\u7684', 'curb': '\u6291\u5236',
    'custody': '\u62d8\u7559',
    'dazzle': '\u4f7f\u76ee\u7729', 'debris': '\u788e\u7247', 'deceased': '\u5df2\u6545\u7684', 'deceive': '\u6b3a\u9a97',
    'decree': '\u6cd5\u4ee4', 'deem': '\u8ba4\u4e3a', 'default': '\u9ed8\u8ba4', 'defect': '\u7f3a\u9677',
    'defer': '\u63a8\u8fdf', 'deficiency': '\u7f3a\u4e4f', 'defy': '\u8fdd\u6297', 'degenerate': '\u9000\u5316',
    'degradation': '\u9000\u5316', 'demographic': '\u4eba\u53e3\u7edf\u8ba1\u7684', 'demolish': '\u62c6\u9664',
    'denounce': '\u8c34\u8d23', 'depict': '\u63cf\u7ed8', 'deploy': '\u90e8\u7f72', 'depreciate': '\u8d2c\u503c',
    'designate': '\u6307\u5b9a', 'deteriorate': '\u6076\u5316', 'detrimental': '\u6709\u5bb3\u7684',
    'devastate': '\u6bc1\u706d', 'deviate': '\u504f\u79bb', 'devise': '\u8bbe\u8ba1', 'diffuse': '\u6269\u6563',
    'diligent': '\u52e4\u594b\u7684', 'dilute': '\u7a00\u91ca', 'dire': '\u53ef\u6015\u7684', 'discard': '\u4e22\u5f03',
    'discern': '\u8fa8\u522b', 'disclose': '\u63ed\u9732', 'discourse': '\u8bba\u8ff0', 'discreet': '\u8c28\u614e\u7684',
    'discrepancy': '\u5dee\u5f02', 'discretion': '\u614e\u91cd', 'dispatch': '\u6d3e\u9063', 'disperse': '\u5206\u6563',
    'displace': '\u53d6\u4ee3', 'disposition': '\u6027\u60c5', 'disproportionate': '\u4e0d\u6210\u6bd4\u4f8b\u7684',
    'disrupt': '\u6270\u4e71', 'dissent': '\u5f02\u8bae', 'distort': '\u6b6a\u66f2', 'distract': '\u5206\u6563\u6ce8\u610f',
    'divert': '\u8f6c\u79fb', 'doctrine': '\u5b66\u8bf4', 'domain': '\u9886\u57df', 'downfall': '\u57ae\u53f0',
    'drastic': '\u6fc0\u70c8\u7684', 'dread': '\u6050\u60e7', 'dubious': '\u53ef\u7591\u7684', 'dwarf': '\u77ee\u5316',
    'dwell': '\u5c45\u4f4f',
    'eccentric': '\u53e4\u602a\u7684', 'eclipse': '\u65e5\u8680', 'edifice': '\u5927\u53a6', 'elapse': '\u6d88\u901d',
    'eligible': '\u5408\u683c\u7684', 'elite': '\u7cbe\u82f1', 'eloquent': '\u96c4\u8fa9\u7684', 'embed': '\u5d4c\u5165',
    'embody': '\u4f53\u73b0', 'eminent': '\u6770\u51fa\u7684', 'empirical': '\u7ecf\u9a8c\u7684', 'empower': '\u6388\u6743',
    'encompass': '\u5305\u56f4', 'endorse': '\u8d5e\u540c', 'enlighten': '\u542f\u53d1', 'enrich': '\u5145\u5b9e',
    'ensue': '\u968f\u540e\u53d1\u751f', 'entail': '\u7275\u6d89', 'envision': '\u5c55\u671b', 'epidemic': '\u6d41\u884c\u75c5',
    'equate': '\u7b49\u540c', 'equity': '\u516c\u5e73', 'erode': '\u4fb5\u8680', 'erratic': '\u4e0d\u7a33\u5b9a\u7684',
    'essence': '\u672c\u8d28', 'eternal': '\u6c38\u6052\u7684', 'ethic': '\u9053\u5fb7', 'evacuate': '\u7591\u6563',
    'evade': '\u9003\u907f', 'evoke': '\u5524\u8d77', 'exacerbate': '\u52a0\u5267', 'excerpt': '\u6458\u5f55',
    'exile': '\u6d41\u653e', 'exotic': '\u5f02\u56fd\u7684', 'expedite': '\u52a0\u901f', 'explicit': '\u660e\u786e\u7684',
    'extinguish': '\u7184\u706d', 'extract': '\u63d0\u53d6', 'extravagant': '\u5962\u4f88\u7684',
    'fabricate': '\u7f16\u9020', 'facet': '\u65b9\u9762', 'facilitate': '\u4fc3\u8fdb', 'faction': '\u6d3e\u7cfb',
    'fallacy': '\u8c2c\u8bba', 'famine': '\u9965\u8352', 'fatigue': '\u75b2\u52b3', 'feasible': '\u53ef\u884c\u7684',
    'feat': '\u529f\u7ee9', 'feeble': '\u865a\u5f31\u7684', 'ferocious': '\u51f6\u731b\u7684', 'fertile': '\u80a5\u6c83\u7684',
    'fidelity': '\u5fe0\u8bda', 'fiscal': '\u8d22\u653f\u7684', 'flaw': '\u7f3a\u9677', 'flee': '\u9003\u8dd1',
    'flicker': '\u95ea\u70c1', 'flock': '\u7fa4', 'flourish': '\u7e41\u8363', 'fluctuate': '\u6ce2\u52a8',
    'foe': '\u654c\u4eba', 'folklore': '\u6c11\u95f4\u4f20\u8bf4', 'formidable': '\u5f3a\u5927\u7684', 'foster': '\u57f9\u517b',
    'fragment': '\u788e\u7247', 'franchise': '\u7279\u8bb8\u7ecf\u8425', 'fraud': '\u6b3a\u8bc8', 'frenzy': '\u72c2\u70ed',
    'friction': '\u6469\u64e6', 'fringe': '\u8fb9\u7f18', 'fruitful': '\u6709\u6210\u679c\u7684', 'fulfill': '\u5b9e\u73b0',
    'furnish': '\u88c5\u5907', 'fury': '\u72c2\u6012', 'futile': '\u5f92\u52b3\u7684',
    'gauge': '\u6d4b\u91cf', 'gazette': '\u516c\u62a5', 'genocide': '\u79cd\u65cf\u706d\u7edd', 'genuine': '\u771f\u6b63\u7684',
    'germ': '\u7ec6\u83cc', 'gigantic': '\u5de8\u5927\u7684', 'glacier': '\u51b0\u5ddd', 'glamour': '\u9b45\u529b',
    'glare': '\u6012\u89c6', 'glitter': '\u95ea\u5149', 'gloom': '\u5fe7\u90c1', 'gorgeous': '\u534e\u4e3d\u7684',
    'grace': '\u4f18\u96c5', 'graft': '\u5ac1\u63a5', 'grasp': '\u6293\u4f4f', 'gratitude': '\u611f\u6fc0',
    'graze': '\u653e\u7267', 'grieve': '\u60b2\u4f24', 'grim': '\u4e25\u5cfb\u7684', 'groan': '\u5455\u541f',
    'gross': '\u603b\u7684', 'grotesque': '\u602a\u8bde\u7684', 'grudge': '\u6028\u6068', 'gulf': '\u6d77\u6e7e',
    'habitat': '\u6816\u606f\u5730', 'halt': '\u505c\u6b62', 'hamper': '\u963b\u7880', 'harass': '\u9a9a\u6270',
    'harmony': '\u548c\u8c10', 'harsh': '\u4e25\u5389\u7684', 'haste': '\u6025\u5fd9', 'haunt': '\u56f0\u6270',
    'hazard': '\u5371\u9669', 'heed': '\u6ce8\u610f', 'heighten': '\u63d0\u9ad8', 'heritage': '\u9057\u4ea7',
    'hierarchy': '\u7b49\u7ea7\u5236\u5ea6', 'hinder': '\u963b\u7880', 'hoist': '\u4e3e\u8d77',
    'homogeneous': '\u540c\u8d28\u7684', 'hostile': '\u654c\u5bf9\u7684', 'hover': '\u76d8\u65cb', 'huddle': '\u6324\u5728\u4e00\u8d77',
    'humble': '\u8c26\u865a\u7684', 'hybrid': '\u6df7\u5408\u7684', 'hygiene': '\u536b\u751f', 'hysterical': '\u6b47\u65af\u5e95\u91cc\u7684',
    'identical': '\u76f8\u540c\u7684', 'illuminate': '\u7167\u4eae', 'illusion': '\u5e7b\u89c9', 'immense': '\u5de8\u5927\u7684',
    'immerse': '\u6c89\u6d78', 'impair': '\u635f\u5bb3', 'impartial': '\u516c\u6b63\u7684', 'imperative': '\u5fc5\u8981\u7684',
    'imperial': '\u5e1d\u56fd\u7684', 'impetus': '\u52a8\u529b', 'implement': '\u5b9e\u65bd', 'implicate': '\u7275\u6d89',
    'implicit': '\u542b\u84c4\u7684', 'impulse': '\u51b2\u52a8', 'inaugurate': '\u5c31\u804c', 'incidence': '\u53d1\u751f\u7387',
    'incline': '\u503e\u5411', 'incorporate': '\u5408\u5e76', 'increment': '\u589e\u52a0', 'incur': '\u62db\u81f4',
    'indigenous': '\u571f\u8457\u7684', 'indignant': '\u6124\u6012\u7684', 'indispensable': '\u4e0d\u53ef\u7f3a\u5c11\u7684',
    'induce': '\u5f15\u8d77', 'infer': '\u63a8\u65ad', 'inferior': '\u4f4e\u7b49\u7684', 'inflate': '\u81a8\u80c0',
    'inflict': '\u65bd\u52a0', 'ingenious': '\u5de7\u5999\u7684', 'inherent': '\u56fa\u6709\u7684', 'inhibit': '\u6291\u5236',
    'initiate': '\u53d1\u8d77', 'innovative': '\u521b\u65b0\u7684', 'inquiry': '\u8be2\u95ee', 'inscribe': '\u94ed\u523b',
    'instigate': '\u5506\u4f7f', 'intact': '\u5b8c\u6574\u7684', 'integral': '\u4e0d\u53ef\u6216\u7f3a\u7684',
    'integrate': '\u6574\u5408', 'integrity': '\u6b63\u76f4', 'intellect': '\u667a\u529b', 'intercept': '\u62e6\u622a',
    'interim': '\u4e34\u65f6\u7684', 'intricate': '\u590d\u6742\u7684', 'intrinsic': '\u5185\u5728\u7684',
    'intuition': '\u76f4\u89c9', 'invoke': '\u8c03\u7528', 'ironic': '\u8bbd\u523a\u7684', 'irrigation': '\u704c\u6ea2',
    'isolate': '\u9694\u79bb', 'ivory': '\u8c61\u7259',
    # CET-4 extras
    'aboard': '\u5728\u8239\u4e0a', 'absorb': '\u5438\u6536', 'abundant': '\u4e30\u5bcc\u7684', 'abuse': '\u6ee5\u7528',
    'acid': '\u9178', 'allocate': '\u5206\u914d', 'allowance': '\u6d25\u8d34', 'alter': '\u6539\u53d8',
    'amend': '\u4fee\u6539', 'ample': '\u5145\u8db3\u7684', 'anchor': '\u951a', 'anticipate': '\u9884\u671f',
    'appliance': '\u5668\u5177', 'applicable': '\u9002\u7528\u7684', 'approximate': '\u8fd1\u4f3c\u7684',
    'arouse': '\u5524\u8d77', 'assemble': '\u96c6\u5408', 'asset': '\u8d44\u4ea7', 'assign': '\u5206\u914d',
    'assumption': '\u5047\u8bbe', 'astonish': '\u4f7f\u60ca\u8bb6', 'attain': '\u8fbe\u5230',
    'bacteria': '\u7ec6\u83cc', 'ban': '\u7981\u6b62', 'barrier': '\u969c\u788d', 'behalf': '\u4ee3\u8868',
    'betray': '\u80cc\u53db', 'bid': '\u51fa\u4ef7', 'bind': '\u7ed1\u5b9a', 'blast': '\u7206\u70b8',
    'bleed': '\u6d41\u8840', 'blend': '\u6df7\u5408', 'bless': '\u795d\u798f', 'bloom': '\u5f00\u82b1',
    'boast': '\u5439\u5618', 'bold': '\u5927\u80c6\u7684', 'boom': '\u7e41\u8363', 'boost': '\u4fc3\u8fdb',
    'bound': '\u5fc5\u5b9a\u7684', 'breed': '\u7e41\u6b96', 'brochure': '\u624b\u518c', 'bureau': '\u5c40',
    'burst': '\u7206\u53d1', 'campaign': '\u8fd0\u52a8', 'carbon': '\u78b3', 'casual': '\u968f\u610f\u7684',
    'catalogue': '\u76ee\u5f55', 'caution': '\u8c28\u614e', 'charm': '\u9b45\u529b', 'chase': '\u8ffd\u9010',
    'cheat': '\u6b3a\u9a97', 'cherish': '\u73cd\u60dc', 'chip': '\u82af\u7247', 'cite': '\u5f15\u7528',
    'civil': '\u516c\u6c11\u7684', 'clarify': '\u6f84\u6e05', 'classify': '\u5206\u7c7b', 'cling': '\u7d27\u8d34',
    'clue': '\u7ebf\u7d22', 'code': '\u4ee3\u7801', 'collapse': '\u5012\u5851', 'column': '\u5217',
    'combat': '\u6218\u6597', 'command': '\u547d\u4ee4', 'commission': '\u59d4\u5458\u4f1a', 'commit': '\u72af\u7f6a',
    'comparable': '\u53ef\u6bd4\u7684', 'compel': '\u5f3a\u8feb', 'compensate': '\u8865\u507f',
    'competent': '\u6709\u80fd\u529b\u7684', 'complement': '\u8865\u5145', 'complicated': '\u590d\u6742\u7684',
    'component': '\u7ec4\u4ef6', 'compose': '\u7ec4\u6210', 'comprehensive': '\u5168\u9762\u7684',
    'compromise': '\u59a5\u534f', 'compulsory': '\u5f3a\u5236\u7684', 'concrete': '\u6df7\u51dd\u571f',
    'condemn': '\u8c34\u8d23', 'confess': '\u627f\u8ba4', 'confine': '\u9650\u5236', 'confront': '\u9762\u5bf9',
    'congress': '\u56fd\u4f1a', 'conscience': '\u826f\u5fc3', 'consensus': '\u5171\u8bc6',
    'consent': '\u540c\u610f', 'conservative': '\u4fdd\u5b88\u7684', 'considerable': '\u76f8\u5f53\u5927\u7684',
    'consist': '\u7ec4\u6210', 'consistent': '\u4e00\u81f4\u7684', 'constant': '\u6301\u7eed\u7684',
    'constitute': '\u6784\u6210', 'construct': '\u5efa\u9020', 'consult': '\u54a8\u8be2',
    'consume': '\u6d88\u8d39', 'contemporary': '\u5f53\u4ee3\u7684', 'contest': '\u6bd4\u8d5b',
    'context': '\u80cc\u666f', 'contradict': '\u77db\u76fe', 'controversial': '\u6709\u4e89\u8bae\u7684',
    'convention': '\u60ef\u4f8b', 'conventional': '\u4f20\u7edf\u7684', 'convert': '\u8f6c\u6362',
    'convey': '\u4f20\u8fbe', 'convince': '\u8bf4\u670d', 'cope': '\u5e94\u5bf9', 'correspond': '\u901a\u4fe1',
    'criterion': '\u6807\u51c6', 'criticize': '\u6279\u8bc4', 'crucial': '\u5173\u952e\u7684',
    'crush': '\u538b\u788e', 'cultivate': '\u57f9\u517b', 'curiosity': '\u597d\u5947\u5fc3',
    'curriculum': '\u8bfe\u7a0b', 'custom': '\u4e60\u4fd7', 'cycle': '\u5faa\u73af',
    'decay': '\u8150\u70c2', 'decline': '\u4e0b\u964d', 'decorate': '\u88c5\u9970', 'dedicate': '\u5949\u732e',
    'defeat': '\u51fb\u8d25', 'deficit': '\u8d64\u5b57', 'definite': '\u660e\u786e\u7684', 'delegate': '\u4ee3\u8868',
    'deliberate': '\u6545\u610f\u7684', 'delicate': '\u7cbe\u81f4\u7684', 'democracy': '\u6c11\u4e3b',
    'demonstrate': '\u8bc1\u660e', 'denial': '\u5426\u8ba4', 'dense': '\u5bc6\u96c6\u7684', 'deny': '\u5426\u8ba4',
    'deposit': '\u5b58\u6b3e', 'depress': '\u4f7f\u6c2e\u4e27', 'deprive': '\u5265\u593a', 'derive': '\u6765\u6e90\u4e8e',
    'deserve': '\u503c\u5f97', 'desperate': '\u7edd\u671b\u7684', 'destruction': '\u6bc1\u706d',
    'detect': '\u68c0\u6d4b', 'device': '\u8bbe\u5907', 'devote': '\u5949\u732e', 'diagnose': '\u8bca\u65ad',
    'differ': '\u4e0d\u540c', 'digital': '\u6570\u5b57\u7684', 'dilemma': '\u56f0\u5883', 'dimension': '\u7ef4\u5ea6',
    'diminish': '\u51cf\u5c11', 'diplomatic': '\u5916\u4ea4\u7684', 'directory': '\u76ee\u5f55',
    'discipline': '\u7eaa\u5f8b', 'discourage': '\u52dd\u963b', 'discrimination': '\u6b67\u89c6',
    'disguise': '\u4f2a\u88c5', 'dismiss': '\u89e3\u96c7', 'disorder': '\u6df7\u4e71', 'display': '\u5c55\u793a',
    'dispose': '\u5904\u7406', 'dispute': '\u4e89\u8bba', 'dissolve': '\u6eb6\u89e3', 'distinction': '\u533a\u522b',
    'distinguish': '\u533a\u5206', 'distribute': '\u5206\u914d', 'district': '\u5730\u533a',
    'disturb': '\u6253\u6270', 'diverse': '\u591a\u6837\u7684', 'divide': '\u5206\u5f00', 'division': '\u90e8\u95e8',
    'domestic': '\u56fd\u5185\u7684', 'dominant': '\u5360\u4e3b\u5bfc\u7684', 'dominate': '\u652f\u914d',
    'donate': '\u6350\u8d60', 'doom': '\u5384\u8fd0', 'draft': '\u8349\u7a3f', 'drain': '\u6392\u6c34',
    'dramatic': '\u620f\u5267\u6027\u7684', 'drift': '\u6f02\u6d41', 'drought': '\u5e72\u65f1', 'dull': '\u65e0\u804a\u7684',
    'dump': '\u503e\u5012', 'durable': '\u8010\u7528\u7684', 'duration': '\u6301\u7eed\u65f6\u95f4',
    'dynamic': '\u52a8\u6001\u7684', 'edition': '\u7248\u672c', 'editor': '\u7f16\u8f91',
    'efficient': '\u9ad8\u6548\u7684', 'elaborate': '\u7cbe\u5fc3\u5236\u4f5c\u7684', 'elderly': '\u5e74\u957f\u7684',
    'elect': '\u9009\u4e3e', 'electronic': '\u7535\u5b50\u7684', 'eliminate': '\u6d88\u9664',
    'embrace': '\u62e5\u62b1', 'emerge': '\u51fa\u73b0', 'emission': '\u6392\u653e', 'emphasis': '\u5f3a\u8c03',
    'emphasize': '\u5f3a\u8c03', 'enable': '\u4f7f\u80fd\u591f', 'encounter': '\u9047\u5230',
    'endure': '\u5fcd\u53d7', 'enforce': '\u6267\u884c', 'engage': '\u53c2\u4e0e', 'enhance': '\u589e\u5f3a',
    'enormous': '\u5de8\u5927\u7684', 'enquiry': '\u8be2\u95ee', 'ensure': '\u786e\u4fdd',
    'enthusiasm': '\u70ed\u60c5', 'entitle': '\u7ed9\u4e88\u6743\u5229', 'entity': '\u5b9e\u4f53',
    'episode': '\u63d2\u66f2', 'equivalent': '\u7b49\u4ef7\u7684', 'era': '\u65f6\u4ee3',
    'evolution': '\u8fdb\u5316', 'evolve': '\u6f14\u53d8', 'exaggerate': '\u5938\u5f20',
    'exceed': '\u8d85\u8fc7', 'excess': '\u8fc7\u91cf', 'excite': '\u6fc0\u52a8', 'exclude': '\u6392\u9664',
    'exclusive': '\u72ec\u5bb6\u7684', 'execute': '\u6267\u884c', 'exhaust': '\u8017\u5c3d',
    'exhibit': '\u5c55\u793a', 'expand': '\u6269\u5927', 'expansion': '\u6269\u5f20',
    'expense': '\u8d39\u7528', 'exploit': '\u5229\u7528', 'explosion': '\u7206\u70b8',
    'expose': '\u66b4\u9732', 'exposure': '\u66dd\u5149', 'extend': '\u5ef6\u4f38',
    'extension': '\u5ef6\u4f38', 'extensive': '\u5e7f\u6cdb\u7684', 'extent': '\u7a0b\u5ea6',
    'external': '\u5916\u90e8\u7684', 'extraordinary': '\u975e\u51e1\u7684', 'extreme': '\u6781\u7aef\u7684',
    'institute': '\u5b66\u9662', 'horizon': '\u5730\u5e73\u7ebf', 'immune': '\u514d\u75ab\u7684',
    'impose': '\u5f3a\u52a0', 'invade': '\u5165\u4fb5',
    'inject': '\u6ce8\u5c04', 'dose': '\u5242\u91cf', 'deputy': '\u526f\u624b', 'derived': '\u884d\u751f\u7684',
    'crack': '\u88c2\u7f1d', 'criteria': '\u6807\u51c6',
    'conceive': '\u6784\u601d',
    # Missing CET-4 words not in Oxford CSV
    'ache': '\u75bc\u75db', 'amuse': '\u9017\u4e50', 'avenue': '\u5927\u8857',
    'awake': '\u9192\u7684', 'bachelor': '\u5b66\u58eb', 'backward': '\u5411\u540e\u7684',
    'bore': '\u4f7f\u538c\u70e6', 'confuse': '\u4f7f\u56f0\u60d1', 'counsel': '\u5fe0\u544a',
}


def load_oxford_translations(csv_path):
    """Load translations from Oxford 5000 CSV file."""
    translations = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            term = row['term'].strip().lower()
            translation = row['translation'].strip()
            if translation:
                translations[term] = translation
    return translations


def check_audio(word, audio_dir):
    """Check if audio file exists for a word."""
    audio_file = f"{word}.wav"
    audio_path = os.path.join(audio_dir, audio_file)
    if os.path.exists(audio_path):
        return f'"{audio_file}"'
    return 'null'


def get_translation(word, oxford_translations, cet_translations):
    """Get translation for a word, preferring Oxford, falling back to CET dict."""
    word_lower = word.lower()
    if word_lower in oxford_translations:
        return oxford_translations[word_lower]
    if word_lower in cet_translations:
        return cet_translations[word_lower]
    return None


def generate_word_entry(word, meaning, audio_str):
    """Generate a single word entry JS string."""
    # Escape any quotes in meaning
    meaning_escaped = meaning.replace("'", "\\'").replace('"', '\\"')
    return f'                {{ word: "{word}", meaning: "{meaning_escaped}", audio: {audio_str} }}'


def generate_wordbook_js(book_id, name, emoji, description, levels_data):
    """Generate the full wordbook JS content."""
    lines = []
    lines.append(f"registerWordbook('{book_id}', {{")
    lines.append(f'    name: "{name}",')
    lines.append(f'    emoji: "{emoji}",')
    lines.append(f"    group: 'exam',")
    lines.append(f'    description: "{description}",')
    lines.append(f'    levels: {{')

    level_keys = list(levels_data.keys())
    for i, (level_key, level_info) in enumerate(levels_data.items()):
        level_name = level_info['name']
        words = level_info['words']
        lines.append(f"        '{level_key}': {{")
        lines.append(f"            name: '{level_name}',")
        lines.append(f'            words: [')
        for j, entry in enumerate(words):
            comma = ',' if j < len(words) - 1 else ''
            lines.append(f'{entry}{comma}')
        lines.append(f'            ]')
        if i < len(level_keys) - 1:
            lines.append(f'        }},')
        else:
            lines.append(f'        }}')

    lines.append(f'    }}')
    lines.append(f'}});')
    lines.append('')  # trailing newline

    return '\n'.join(lines)


def main():
    print("=" * 60)
    print("CET Wordbook Generator")
    print("=" * 60)

    # Load Oxford translations
    print(f"\nLoading Oxford 5000 translations from: {OXFORD_CSV}")
    oxford_translations = load_oxford_translations(OXFORD_CSV)
    print(f"  Loaded {len(oxford_translations)} Oxford translations")

    # Deduplicate CET4 words
    cet4_words = list(dict.fromkeys(CET4_WORDS))  # preserve order, remove duplicates
    print(f"\nCET-4 words (after dedup): {len(cet4_words)}")

    # Build CET4 set for deduplication
    cet4_set = set(w.lower() for w in cet4_words)

    # Deduplicate CET6 words and remove any that are already in CET4
    cet6_words_raw = list(dict.fromkeys(CET6_WORDS))
    cet6_words = [w for w in cet6_words_raw if w.lower() not in cet4_set]
    removed_dupes = len(cet6_words_raw) - len(cet6_words)
    if removed_dupes > 0:
        print(f"  Removed {removed_dupes} CET-6 words that were already in CET-4")
    print(f"CET-6 words (after dedup, excluding CET-4): {len(cet6_words)}")

    # Process CET-4
    print(f"\nProcessing CET-4 vocabulary...")
    cet4_split = 320  # first 320 = high-freq, rest = core
    cet4_high_freq = cet4_words[:cet4_split]
    cet4_core = cet4_words[cet4_split:]
    print(f"  High-freq: {len(cet4_high_freq)} words")
    print(f"  Core: {len(cet4_core)} words")

    cet4_missing = []
    cet4_entries_high = []
    for word in cet4_high_freq:
        meaning = get_translation(word, oxford_translations, CET_TRANSLATIONS)
        if meaning is None:
            cet4_missing.append(word)
            meaning = word  # fallback
        audio = check_audio(word, AUDIO_DIR)
        cet4_entries_high.append(generate_word_entry(word, meaning, audio))

    cet4_entries_core = []
    for word in cet4_core:
        meaning = get_translation(word, oxford_translations, CET_TRANSLATIONS)
        if meaning is None:
            cet4_missing.append(word)
            meaning = word
        audio = check_audio(word, AUDIO_DIR)
        cet4_entries_core.append(generate_word_entry(word, meaning, audio))

    if cet4_missing:
        print(f"  WARNING: {len(cet4_missing)} CET-4 words missing translations: {cet4_missing[:20]}...")

    # Count audio hits for CET-4
    cet4_audio_count = sum(1 for w in cet4_words if os.path.exists(os.path.join(AUDIO_DIR, f"{w}.wav")))
    print(f"  Audio available: {cet4_audio_count}/{len(cet4_words)}")

    # Process CET-6
    print(f"\nProcessing CET-6 vocabulary...")
    cet6_split = 240  # first 240 = high-freq, rest = core
    cet6_high_freq = cet6_words[:cet6_split]
    cet6_core = cet6_words[cet6_split:]
    print(f"  High-freq: {len(cet6_high_freq)} words")
    print(f"  Core: {len(cet6_core)} words")

    cet6_missing = []
    cet6_entries_high = []
    for word in cet6_high_freq:
        meaning = get_translation(word, oxford_translations, CET_TRANSLATIONS)
        if meaning is None:
            cet6_missing.append(word)
            meaning = word
        audio = check_audio(word, AUDIO_DIR)
        cet6_entries_high.append(generate_word_entry(word, meaning, audio))

    cet6_entries_core = []
    for word in cet6_core:
        meaning = get_translation(word, oxford_translations, CET_TRANSLATIONS)
        if meaning is None:
            cet6_missing.append(word)
            meaning = word
        audio = check_audio(word, AUDIO_DIR)
        cet6_entries_core.append(generate_word_entry(word, meaning, audio))

    if cet6_missing:
        print(f"  WARNING: {len(cet6_missing)} CET-6 words missing translations: {cet6_missing[:20]}...")

    # Count audio hits for CET-6
    cet6_audio_count = sum(1 for w in cet6_words if os.path.exists(os.path.join(AUDIO_DIR, f"{w}.wav")))
    print(f"  Audio available: {cet6_audio_count}/{len(cet6_words)}")

    # Generate CET-4 JS
    cet4_levels = {
        '\u9ad8\u9891': {
            'name': '\u2b50 \u9ad8\u9891\u8bcd',
            'words': cet4_entries_high,
        },
        '\u6838\u5fc3': {
            'name': '\U0001f4dd \u6838\u5fc3\u8bcd',
            'words': cet4_entries_core,
        },
    }
    cet4_js = generate_wordbook_js(
        'cet4',
        '\u56db\u7ea7\u8bcd\u6c47',
        '\U0001f393',
        '\u5927\u5b66\u82f1\u8bed\u56db\u7ea7\u6838\u5fc3\u8bcd\u6c47',
        cet4_levels
    )

    # Generate CET-6 JS
    cet6_levels = {
        '\u9ad8\u9891': {
            'name': '\u2b50 \u9ad8\u9891\u8bcd',
            'words': cet6_entries_high,
        },
        '\u6838\u5fc3': {
            'name': '\U0001f4dd \u6838\u5fc3\u8bcd',
            'words': cet6_entries_core,
        },
    }
    cet6_js = generate_wordbook_js(
        'cet6',
        '\u516d\u7ea7\u8bcd\u6c47',
        '\U0001f393',
        '\u5927\u5b66\u82f1\u8bed\u516d\u7ea7\u6838\u5fc3\u8bcd\u6c47',
        cet6_levels
    )

    # Write output files
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cet4_path = os.path.join(OUTPUT_DIR, 'cet4_vocabulary.js')
    with open(cet4_path, 'w', encoding='utf-8') as f:
        f.write(cet4_js)
    print(f"\nWritten: {cet4_path}")

    cet6_path = os.path.join(OUTPUT_DIR, 'cet6_vocabulary.js')
    with open(cet6_path, 'w', encoding='utf-8') as f:
        f.write(cet6_js)
    print(f"Written: {cet6_path}")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"CET-4 Wordbook:")
    print(f"  Total words: {len(cet4_words)}")
    print(f"  \u9ad8\u9891 (high-freq): {len(cet4_high_freq)}")
    print(f"  \u6838\u5fc3 (core):      {len(cet4_core)}")
    print(f"  Audio coverage: {cet4_audio_count}/{len(cet4_words)} ({100*cet4_audio_count/len(cet4_words):.1f}%)")
    print(f"  Missing translations: {len(cet4_missing)}")
    print(f"\nCET-6 Wordbook:")
    print(f"  Total words: {len(cet6_words)}")
    print(f"  \u9ad8\u9891 (high-freq): {len(cet6_high_freq)}")
    print(f"  \u6838\u5fc3 (core):      {len(cet6_core)}")
    print(f"  Audio coverage: {cet6_audio_count}/{len(cet6_words)} ({100*cet6_audio_count/len(cet6_words):.1f}%)")
    print(f"  Missing translations: {len(cet6_missing)}")
    if cet4_missing:
        print(f"\nCET-4 words without translation: {cet4_missing}")
    if cet6_missing:
        print(f"CET-6 words without translation: {cet6_missing}")
    print(f"\nDone!")


if __name__ == '__main__':
    main()
