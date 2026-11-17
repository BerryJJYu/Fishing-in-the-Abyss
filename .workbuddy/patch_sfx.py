# -*- coding: utf-8 -*-
# 音效挂接补丁 v7（从文件读取模板，避免 heredoc 嵌套问题）
s = open('D:/self-project/game/src/template.html', encoding='utf-8').read()

edits = [
  ("""  const mag = effDmg.exponent;
  let color = '#e8e0d0', size = 14;""",
   """  const mag = effDmg.exponent;
  SFX.hit();
  if (crit) SFX.crit();
  if (mag >= 6) { const bT = Math.floor(mag / 6); if ((S._brk || 0) < bT) { S._brk = bT; SFX.breakTier(bT); } }
  let color = '#e8e0d0', size = 14;"""),
  ("""  S.gold = S.gold.plus(ECON.zoneGold(S.zone).times(m.goldGain).times(comboMult()));
  killFx();""",
   """  SFX.kill(); SFX.coin();
  S.gold = S.gold.plus(ECON.zoneGold(S.zone).times(m.goldGain).times(comboMult()));
  killFx();"""),
  ("""  if (ECON.isBoss(S.zone)) {
    dropGear();
    addLog(`[战斗] ${ECON.bossName(S.zone)} 被物理超度。临终遗言："我本可以直接躺平的……"`, '');""",
   """  if (ECON.isBoss(S.zone)) {
    SFX.bossKill();
    dropGear();
    addLog(`[战斗] ${ECON.bossName(S.zone)} 被物理超度。临终遗言："我本可以直接躺平的……"`, '');"""),
  ("""  if (ECON.isBoss(S.zone)) {
    addLog(`[遭遇] Boss出现：${ECON.bossName(S.zone)}（第${S.zone}区）。它开始念PPT。`, 'ev-t2');
  }""",
   """  if (ECON.isBoss(S.zone)) {
    SFX.bossSpawn();
    addLog(`[遭遇] Boss出现：${ECON.bossName(S.zone)}（第${S.zone}区）。它开始念PPT。`, 'ev-t2');
  }"""),
  ("""  S.pendingEquip = { item, at: Date.now() };
  const qName = GEARQ[item.quality].name;""",
   """  S.pendingEquip = { item, at: Date.now() };
  SFX.drop();
  const qName = GEARQ[item.quality].name;"""),
  ("""  if (old) S.scrap += GSYS.salvageValue(old);
  S.gear[item.slot] = item;
}""",
   """  if (old) S.scrap += GSYS.salvageValue(old);
  S.gear[item.slot] = item;
  SFX.equip();
}"""),
  ("""  if (r.success) {
    S.enh[slot] = r.newLv;
    const txt = r.crit ? pick1(BS_TEXTS.crit)""",
   """  if (r.success) {
    S.enh[slot] = r.newLv;
    SFX.enhance(true, r.crit);
    const txt = r.crit ? pick1(BS_TEXTS.crit)"""),
  ("""  } else {
    bsSay(pick1(BS_TEXTS.fail));""",
   """  } else {
    SFX.enhance(false, false);
    bsSay(pick1(BS_TEXTS.fail));"""),
  ("""    S.buffs.push({ kind: 'global', mult: p.mult, until: now + p.dur * 1000 });
    addLog('[技能] 精神攻击发动""",
   """    S.buffs.push({ kind: 'global', mult: p.mult, until: now + p.dur * 1000 });
    SFX.skill('fury');
    addLog('[技能] 精神攻击发动"""),
  ("""    addFloater('掀桌! ' + ECON.fmt(dmg), '#ff3c6c', 26);
    shake = 12;""",
   """    addFloater('掀桌! ' + ECON.fmt(dmg), '#ff3c6c', 26);
    SFX.skill('slam');
    shake = 12;"""),
  ("""    const g = ECON.zoneGold(S.zone).times(skillParamsOf('tax').goldSec).times(m.goldGain);
    S.gold = S.gold.plus(g);""",
   """    const g = ECON.zoneGold(S.zone).times(skillParamsOf('tax').goldSec).times(m.goldGain);
    SFX.skill('tax');
    S.gold = S.gold.plus(g);"""),
  ("""  S.tauntUntil = now + 6000;
  S.tauntCdUntil = now + 12000 - (S.stats.tauntCdReduce || 0) * 1000;
  S.stats.taunts++;""",
   """  S.tauntUntil = now + 6000;
  S.tauntCdUntil = now + 12000 - (S.stats.tauntCdReduce || 0) * 1000;
  S.stats.taunts++;
  SFX.taunt();"""),
  ("""  addLog(body.join(' '), 'ev-t' + ev.tier.slice(1));
  // 选项分支：弹窗二选一""",
   """  SFX.bell();
  addLog(body.join(' '), 'ev-t' + ev.tier.slice(1));
  // 选项分支：弹窗二选一"""),
  ("""    const win = Math.random() < c.chance;
    outcome = applyEventEffect(win ? c.win : c.lose, win ? '赌赢' : '赌输');""",
   """    const win = Math.random() < c.chance;
    (win ? SFX.gambleWin() : SFX.gambleLose());
    outcome = applyEventEffect(win ? c.win : c.lose, win ? '赌赢' : '赌输');"""),
  ("""  document.getElementById('ceremony').classList.remove('hidden');
  softReset();
  save();
};""",
   """  SFX.organ();
  document.getElementById('ceremony').classList.remove('hidden');
  softReset();
  save();
};"""),
  ("""  showPopup('【目标达成】', ['「' + o.text + '」已完成'""",
   """  SFX.claim();
  showPopup('【目标达成】', ['「' + o.text + '」已完成'"""),
  ("""      showPopup('🏆 成就解锁！', ['「' + a.name + '」—— ' + a.desc""",
   """      SFX.chime();
      showPopup('🏆 成就解锁！', ['「' + a.name + '」—— ' + a.desc"""),
]
for i, (old, new) in enumerate(edits):
    assert old in s, "锚点%d缺失: %s" % (i, old[:50])
    s = s.replace(old, new)

old = """  S.combo = 0; S.lastKillAt = 0;
  S.hp = S.hpMax = ECON.zoneHP(S.zone); S.stunUntil = 0;
}"""
new = """  S.combo = 0; S.lastKillAt = 0;
  S._brk = 0;
  S.hp = S.hpMax = ECON.zoneHP(S.zone); S.stunUntil = 0;
}"""
assert old in s, "brk"
s = s.replace(old, new)
open('D:/self-project/game/src/template.html', 'w', encoding='utf-8').write(s)
print("音效挂接完成（%d 处）" % (len(edits) + 1))
