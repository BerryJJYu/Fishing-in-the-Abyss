# -*- coding: utf-8 -*-
# v7 天赋树第一批重做（含写盘）
s = open('D:/self-project/game/src/template.html', encoding='utf-8').read()

# ===== 1. State: 天赋 =====
old = """  souls: 0, shop: { tyr: 0, sqz: 0, mad: 0 },"""
new = """  souls: 0, shop: { tyr: 0, sqz: 0, mad: 0 },
  talents: {},"""
assert old in s, "state"
s = s.replace(old, new)

# ===== 2. HTML: 商店面板下天赋区 =====
old = """      <div style="margin-top:4px"><button id="shopMad">发疯·事件 ×1.5 (<span id="shopMadCost">1</span>) Lv.<span id="shopMadLv">0</span></button></div>
    </div>
  </div>"""
new = """      <div style="margin-top:4px"><button id="shopMad">发疯·事件 ×1.5 (<span id="shopMadCost">1</span>) Lv.<span id="shopMadLv">0</span></button></div>
      <div class="boxtitle" style="margin-top:8px">转 生 天 赋 树（需对应线等级，效果改变玩法）</div>
      <div id="talentArea" style="font-size:11px;line-height:1.7"></div>
    </div>
  </div>"""
assert old in s, "talenthtml"
s = s.replace(old, new)

# ===== 3. JS: 天赋定义 + 购买 + 事件委托 =====
old = """document.getElementById('shopMad').onclick = () => buyShop('mad');"""
new = """document.getElementById('shopMad').onclick = () => buyShop('mad');

// ===== 转生天赋树（商店三线的深层分支，满级线解锁改变玩法的机制） =====
const TALENTS = [
  { id: 't1', line: 'tyr', needLv: 3, cost: 4,  name: '处决之眼',   desc: '普攻直接处决血量低于15%的敌人' },
  { id: 't2', line: 'tyr', needLv: 5, cost: 7,  name: '狂暴',       desc: '连杀金币上限 ×3 → ×6' },
  { id: 't3', line: 'tyr', needLv: 8, cost: 12, name: '战争践踏',   desc: '掀桌一击冷却减半（45s→22s）' },
  { id: 't4', line: 'sqz', needLv: 3, cost: 4,  name: '骷髅远征队', desc: '每60秒骷髅兵自动上交当前区金币×30' },
  { id: 't5', line: 'sqz', needLv: 5, cost: 7,  name: '深夜加班',   desc: '离线结算上限 8小时 → 16小时' },
  { id: 't6', line: 'sqz', needLv: 8, cost: 12, name: '压榨的艺术', desc: '收保护费效果 ×2' },
  { id: 't7', line: 'mad', needLv: 3, cost: 4,  name: '加个麦克风', desc: '事件选项解锁第三项：30%概率×500 / 70%亏70%金币' },
  { id: 't8', line: 'mad', needLv: 5, cost: 7,  name: '传说事件池', desc: '传说级事件(t4)权重 ×3' },
  { id: 't9', line: 'mad', needLv: 8, cost: 12, name: '精神污染',   desc: '所有主动技能冷却 -30%' },
];
function hasTalent(id) { return !!S.talents[id]; }
function buyTalent(id) {
  const t = TALENTS.find(x => x.id === id);
  if (!t || S.talents[id]) return;
  if (S.shop[t.line] < t.needLv) return;
  if (S.souls < t.cost) return;
  S.souls -= t.cost;
  S.talents[id] = true;
  showPopup('🌟 天赋点亮', ['「' + t.name + '」—— ' + t.desc, '魔王：这才像话。工资不发，天赋管够。'], 'ev-t3');
  addLog('[天赋] 解锁「' + t.name + '」：' + t.desc, 'ev-t3');
  save();
}
document.getElementById('talentArea').addEventListener('click', e => {
  const b = e.target.closest('button[data-tal]');
  if (b) buyTalent(b.dataset.tal);
});"""
assert old in s, "talentdef"
s = s.replace(old, new)

# ===== 4. 效果接线 =====
old = """function comboMult() { return Math.min(C.comboCap, 1 + S.combo * C.comboStep); }"""
new = """function comboMult() { return Math.min(hasTalent('t2') ? C.comboCap * 2 : C.comboCap, 1 + S.combo * C.comboStep); }"""
assert old in s, "t2"
s = s.replace(old, new)

old = """function effCd(id) { return SKILLS[id].cd * (1 - Math.min(0.3, S.stats.cdReduce || 0)); }"""
new = """function effCd(id) {
  let cd = SKILLS[id].cd * (1 - Math.min(0.3, S.stats.cdReduce || 0));
  if (id === 'slam' && hasTalent('t3')) cd *= 0.5;
  if (hasTalent('t9')) cd *= 0.7;
  return cd;
}"""
assert old in s, "cd"
s = s.replace(old, new)

old = """  S.hp = S.hp.minus(effDmg);
  if (S.hp.lte(0)) kill(m);
}"""
new = """  if (hasTalent('t1') && S.hp.div(S.hpMax).toNumber() < 0.15) { effDmg = new D('1e3000'); addFloater('处决！', '#ff3c6c', 24); }
  S.hp = S.hp.minus(effDmg);
  if (S.hp.lte(0)) kill(m);
}"""
assert old in s, "t1"
s = s.replace(old, new)

old = """  eventTimer += TICK;
  // 换装对比 10 秒超时自动装备"""
new = """  expeditionTimer += TICK;
  if (hasTalent('t4') && expeditionTimer >= 60) {
    expeditionTimer = 0;
    const g = ECON.zoneGold(S.zone).times(30).times(m.goldGain);
    S.gold = S.gold.plus(g);
    addLog('[远征] 骷髅兵远征队凯旋！上交战利品 ' + ECON.fmt(g) + ' 金币。队长申请转正，已读不回。', 'ev-t2');
  }
  eventTimer += TICK;
  // 换装对比 10 秒超时自动装备"""
assert old in s, "t4"
s = s.replace(old, new)
old = "let lastTickAt = performance.now(), saveTimer = 0, eventTimer = 0, achTimer = 0;"
new = "let lastTickAt = performance.now(), saveTimer = 0, eventTimer = 0, achTimer = 0, expeditionTimer = 0;"
assert old in s, "timer"
s = s.replace(old, new)

old = """    const g = ECON.zoneGold(S.zone).times(skillParamsOf('tax').goldSec).times(m.goldGain);
    SFX.skill('tax');"""
new = """    const g = ECON.zoneGold(S.zone).times(skillParamsOf('tax').goldSec).times(m.goldGain).times(hasTalent('t6') ? 2 : 1);
    SFX.skill('tax');"""
assert old in s, "t6"
s = s.replace(old, new)

old = """    showPopup(title + ' · 你来决策', body, 'ev-t' + ev.tier.slice(1), {
      sticky: true,
      buttons: ev.choices.map((c, i) => ({
        label: (i === 0 ? 'A: ' : 'B: ') + c.text,
        cb: () => resolveChoice(ev, i),
      })),
    });
    return;"""
new = """    const chs = ev.choices.slice();
    if (hasTalent('t7') && chs.length === 2) {
      chs.push({ text: 'C: 疯狂模式——赌上一切！', kind: 'gamble', chance: 0.3,
        win: { kind: 'goldMult', mult: 500, log: '深渊骰子为你停在了六！宇宙都在配合你发疯。' },
        lose: { kind: 'goldLoss', rate: 0.7, log: '深渊骰子没有骰子。它只是看着你，然后拿走了钱。' } });
    }
    showPopup(title + ' · 你来决策', body, 'ev-t' + ev.tier.slice(1), {
      sticky: true,
      buttons: chs.map((c, i) => ({
        label: (['A: ', 'B: ', 'C: '][i] || '') + c.text,
        cb: () => resolveChoice({ choices: chs, tier: ev.tier }, i),
      })),
    });
    return;"""
assert old in s, "t7"
s = s.replace(old, new)

old = """function fireEvent() {
  const ev = ECON.pickEvent(EVENTS, Math.random);"""
new = """function fireEvent() {
  let tbl = EVENTS;
  if (hasTalent('t8')) {
    tbl = JSON.parse(JSON.stringify(EVENTS));
    const t4 = tbl.tiers.find(t => t.id === 't4');
    const t1 = tbl.tiers.find(t => t.id === 't1');
    if (t4 && t1) { t4.weight += t1.weight * 0.5; t1.weight *= 0.5; }
  }
  const ev = ECON.pickEvent(tbl, Math.random);"""
assert old in s, "t8"
s = s.replace(old, new)

old = "      const r = ECON.simulateOffline(S, AFFIX, delta, Date.now(), Math.pow(C.shopSqueezeMult, S.shop.sqz));"
new = "      const r = ECON.simulateOffline(S, AFFIX, delta, Date.now(), Math.pow(C.shopSqueezeMult, S.shop.sqz), hasTalent('t5') ? 16 * 3600 : C.offlineCapSec);"
assert old in s, "t5"
s = s.replace(old, new)

open('D:/self-project/game/src/template.html', 'w', encoding='utf-8').write(s)
print("天赋树第一批重做完成（含写盘），talentArea 数:",
      open('D:/self-project/game/src/template.html', encoding='utf-8').read().count('talentArea'))
