# -*- coding: utf-8 -*-
# 任务3: 离线远征队（主动派遣）
s = open('D:/self-project/game/src/template.html', encoding='utf-8').read()

# ===== 1. State =====
old = """  dp: 0, dpShop: { might: 0, haste: 0, touch: 0 },"""
new = """  dp: 0, dpShop: { might: 0, haste: 0, touch: 0 },
  exp: { '033': null, '077': null, '999': null },"""
assert old in s, "state"; s = s.replace(old, new)

# ===== 2. HTML: 远征队面板（panel4） =====
old = """    <div style="font-size:10px;color:var(--parchment-dim);margin-top:4px">飞升保留：装备/强化/天赋/商店/成就。清空：区域/等级/金币。</div>
  </div>
</div>"""
new = """    <div style="font-size:10px;color:var(--parchment-dim);margin-top:4px">飞升保留：装备/强化/天赋/商店/成就。清空：区域/等级/金币。</div>
  </div>
</div>
<div id="panel4" style="display:flex; gap:8px; margin-top:8px; flex-wrap:wrap;">
  <div class="box flex1">
    <div class="boxtitle">骷 髅 远 征 队（主动派遣 · 5 分钟 · 派出去的兵不会摸鱼，它们已经在摸了）</div>
    <div id="expArea" style="font-size:11px;line-height:1.8"></div>
  </div>
</div>"""
assert old in s, "html"; s = s.replace(old, new)

# ===== 3. 远征逻辑 =====
old = """// ===== 成就墙 ====="""
new = """// ===== 骷髅远征队（主动派遣） =====
const EXP_SOLDIERS = { '033': '工号033 · 冒险家（调薪被拒型）', '077': '工号077 · 财迷（会吞差价型）', '999': '工号999 · 老油条（摸鱼资深型）' };
const EXP_PLACES = {
  mine:  { name: '深渊矿场', desc: '稳定收益' },
  tomb:  { name: '腐朽墓穴', desc: '挖装备碎屑' },
  angel: { name: '天使之门', desc: '50%大奖 / 50%空手' },
};
const EXP_DUR_MS = 5 * 60 * 1000;   // 原型 5 分钟（正式版 30 分钟）
function dispatchExp(soldier, place) {
  if (S.exp[soldier]) return;
  S.exp[soldier] = { place, startAt: Date.now(), dur: EXP_DUR_MS };
  addLog('[远征] ' + soldier + ' 号骷髅兵出发前往' + EXP_PLACES[place].name + '。它敬了个礼，骨头散了半边。', 'ev-t2');
  save();
}
function settleExp(soldier) {
  const e = S.exp[soldier];
  if (!e) return;
  const m = mults();
  const pl = e.place;
  let msg = '', rewardTxt = '';
  if (pl === 'mine') {
    const g = ECON.passiveGold(S.zone).times(50).times(m.goldGain);
    S.gold = S.gold.plus(g);
    msg = soldier + ' 号从矿场回来，交出 ' + ECON.fmt(g) + ' 金币。工牌上多了三个爪印。';
    rewardTxt = ECON.fmt(g) + ' 金币';
  } else if (pl === 'tomb') {
    const sc = 10 + Math.floor(S.zone * 2);
    S.scrap += sc;
    msg = soldier + ' 号从墓穴刨出 ' + sc + ' 碎屑。它坚持认为其中有几块是文物，已被驳回。';
    rewardTxt = sc + ' 碎屑';
  } else {
    if (Math.random() < 0.5) {
      const g = ECON.zoneGold(S.zone).times(120).times(m.goldGain);
      S.gold = S.gold.plus(g);
      msg = soldier + ' 号被天使客服拉住推销了三小时，竟然带回了 ' + ECON.fmt(g) + ' 金币的和解金。';
      rewardTxt = ECON.fmt(g) + ' 金币（大奖）';
      SFX.gambleWin();
    } else {
      msg = soldier + ' 号空手而归。天使说："亲亲，这边建议您下次再来哦～"';
      rewardTxt = '什么都没有。纯纯的陪伴。';
      SFX.gambleLose();
    }
  }
  S.exp[soldier] = null;
  SFX.claim();
  showPopup('【远征队归来】', ['骷髅兵 ' + soldier + ' 号已完成派遣。', rewardTxt, msg], 'ev-t3');
  addLog('[远征归来] ' + msg, 'ev-t3');
  save();
}
document.getElementById('expArea').addEventListener('click', e => {
  const b = e.target.closest('button[data-exp]');
  if (!b) return;
  const [soldier, place] = b.dataset.exp.split('|');
  if (place === 'recall') settleExp(soldier);
  else dispatchExp(soldier, place);
});

// ===== 成就墙 ====="""
assert old in s, "exp"; s = s.replace(old, new)

# ===== 4. tick 到期收货 =====
old = """  expeditionTimer += TICK;
  if (hasTalent('t4') && expeditionTimer >= 60) {"""
new = """  for (const sd of Object.keys(S.exp)) {
    const e = S.exp[sd];
    if (e && Date.now() - e.startAt >= e.dur) settleExp(sd);
  }
  expeditionTimer += TICK;
  if (hasTalent('t4') && expeditionTimer >= 60) {"""
assert old in s, "tick"; s = s.replace(old, new)

# ===== 5. save v8 加字段 =====
old = """    bossDex: S.bossDex, glitch: S.glitch, dp: S.dp, dpShop: S.dpShop,
    buffs: S.buffs, lastSave: Date.now(),"""
new = """    bossDex: S.bossDex, glitch: S.glitch, dp: S.dp, dpShop: S.dpShop,
    exp: S.exp,
    buffs: S.buffs, lastSave: Date.now(),"""
assert old in s, "save"; s = s.replace(old, new)
old = """            if (d.v >= 8) { S.dp = d.dp || 0; S.dpShop = d.dpShop || { might: 0, haste: 0, touch: 0 }; }"""
new = """            if (d.v >= 8) { S.dp = d.dp || 0; S.dpShop = d.dpShop || { might: 0, haste: 0, touch: 0 }; S.exp = d.exp || S.exp; }"""
assert old in s, "load"; s = s.replace(old, new)

open('D:/self-project/game/src/template.html', 'w', encoding='utf-8').write(s)
print("任务3补丁完成（写盘核验: exp=%s)" % ('dispatchExp' in s))
