# -*- coding: utf-8 -*-
# 任务C: 周目挑战 + 神格天赋树
s = open('D:/self-project/game/src/template.html', encoding='utf-8').read()

# ===== 1. State =====
old = """  dp: 0, dpShop: { might: 0, haste: 0, touch: 0 },"""
new = """  dp: 0, dpShop: { might: 0, haste: 0, touch: 0 }, dpTalents: {},
  challenge: null, doneChallenges: [],"""
assert old in s, "state"; s = s.replace(old, new)

# ===== 2. 定义 + UI 逻辑（插在神格商店购买后） =====
old = """document.getElementById('dpTouch').onclick = () => buyDp('touch');"""
new = """document.getElementById('dpTouch').onclick = () => buyDp('touch');

// ===== 神格天赋树（神格点的深层投资） =====
const DP_TALENTS = [
  { id: 'd1', name: '万物归一', desc: '神威每级 ×10 → ×12', need: () => S.dpShop.might >= 2, needTxt: '神威 Lv.2', cost: 3 },
  { id: 'd2', name: '时间领主', desc: '神速每级 ×1.5 → ×1.8', need: () => S.dpShop.haste >= 2, needTxt: '神速 Lv.2', cost: 3 },
  { id: 'd3', name: '圣光留存', desc: '飞升后保留武器槽装备', need: () => S.dp >= 5 || S.stats.lifetimeSouls >= 30, needTxt: '累计黑魂30或神格5', cost: 5 },
];
function hasDpTalent(id) { return !!S.dpTalents[id]; }
function buyDpTalent(id) {
  const t = DP_TALENTS.find(x => x.id === id);
  if (!t || hasDpTalent(id)) return;
  if (!t.need()) return;
  if (S.dp < t.cost) return;
  S.dp -= t.cost;
  S.dpTalents[id] = true;
  showPopup('✨ 神格天赋', ['「' + t.name + '」—— ' + t.desc, '神明表示：这个方向有前途。'], 'ev-t3');
  addLog('[神格天赋] 解锁「' + t.name + '」：' + t.desc, 'ev-t3');
  save();
}
document.getElementById('dpTalentArea').addEventListener('click', e => {
  const b = e.target.closest('button[data-dpt]');
  if (b) buyDpTalent(b.dataset.dpt);
});

// ===== 周目挑战 =====
const CHALLENGES = [
  { id: 'ch_nocrit',  name: '禁暴击周目',   desc: '全程无暴击。 crit是什么？没听说过。', dpReward: 2 },
  { id: 'ch_noskill', name: '无技可施周目', desc: '主动技能全部失效。纯靠硬砍。',          dpReward: 2 },
  { id: 'ch_bare',    name: '空手周目',     desc: '装备加成衰减至30%。拳头的时代。',      dpReward: 3 },
];
function startChallenge(id) {
  if (S.challenge || S.doneChallenges.includes(id)) return;
  S.challenge = id;
  const c = CHALLENGES.find(x => x.id === id);
  showPopup('⚔ 周目挑战开始', ['「' + c.name + '」—— ' + c.desc, '达成条件：挑战期间飞升（区80）。', '奖励：神格点 ×' + c.dpReward + ' + 独占纪录。', '魔王：自虐玩法都出来了，深渊就业形势严峻。'], 'ev-t3');
  addLog('[挑战] 周目挑战开始「' + c.name + '」', 'ev-t3');
  save();
}
function settleChallenge() {
  const c = CHALLENGES.find(x => x.id === S.challenge);
  if (!c) return;
  S.doneChallenges.push(c.id);
  const bonus = c.dpReward * 2;
  S.dp += bonus;
  showPopup('🏆 挑战完成！', ['「' + c.name + '」周目达成！', '奖励：神格点 ×' + bonus + '（双倍）', '成就墙上已留名。魔王递来一面锦旗：深渊最卷。'], 'ev-t3');
  addLog('[挑战完成] 「' + c.name + '」达成！神格 +' + bonus, 'ev-t3');
  S.challenge = null;
}"""
assert old in s, "def"; s = s.replace(old, new)

# ===== 3. 挑战规则接线 =====
# 无暴击
old = """function crtP() { return ECON.critParams(S.crt); }"""
new = """function crtP() {
  const p = ECON.critParams(S.crt);
  if (S.challenge === 'ch_nocrit') p.rate = 0;
  return p;
}"""
assert old in s, "nocrit"; s = s.replace(old, new)
# 无技能
old = """function useSkill(id) {
  const sk = SKILLS[id];
  const now = Date.now();"""
new = """function useSkill(id) {
  if (S.challenge === 'ch_noskill') return;
  const sk = SKILLS[id];
  const now = Date.now();"""
assert old in s, "noskill"; s = s.replace(old, new)
# 空手周目
old = """function gearEffects() { return GSYS.itemEffects(S.gear, S.enh); }"""
new = """function gearEffects() {
  const ge = GSYS.itemEffects(S.gear, S.enh);
  if (S.challenge === 'ch_bare') for (const e of ge) if (e.type === 'always') e.mult *= 0.3;
  return ge;
}"""
assert old in s, "bare"; s = s.replace(old, new)
# 飞升结算
old = """document.getElementById('ascendBtn').onclick = () => {
  const gain = Math.floor(S.maxZone / 80);
  if (gain <= 0) return;
  S.dp += gain;"""
new = """document.getElementById('ascendBtn').onclick = () => {
  const gain = Math.floor(S.maxZone / 80);
  if (gain <= 0) return;
  if (S.challenge && S.maxZone >= 80) { const c = CHALLENGES.find(x => x.id === S.challenge); if (c) { settleChallenge(); gain += 0; } }
  S.dp += gain;"""
assert old in s, "settle"; s = s.replace(old, new)

# ===== 4. HTML: 挑战面板 + 神格天赋区 =====
old = """    <div style="font-size:10px;color:var(--parchment-dim);margin-top:4px">飞升保留：装备/强化/天赋/商店/成就。清空：区域/等级/金币。</div>
  </div>
</div>
<div id="panel4" style="display:flex; gap:8px; margin-top:8px; flex-wrap:wrap;">"""
new = """    <div style="font-size:10px;color:var(--parchment-dim);margin-top:4px">飞升保留：装备/强化/天赋/商店/成就。清空：区域/等级/金币。</div>
    <div class="boxtitle" style="margin-top:8px">神 格 天 赋 树（神格点的深层投资）</div>
    <div id="dpTalentArea" style="font-size:11px;line-height:1.7"></div>
    <div class="boxtitle" style="margin-top:8px">周 目 挑 战（激活后于本周期内飞升即达成，奖励双倍神格）</div>
    <div id="chalArea" style="font-size:11px;line-height:1.7"></div>
  </div>
</div>
<div id="panel4" style="display:flex; gap:8px; margin-top:8px; flex-wrap:wrap;">"""
assert old in s, "html"; s = s.replace(old, new)

# ===== 5. 渲染 (refreshUI 尾部) =====
old = """  // 远征队渲染"""
new = """  // 神格天赋 + 周目挑战渲染
  const dta = document.getElementById('dpTalentArea');
  if (dta) {
    dta.innerHTML = DP_TALENTS.map(t => {
      const owned = hasDpTalent(t.id);
      const ok = t.need() && S.dp >= t.cost;
      return `<div><span style="${owned ? 'color:var(--green)' : 'color:var(--gold)'}">${owned ? '✨' : '✧'} ${t.name}</span> <small>${t.desc}</small> ${owned ? '<b>✓</b>' : `<button data-dpt="${t.id}" style="font-size:10px;padding:2px 8px" ${ok ? '' : 'disabled'}>${t.cost}点</button><small> ${t.needTxt}</small>`}</div>`;
    }).join('');
  }
  const ca = document.getElementById('chalArea');
  if (ca) {
    ca.innerHTML = CHALLENGES.map(c => {
      const done = S.doneChallenges.includes(c.id);
      const active = S.challenge === c.id;
      const blocked = !!S.challenge;
      let st = done ? '<b style="color:var(--green)">🏆已达成</b>' : active ? '<b style="color:var(--gold)">⚔进行中</b>' : '';
      const btn = (done || active || blocked) ? '' : `<button data-chal="${c.id}" style="font-size:10px;padding:2px 8px">激活 (奖${c.dpReward * 2}点)</button>`;
      return `<div><span style="${active ? 'color:var(--gold)' : ''}">${c.name}</span> <small>${c.desc}</small> ${st}${btn}</div>`;
    }).join('');
  }
  // 远征队渲染"""
assert old in s, "render"; s = s.replace(old, new)

# ===== 6. 事件委托 + 飞升保留武器(d3) =====
old = """document.getElementById('talentArea').addEventListener('click', e => {"""
new = """document.getElementById('chalArea').addEventListener('click', e => {
  const b = e.target.closest('button[data-chal]');
  if (b) startChallenge(b.dataset.chal);
});
document.getElementById('talentArea').addEventListener('click', e => {"""
assert old in s, "dele"; s = s.replace(old, new)

# d3 飞升保留武器
old = """  SFX.organ();
  S.zone = 1; S.level = 0; S.gold = new D(0);
  S.hp = S.hpMax = ECON.zoneHP(S.zone);
  S.affixes = []; S.buffs = []; S.combo = 0; S.maxZone = 1; S._brk = 0;
  save();
};"""
new = """  SFX.organ();
  const keepWeapon = hasDpTalent('d3') ? S.gear.weapon : null;
  S.zone = 1; S.level = 0; S.gold = new D(0);
  S.hp = S.hpMax = ECON.zoneHP(S.zone);
  S.affixes = []; S.buffs = []; S.combo = 0; S.maxZone = 1; S._brk = 0;
  S.gear = { weapon: keepWeapon, armor: null, trinket: null };
  save();
};"""
assert old in s, "d3"; s = s.replace(old, new)

# ===== 7. save v8 追加字段 =====
old = """    exp: S.exp, morningDate: S.morningDate,
    buffs: S.buffs, lastSave: Date.now(),"""
new = """    exp: S.exp, morningDate: S.morningDate,
    dpTalents: S.dpTalents, challenge: S.challenge, doneChallenges: S.doneChallenges,
    buffs: S.buffs, lastSave: Date.now(),"""
assert old in s, "save"; s = s.replace(old, new)
old = """            if (d.v >= 8) { S.dp = d.dp || 0; S.dpShop = d.dpShop || { might: 0, haste: 0, touch: 0 }; S.exp = d.exp || S.exp; S.morningDate = d.morningDate || ''; }"""
new = """            if (d.v >= 8) {
              S.dp = d.dp || 0; S.dpShop = d.dpShop || { might: 0, haste: 0, touch: 0 }; S.exp = d.exp || S.exp; S.morningDate = d.morningDate || '';
              S.dpTalents = d.dpTalents || {}; S.challenge = d.challenge || null; S.doneChallenges = d.doneChallenges || [];
            }"""
assert old in s, "load"; s = s.replace(old, new)

open('D:/self-project/game/src/template.html', 'w', encoding='utf-8').write(s)
print("任务C补丁完成（写盘核验: chal=%s dpt=%s)" % ('CHALLENGES' in s, 'DP_TALENTS' in s))
