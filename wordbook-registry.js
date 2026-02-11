// ============================================================
// Word2048 词书注册系统
// 所有词书通过 registerWordbook() 注册到全局注册表
// ============================================================

const WORDBOOK_REGISTRY = {};

/**
 * 注册一本词书
 * @param {string} id - 词书唯一标识 (如 'oxford_5000', 'scene_food', 'cet4')
 * @param {object} config - 词书配置
 * @param {string} config.name - 词书名称
 * @param {string} config.emoji - 词书图标
 * @param {string} config.description - 词书描述
 * @param {string} [config.group] - 词书分组 ('exam'|'scene'|'general')
 * @param {object} config.levels - 等级/分类 { levelId: { name, words: [{word, meaning, audio}] } }
 */
function registerWordbook(id, config) {
    // 计算总词数
    let totalWords = 0;
    Object.values(config.levels).forEach(level => {
        totalWords += level.words ? level.words.length : 0;
    });
    config.totalWords = totalWords;
    config.id = id;
    WORDBOOK_REGISTRY[id] = config;
}
