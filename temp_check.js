
// ───────────────────────────────────────────
// SIDEBAR TOGGLE (mobile + desktop collapse)
// ───────────────────────────────────────────
const app = document.getElementById(\'app\');
const collapseBtn = document.getElementById(\'collapse-btn\');

function openMobileSidebar(){
  app.classList.add(\'mobile-open\');
  document.body.style.overflow = \'hidden\';
}
function closeMobileSidebar(){
  app.classList.remove(\'mobile-open\');
  document.body.style.overflow = \'\';
}
function toggleCollapse(){
  const collapsed = app.classList.toggle(\'sidebar-collapsed\');
  collapseBtn.textContent = collapsed ? \'▶\' : \'◀\';
  collapseBtn.title = collapsed ? \'Expand sidebar\' : \'Collapse sidebar\';
  try { localStorage.setItem(\'sidebarCollapsed\', collapsed ? \'1\' : \'0\'); } catch(e){}
}
// Restore desktop collapse state
try {
  if(localStorage.getItem(\'sidebarCollapsed\') === \'1\'){
    app.classList.add(\'sidebar-collapsed\');
    collapseBtn.textContent = \'▶\';
    collapseBtn.title = \'Expand sidebar\';
  }
} catch(e){}
// Close sidebar when nav item clicked on mobile
document.querySelectorAll(\'.nav-item\').forEach(el => {
  el.addEventListener(\'click\', () => {
    if(window.innerWidth <= 768) closeMobileSidebar();
  });
});
// Close on ESC key
document.addEventListener(\'keydown\', e => { if(e.key === \'Escape\') closeMobileSidebar(); });

// ───────────────────────────────────────────
// AUTH
// ───────────────────────────────────────────
const PWD = "MINNAL@2025";
let token = "";
let C = {};

function togglePwd(){
  const i=document.getElementById(\'pwdIn\');
  i.type = i.type===\'password\'?\'text\':\'password\';
}
document.getElementById(\'pwdIn\').onkeypress = e => { if(e.key===\'Enter\') tryLogin(); };

async function tryLogin(){
  const pwd = document.getElementById('pwdIn').value.trim();
  const err = document.getElementById('loginErr');
  const btn = document.getElementById('loginBtn');
  
  if(!pwd){ err.textContent='Enter password'; return; }
  
  btn.disabled = true;
  btn.textContent = 'Authenticating...';

  try {
    // 1. Try server-side authentication first
    const r = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: pwd })
    });

    if (r.ok) {
      const d = await r.json();
      token = d.token;
      proceedToApp();
      return;
    } else if (r.status === 401) {
      err.textContent = 'Wrong password';
      btn.disabled = false;
      btn.textContent = 'Login';
      return;
    }
    // If other error (like 404), fall back to local check
    throw new Error('API unavailable');

  } catch(e) {
    // 2. Fallback to local hardcoded check (for offline/local use)
    if (pwd === PWD) {
      token = pwd;
      proceedToApp();
    } else {
      err.textContent = 'Wrong password';
      btn.disabled = false;
      btn.textContent = 'Login';
    }
  }
}

function proceedToApp() {
  document.getElementById('loginPage').style.display = 'none';
  document.getElementById('app').style.display = 'flex';
  
  // Load data in background
  loadConfig();
  loadStats();
  setInterval(loadStats, 15000);
}

function doLogout(){
  document.getElementById(\'app\').style.display=\'none\';
  document.getElementById(\'loginPage\').style.display=\'flex\';
  document.getElementById(\'pwdIn\').value=\'\';
  document.getElementById(\'loginErr\').textContent=\'\';
}

// ───────────────────────────────────────────
// NAVIGATION
// ───────────────────────────────────────────
document.querySelectorAll(\'.nav-item\').forEach(el => {
  el.addEventListener(\'click\', () => {
    document.querySelectorAll(\'.nav-item\').forEach(n=>n.classList.remove(\'active\'));
    document.querySelectorAll(\'.pg\').forEach(p=>p.classList.remove(\'on\'));
    el.classList.add(\'active\');
    const pg = document.getElementById(\'pg-\'+el.dataset.pg);
    if(pg) pg.classList.add(\'on\');
    document.getElementById(\'topbar-title\').textContent = el.querySelector(\'span+*\')?.textContent || el.textContent;
  });
});

// ───────────────────────────────────────────
// DEFAULTS
// ───────────────────────────────────────────
const DEF = {
  bot:{name:"MINNAL",tagline:"The Lightning Engine",developer:"Sahad",embed_color:"#9b59b6",prefix:"/"},
  channels:{welcome_channel_id:"",leave_channel_id:"",music_channel_id:"",ticket_channel_id:"",game_update_channel_id:"",meme_channel_id:"",log_channel_id:"",announcement_channel_id:"",giveaway_channel_id:"",default_voice_channel_id:"",announcement_voice_channel_id:""},
  roles:{verified_role_id:"",unverified_role_id:"",staff_role_id:"",muted_role_id:"",bot_role_id:"",member_role_id:""},
  welcome:{enabled:true,channel_id:"",title:"Welcome!",message:"Hey {member}, welcome to {server}! 🎉",image_url:"",leave_enabled:true,leave_message:"Goodbye {member}... 👋",leave_image_url:""},
  dm_join:{enabled:true,message:"👋 Hey **{member}**, welcome to **{server}**!\\n\\nPlease verify your account to join the fam! 🎉"},
  verify:{enabled:true,channel_id:"",verified_role_id:"",unverified_role_id:"",message:"Click the button below to verify!",button_label:"✅ Verify"},
  tickets:{enabled:true,channel_id:"",staff_role_id:"",category_id:"",welcome_message:"Hello {user}! Our staff will assist you shortly.",close_message:"Ticket closed.",log_channel_id:""},
  autorole:{enabled:false,role_ids:[],bot_role_id:""},
  giveaways:{enabled:true,manager_role_id:"",default_duration_hours:24,default_winners:1},
  summon:{enabled:true,trigger_channel_id:"",domain_names:["Minnal Cave","Sukuna\'s Shrine","Gojo\'s Infinity"]},
  voices:{enabled:true,voice_list:[{spell:"Domain Expansion!",anime:"Sukuna",voice_text:"Domain Expansion!",audio_file:""},{spell:"Rasengan!",anime:"Naruto",voice_text:"Rasengan!",audio_file:""}]},
  bio:{rotation_minutes:5,statuses:[{type:"watching",name:"Server"},{type:"playing",name:"/help | MINNAL"}]},
  memes:{enabled:true,channel_id:"",troll_messages:["{target} got trolled! 💀"]},
  economy:{currency_name:"Coins",currency_symbol:"⚡",starting_balance:100,daily_reward:100,weekly_reward:1000,rob_enabled:true,gamble_enabled:true},
  music:{enabled:true,default_source:"soundcloud",max_queue_size:50,channel_id:"",dj_role_id:"",volume:100},
  sentinel:{enabled:true,log_channel_id:"",anti_spam:true,anti_raid:true,anti_link:false,warn_limit:3,mute_duration_minutes:10},
  ghost_ping:{enabled:true,log_channel_id:"",alert_message:"👻 {user} ghost pinged {target}!"},
  codepilot:{enabled:true,allowed_channel_ids:[],max_response_length:2000}
};

// ───────────────────────────────────────────
// CONFIG LOAD / FILL
// ───────────────────────────────────────────
async function loadConfig(){
  try {
    const r = await fetch(\'/api/config\',{headers:{Authorization:\'Bearer \'+token}});
    if(r.ok){ const d = await r.json(); C = d.config; }
    else throw new Error();
  } catch(e) {
    const s = localStorage.getItem(\'minnalcfg\');
    C = s ? JSON.parse(s) : JSON.parse(JSON.stringify(DEF));
  }
  for(const k in DEF) if(!C[k]) C[k] = JSON.parse(JSON.stringify(DEF[k]));
  fillUI();
  updateSummary();
}

function g(id){ return (document.getElementById(id)||{}).value||\'\'; }
function s(id,v){ const el=document.getElementById(id); if(el) el.value=v==null?\'\':v; }
function gc(id){ return !!(document.getElementById(id)||{}).checked; }
function sc(id,v){ const el=document.getElementById(id); if(el) el.checked=!!v; }

function fillUI(){
  const b=C.bot||DEF.bot;
  s(\'b-name\',b.name); s(\'b-tag\',b.tagline); s(\'b-dev\',b.developer); s(\'b-color\',b.embed_color); s(\'b-prefix\',b.prefix||\'/\');
  s(\'b-color-picker\',b.embed_color);

  const ch=C.channels||DEF.channels;
  s(\'ch-welcome\',ch.welcome_channel_id); s(\'ch-leave\',ch.leave_channel_id); s(\'ch-music\',ch.music_channel_id);
  s(\'ch-ticket\',ch.ticket_channel_id); s(\'ch-game\',ch.game_update_channel_id); s(\'ch-meme\',ch.meme_channel_id);
  s(\'ch-log\',ch.log_channel_id); s(\'ch-announcement\',ch.announcement_channel_id); s(\'ch-giveaway\',ch.giveaway_channel_id);
  s(\'ch-voice-default\',ch.default_voice_channel_id); s(\'ch-voice-announcement\',ch.announcement_voice_channel_id);

  const rl=C.roles||DEF.roles;
  s(\'rl-verified\',rl.verified_role_id); s(\'rl-unverified\',rl.unverified_role_id); s(\'rl-staff\',rl.staff_role_id);
  s(\'rl-muted\',rl.muted_role_id); s(\'rl-bot\',rl.bot_role_id); s(\'rl-member\',rl.member_role_id);

  const wc=C.welcome||DEF.welcome;
  sc(\'wc-on\',wc.enabled); s(\'wc-ch\',wc.channel_id); s(\'wc-title\',wc.title); s(\'wc-msg\',wc.message); s(\'wc-img\',wc.image_url);
  sc(\'lv-on\',wc.leave_enabled); s(\'lv-ch\',wc.leave_channel_id||\'\'); s(\'lv-msg\',wc.leave_message||\'\'); s(\'lv-img\',wc.leave_image_url||\'\');

  const dm=C.dm_join||DEF.dm_join;
  sc(\'dm-on\',dm.enabled); s(\'dm-msg\',dm.message);

  const vr=C.verify||DEF.verify;
  sc(\'vr-on\',vr.enabled); s(\'vr-ch\',vr.channel_id); s(\'vr-btn\',vr.button_label); s(\'vr-vrole\',vr.verified_role_id); s(\'vr-urole\',vr.unverified_role_id); s(\'vr-msg\',vr.message);

  const tk=C.tickets||DEF.tickets;
  sc(\'tk-on\',tk.enabled); s(\'tk-ch\',tk.channel_id); s(\'tk-staff\',tk.staff_role_id); s(\'tk-cat\',tk.category_id); s(\'tk-log\',tk.log_channel_id); s(\'tk-welcome\',tk.welcome_message); s(\'tk-close\',tk.close_message);

  const ar=C.autorole||DEF.autorole;
  sc(\'ar-on\',ar.enabled); s(\'ar-roles\',(ar.role_ids||[]).join(\'\\n\')); s(\'ar-botrole\',ar.bot_role_id||\'\');

  const gw=C.giveaways||DEF.giveaways;
  sc(\'gw-on\',gw.enabled); s(\'gw-role\',gw.manager_role_id); s(\'gw-dur\',gw.default_duration_hours); s(\'gw-win\',gw.default_winners);

  const sn=C.sentinel||DEF.sentinel;
  sc(\'sn-on\',sn.enabled); s(\'sn-log\',sn.log_channel_id); sc(\'sn-spam\',sn.anti_spam); sc(\'sn-raid\',sn.anti_raid); sc(\'sn-link\',sn.anti_link); s(\'sn-warn\',sn.warn_limit); s(\'sn-mute\',sn.mute_duration_minutes);

  const gp=C.ghost_ping||DEF.ghost_ping;
  sc(\'gp-on\',gp.enabled); s(\'gp-log\',gp.log_channel_id); s(\'gp-msg\',gp.alert_message);

  const mu=C.music||DEF.music;
  sc(\'mu-on\',mu.enabled); s(\'mu-ch\',mu.channel_id||\'\'); s(\'mu-dj\',mu.dj_role_id||\'\'); s(\'mu-src\',mu.default_source); s(\'mu-queue\',mu.max_queue_size); s(\'mu-vol\',mu.volume||100);

  const mm=C.memes||DEF.memes;
  sc(\'mm-on\',mm.enabled); s(\'mm-ch\',mm.channel_id); renderTrols();

  const sm=C.summon||DEF.summon;
  sc(\'sm-on\',sm.enabled); s(\'sm-ch\',sm.trigger_channel_id); renderDoms();

  sc(\'vo-on\',(C.voices||DEF.voices).enabled); renderVoices();

  const bi=C.bio||DEF.bio;
  s(\'bi-rot\',bi.rotation_minutes); renderBio();

  const ec=C.economy||DEF.economy;
  s(\'ec-name\',ec.currency_name); s(\'ec-sym\',ec.currency_symbol); s(\'ec-start\',ec.starting_balance);
  s(\'ec-daily\',ec.daily_reward); s(\'ec-weekly\',ec.weekly_reward); sc(\'ec-rob\',ec.rob_enabled); sc(\'ec-gamble\',ec.gamble_enabled);

  const cp=C.codepilot||DEF.codepilot;
  sc(\'cp-on\',cp.enabled); s(\'cp-channels\',(cp.allowed_channel_ids||[]).join(\'\\n\')); s(\'cp-maxlen\',cp.max_response_length);

  // Color picker sync
  document.getElementById(\'b-color-picker\').oninput = function(){ s(\'b-color\',this.value); };
  document.getElementById(\'b-color\').oninput = function(){ if(/^#[0-9a-f]{6}$/i.test(this.value)) s(\'b-color-picker\',this.value); };
}

// ───────────────────────────────────────────
// SAVE
// ───────────────────────────────────────────
async function save(sec){
  collectSection(sec);
  localStorage.setItem(\'minnalcfg\', JSON.stringify(C));
  try {
    const r = await fetch(\'/api/save\',{
      method:\'POST\',
      headers:{\'Content-Type\':\'application/json\',\'Authorization\':\'Bearer \'+token},
      body:JSON.stringify({section:sec,data:C[sec]})
    });
    if(r.ok){ toast(\'✅ Saved to bot!\',\'ok\'); }
    else { toast(\'Saved locally (bot offline)\',\'info\'); }
  } catch(e){ toast(\'Saved locally (bot offline)\',\'info\'); }
  updateSummary();
}

function collectSection(sec){
  if(sec===\'bot\') C.bot={name:g(\'b-name\'),tagline:g(\'b-tag\'),developer:g(\'b-dev\'),embed_color:g(\'b-color\'),prefix:g(\'b-prefix\')||\'/\'};
  else if(sec===\'channels\') C.channels={welcome_channel_id:g(\'ch-welcome\'),leave_channel_id:g(\'ch-leave\'),music_channel_id:g(\'ch-music\'),ticket_channel_id:g(\'ch-ticket\'),game_update_channel_id:g(\'ch-game\'),meme_channel_id:g(\'ch-meme\'),log_channel_id:g(\'ch-log\'),announcement_channel_id:g(\'ch-announcement\'),giveaway_channel_id:g(\'ch-giveaway\'),default_voice_channel_id:g(\'ch-voice-default\'),announcement_voice_channel_id:g(\'ch-voice-announcement\')};
  else if(sec===\'roles\') C.roles={verified_role_id:g(\'rl-verified\'),unverified_role_id:g(\'rl-unverified\'),staff_role_id:g(\'rl-staff\'),muted_role_id:g(\'rl-muted\'),bot_role_id:g(\'rl-bot\'),member_role_id:g(\'rl-member\')};
  else if(sec===\'welcome\') C.welcome={enabled:gc(\'wc-on\'),channel_id:g(\'wc-ch\'),title:g(\'wc-title\'),message:g(\'wc-msg\'),image_url:g(\'wc-img\'),leave_enabled:gc(\'lv-on\'),leave_channel_id:g(\'lv-ch\'),leave_message:g(\'lv-msg\'),leave_image_url:g(\'lv-img\')};
  else if(sec===\'dm_join\') C.dm_join={enabled:gc(\'dm-on\'),message:g(\'dm-msg\')};
  else if(sec===\'verify\') C.verify={enabled:gc(\'vr-on\'),channel_id:g(\'vr-ch\'),verified_role_id:g(\'vr-vrole\'),unverified_role_id:g(\'vr-urole\'),message:g(\'vr-msg\'),button_label:g(\'vr-btn\')};
  else if(sec===\'tickets\') C.tickets={enabled:gc(\'tk-on\'),channel_id:g(\'tk-ch\'),staff_role_id:g(\'tk-staff\'),category_id:g(\'tk-cat\'),log_channel_id:g(\'tk-log\'),welcome_message:g(\'tk-welcome\'),close_message:g(\'tk-close\')};
  else if(sec===\'autorole\'){const ids=g(\'ar-roles\').split(\'\\n\').map(x=>x.trim()).filter(Boolean);C.autorole={enabled:gc(\'ar-on\'),role_ids:ids,bot_role_id:g(\'ar-botrole\')};}
  else if(sec===\'giveaways\') C.giveaways={enabled:gc(\'gw-on\'),manager_role_id:g(\'gw-role\'),default_duration_hours:parseInt(g(\'gw-dur\'))||24,default_winners:parseInt(g(\'gw-win\'))||1};
  else if(sec===\'sentinel\') C.sentinel={enabled:gc(\'sn-on\'),log_channel_id:g(\'sn-log\'),anti_spam:gc(\'sn-spam\'),anti_raid:gc(\'sn-raid\'),anti_link:gc(\'sn-link\'),warn_limit:parseInt(g(\'sn-warn\'))||3,mute_duration_minutes:parseInt(g(\'sn-mute\'))||10};
  else if(sec===\'ghost_ping\') C.ghost_ping={enabled:gc(\'gp-on\'),log_channel_id:g(\'gp-log\'),alert_message:g(\'gp-msg\')};
  else if(sec===\'economy\') C.economy={currency_name:g(\'ec-name\'),currency_symbol:g(\'ec-sym\'),starting_balance:parseInt(g(\'ec-start\'))||100,daily_reward:parseInt(g(\'ec-daily\'))||100,weekly_reward:parseInt(g(\'ec-weekly\'))||1000,rob_enabled:gc(\'ec-rob\'),gamble_enabled:gc(\'ec-gamble\')};
  else if(sec===\'music\') C.music={enabled:gc(\'mu-on\'),channel_id:g(\'mu-ch\'),dj_role_id:g(\'mu-dj\'),default_source:g(\'mu-src\'),max_queue_size:parseInt(g(\'mu-queue\'))||50,volume:parseInt(g(\'mu-vol\'))||100};
  else if(sec===\'memes\') C.memes={enabled:gc(\'mm-on\'),channel_id:g(\'mm-ch\'),troll_messages:C.memes.troll_messages};
  else if(sec===\'summon\') C.summon={enabled:gc(\'sm-on\'),trigger_channel_id:g(\'sm-ch\'),domain_names:C.summon.domain_names};
  else if(sec===\'voices\') C.voices={enabled:gc(\'vo-on\'),voice_list:C.voices.voice_list};
  else if(sec===\'bio\') C.bio={rotation_minutes:parseInt(g(\'bi-rot\'))||5,statuses:C.bio.statuses};
  else if(sec===\'codepilot\'){const chs=g(\'cp-channels\').split(\'\\n\').map(x=>x.trim()).filter(Boolean);C.codepilot={enabled:gc(\'cp-on\'),allowed_channel_ids:chs,max_response_length:parseInt(g(\'cp-maxlen\'))||2000};}
}

// ───────────────────────────────────────────
// STATS
// ───────────────────────────────────────────
async function loadStats(){
  try {
    const r = await fetch(\'/api/stats\');
    const d = await r.json();
    if(d.online){
      document.getElementById(\'st-latency\').textContent=d.latency;
      document.getElementById(\'st-uptime\').textContent=d.uptime;
      document.getElementById(\'st-guilds\').textContent=d.guilds;
      document.getElementById(\'st-users\').textContent=d.users.toLocaleString();
      document.getElementById(\'st-cpu\').textContent=d.cpu;
      document.getElementById(\'st-ram\').textContent=d.ram;
      document.getElementById(\'st-online\').textContent=\'Online\';
      document.getElementById(\'st-ping\').textContent=d.latency;
      document.getElementById(\'botStatus\').innerHTML=\'<span class="status-dot"></span>Bot Online\';
      document.getElementById(\'botStatus\').style.color=\'var(--green)\';
    }
  } catch(e){ document.getElementById(\'botStatus\').textContent=\'Bot Offline\'; }
}

function updateSummary(){
  const lines=[];
  const ch=C.channels||{};
  const rl=C.roles||{};
  const filled=k=>k&&k!==\'\';
  lines.push(`<b>Channels configured:</b> ${Object.values(ch).filter(filled).length}/${Object.keys(ch).length}`);
  lines.push(`<b>Roles configured:</b> ${Object.values(rl).filter(filled).length}/${Object.keys(rl).length}`);
  lines.push(`<b>Economy:</b> ${(C.economy||{}).currency_symbol||\'⚡\'} ${(C.economy||{}).currency_name||\'Coins\'} — Daily: ${(C.economy||{}).daily_reward||100}`);
  lines.push(`<b>Bot status rotations:</b> ${((C.bio||{}).statuses||[]).length} statuses, every ${(C.bio||{}).rotation_minutes||5}m`);
  lines.push(`<b>Voice spells:</b> ${((C.voices||{}).voice_list||[]).length} spells`);
  lines.push(`<b>Domain names:</b> ${((C.summon||{}).domain_names||[]).length}`);
  document.getElementById(\'cfgSummary\').innerHTML=lines.join(\'<br>\');
}

// ───────────────────────────────────────────
// LISTS — DOMAINS
// ───────────────────────────────────────────
function renderDoms(){
  const c=document.getElementById(\'domLst\'); c.innerHTML=\'\';
  const arr=(C.summon||{}).domain_names||[];
  if(!arr.length){c.innerHTML=\'<div class="empty-lst">No domains added</div>\';return;}
    arr.forEach((n,i)=>{
    const d=document.createElement(\'div\'); d.className=\'lst-item\';
    d.innerHTML=`<input type="text" value="${esc(n)}"><button class="btn btn-sm btn-red" onclick="delDom(${i})">✕</button>`;
    d.querySelector(\'input\').onchange=function(){C.summon.domain_names[i]=this.value;};
    c.appendChild(d);
  });
}
function addDom(){const v=document.getElementById(\'newDom\').value.trim();if(!v)return;C.summon.domain_names.push(v);document.getElementById(\'newDom\').value=\'\';renderDoms();}
function delDom(i){C.summon.domain_names.splice(i,1);renderDoms();}

// ───────────────────────────────────────────
// LISTS — VOICES
// ───────────────────────────────────────────
function renderVoices(){
  const c=document.getElementById(\'voiceList\'); c.innerHTML=\'\';
  const arr=(C.voices||{}).voice_list||[];
  if(!arr.length){c.innerHTML=\'<div class="empty-lst">No voice spells added</div>\';return;}
    arr.forEach((v,i)=>{
    const hasAudio=v.audio_file&&v.audio_file.trim();
    const d=document.createElement(\'div\'); d.className=\'vcard\';
    d.innerHTML=`<div class="vcard-head"><strong>#${i+1} — ${esc(v.spell)}</strong><div style="display:flex;gap:6px;align-items:center"><span class="badge ${hasAudio?\'badge-audio\':\'badge-tts\'}">${hasAudio?\'🔊 Audio\':\'🗣️ TTS\'}</span><button class="btn btn-sm btn-red" onclick="delVoice(${i})">✕</button></div></div>
      <div class="row2"><div><label>Spell Trigger</label><input value="${esc(v.spell)}"></div><div><label>Character</label><input value="${esc(v.anime)}"></div></div>
      <div class="row2"><div><label>TTS Text</label><input value="${esc(v.voice_text)}"></div><div><label>Audio File</label><input value="${esc(v.audio_file||\'\')}"></div></div>`;
    const ins=d.querySelectorAll(\'input\');
    ins[0].onchange=e=>{C.voices.voice_list[i].spell=e.target.value;};
    ins[1].onchange=e=>{C.voices.voice_list[i].anime=e.target.value;};
    ins[2].onchange=e=>{C.voices.voice_list[i].voice_text=e.target.value;};
    ins[3].onchange=e=>{C.voices.voice_list[i].audio_file=e.target.value;renderVoices();};
    c.appendChild(d);
  });
}
function addVoice(){
  const spell=g(\'nv-spell\').trim(),chr=g(\'nv-char\').trim(),tts=g(\'nv-tts\').trim(),file=g(\'nv-file\').trim();
  if(!spell||!chr){toast(\'Fill Spell and Character\',\'err\');return;}
  C.voices.voice_list.push({spell,anime:chr,voice_text:tts||spell,audio_file:file});
  [\'nv-spell\',\'nv-char\',\'nv-tts\',\'nv-file\'].forEach(id=>s(id,\'\'));
  renderVoices(); toast(\'Voice spell added!\',\'ok\');
}
function delVoice(i){C.voices.voice_list.splice(i,1);renderVoices();}

// ───────────────────────────────────────────
// LISTS — BIO
// ───────────────────────────────────────────
function renderBio(){
  const c=document.getElementById(\'bioLst\'); c.innerHTML=\'\';
  const arr=(C.bio||{}).statuses||[];
  if(!arr.length){c.innerHTML=\'<div class="empty-lst">No statuses added</div>\';return;}
    arr.forEach((st,i)=>{
    const d=document.createElement(\'div\'); d.className=\'lst-item\';
    d.innerHTML=`<span style="font-size:11px;color:var(--muted);width:70px;flex-shrink:0;text-transform:capitalize">${st.type}</span><input type="text" value="${esc(st.name)}"><button class="btn btn-sm btn-red" onclick="delBio(${i})">✕</button>`;
    d.querySelector(\'input\').onchange=function(){C.bio.statuses[i].name=this.value;};
    c.appendChild(d);
  });
}
function addBio(){
  const t=g(\'nb-type\'),n=g(\'nb-name\').trim();
  if(!n)return;
  C.bio.statuses.push({type:t,name:n}); s(\'nb-name\',\'\'); renderBio();
}
function delBio(i){C.bio.statuses.splice(i,1);renderBio();}

// ───────────────────────────────────────────
// LISTS — TROLL MSGS
// ───────────────────────────────────────────
function renderTrols(){
  const c=document.getElementById(\'trolLst\'); c.innerHTML=\'\';
  const arr=(C.memes||{}).troll_messages||[];
  if(!arr.length){c.innerHTML=\'<div class="empty-lst">No troll messages</div>\';return;}
    arr.forEach((m,i)=>{
    const d=document.createElement(\'div\'); d.className=\'lst-item\';
    d.innerHTML=`<input type="text" value="${esc(m)}"><button class="btn btn-sm btn-red" onclick="delTrol(${i})">✕</button>`;
    d.querySelector(\'input\').onchange=function(){C.memes.troll_messages[i]=this.value;};
    c.appendChild(d);
  });
}
function addTrol(){const v=document.getElementById(\'newTrol\').value.trim();if(!v)return;C.memes.troll_messages.push(v);document.getElementById(\'newTrol\').value=\'\';renderTrols();}
function delTrol(i){C.memes.troll_messages.splice(i,1);renderTrols();}

// ───────────────────────────────────────────
// IMPORT / EXPORT
// ───────────────────────────────────────────
function doExport(){
  const blob=new Blob([JSON.stringify(C,null,2)],{type:\'application/json\'});
  const a=document.createElement(\'a\'); a.href=URL.createObjectURL(blob);
  a.download=\'minnal-settings.json\'; a.click();
  toast(\'Config exported!\',\'ok\');
}
function doImport(e){
  const file=e.target.files[0]; if(!file)return;
  const reader=new FileReader();
  reader.onload=function(ev){
    try{C=JSON.parse(ev.target.result);fillUI();localStorage.setItem(\'minnalcfg\',JSON.stringify(C));toast(\'Config imported!\',\'ok\');}
    catch(er){toast(\'Invalid JSON file\',\'err\');}
  };
  reader.readAsText(file);
  e.target.value=\'\';
}

// ───────────────────────────────────────────
// TOAST
// ───────────────────────────────────────────
let toastTimer;
function toast(msg,type=\'ok\'){
  const t=document.getElementById(\'toast\');
  t.textContent=msg; t.className=\'toast \'+type+\' show\';
  clearTimeout(toastTimer);
  toastTimer=setTimeout(()=>t.classList.remove(\'show\'),3000);
}

function esc(s){if(!s)return\'\';return String(s).replace(/&/g,\'&amp;\').replace(/\"/g,\'&quot;\').replace(/\'/g,\'&#39;\').replace(/</g,\'&lt;\').replace(/>/g,\'&gt;\');}

// ───────────────────────────────────────────
// VIEW TOGGLE
// ───────────────────────────────────────────
function switchToMobileView() {
  const app = document.getElementById(\'app\');
  app.style.maxWidth = \'420px\';
  app.style.margin = \'20px auto\';
  app.style.border = \'1px solid var(--border)\';
  app.style.borderRadius = \'10px\';
  app.style.boxShadow = \'0 10px 30px rgba(0,0,0,.3)\';
  app.style.height = \'calc(100vh - 40px)\';
  app.style.overflow = \'auto\';
  toast(\'Switched to Mobile View\', \'info\');
}

function switchToDesktopView() {
  const app = document.getElementById(\'app\');
  app.style.maxWidth = \'\';
  app.style.margin = \'\';
  app.style.border = \'\';
  app.style.borderRadius = \'\';
  app.style.boxShadow = \'\';
  app.style.height = \'\';
  app.style.overflow = \'\';
  toast(\'Switched to Desktop View\', \'ok\');
}

// ───────────────────────────────────────────
// GITHUB SYNC
// ───────────────────────────────────────────
async function doPush(){
  const btn = document.getElementById(\'ghPushBtn\');
  const result = document.getElementById(\'gh-push-result\');
  const msg = document.getElementById(\'gh-push-msg\');
  const steps = document.getElementById(\'gh-push-steps\');

  btn.disabled = true;
  btn.innerHTML = \'<span class="spin"></span> Pushing to GitHub...\';
  result.style.display = \'none\';

  try {
    const r = await fetch(\'/api/github/push\', {
      method: \'POST\',
      headers: { \'Authorization\': \'Bearer \' + token }
    });
    const d = await r.json();

    result.style.display = \'block\';
    if(r.ok && d.success){
      msg.style.color = \'var(--green)\';
      msg.textContent = \'✅ \' + d.message;
      steps.textContent = (d.steps || []).join(\'\\n\');
      toast(\'Pushed to GitHub!\', \'ok\');
      loadGHStatus();
    } else {
      msg.style.color = \'var(--red)\';
      msg.textContent = \'❌ \' + (d.detail || \'Push failed\');
      steps.textContent = (d.steps || []).join(\'\\n\');
      toast(\'Push failed\', \'err\');
    }
  } catch(e) {
    result.style.display = \'block\';
    msg.style.color = \'var(--red)\';
    msg.textContent = \'❌ Cannot reach bot — make sure the bot is running on port 6000\';
    toast(\'Push failed — bot offline\', \'err\');
  }

  btn.disabled = false;
  btn.innerHTML = \'🐙 Push Settings to GitHub\';
}

async function quickPush(){
  toast(\'Pushing to GitHub...\', \'info\');
  try {
    const r = await fetch(\'/api/github/push\', {
      method: \'POST\',
      headers: { \'Authorization\': \'Bearer \' + token }
    });
    const d = await r.json();
    if(r.ok && d.success){ toast(\'🐙 \' + d.message, \'ok\'); }
    else { toast(\'Push failed: \' + (d.detail || \'error\'), \'err\'); }
  } catch(e) { toast(\'Bot offline — cannot push\', \'err\'); }
}

async function loadGHStatus(){
  try {
    const r = await fetch(\'/api/github/status\', {
      headers: { \'Authorization\': \'Bearer \' + token }
    });
    const d = await r.json();

    if(!d.has_token){
      document.getElementById(\'gh-token-warn\').style.display = \'block\';
    }

    const commits = d.recent_commits || [];
    document.getElementById(\'gh-commits\').innerHTML = commits.length
      ? commits.map(c => `<div>📌 ${esc(c)}</div>`).join(\'\')
      : \'<div>No commits yet</div>\';

    const dirty = d.uncommitted_changes;
    document.getElementById(\'gh-dirty\').textContent = dirty
      ? dirty
      : \'✅ Working tree clean — nothing to commit\';
    document.getElementById(\'gh-dirty\').style.color = dirty ? \'var(--yellow)\' : \'var(--green)\';
  } catch(e) {
    document.getElementById(\'gh-commits\').textContent = \'Bot offline\';
    document.getElementById(\'gh-dirty\').textContent = \'Cannot connect to bot\';
  }
}

// Load GitHub status when GitHub page is opened
document.querySelector(\'[data-pg="github"]\').addEventListener(\'click\', () => {
  loadGHStatus();
});

