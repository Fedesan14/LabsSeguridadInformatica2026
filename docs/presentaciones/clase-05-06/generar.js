// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
// Generador del deck de la clase 05-06 (cruce a ofensiva).
// Uso:  npm install && npm run build   (requiere Node + pptxgenjs 4.0.1)
// Salida: docs/clase-05-06-cruce-ofensiva.pptx
const path = require("path");
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";
p.author = "Ing. Fernando Boiero";
p.company = "CyberLab UTN FRVM";
p.title = "Clase 05-06 — Cruce a ofensiva";

// ── paleta (idéntica a presentacion.html) ──
const BG="0a0e12", S1="111a22", S2="16222c", BD="213039", BD2="2c404c";
const TX="cdd8de", MU="7c909b", DIM="556570";
const GR="39d98a", CY="4cc9f0", AM="f0b429", VI="b19cf0", RD="e0645b";
const MONO="Courier New", SANS="Calibri";
const W=13.333, H=7.5, M=0.62, CW=W-2*M;

function bg(s){ s.background={color:BG}; }
function eyebrow(s,t,x,y,w,c){ s.addText(t.toUpperCase(),{x,y,w:w||CW,h:0.3,fontFace:MONO,fontSize:11,color:c||GR,charSpacing:3,bold:true,margin:0,valign:"middle"}); }
function title(s,t,x,y,w,sz){ s.addText(t,{x,y,w:w||CW,h:0.85,fontFace:SANS,fontSize:sz||34,bold:true,color:TX,margin:0,valign:"middle"}); }
function card(s,x,y,w,h,fill,line){ s.addShape(p.ShapeType.roundRect,{x,y,w,h,rectRadius:0.09,fill:{color:fill||S1},line:{color:line||BD,width:1}}); }
function foot(s,t){ s.addText(t,{x:M,y:H-0.5,w:CW,h:0.3,fontFace:MONO,fontSize:10,color:DIM,margin:0,valign:"middle"}); }
function flagchip(s,t,x,y,w){ s.addShape(p.ShapeType.roundRect,{x,y,w,h:0.34,rectRadius:0.05,fill:{color:"1a1710"},line:{color:AM,width:0.75}}); s.addText(t,{x:x+0.1,y,w:w-0.2,h:0.34,fontFace:MONO,fontSize:11,color:AM,margin:0,valign:"middle"}); }

// terminal mock
function term(s,x,y,w,lines){
  const h=0.46+lines.length*0.28+0.16;
  s.addShape(p.ShapeType.roundRect,{x,y,w,h,rectRadius:0.08,fill:{color:"080c10"},line:{color:BD2,width:1}});
  s.addShape(p.ShapeType.rect,{x,y,w,h:0.34,fill:{color:"0d141b"},line:{color:BD,width:0.5}});
  [RD,AM,GR].forEach((c,i)=>s.addShape(p.ShapeType.ellipse,{x:x+0.16+i*0.22,y:y+0.12,w:0.11,h:0.11,fill:{color:c},line:{width:0}}));
  lines.forEach((ln,i)=>{
    s.addText(ln.t,{x:x+0.18,y:y+0.44+i*0.28,w:w-0.36,h:0.26,fontFace:MONO,fontSize:ln.sz||11.5,color:ln.c||TX,margin:0,valign:"middle"});
  });
  return h;
}

// ───────────────────────────── 1 · COVER ─────────────────────────────
let s=p.addSlide(); bg(s);
s.addShape(p.ShapeType.rect,{x:0,y:0,w:W,h:0.06,fill:{color:GR},line:{width:0}});
eyebrow(s,"CyberLab UTN FRVM · Seguridad Ofensiva",M,0.9,CW,GR);
s.addText("Cruce a ofensiva",{x:M,y:2.2,w:CW,h:1.1,fontFace:SANS,fontSize:58,bold:true,color:TX,margin:0});
s.addText([
  {text:"Clase 05-06",options:{color:GR,bold:true}},
  {text:"   ·   Reconocimiento + Enumeración",options:{color:MU}},
],{x:M,y:3.4,w:CW,h:0.5,fontFace:MONO,fontSize:20,margin:0});
s.addText("Se termina de escribir código. Empieza a atacar.",{x:M,y:4.15,w:CW,h:0.5,fontFace:SANS,fontSize:17,italic:true,color:TX,margin:0});
term(s,M,4.9,6.2,[
  {t:"$ ./ctf lab 05   # levanta PhantomCorp",c:GR},
  {t:"$ make shell     # consola del atacante",c:TX},
]);
s.addText("Ing. Fernando Boiero  ·  UTN FRVM  ·  2026",{x:W-5.3,y:H-0.55,w:4.7,h:0.3,fontFace:MONO,fontSize:11,color:DIM,align:"right",margin:0});
s.addNotes("Clase bisagra. Venimos de 3 semanas de parate y el curso está atrasado (entregas en lab 01-03). Hoy: reencuadrar, diagnosticar y arrancar ofensiva CON red. No corremos.");

// ───────────────────────────── 2 · DÓNDE ESTÁBAMOS ─────────────────────
s=p.addSlide(); bg(s);
eyebrow(s,"Reencuadre",M,0.55);
title(s,"Tres semanas después: ¿dónde estamos?",M,0.95,CW,32);
const colW=(CW-0.5)/2;
card(s,M,2.1,colW,3.9,S1,BD);
eyebrow(s,"Lo que ya hicimos — Bloque 1",M+0.3,2.35,colW-0.6,CY);
["01 · Tríada CIA + integridad (hashing)","02 · Criptografía (XOR, HMAC, Kerckhoffs)","03 · Autenticación (PBKDF2, salt, TOTP)","04 · Riesgo y marcos (ALE, ISO/NIST)"].forEach((t,i)=>{
  s.addText(t,{x:M+0.3,y:2.8+i*0.62,w:colW-0.6,h:0.5,fontFace:MONO,fontSize:13,color:TX,margin:0,valign:"middle"});
});
s.addText("Escribiste código. Entendiste QUÉ se protege.",{x:M+0.3,y:5.4,w:colW-0.6,h:0.45,fontFace:SANS,fontSize:13,italic:true,color:MU,margin:0});
card(s,M+colW+0.5,2.1,colW,3.9,"14110d",AM);
eyebrow(s,"Lo que empieza HOY — Bloque 2",M+colW+0.8,2.35,colW-0.6,AM);
["05 · Reconocimiento  ← hoy","06 · Enumeración      ← hoy","07 · Explotación (SQLi, RCE…)","08 · Post-explotación (pivoting)"].forEach((t,i)=>{
  s.addText(t,{x:M+colW+0.8,y:2.8+i*0.62,w:colW-0.6,h:0.5,fontFace:MONO,fontSize:13,color:(i<2?AM:MU),margin:0,valign:"middle",bold:i<2});
});
s.addText("Dejás de escribir. Empezás a ROMPER.",{x:M+colW+0.8,y:5.4,w:colW-0.6,h:0.45,fontFace:SANS,fontSize:13,italic:true,color:TX,margin:0});
foot(s,"El material llega al lab 11. El curso real está en 01-03. Hoy consolidamos y arrancamos — sin correr.");
s.addNotes("Honestidad con el curso: no venimos al día. No pasa nada, pero lo nombramos. El bloque 2 exige la base del bloque 1; por eso primero el diagnóstico.");

// ───────────────────────────── 3 · EL ARCO ─────────────────────────────
s=p.addSlide(); bg(s);
eyebrow(s,"El mapa completo",M,0.55);
title(s,"El arco: de entender a romper, defender e investigar",M,0.95,CW,28);
const blocks=[
  {k:"B1 · Fundamentos",c:CY,labs:"01 02 03 04",d:"Código. Qué protegés."},
  {k:"B2 · Ofensiva a mano",c:AM,labs:"05 06 07 08",d:"Docker. Atacás a mano."},
  {k:"B3 · Agentes + Defensa",c:GR,labs:"09 10",d:"IA dirigida. Blue vs Red."},
  {k:"B4 · Integración",c:VI,labs:"11 + Final",d:"Forensia. Engagement."},
];
const bw=(CW-3*0.3)/4;
blocks.forEach((b,i)=>{
  const x=M+i*(bw+0.3);
  card(s,x,2.3,bw,3.2,S1,i===1?AM:BD);
  eyebrow(s,b.k,x+0.22,2.55,bw-0.44,b.c);
  s.addText(b.labs,{x:x+0.22,y:3.1,w:bw-0.44,h:0.7,fontFace:MONO,fontSize:22,bold:true,color:b.c,margin:0,valign:"middle"});
  s.addText(b.d,{x:x+0.22,y:3.95,w:bw-0.44,h:1.2,fontFace:SANS,fontSize:13,color:TX,margin:0,valign:"top"});
  if(i===1) s.addText("◀ ACÁ ESTAMOS",{x:x+0.22,y:5.0,w:bw-0.44,h:0.35,fontFace:MONO,fontSize:11,bold:true,color:AM,margin:0});
});
foot(s,"Un solo hilo: la auditoría de PhantomCorp S.A. atraviesa todo el bloque ofensivo.");
s.addNotes("La progresión es deliberada: manual (05-08) antes que agentes (09). No podés dirigir un agente que hace lo que vos no sabés hacer.");

// ───────────────────────────── 4 · CAMBIO DE CHIP ─────────────────────
s=p.addSlide(); bg(s);
eyebrow(s,"El cambio de chip",M,0.55);
title(s,"Misma información, dos preguntas opuestas",M,0.95,CW,30);
card(s,M,2.2,colW,3.6,S1,CY);
eyebrow(s,"Hasta ahora · el defensor",M+0.3,2.45,colW-0.6,CY);
["¿Qué tengo que proteger?","¿Qué propiedad (C-I-A) está en juego?","¿Cómo lo guardo bien?","¿Qué control pongo?"].forEach((t,i)=>{
  s.addText("› "+t,{x:M+0.3,y:3.0+i*0.6,w:colW-0.6,h:0.5,fontFace:SANS,fontSize:15,color:TX,margin:0,valign:"middle"});
});
card(s,M+colW+0.5,2.2,colW,3.6,"14110d",AM);
eyebrow(s,"Desde hoy · el atacante",M+colW+0.8,2.45,colW-0.6,AM);
["¿Qué tiene expuesto?","¿Qué versión corre y qué CVE tiene?","¿Dónde se configuró mal?","¿Por dónde entro?"].forEach((t,i)=>{
  s.addText("› "+t,{x:M+colW+0.8,y:3.0+i*0.6,w:colW-0.6,h:0.5,fontFace:SANS,fontSize:15,color:TX,margin:0,valign:"middle"});
});
s.addText("El mejor pentester piensa como defensor. El mejor defensor piensa como atacante. Es el MISMO conocimiento, dado vuelta.",{x:M,y:6.1,w:CW,h:0.6,fontFace:SANS,fontSize:14,italic:true,color:GR,margin:0});
s.addNotes("Esta diapo justifica por qué pudimos empezar por los fundamentos: son las dos caras de lo mismo. Ahora miramos del lado rojo.");

// ───────────────────────────── 5 · DIAGNÓSTICO ─────────────────────────
s=p.addSlide(); bg(s);
eyebrow(s,"Primero, el espejo",M,0.55,CW,AM);
title(s,"5 minutos: ¿dónde estás parado?",M,0.95,CW,32);
s.addText("Antes de tirar el primer nmap: un diagnóstico corto y autocorregible. No es nota — es para que sepas si estás listo, o si te falta base.",{x:M,y:1.95,w:CW,h:0.7,fontFace:SANS,fontSize:15,color:TX,margin:0});
let th=term(s,M,2.9,6.4,[
  {t:"$ cp docs/diagnostico-respuestas.txt mi.txt",c:TX},
  {t:"$ python3 bin/diagnostico.py mi.txt",c:GR},
  {t:"  Fundamentos: 8/8   Ofensiva-ready: 3/3",c:MU},
  {t:"  estado=LISTO",c:GR},
]);
const est=[["LISTO","base + entorno ok → a romper",GR],["CASI","1-2 huecos → repaso puntual",AM],["REPASAR","<50% base → volvé a 01-04",RD],["ENTORNO","sin Docker → taller de setup",CY]];
est.forEach((e,i)=>{
  const y=2.9+i*0.72;
  card(s,M+6.8,y,CW-6.8,0.6,S1,BD);
  s.addText(e[0],{x:M+6.95,y,w:1.5,h:0.6,fontFace:MONO,fontSize:13,bold:true,color:e[2],margin:0,valign:"middle"});
  s.addText(e[1],{x:M+8.45,y,w:CW-6.8-1.75,h:0.6,fontFace:SANS,fontSize:12.5,color:TX,margin:0,valign:"middle"});
});
foot(s,"Pegás la línea RESULTADO en tu entrega. El docente levanta el semáforo del aula y ajusta la clase.");
s.addNotes("Correr EN CLASE. 20 min. Si predomina ENTORNO, la clase se vuelve taller de Docker, sin culpa. Bloque B se contesta operando el lab 05.");

// ───────────────────────────── 6 · RECON IDEA ─────────────────────────
s=p.addSlide(); bg(s);
eyebrow(s,"Lab 05 · Reconocimiento",M,0.55,CW,AM);
title(s,"Recon: mirar antes de tocar",M,0.95,CW,34);
s.addText("El ladrón mira la casa una semana antes de entrar: qué puertas hay, cuáles cierran mal, cuándo no hay nadie. Eso es recon. Y es el 80% del trabajo.",{x:M,y:2.0,w:CW,h:0.8,fontFace:SANS,fontSize:16,color:TX,margin:0});
const loop=["descubrir","identificar","clasificar","priorizar"];
loop.forEach((t,i)=>{
  const x=M+i*(2.9+0.25);
  card(s,x,3.2,2.9,1.1,S1,GR);
  s.addText((i+1)+"",{x:x+0.2,y:3.35,w:0.6,h:0.8,fontFace:MONO,fontSize:30,bold:true,color:DIM,margin:0,valign:"middle"});
  s.addText(t,{x:x+0.85,y:3.35,w:1.9,h:0.8,fontFace:SANS,fontSize:16,bold:true,color:GR,margin:0,valign:"middle"});
  if(i<3) s.addText("→",{x:x+2.9-0.02,y:3.2,w:0.3,h:1.1,fontFace:SANS,fontSize:20,color:MU,align:"center",valign:"middle",margin:0});
});
s.addText([{text:"Un puerto abierto NO es un hallazgo. ",options:{bold:true,color:AM}},{text:"Un puerto identificado y clasificado — “el 21 corre ProFTPD 1.3.5, CVE-2015-3306” — ESO es un hallazgo.",options:{color:TX}}],{x:M,y:4.8,w:CW,h:1.0,fontFace:SANS,fontSize:16,margin:0});
foot(s,"Pasivo (no hace ruido) primero; activo (nmap) después. El que escanea a lo bruto ya se anunció.");
s.addNotes("Martillar el bucle. El error del principiante: gritar 'encontré algo' cuando encontró puertos. El hallazgo aparece al clasificar.");

// ───────────────────────────── 7 · RECON TOOLS + TARGET ───────────────
s=p.addSlide(); bg(s);
eyebrow(s,"Lab 05 · El arsenal y el objetivo",M,0.55,CW,AM);
title(s,"PhantomCorp: 4 servicios, 5 flags",M,0.95,CW,30);
const tools=[["nmap","mapea puertos y versiones"],["ncat / nc","banner grabbing"],["curl -I","headers HTTP y robots.txt"],["whois / dig","recon pasivo de dominios"]];
tools.forEach((t,i)=>{ const y=2.1+i*0.62; flagchip; s.addShape(p.ShapeType.roundRect,{x:M,y,w:2.5,h:0.44,rectRadius:0.05,fill:{color:"0e1a1f"},line:{color:CY,width:0.75}}); s.addText(t[0],{x:M+0.12,y,w:2.3,h:0.44,fontFace:MONO,fontSize:13,color:CY,bold:true,margin:0,valign:"middle"}); s.addText(t[1],{x:M+2.7,y,w:3.6,h:0.44,fontFace:SANS,fontSize:13,color:TX,margin:0,valign:"middle"}); });
const svc=[["21","FTP — banner ProFTPD (clasificar vs CVE)"],["80","Web — headers que filtran + robots.txt"],["8080","Servicio 'dev' olvidado en producción"],["31337","Mantenimiento en puerto alto 'eleet'"]];
card(s,M+6.7,2.0,CW-6.7,3.3,S1,BD);
eyebrow(s,"Superficie de PhantomCorp",M+6.9,2.2,CW-6.7-0.4,AM);
svc.forEach((v,i)=>{ const y=2.75+i*0.6; s.addText(v[0],{x:M+6.9,y,w:0.8,h:0.5,fontFace:MONO,fontSize:15,bold:true,color:AM,margin:0,valign:"middle"}); s.addText(v[1],{x:M+7.7,y,w:CW-6.7-1.2,h:0.5,fontFace:SANS,fontSize:12,color:TX,margin:0,valign:"middle"}); });
flagchip(s,"FLAG{...} × 5  — se descubren operando, no leyendo",M,4.9,6.3);
foot(s,"NO se publican puertos al host: se escanea desde la consola por la red interna de Docker.");
s.addNotes("Demo en vivo recomendada: nmap -p- phantomcorp, luego curl -I, luego /robots.txt. Mostrar cómo el header Server y el robots regalan info.");

// ───────────────────────────── 8 · ENUM IDEA ─────────────────────────
s=p.addSlide(); bg(s);
eyebrow(s,"Lab 06 · Enumeración",M,0.55,CW,AM);
title(s,"Del mapa al detalle: sacarle TODO a cada servicio",M,0.95,CW,28);
s.addText("El recon te dijo 'hay un servidor web'. ¿Y ahora? Un web server no es una cosa: son decenas de rutas, archivos y métodos que NO están en el index. Enumerar es preguntar por lo oculto.",{x:M,y:2.0,w:CW,h:0.9,fontFace:SANS,fontSize:16,color:TX,margin:0});
const en=[["Directorios","/backup que nadie linkeó",CY],[".git expuesto","el código fuente completo",RD],["Métodos HTTP","PUT habilitado = subir shell",AM],["API de usuarios","lista de users y roles",VI],["Fingerprint","PhantomCMS 3.7 exacto",GR]];
const ew=(CW-4*0.25)/5;
en.forEach((e,i)=>{ const x=M+i*(ew+0.25); card(s,x,3.1,ew,2.3,S1,e[2]); s.addText(e[0],{x:x+0.15,y:3.3,w:ew-0.3,h:0.8,fontFace:SANS,fontSize:14,bold:true,color:e[2],margin:0,valign:"top"}); s.addText(e[1],{x:x+0.15,y:4.2,w:ew-0.3,h:1.0,fontFace:SANS,fontSize:12,color:TX,margin:0,valign:"top"}); });
s.addText("Diferencia entre 'hay un web server' y 'hay un web server con /backup, .git filtrado, API de usuarios y PUT habilitado'. Lo segundo es un PLAN DE ATAQUE.",{x:M,y:5.7,w:CW,h:0.7,fontFace:SANS,fontSize:14,italic:true,color:GR,margin:0});
foot(s,"Tools: dirb / gobuster · whatweb · nmap NSE · curl. 5 flags, cada una una técnica distinta.");
s.addNotes("El robots.txt, que le pedís a Google que NO indexe, es un mapa de rutas sensibles para el atacante. La ironía más vieja del libro.");

// ───────────────────────────── 9 · EJERCICIOS NUEVOS ──────────────────
s=p.addSlide(); bg(s);
eyebrow(s,"Ejercicios nuevos de la clase",M,0.55,CW,VI);
title(s,"Estos no se capturan. Se razonan.",M,0.95,CW,32);
s.addText("Capturar una flag demuestra que PUDISTE. Clasificar lo que encontraste demuestra que ENTENDISTE. Casi sin flags: acá se paga criterio.",{x:M,y:1.95,w:CW,h:0.7,fontFace:SANS,fontSize:15,color:TX,margin:0});
const ex=[["E05 · Recon pasivo primero","inferir sin escanear + el comentario olvidado"],["E05 · El puerto que cuenta una historia","31337: por qué desconfiar, qué CIA amenaza"],["E05 · Mapa con PRIORIDAD, no lista","exposición × impacto → a quién pegar primero"],["E06 · Del .git a la intención","qué más pedirías y qué revela cada archivo"],["E06 · PUT = webshell (en teoría)","la cadena método→RCE, sin ejecutarla"],["E06 · La API que habla de más","plan de ataque priorizado para el lab 07"]];
ex.forEach((e,i)=>{ const x=M+(i%2)*(colW+0.5), y=2.8+Math.floor(i/2)*1.05; card(s,x,y,colW,0.9,S1,BD); s.addText(e[0],{x:x+0.25,y:y+0.12,w:colW-0.5,h:0.35,fontFace:MONO,fontSize:12.5,bold:true,color:VI,margin:0,valign:"middle"}); s.addText(e[1],{x:x+0.25,y:y+0.46,w:colW-0.5,h:0.35,fontFace:SANS,fontSize:12,color:MU,margin:0,valign:"middle"}); });
foot(s,"docs/EJERCICIOS-CLASE-05-06.md · se corrige criterio, no cantidad. 3 líneas bien fundadas > media carilla de relleno.");
s.addNotes("Para los grupos LISTO: que no aflojen. Estos ejercicios son el puente real recon/enum → explotación.");

// ───────────────────────────── 10 · USO RESPONSABLE ───────────────────
s=p.addSlide(); bg(s);
s.addShape(p.ShapeType.rect,{x:0,y:0,w:0.12,h:H,fill:{color:RD},line:{width:0}});
eyebrow(s,"La regla que no se negocia",M,0.7,CW,RD);
title(s,"Esto es un delito fuera del laboratorio",M,1.15,CW,30);
s.addText([
  {text:"Todo",options:{bold:true,color:RD}},
  {text:" se practica EXCLUSIVAMENTE contra los contenedores de la cátedra, en tu máquina.",options:{color:TX}},
],{x:M,y:2.3,w:CW,h:0.7,fontFace:SANS,fontSize:18,margin:0});
["Estas técnicas contra sistemas de terceros son delito en Argentina — Ley 26.388.","Nada afuera del alcance. Ni 'para probar'. Ni un ping a un dominio ajeno.","Operar fuera del alcance = causal de rechazo automático del lab.","El pentester profesional trabaja con autorización escrita. Siempre."].forEach((t,i)=>{
  s.addText("›  "+t,{x:M,y:3.2+i*0.62,w:CW,h:0.5,fontFace:SANS,fontSize:15,color:TX,margin:0,valign:"middle"});
});
foot(s,"Ver CONTRIBUTING.md § Uso responsable. El CI de PRs valida reglas de entrega automáticamente.");
s.addNotes("No pasar rápido por esta diapo. Es la frontera ética y legal del curso. El target es nuestro; el mundo, no.");

// ───────────────────────────── 11 · LA PEDIDA ─────────────────────────
s=p.addSlide(); bg(s);
eyebrow(s,"Qué entregan de esta clase",M,0.55,CW,GR);
title(s,"La pedida — concreta y alcanzable",M,0.95,CW,32);
const ask=[
  ["TODOS","1","Línea RESULTADO del diagnóstico, pegada en el PR",AM],
  ["TODOS","2","Lab 05 completo: 5 flags + mapa de superficie (la nota)",GR],
  ["TODOS","3","Lab 06 arrancado: al menos R1 (directorios) y R2 (.git)",GR],
  ["LISTO","4","Un ejercicio nuevo de EJERCICIOS-CLASE-05-06.md",VI],
  ["REPASAR","!","Cerrar labs 01-03 primero. El diagnóstico te dice qué tema",RD],
];
ask.forEach((a,i)=>{ const y=2.15+i*0.82; card(s,M,y,CW,0.68,S1,BD); s.addShape(p.ShapeType.roundRect,{x:M+0.2,y:y+0.14,w:1.4,h:0.4,rectRadius:0.05,fill:{color:"0e1a1f"},line:{color:a[3],width:0.75}}); s.addText(a[0],{x:M+0.2,y:y+0.14,w:1.4,h:0.4,fontFace:MONO,fontSize:10.5,bold:true,color:a[3],align:"center",margin:0,valign:"middle"}); s.addText(a[1],{x:M+1.8,y,w:0.5,h:0.68,fontFace:MONO,fontSize:18,bold:true,color:a[3],margin:0,valign:"middle"}); s.addText(a[2],{x:M+2.4,y,w:CW-2.6,h:0.68,fontFace:SANS,fontSize:14.5,color:TX,margin:0,valign:"middle"}); });
foot(s,"Las flags enganchan; el informe es lo que evalúa la rúbrica. Entrega por fork + PR, grupos de 4-5.");
s.addNotes("Alcanzable a propósito: el curso viene atrasado. Mejor que recuperen ritmo con algo que pueden cerrar, que mandarlos a lab 07 y que se frustren.");

// ───────────────────────────── 12 · CIERRE ─────────────────────────────
s=p.addSlide(); bg(s);
s.addShape(p.ShapeType.rect,{x:0,y:H-0.06,w:W,h:0.06,fill:{color:GR},line:{width:0}});
eyebrow(s,"A trabajar",M,1.3,CW,GR);
s.addText("A romper PhantomCorp.",{x:M,y:2.0,w:CW,h:1.0,fontFace:SANS,fontSize:48,bold:true,color:TX,margin:0});
s.addText("Con método. Con criterio. Y sabiendo por qué funciona cada cosa.",{x:M,y:3.2,w:CW,h:0.5,fontFace:SANS,fontSize:18,italic:true,color:MU,margin:0});
term(s,M,4.0,7.2,[
  {t:"$ ./ctf lab 05 && make shell",c:GR},
  {t:"$ nmap -p- phantomcorp",c:TX},
  {t:"$ curl -I http://phantomcorp",c:TX},
  {t:"# el 80% del trabajo es mirar bien",c:DIM},
]);
s.addText("github.com/fboiero/LabsSeguridadInformatica2026",{x:M,y:H-0.95,w:CW,h:0.35,fontFace:MONO,fontSize:13,color:CY,margin:0});
foot(s,"Dudas: un Issue en el repo. Es público y la respuesta le sirve a todo el curso.");
s.addNotes("Cerrar con energía. Repasar la pedida. Recordar: hoy diagnosticamos, arrancamos recon+enum, y la próxima quiero el lab 05 cerrado.");

p.writeFile({fileName: path.join(__dirname, "..", "..", "clase-05-06-cruce-ofensiva.pptx")}).then(f=>console.log("OK deck:",f));
