# -*- coding: utf-8 -*-
# 任务3补丁第二部分: refreshUI 远征区渲染
s = open('D:/self-project/game/src/template.html', encoding='utf-8').read()

old = """  // 目标列表：显示前3个未领取的"""
new = """  // 远征队渲染
  const expArea = document.getElementById('expArea');
  if (expArea) {
    let ehtml = '';
    for (const sd of Object.keys(S.exp)) {
      const e = S.exp[sd];
      if (e) {
        const remain = Math.max(0, Math.ceil((e.startAt + e.dur - Date.now()) / 1000));
        const mm = Math.floor(remain / 60), ss = remain % 60;
        ehtml += `<div><span style="color:var(--gold)">${sd}号</span> 远征中：${EXP_PLACES[e.place].name} <small>剩余 ${mm}分${ss < 10 ? '0' + ss : ss}秒</small> <button data-exp="${sd}|recall" style="font-size:10px;padding:2px 8px" ${remain > 0 ? 'disabled' : ''}>召回结算</button></div>`;
      } else {
        ehtml += `<div><span style="color:var(--parchment)">${sd}号</span> 待命：` +
          Object.keys(EXP_PLACES).map(p => `<button data-exp="${sd}|${p}" style="font-size:10px;padding:2px 8px">${EXP_PLACES[p].name}</button>`).join(' ') + `</div>`;
      }
    }
    expArea.innerHTML = ehtml;
  }
  // 目标列表：显示前3个未领取的"""
assert old in s, "render"; s = s.replace(old, new)
open('D:/self-project/game/src/template.html', 'w', encoding='utf-8').write(s)
print("远征渲染完成")
