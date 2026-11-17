# -*- coding: utf-8 -*-
# 任务A应用层: 精英怪 + 重铸UI
s = open('D:/self-project/game/src/template.html', encoding='utf-8').read()

# ===== 1. State =====
old = """  exp: { '033': null, '077': null, '999': null },"""
new = """  exp: { '033': null, '077': null, '999': null },
  elite: null,"""
assert old in s, "state"; s = s.replace(old, new)

# ===== 2. 生成精英 (kill 的 zone++ 后) =====
old = """  S.zone += 1;
  S.hp = S.hpMax = ECON.zoneHP(S.zone);
  if (ECON.isBoss(S.zone)) {
    SFX.bossSpawn();
    addLog(`[遭遇] Boss出现：${ECON.bossName(S.zone)}（第${S.zone}区）。它开始念PPT。`, 'ev-t2');
  }
}"""
new = """  S.zone += 1;
  S.hp = S.hpMax = ECON.zoneHP(S.zone);
  if (!ECON.isBoss(S.zone) && Math.random() < 0.10) {
    // 精英怪: 血量×2~4 金币×2~4 必掉装备
    S.elite = GSYS.rollElite();
    S.hp = S.hp.times(S.elite.hpMult);
    S.hpMax = S.hp.times(1);
    addLog('[遭遇] 精英怪出现！词缀：' + S.elite.affixes.map(a => GSYS.ELITE_AFFIXES.find(x => x.id === a).name).join('·') + '。它看起来很有钱。', 'ev-t2');
  }
  if (ECON.isBoss(S.zone)) {
    SFX.bossSpawn();
    addLog(`[遭遇] Boss出现：${ECON.bossName(S.zone)}（第${S.zone}区）。它开始念PPT。`, 'ev-t2');
  }
}"""
assert old in s, "spawn"; s = s.replace(old, new)

# ===== 3. 精英结算: 金币乘区+掉落+护盾+迅捷 =====
old = """  SFX.kill(); SFX.coin();
  S.gold = S.gold.plus(ECON.zoneGold(S.zone).times(m.goldGain).times(comboMult()));"""
new = """  SFX.kill(); SFX.coin();
  let goldMult = comboMult();
  if (S.elite) {
    goldMult *= S.elite.goldMult;
    S.gold = S.gold.plus(ECON.zoneGold(S.zone).times(goldMult));
    // 精英必掉装备
    const drop = GSYS.rollItem(S.zone, true);
    drop.quality = (S.elite.affixes.length >= 2 && drop.quality === 'yellow') ? 'ancient' : drop.quality;
    drop.gs = GSYS.computeGS(drop);
    const dispE = GSYS.dropDisposition(drop, S.gear[drop.slot] ? S.gear[drop.slot].gs : 0);
    if (dispE.action === 'salvage') S.scrap += dispE.scrap;
    else { S.pendingEquip = { item: drop, at: Date.now() }; SFX.drop(); showPopup('【精英掉落】' + GEARQ[drop.quality].name, ['「' + drop.name + '」 GS ' + drop.gs, '（10秒后自动装备）'], 'ev-t3', { sticky: true, buttons: [{ label: '一键装备', cb: () => { S.pendingEquip = null; equipItem(drop); } }] }); }
    addLog('[精英] 精英怪倒下！掉落「' + drop.name + '」（GS ' + drop.gs + '）', 'ev-t3');
    S.elite = null;
    S.gold = S.gold.minus(ECON.zoneGold(S.zone).times(goldMult).times(m.goldGain).times(0));
  } else {
    S.gold = S.gold.plus(ECON.zoneGold(S.zone).times(m.goldGain).times(goldMult));
  }
  if (false) burst("""
assert old in s, "killgold"; s = s.replace(old, new)
# 清理上一替换遗留的 "if (false) burst(" 行——把它还原成 killFx()
old2 = """  if (false) burst("""
new2 = """  killFx();"""
assert old2 in s, "burst"; s = s.replace(old2, new2)

# ===== 4. 护盾/迅捷效果 =====
old = """  if (hasTalent('t1') && S.hp.div(S.hpMax).toNumber() < 0.15) { effDmg = new D('1e3000'); addFloater('处决！', '#ff3c6c', 24); }"""
new = """  if (S.elite && S.elite.affixes.includes('shield') && S.hp.div(S.hpMax).toNumber() > 0.5) effDmg = effDmg.times(0.5);
  if (hasTalent('t1') && S.hp.div(S.hpMax).toNumber() < 0.15) { effDmg = new D('1e3000'); addFloater('处决！', '#ff3c6c', 24); }"""
assert old in s, "shield"; s = s.replace(old, new)

old = """function mults() {
  const m = ECON.computeMults(S.affixes, AFFIX, currentBoss(), S.buffs, Math.pow(C.shopTyrannyMult, S.shop.tyr) * Math.pow(1.05, S.achievements.length), Date.now(), { spdLv: S.spd, gearEffects: gearEffects() });
  if (S.glitch.mult > 0) m.allDmg *= S.glitch.mult;
  if (S.dpShop.might > 0) m.allDmg *= Math.pow(10, S.dpShop.might);
  if (S.dpShop.haste > 0) m.atkSpeed *= Math.pow(1.5, S.dpShop.haste);
  return m;
}"""
new = """function mults() {
  const m = ECON.computeMults(S.affixes, AFFIX, currentBoss(), S.buffs, Math.pow(C.shopTyrannyMult, S.shop.tyr) * Math.pow(1.05, S.achievements.length), Date.now(), { spdLv: S.spd, gearEffects: gearEffects() });
  if (S.glitch.mult > 0) m.allDmg *= S.glitch.mult;
  if (S.dpShop.might > 0) m.allDmg *= Math.pow(10, S.dpShop.might);
  if (S.dpShop.haste > 0) m.atkSpeed *= Math.pow(1.5, S.dpShop.haste);
  if (S.elite && S.elite.affixes.includes('swift')) m.atkSpeed *= 0.8;
  return m;
}"""
assert old in s, "swift"; s = s.replace(old, new)

# ===== 5. 重铸按钮 (装备栏每件) + 处理器 =====
old = """    const aff = it.affixes.map(a => (a.kind === 'special' ? '★' : '×') + ECON.fmt(new D(a.mult)) + (a.key === 'sp_glitch' && S.glitch.mult > 0 ? '(今日实为×' + S.glitch.mult + ')' : '')).join(' ');
    ghtml += `<div class="chip" style="border-color:${qc};color:${qc};display:block;margin:3px 0">${slotNames[slot]} ${it.name} <small>[GS ${it.gs}${enhLv ? ' · 强化+' + enhLv : ''}]</small><br><small>${aff}</small></div>`;"""
new = """    const aff = it.affixes.map(a => (a.kind === 'special' ? '★' : '×') + ECON.fmt(new D(a.mult)) + (a.key === 'sp_glitch' && S.glitch.mult > 0 ? '(今日实为×' + S.glitch.mult + ')' : '')).join(' ');
    const rCost = 500 + it.ilvl * 2;
    ghtml += `<div class="chip" style="border-color:${qc};color:${qc};display:block;margin:3px 0">${slotNames[slot]} ${it.name} <small>[GS ${it.gs}${enhLv ? ' · 强化+' + enhLv : ''}]</small><br><small>${aff}</small><br><button data-reforge="${slot}" style="font-size:10px;padding:2px 8px;margin-top:3px">重铸 (${rCost}屑) GS变赌</button></div>`;"""
assert old in s, "reforgebtn"; s = s.replace(old, new)

# ===== 6. 重铸事件委托 + 处理器 =====
old = """document.getElementById('objList').addEventListener('click', e => {
  const b = e.target.closest('button[data-obj]');
  if (b) claimObjective(Number(b.dataset.obj));
});"""
new = """document.getElementById('objList').addEventListener('click', e => {
  const b = e.target.closest('button[data-obj]');
  if (b) claimObjective(Number(b.dataset.obj));
});
// 装备重铸
function doReforge(slot) {
  const it = S.gear[slot];
  if (!it) return;
  const cost = 500 + it.ilvl * 2;
  if (S.scrap < cost) { bsSay('重铸要碎屑。' + cost + ' 屑。别拿眼泪糊弄我。'); return; }
  S.scrap -= cost;
  const oldGS = it.gs;
  const ni = GSYS.reforge(it);
  S.gear[slot] = ni;
  const delta = ni.gs - oldGS;
  bsSay(delta > 0 ? '重铸出炉，GS +' + delta + '。矿石都说这次烧得好。' : delta < 0 ? '重铸出炉，GS ' + delta + '。矿石产地问题，已反映。' : '重铸出炉，一模一样。玄学。');
  addLog(`[重铸] ${ni.name} GS ${oldGS} → ${ni.gs}（${delta >= 0 ? '+' : ''}${delta}）`, delta > 0 ? 'ev-t3' : '');
  save();
}
document.getElementById('gearList').addEventListener('click', e => {
  const b = e.target.closest('button[data-reforge]');
  if (b) doReforge(b.dataset.reforge);
});"""
assert old in s, "reforgeevt"; s = s.replace(old, new)

open('D:/self-project/game/src/template.html', 'w', encoding='utf-8').write(s)
print("任务A应用层完成（写盘核验: elite=%s reforge=%s)" % ('S.elite' in s, 'doReforge' in s))
