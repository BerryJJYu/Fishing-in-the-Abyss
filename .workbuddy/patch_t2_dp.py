# -*- coding: utf-8 -*-
# 任务2: 神格点/飞升二级货币（区80 解锁，二级转生）
s = open('D:/self-project/game/src/template.html', encoding='utf-8').read()

# ===== State =====
old = """  glitch: { date: '', mult: 0 },"""
new = """  glitch: { date: '', mult: 0 },
  dp: 0, dpShop: { might: 0, haste: 0, touch: 0 },"""
assert old in s, "state"; s = s.replace(old, new)

# ===== mults 神格乘区 =====
old = """function mults() {
  const m = ECON.computeMults(S.affixes, AFFIX, currentBoss(), S.buffs, Math.pow(C.shopTyrannyMult, S.shop.tyr) * Math.pow(1.05, S.achievements.length), Date.now(), { spdLv: S.spd, gearEffects: gearEffects() });
  if (S.glitch.mult > 0) m.allDmg *= S.glitch.mult;
  return m;
}"""
new = """function mults() {
  const m = ECON.computeMults(S.affixes, AFFIX, currentBoss(), S.buffs, Math.pow(C.shopTyrannyMult, S.shop.tyr) * Math.pow(1.05, S.achievements.length), Date.now(), { spdLv: S.spd, gearEffects: gearEffects() });
  if (S.glitch.mult > 0) m.allDmg *= S.glitch.mult;
  if (S.dpShop.might > 0) m.allDmg *= Math.pow(10, S.dpShop.might);
  if (S.dpShop.haste > 0) m.atkSpeed *= Math.pow(1.5, S.dpShop.haste);
  return m;
}"""
assert old in s, "mults"; s = s.replace(old, new)

# ===== 飞升仪式按钮（zone>=80） =====
old = """  <button id="prestigeBtn" class="hidden">【掀桌子重开时间线】<br>献祭一切 → 黑魂工资 +<span id="uiSoulsGain">5</span> 点</button>"""
new = """  <button id="prestigeBtn" class="hidden">【掀桌子重开时间线】<br>献祭一切 → 黑魂工资 +<span id="uiSoulsGain">5</span> 点</button>
  <button id="ascendBtn" class="hidden" style="background:linear-gradient(180deg,#1a2a4a,#0a1428);border-color:#6c9cff;color:#9cc8ff;">【飞升·面见摸鱼之神】<br>区80解锁 → 神格点 +<span id="uiDpGain">1</span> · 保留装备与天赋</button>"""
assert old in s, "btn"; s = s.replace(old, new)

# ===== 事件收益吃神触 =====
old = """  const m = mults();
  const mad = Math.pow(C.shopMadnessMult, S.shop.mad);
  const title = `【${EVENTS.tiers.find(t => t.id === ev.tier).label}】"""
new = """  const m = mults();
  const mad = Math.pow(C.shopMadnessMult, S.shop.mad) * Math.pow(3, S.dpShop.touch);
  const title = `【${EVENTS.tiers.find(t => t.id === ev.tier).label}】"""
assert old in s, "touch"; s = s.replace(old, new)

# ===== 飞升处理器 + 神格商店 =====
old = """// ===== 成就墙 ====="""
new = """// ===== 飞升与神格（区80 解锁的二级转生） =====
document.getElementById('ascendBtn').onclick = () => {
  const gain = Math.floor(S.maxZone / 80);
  if (gain <= 0) return;
  S.dp += gain;
  S.timeline.unshift({ n: '飞升' + (S.timeline.filter(t => String(t.n).indexOf('飞升') === 0).length + 1), maxZone: S.maxZone, souls: gain, title: '面见摸鱼之神（它在看剧）', date: new Date().toLocaleDateString() });
  showPopup('【飞升】', [
    '你推开神座摸鱼间的门。神明正窝在沙发上看剧，头也没回：',
    '"哦，来了啊。自己拿工牌上墙。咖啡在那边，自己冲。"',
    '—— 获得 神格点 ×' + gain + '（累计 ' + S.dp + '）。装备、强化、天赋、商店全部保留。',
  ], 'ev-t3');
  SFX.organ();
  S.zone = 1; S.level = 0; S.gold = new D(0);
  S.hp = S.hpMax = ECON.zoneHP(S.zone);
  S.affixes = []; S.buffs = []; S.combo = 0; S.maxZone = 1; S._brk = 0;
  save();
};
const DP_SHOP = [
  { id: 'might', name: '神威·全局 ×10', costLv: 1 },
  { id: 'haste', name: '神速·攻速 ×1.5', costLv: 1 },
  { id: 'touch', name: '神触·事件 ×3', costLv: 1 },
];
function buyDp(id) {
  const lv = S.dpShop[id];
  const cost = lv + 1;
  if (S.dp < cost) return;
  S.dp -= cost;
  S.dpShop[id]++;
  save();
}
document.getElementById('dpMight').onclick = () => buyDp('might');
document.getElementById('dpHaste').onclick = () => buyDp('haste');
document.getElementById('dpTouch').onclick = () => buyDp('touch');

// ===== 成就墙 ====="""
assert old in s, "ascend"; s = s.replace(old, new)

# ===== HTML: 神格商店按钮 =====
old = """    <div id="bsMsg" style="font-size:11px;color:var(--parchment);margin-top:6px;min-height:16px">铁匠：想强化就说话，别拿眼睛锯我。</div>
  </div>
</div>"""
new = """    <div id="bsMsg" style="font-size:11px;color:var(--parchment);margin-top:6px;min-height:16px">铁匠：想强化就说话，别拿眼睛锯我。</div>
  </div>
  <div class="box flex1" id="dpBox">
    <div class="boxtitle">神 格 商 店（神格点：<span id="uiDp" style="color:var(--gold)">0</span> · 飞升区80解锁）</div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;">
      <button id="dpMight">神威 全局×10 (<span id="dpMightCost">1</span>) Lv.<span id="dpMightLv">0</span></button>
      <button id="dpHaste">神速 攻速×1.5 (<span id="dpHasteCost">1</span>) Lv.<span id="dpHasteLv">0</span></button>
      <button id="dpTouch">神触 事件×3 (<span id="dpTouchCost">1</span>) Lv.<span id="dpTouchLv">0</span></button>
    </div>
    <div style="font-size:10px;color:var(--parchment-dim);margin-top:4px">飞升保留：装备/强化/天赋/商店/成就。清空：区域/等级/金币。</div>
  </div>
</div>"""
assert old in s, "dphtml"; s = s.replace(old, new)

# ===== refreshUI: 飞升按钮与神格商店状态 =====
old = """  $('prestigeBtn').classList.toggle('hidden', S.zone < C.prestigeReqZone);"""
new = """  $('prestigeBtn').classList.toggle('hidden', S.zone < C.prestigeReqZone);
  // 飞升与神格
  const dpGain = Math.floor(S.maxZone / 80);
  $('uiDpGain').textContent = dpGain;
  document.getElementById('ascendBtn').classList.toggle('hidden', S.maxZone < 80);
  document.getElementById('dpBox').style.display = (S.dp > 0 || S.maxZone >= 80) ? '' : 'none';
  $('uiDp').textContent = S.dp;
  for (const d of DP_SHOP) {
    const lv = S.dpShop[d.id], cost = lv + 1;
    $(d.id + 'Lv').textContent = lv; $(d.id + 'Cost').textContent = cost;
    $(d.id).disabled = S.dp < cost;
  }"""
assert old in s, "refresh"; s = s.replace(old, new)

# ===== save v8 =====
old = """    bossDex: S.bossDex, glitch: S.glitch,
    buffs: S.buffs, lastSave: Date.now(),"""
new = """    bossDex: S.bossDex, glitch: S.glitch, dp: S.dp, dpShop: S.dpShop,
    buffs: S.buffs, lastSave: Date.now(),"""
assert old in s, "save"; s = s.replace(old, new)
old = """            if (d.v >= 7) { S.bossDex = d.bossDex || {}; S.glitch = d.glitch || S.glitch; }"""
new = """            if (d.v >= 7) { S.bossDex = d.bossDex || {}; S.glitch = d.glitch || S.glitch; }
            if (d.v >= 8) { S.dp = d.dp || 0; S.dpShop = d.dpShop || { might: 0, haste: 0, touch: 0 }; }"""
assert old in s, "load"; s = s.replace(old, new)

open('D:/self-project/game/src/template.html', 'w', encoding='utf-8').write(s)
print("任务2补丁完成（写盘核验: dp=%s ascendBtn=%s)" % ('S.dp' in s, 'ascendBtn' in s))
