/* 深渊摸鱼录 - 装备系统算法类 (GEAR)
 * 纯逻辑层：无 DOM 依赖。对齐 步骤1-装备与槽位强化体系设计.md + config/装备系统配置.json
 * 核心职责：装备掉落(rollItem) / 装备评分(computeGS) / 自动分解(salvageValue) / 槽位强化(enhanceRoll)
 * 墙力安全：词条数值锚定 ilvl，槽位强化封顶 ×2.5，无无界指数源。
 */
(function (root) {
  'use strict';

  function createGearSystem(cfg, econ) {
    const C = cfg;
    const Q = {}; C.quality.forEach(q => Q[q.id] = q);
    const QLIST = C.quality.map(q => q.id);
    const SP = {}; C.specialAffixes.forEach(a => SP[a.id] = a);
    const BASIC = C.basicAffixes;

    // ---------- 品质与掉落 ----------
    function rollQuality(isBoss, rng) {
      const r = (rng || Math.random)() * 100;
      let acc = 0;
      for (const q of C.quality) {
        acc += isBoss ? q.bossWeight : q.dropWeight;
        if (r < acc) return q.id;
      }
      return 'white';
    }
    function rollSlot(rng) {
      const keys = Object.keys(C.slots);
      return keys[Math.floor((rng || Math.random)() * keys.length)];
    }
    function pickBasicAffix(slot, exclude, rng) {
      const keys = Object.keys(BASIC);
      let total = 0;
      const w = {};
      for (const k of keys) {
        if (exclude.includes(k)) continue;
        w[k] = BASIC[k].slotWeights[slot] || 1;
        total += w[k];
      }
      if (total <= 0) return 'atk';
      let r = (rng || Math.random)() * total;
      for (const k of keys) { if (exclude.includes(k)) continue; r -= w[k]; if (r <= 0) return k; }
      return keys[0];
    }
    function pickSpecialAffix(slot, qualityId, exclude, rng) {
      const qi = QLIST.indexOf(qualityId);
      const pool = C.specialAffixes.filter(a => {
        if (exclude.includes(a.id)) return false;
        const minQi = QLIST.indexOf(a.minQuality);
        if (qi < minQi) return false;
        return (a.slotWeights[slot] || 0) > 0;
      });
      if (pool.length === 0) return null;
      let total = 0;
      for (const a of pool) total += a.slotWeights[slot];
      let r = (rng || Math.random)() * total;
      for (const a of pool) { r -= a.slotWeights[slot]; if (r <= 0) return a.id; }
      return pool[0].id;
    }

    // ---------- 装备生成 ----------
    function genName(qualityId, slot, rng) {
      const A = C.nameGen.adj[qualityId], N = C.nameGen.noun[slot], S = C.nameGen.suffix;
      const pick = arr => arr[Math.floor((rng || Math.random)() * arr.length)];
      let name = pick(A) + pick(N);
      if ((rng || Math.random)() < 0.5) name += pick(S);
      return name;
    }

    // rollItem: 掉落一件装备
    // ilvl: 掉落区域数; isBoss: Boss掉落(品质更优 & ilvl+5)
    function rollItem(ilvl, isBoss, rng) {
      rng = rng || Math.random;
      const qid = rollQuality(isBoss, rng);
      const q = Q[qid];
      const slot = rollSlot(rng);
      const finalIlvl = ilvl + (isBoss ? 5 : 0);
      const [cMin, cMax] = q.coeff;
      const c = cMin + rng() * (cMax - cMin);
      const P = c * (1 + finalIlvl / 10);          // 主词条倍率
      const [nMin, nMax] = q.affixCount;
      const nAffix = nMin + Math.floor(rng() * (nMax - nMin + 1));

      const usedBasic = [], usedSpecial = [];
      const affixes = [];
      // 主词条（基础池，槽位权重）
      const pKey = pickBasicAffix(slot, usedBasic, rng);
      usedBasic.push(pKey);
      affixes.push({ key: pKey, kind: 'basic', mult: P, effects: [{ type: 'always', zone: BASIC[pKey].zone, mult: P }] });
      // 副词条
      const specialQuota = { white: 0, blue: 0, yellow: 0, ancient: 1, primal: 1, chaos: 2 }[qid];
      let specials = 0;
      for (let i = 1; i < nAffix; i++) {
        if (specials < specialQuota && rng() < 0.85) {
          const spId = pickSpecialAffix(slot, qid, usedSpecial, rng);
          if (spId) {
            usedSpecial.push(spId);
            const sp = SP[spId];
            specials++;
            affixes.push({ key: spId, kind: 'special', mult: sp.mult, text: sp.text, effects: sp.effects, name: sp.name });
            continue;
          }
        }
        const key = pickBasicAffix(slot, usedBasic, rng);
        usedBasic.push(key);
        const subMult = Math.pow(P, 0.6);
        affixes.push({ key, kind: 'basic', mult: subMult, effects: [{ type: 'always', zone: BASIC[key].zone, mult: subMult }] });
      }
      // 暗金以下若配额未用不补；混沌必带2特效已在循环保证（nAffix=6, quota=2, 85%倾向）
      const item = {
        id: 'it_' + Date.now().toString(36) + Math.floor(rng() * 1e6).toString(36),
        slot, quality: qid, ilvl: finalIlvl,
        name: genName(qid, slot, rng),
        affixes,
        power: P,
        cosmetic: affixes.some(a => SP[a.key] && SP[a.key].cosmetic) ? 'leek' : null,
      };
      item.gs = computeGS(item);
      return item;
    }

    // ---------- 装备评分 ----------
    // GS = ⌊ ilvl × Q × (1 + Σ log10(词条倍率)×100) ⌋ —— 对数压乘法爆炸，永不溢出
    function computeGS(item) {
      const q = Q[item.quality];
      let sum = 0;
      for (const a of item.affixes) sum += Math.log10(Math.max(1, a.mult)) * 100;
      return Math.floor(item.ilvl * q.q * (1 + sum));
    }

    // ---------- 自动分解 ----------
    function salvageValue(item) { return C.salvage.byQuality[item.quality]; }
    // 掉落处置：GS 对比同槽已装备 → 分解 or 提示换装
    function dropDisposition(item, equippedGS) {
      if (item.gs <= equippedGS) return { action: 'salvage', scrap: salvageValue(item) };
      return { action: 'equip_offer', scrap: 0 };
    }

    // ---------- 槽位强化 ----------
    function slotMult(lv) { return 1 + C.enhance.slotMultPerLevel * Math.min(lv, C.enhance.maxLevel); }
    function scrapCost(lv) { return 9 * Math.ceil(3 * Math.pow(1.9, lv)); }
    // 强化金币成本锚定非Boss公式(passiveGold)：Boss区金币×24~273巨额乘区，
    // 若撞上Boss区会导致成本脉冲式暴涨（实测区70成本从163T暴涨到44AA）
    function goldCost(lv, passiveGoldFn) { return passiveGoldFn(10 + lv * 6); }
    // enhanceRoll: 强化判定（85%成功/连败2次保底/10%暴击+2级/失败不降级）
    function enhanceRoll(lv, pity, rng) {
      rng = rng || Math.random;
      if (lv >= C.enhance.maxLevel) return { success: false, crit: false, newLv: lv, pity: 0, full: true };
      let success = rng() < C.enhance.successRate;
      if (pity >= C.enhance.pityAfterFails) success = true;   // 保底
      let crit = false;
      let newLv = lv, newPity = pity;
      if (success) {
        crit = rng() < C.enhance.critChance;
        newLv = Math.min(C.enhance.maxLevel, lv + (crit ? 2 : 1));
        newPity = 0;
      } else {
        newPity = pity + 1;  // 失败不降级，只费材料
      }
      return { success, crit, newLv, pity: newPity };
    }

    // ---------- 词条效果归一化（供 computeMults / 应用层直接消费） ----------
    // equipped: {weapon: item|null, armor: item|null, trinket: item|null}
    // enhLv: {weapon: lv, armor: lv, trinket: lv}
    // 返回 effects 数组：基础词条乘 slotMult，特效词条原样
    function itemEffects(equipped, enhLv) {
      const out = [];
      for (const slotKey of Object.keys(C.slots)) {
        const item = equipped[slotKey];
        if (!item) continue;
        const sm = slotMult((enhLv || {})[slotKey] || 0);
        for (const a of item.affixes) {
          if (a.kind === 'basic') {
            for (const e of a.effects) out.push({ type: 'always', zone: e.zone, mult: e.mult * sm });
          } else {
            for (const e of a.effects) out.push(e);
          }
        }
      }
      return out;
    }

    // ---------- 重铸: 保留品质/槽位/ilvl/特效词条, 重摇基础词条选择与数值 ----------
    function reforge(item, rng) {
      rng = rng || Math.random;
      const q = Q[item.quality];
      const [cMin, cMax] = q.coeff;
      const c = cMin + rng() * (cMax - cMin);
      const P = c * (1 + item.ilvl / 10);
      const keepSpecial = item.affixes.filter(a => a.kind === 'special');
      const usedBasic = [];
      const newAffixes = [];
      // 主词条
      const pKey = pickBasicAffix(item.slot, usedBasic, rng);
      usedBasic.push(pKey);
      newAffixes.push({ key: pKey, kind: 'basic', mult: P, effects: [{ type: 'always', zone: BASIC[pKey].zone, mult: P }] });
      // 副词条数量 = 原基础词条数(不含特效) - 1 … 按品质档重定
      const basicTotal = item.affixes.length - keepSpecial.length;
      for (let i = 1; i < basicTotal; i++) {
        const key = pickBasicAffix(item.slot, usedBasic, rng);
        usedBasic.push(key);
        const subMult = Math.pow(P, 0.6);
        newAffixes.push({ key, kind: 'basic', mult: subMult, effects: [{ type: 'always', zone: BASIC[key].zone, mult: subMult }] });
      }
      // 特效词条回填
      for (const sp of keepSpecial) newAffixes.push(sp);
      const ni = Object.assign({}, item, { affixes: newAffixes, power: P });
      ni.gs = computeGS(ni);
      return ni;
    }
    const ELITE_AFFIXES = [
      { id: 'tough',  name: '坚韧', desc: '血量 ×2' },
      { id: 'greedy', name: '贪婪', desc: '金币 ×2' },
      { id: 'swift',  name: '迅捷', desc: '你的攻速 -20%' },
      { id: 'shield', name: '护盾', desc: '血量高于50%时受伤减半' },
    ];
    function rollElite(rng) {
      rng = rng || Math.random;
      const pool = ELITE_AFFIXES.slice();
      const n = 1 + (rng() < 0.35 ? 1 : 0);
      const affixes = [];
      for (let i = 0; i < n && pool.length; i++) {
        const k = Math.floor(rng() * pool.length);
        affixes.push(pool.splice(k, 1)[0].id);
      }
      return { affixes, hpMult: affixes.includes('tough') ? 4 : 2, goldMult: affixes.includes('greedy') ? 4 : 2 };
    }
    return { rollItem, computeGS, salvageValue, dropDisposition, slotMult, scrapCost, goldCost, enhanceRoll, itemEffects, rollQuality, QUALITY: Q, SPECIALS: SP, reforge, ELITE_AFFIXES, rollElite };
  }

  const api = { createGearSystem };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.GEAR = api;
})(typeof window !== 'undefined' ? window : globalThis);
