# -*- coding: utf-8 -*-
# 任务1: Boss图鉴 + 质检员每日重摇 + 大葱外观
s = open('D:/self-project/game/src/template.html', encoding='utf-8').read()

# ===== State =====
old = """  achievements: [], timeline: [],"""
new = """  achievements: [], timeline: [], bossDex: {},
  glitch: { date: '', mult: 0 },"""
assert old in s, "state"; s = s.replace(old, new)

# ===== Boss 击杀入图鉴 =====
old = """  if (ECON.isBoss(S.zone)) S.stats.bosses++;"""
new = """  if (ECON.isBoss(S.zone)) { S.stats.bosses++; S.bossDex[ECON.bossName(S.zone)] = (S.bossDex[ECON.bossName(S.zone)] || 0) + 1; }"""
assert old in s, "dex"; s = s.replace(old, new)

# ===== Boss 图鉴文案 + hall 渲染区块 =====
old = """function renderHall() {"""
new = """const BOSS_LORE = {
  '加班史莱姆': '第一个Boss。它只是想准时下班，没想挡路。愿它在天堂不用打卡。',
  '堕落的天启之焰审判者·终焉形态': '名字长到被长名猎手克制，是全体玩家GS的垫脚石。审判别人的时候没想到自己也会被审判。',
  '血钟看守者': '看守血钟一千年，钟没响过一次。失业当天表示如释重负。',
  '万魔殿PPT魔导书·路西法监制版': '每一页都是一个闭环。读完的人要么成神，要么成病。',
  '矿场工头·哥布林包工头': '欠条比命硬。死后欠条自动继承给长子。',
  '深渊颂歌者·其名超乎想象地长到离谱': '唱歌非常好听，但名字印在专辑封面上会溢出。',
  '客服天使·亲亲这边建议您毁灭呢': '话术等级：神级。建议全深渊客服培训以它为教材。',
  '魔王(实习期)': '魔王也需要从实习做起。它的转正答辩至今没通过，因为评委也还在实习。',
};
function renderHall() {"""
assert old in s, "lore"; s = s.replace(old, new)

old = """  const tl = document.getElementById('tlList');"""
new = """  // Boss 图鉴
  document.getElementById('dexGrid').innerHTML = Object.keys(BOSS_LORE).map(name => {
    const kills = S.bossDex[name] || 0;
    const on = kills > 0;
    return `<div class="ach ${on ? 'on' : 'off'}" style="width:230px"><b>${on ? '💀 ' : '🔒 ??? '}${on ? name : '未遭遇'}</b>${on ? '击杀 ×' + kills + '<br><small style="color:var(--parchment-dim)">' + BOSS_LORE[name] + '</small>' : '<small>在深渊某处等着你</small>'}</div>`;
  }).join('');
  const tl = document.getElementById('tlList');"""
assert old in s, "dexrender"; s = s.replace(old, new)

old = """    <h3>🏆 成 就 墙</h3>"""
new = """    <h3>💀 Boss 图 鉴（物理超度花名册）</h3>
    <div id="dexGrid"></div>
    <h3>🏆 成 就 墙</h3>"""
assert old in s, "dexhtml"; s = s.replace(old, new)

# ===== 质检员每日重摇 =====
old = """function gearEffects() { return GSYS.itemEffects(S.gear, S.enh); }"""
new = """function gearEffects() { return GSYS.itemEffects(S.gear, S.enh); }
// 质检员的错别字：持有 glitch 装备时每日重摇 allDmg 倍率（log均匀 5~500）
function checkGlitchReroll() {
  const hasGlitch = Object.values(S.gear).some(it => it && it.affixes.some(a => a.key === 'sp_glitch'));
  const today = new Date().toDateString();
  if (!hasGlitch) { S.glitch.mult = 0; return; }
  if (S.glitch.date !== today) {
    S.glitch.date = today;
    S.glitch.mult = Math.round(Math.pow(10, 0.7 + Math.random() * 2.0) * 10) / 10;
    showPopup('【质检员的错别字】今日重摇', ['那件彩色装备的属性被质检员又填错了。', '今日效果：全局 ×' + S.glitch.mult, '（质检员表示：反正没人看它的代码。）'], 'ev-t3');
  }
}"""
assert old in s, "glitch"; s = s.replace(old, new)

# mults 应用 glitch（在 achievements 加成后）
old = "function mults() { return GSYS.multsWrap ? GSYS.multsWrap() : ECON.computeMults(S.affixes, AFFIX, currentBoss(), S.buffs, Math.pow(C.shopTyrannyMult, S.shop.tyr) * Math.pow(1.05, S.achievements.length), Date.now(), { spdLv: S.spd, gearEffects: gearEffects() }); }"
# 若上式不存在则用真实锚点
if old not in s:
    old = """function mults() { return ECON.computeMults(S.affixes, AFFIX, currentBoss(), S.buffs, Math.pow(C.shopTyrannyMult, S.shop.tyr) * Math.pow(1.05, S.achievements.length), Date.now(), { spdLv: S.spd, gearEffects: gearEffects() }); }"""
    new = """function mults() {
  const m = ECON.computeMults(S.affixes, AFFIX, currentBoss(), S.buffs, Math.pow(C.shopTyrannyMult, S.shop.tyr) * Math.pow(1.05, S.achievements.length), Date.now(), { spdLv: S.spd, gearEffects: gearEffects() });
  if (S.glitch.mult > 0) m.allDmg *= S.glitch.mult;
  return m;
}"""
    assert old in s, "glitchmult"; s = s.replace(old, new)

# tick 每分钟检查重摇 + load 时
old = """  achTimer += TICK;
  if (achTimer >= 1) { achTimer = 0; checkAchievements(); }"""
new = """  achTimer += TICK;
  if (achTimer >= 1) { achTimer = 0; checkAchievements(); checkGlitchReroll(); }"""
assert old in s, "glitchtick"; s = s.replace(old, new)

# 装备栏显示今日重摇
old = """    const aff = it.affixes.map(a => (a.kind === 'special' ? '★' : '×') + ECON.fmt(new D(a.mult))).join(' ');"""
new = """    const aff = it.affixes.map(a => (a.kind === 'special' ? '★' : '×') + ECON.fmt(new D(a.mult)) + (a.key === 'sp_glitch' && S.glitch.mult > 0 ? '(今日实为×' + S.glitch.mult + ')' : '')).join(' ');"""
assert old in s, "glitchui"; s = s.replace(old, new)

# ===== 大葱外观渲染 =====
old = """  } else {
    ctx.fillStyle = '#c0c0d0'; ctx.fillRect(150, 234, 26, 3); // 待机持剑
  }"""
new = """  } else if (S.gear.weapon && S.gear.weapon.cosmetic === 'leek') {
    // 大葱外观：绿茎白根，随呼吸轻晃
    const wob = Math.sin(t / 250) * 2;
    ctx.fillStyle = '#3caa3c'; ctx.fillRect(150, 218 + wob, 6, 22);
    ctx.fillStyle = '#7cd67c'; ctx.fillRect(150, 218 + wob, 3, 10);
    ctx.fillStyle = '#e8e8d0'; ctx.fillRect(150, 238, 6, 8);
    ctx.fillStyle = '#c8b878'; ctx.fillRect(148, 246, 10, 3);
  } else {
    ctx.fillStyle = '#c0c0d0'; ctx.fillRect(150, 234, 26, 3); // 待机持剑
  }"""
assert old in s, "leek"; s = s.replace(old, new)

# ===== save v7 =====
old = """    gear: S.gear, enh: S.enh, pity: S.pity, scrap: S.scrap, talents: S.talents,
    buffs: S.buffs, lastSave: Date.now(),"""
new = """    gear: S.gear, enh: S.enh, pity: S.pity, scrap: S.scrap, talents: S.talents,
    bossDex: S.bossDex, glitch: S.glitch,
    buffs: S.buffs, lastSave: Date.now(),"""
assert old in s, "save"; s = s.replace(old, new)
old = """          if (d.v >= 6) S.talents = d.talents || {};"""
new = """          if (d.v >= 6) {
            S.talents = d.talents || {};
            if (d.v >= 7) { S.bossDex = d.bossDex || {}; S.glitch = d.glitch || S.glitch; }
          }"""
assert old in s, "load"; s = s.replace(old, new)

open('D:/self-project/game/src/template.html', 'w', encoding='utf-8').write(s)
print("任务1补丁完成（写盘核验: bossDex=%s glitch=%s leek=%s)" % (
  'bossDex' in s, 'checkGlitchReroll' in s, '大葱外观'))
