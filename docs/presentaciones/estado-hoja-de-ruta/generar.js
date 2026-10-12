// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
// Deck de ESTADO + HOJA DE RUTA para mostrar en clase (dónde estamos, qué falta, fechas).
// Uso:  npm install && npm run build     Salida: docs/estado-y-hoja-de-ruta.pptx
const path = require("path");
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";
p.author = "Ing. Fernando Boiero";
p.company = "CyberLab UTN FRVM";
p.title = "Estado del curso + hoja de ruta";

const BG="0a0e12",S1="111a22",BD="213039",BD2="2c404c";
const TX="cdd8de",MU="7c909b",DIM="556570";
const GR="39d98a",CY="4cc9f0",AM="f0b429",VI="b19cf0",RD="e0645b";
const MONO="Courier New",SANS="Calibri";
const W=13.333,H=7.5,M=0.62,CW=W-2*M;

const bg=s=>s.background={color:BG};
const eyebrow=(s,t,y,c)=>s.addText(t.toUpperCase(),{x:M,y,w:CW,h:0.3,fontFace:MONO,fontSize:11,color:c||GR,charSpacing:3,bold:true,margin:0,valign:"middle"});
const title=(s,t,y,sz)=>s.addText(t,{x:M,y,w:CW,h:0.85,fontFace:SANS,fontSize:sz||34,bold:true,color:TX,margin:0,valign:"middle"});
const card=(s,x,y,w,h,f,l)=>s.addShape(p.ShapeType.roundRect,{x,y,w,h,rectRadius:0.09,fill:{color:f||S1},line:{color:l||BD,width:1}});
const foot=(s,t)=>s.addText(t,{x:M,y:H-0.5,w:CW,h:0.3,fontFace:MONO,fontSize:10,color:DIM,margin:0,valign:"middle"});

// ───── 1 · COVER ─────
let s=p.addSlide(); bg(s);
s.addShape(p.ShapeType.rect,{x:0,y:0,w:W,h:0.06,fill:{color:GR},line:{width:0}});
eyebrow(s,"CyberLab UTN FRVM · Estado del curso",0.9,GR);
s.addText("¿Dónde estamos?\n¿Qué falta?",{x:M,y:2.0,w:CW,h:2.0,fontFace:SANS,fontSize:52,bold:true,color:TX,margin:0,lineSpacingMultiple:0.95});
s.addText("Hoja de ruta y fechas para llegar bien al final.",{x:M,y:4.3,w:CW,h:0.5,fontFace:SANS,fontSize:18,italic:true,color:MU,margin:0});
s.addText([{text:"Viernes 09/10/2026",options:{color:GR,bold:true}},{text:"   ·   arranca el Bloque 2: ofensiva a mano",options:{color:MU}}],{x:M,y:5.1,w:CW,h:0.4,fontFace:MONO,fontSize:16,margin:0});
s.addText("Ing. Fernando Boiero · UTN FRVM · 2026",{x:W-5.3,y:H-0.55,w:4.7,h:0.3,fontFace:MONO,fontSize:11,color:DIM,align:"right",margin:0});
s.addNotes("Deck de reencuadre. Objetivo: que vean el mapa completo, dónde están parados, qué deben y cuándo. Honesto pero motivador.");

// ───── 2 · EL ARCO ─────
s=p.addSlide(); bg(s);
eyebrow(s,"El recorrido completo",0.55);
title(s,"4 bloques · 11 labs + final",0.95,30);
const bl=[["B1 · Fundamentos",CY,"01 02 03 04","código"],["B2 · Ofensiva a mano",AM,"05 06 07 08","Docker · acá vamos"],["B3 · Agentes + Defensa",GR,"09 10","IA + Blue/Red"],["B4 · Integración",VI,"11 + Final","forensia + engagement"]];
const bw=(CW-3*0.3)/4;
bl.forEach((b,i)=>{const x=M+i*(bw+0.3);card(s,x,2.3,bw,3.1,S1,i===1?AM:BD);
  s.addText(b[0].toUpperCase(),{x:x+0.2,y:2.5,w:bw-0.4,h:0.5,fontFace:MONO,fontSize:11,bold:true,color:b[1],charSpacing:1,margin:0,valign:"top"});
  s.addText(b[2],{x:x+0.2,y:3.15,w:bw-0.4,h:0.7,fontFace:MONO,fontSize:20,bold:true,color:b[1],margin:0,valign:"middle"});
  s.addText(b[3],{x:x+0.2,y:3.95,w:bw-0.4,h:0.6,fontFace:SANS,fontSize:13,color:TX,margin:0,valign:"top"});
  if(i===1)s.addText("◀ HOY",{x:x+0.2,y:4.95,w:bw-0.4,h:0.35,fontFace:MONO,fontSize:12,bold:true,color:AM,margin:0});});
foot(s,"Un solo hilo: la auditoría de PhantomCorp S.A. atraviesa todo el bloque ofensivo.");
s.addNotes("Recordar la filosofía: manual (05-08) antes que agentes (09). No se dirige un agente que hace lo que no sabés hacer.");

// ───── 3 · DÓNDE ESTAMOS (honesto) ─────
s=p.addSlide(); bg(s);
eyebrow(s,"La foto, sin maquillaje",0.55,AM);
title(s,"Dónde estamos de verdad",0.95,32);
const col=(CW-0.5)/2;
card(s,M,2.1,col,3.7,S1,CY);
s.addText("EN CLASE vimos",{x:M+0.3,y:2.35,w:col-0.6,h:0.35,fontFace:MONO,fontSize:12,bold:true,color:CY,charSpacing:1,margin:0});
["Bloque 1 completo (labs 01-04)","Fundamentos: CIA, hashing, cripto,","auth y gestión de riesgo","Hoy arrancamos recon + enum (05-06)"].forEach((t,i)=>s.addText(t,{x:M+0.3,y:2.85+i*0.52,w:col-0.6,h:0.45,fontFace:SANS,fontSize:14,color:TX,margin:0,valign:"middle"}));
card(s,M+col+0.5,2.1,col,3.7,"14110d",AM);
s.addText("PERO en ENTREGAS",{x:M+col+0.8,y:2.35,w:col-0.6,h:0.35,fontFace:MONO,fontSize:12,bold:true,color:AM,charSpacing:1,margin:0});
["El grueso entregó hasta lab 01-02","Hace ~3 semanas que no entra nada","Hay una deuda que cerrar YA","La clase corre; la entrega quedó atrás"].forEach((t,i)=>s.addText("› "+t,{x:M+col+0.8,y:2.85+i*0.52,w:col-0.6,h:0.45,fontFace:SANS,fontSize:14,color:TX,margin:0,valign:"middle"}));
s.addText("La buena: nada está perdido. La exigente: es AHORA. Lo que viene se para sobre lo que ya debíamos tener cerrado.",{x:M,y:6.05,w:CW,h:0.6,fontFace:SANS,fontSize:15,italic:true,bold:true,color:GR,margin:0});
s.addNotes("No es para humillar: es para que vean el gap y reaccionen. Decir claro que el bloque 2 exige el bloque 1 cerrado.");

// ───── 4 · QUÉ FALTA ─────
s=p.addSlide(); bg(s);
eyebrow(s,"Lo que queda por delante",0.55,VI);
title(s,"Qué falta",0.95,34);
const rows=[["Bloque 1 · código","01 ✓   02 ✓   03 ✓   04 ✓","visto en clase — falta CERRAR entregas",CY],
["Bloque 2 · ofensiva","05 · 06 (HOY)   07   08","recon, enum, explotación, post-expl.",AM],
["Bloque 3 · agentes+def","09   10","agentes de IA + detección/evasión",GR],
["Bloque 4 · integración","11   +   FINAL","forensia + engagement completo",VI]];
rows.forEach((r,i)=>{const y=2.2+i*1.0;card(s,M,y,CW,0.85,S1,BD);
  s.addText(r[0],{x:M+0.25,y:y+0.1,w:3.3,h:0.65,fontFace:SANS,fontSize:14,bold:true,color:r[3],margin:0,valign:"middle"});
  s.addText(r[1],{x:M+3.7,y:y+0.1,w:4.0,h:0.65,fontFace:MONO,fontSize:15,color:TX,margin:0,valign:"middle"});
  s.addText(r[2],{x:M+7.8,y:y+0.1,w:CW-8.0,h:0.65,fontFace:SANS,fontSize:12.5,color:MU,margin:0,valign:"middle"});});
foot(s,"Las flags enganchan; el informe es lo que evalúa la rúbrica. Entrega por fork + PR, grupos de 4-5.");
s.addNotes("Mapa de deuda. Enfatizar que 01-04 hay que cerrarlos aunque la clase avance — tienen fecha límite (slide siguiente).");

// ───── 5 · EL CALENDARIO (estrella) ─────
s=p.addSlide(); bg(s);
eyebrow(s,"La hoja de ruta · viernes 18:30",0.5,GR);
title(s,"El calendario hasta el final",0.9,30);
const cal=[
["09/10","Lab 05 + 06 — Reconocimiento + Enumeración","HOY",GR],
["16/10","Lab 07 — Explotación · parte 1","",TX],
["23/10","Lab 07 — Explotación · parte 2","",TX],
["30/10","Lab 08 — Post-explotación · parte 1","",TX],
["06/11","Lab 08 — Post-explotación · parte 2","LÍMITE 01-04",AM],
["13/11","Lab 09 — Agentes de pentest","",TX],
["20/11","Lab 10 — Detección / Evasión","",TX],
["27/11","Lab 11 — Forensia (DFIR)","",TX],
["04/12","Práctico FINAL — engagement + informe","ENTREGA",VI]];
const ry=1.95, rh=0.52;
cal.forEach((r,i)=>{const y=ry+i*rh; const hoy=r[2]==="HOY";
  if(hoy) card(s,M,y,CW,rh-0.08,"10241c",GR);
  s.addText(r[0],{x:M+0.15,y,w:1.1,h:rh-0.08,fontFace:MONO,fontSize:14,bold:true,color:r[3],margin:0,valign:"middle"});
  s.addShape(p.ShapeType.ellipse,{x:M+1.35,y:y+(rh-0.08)/2-0.05,w:0.1,h:0.1,fill:{color:r[3]},line:{width:0}});
  s.addText(r[1],{x:M+1.65,y,w:CW-1.65-2.4,h:rh-0.08,fontFace:SANS,fontSize:13.5,color:hoy?TX:TX,bold:hoy,margin:0,valign:"middle"});
  if(r[2]&&!hoy){s.addShape(p.ShapeType.roundRect,{x:W-M-2.2,y:y+0.04,w:2.2,h:rh-0.16,rectRadius:0.04,fill:{color:"14110d"},line:{color:r[3],width:0.75}});s.addText(r[2],{x:W-M-2.2,y:y+0.04,w:2.2,h:rh-0.16,fontFace:MONO,fontSize:10.5,bold:true,color:r[3],align:"center",margin:0,valign:"middle"});}
  if(hoy)s.addText("HOY",{x:W-M-2.2,y,w:2.2,h:rh-0.08,fontFace:MONO,fontSize:11,bold:true,color:GR,align:"center",margin:0,valign:"middle"});});
foot(s,"Ritmo holgado: los labs 07 y 08 (los más duros) se llevan dos clases. Fechas sujetas a feriados/paros.");
s.addNotes("LA slide. Dos hitos que tienen que quedar grabados: 06/11 límite para cerrar 01-04, y 04/12 entrega del final. 07 y 08 van en 2 clases c/u por ser los más pesados.");

// ───── 6 · TUS DOS DEUDAS ─────
s=p.addSlide(); bg(s);
eyebrow(s,"Lo que tenés que hacer",0.55,AM);
title(s,"Tus dos tareas, en paralelo",0.95,32);
card(s,M,2.2,col,3.5,"14110d",RD);
s.addText("1 · PONERTE AL DÍA",{x:M+0.3,y:2.45,w:col-0.6,h:0.4,fontFace:MONO,fontSize:14,bold:true,color:RD,charSpacing:1,margin:0});
s.addText("Cerrá los labs 01-04.",{x:M+0.3,y:2.95,w:col-0.6,h:0.45,fontFace:SANS,fontSize:17,bold:true,color:TX,margin:0});
["Son la base de todo lo que viene.","Fecha límite: viernes 06/11.","Después de esa fecha, baja de la nota.","El diagnóstico te dice qué tema repasar."].forEach((t,i)=>s.addText("› "+t,{x:M+0.3,y:3.55+i*0.5,w:col-0.6,h:0.45,fontFace:SANS,fontSize:13.5,color:TX,margin:0,valign:"middle"}));
card(s,M+col+0.5,2.2,col,3.5,"10241c",GR);
s.addText("2 · SEGUIR EL RITMO",{x:M+col+0.8,y:2.45,w:col-0.6,h:0.4,fontFace:MONO,fontSize:14,bold:true,color:GR,charSpacing:1,margin:0});
s.addText("Arrancá recon + enum HOY.",{x:M+col+0.8,y:2.95,w:col-0.6,h:0.45,fontFace:SANS,fontSize:17,bold:true,color:TX,margin:0});
["Lab 05 completo + Lab 06 arrancado.","Corré el diagnóstico de clase primero.","Un lab nuevo cada semana (ver fechas).","No dejes que se te amontone al final."].forEach((t,i)=>s.addText("› "+t,{x:M+col+0.8,y:3.55+i*0.5,w:col-0.6,h:0.45,fontFace:SANS,fontSize:13.5,color:TX,margin:0,valign:"middle"}));
s.addText("Sí, las dos a la vez. El que se queda esperando a cerrar lo viejo para empezar lo nuevo, llega tarde a los dos.",{x:M,y:6.0,w:CW,h:0.6,fontFace:SANS,fontSize:14,italic:true,color:AM,margin:0});
s.addNotes("Dejar clarísimo: no es 'primero termino lo viejo y después empiezo'. Es en paralelo. 06/11 es la fecha dura de los atrasados.");

// ───── 7 · CÓMO NO PERDERTE ─────
s=p.addSlide(); bg(s);
eyebrow(s,"Herramientas para no perderte",0.55,CY);
title(s,"Tres comandos y estás al día",0.95,30);
const cmds=[["Sincronizá tu fork","git fetch upstream && git merge upstream/main","traé la clase de hoy y el diagnóstico"],
["Medí dónde estás","python3 bin/diagnostico.py mi-diagnostico.txt","5 min: te dice si estás listo o te falta base"],
["Mirá tu progreso","./ctf status 05","qué flags llevás y qué te falta en cada lab"]];
cmds.forEach((c,i)=>{const y=2.2+i*1.3;card(s,M,y,CW,1.1,S1,BD);
  s.addText((i+1)+"",{x:M+0.25,y:y+0.2,w:0.6,h:0.7,fontFace:MONO,fontSize:28,bold:true,color:DIM,margin:0,valign:"middle"});
  s.addText(c[0],{x:M+1.0,y:y+0.15,w:CW-1.3,h:0.4,fontFace:SANS,fontSize:16,bold:true,color:GR,margin:0,valign:"middle"});
  s.addShape(p.ShapeType.roundRect,{x:M+1.0,y:y+0.55,w:7.2,h:0.4,rectRadius:0.04,fill:{color:"080c10"},line:{color:BD2,width:0.75}});
  s.addText("$ "+c[1],{x:M+1.15,y:y+0.55,w:7.0,h:0.4,fontFace:MONO,fontSize:11.5,color:CY,margin:0,valign:"middle"});
  s.addText(c[2],{x:M+8.4,y:y+0.55,w:CW-8.6,h:0.4,fontFace:SANS,fontSize:12,italic:true,color:MU,margin:0,valign:"middle"});});
foot(s,"¿Dudas? Un Issue en el repo. Es público y la respuesta le sirve a todo el curso.");
s.addNotes("Práctico. Si no tienen upstream, el comando para agregarlo está en NOVEDADES.md y CONTRIBUTING.md.");

// ───── 8 · CIERRE ─────
s=p.addSlide(); bg(s);
s.addShape(p.ShapeType.rect,{x:0,y:H-0.06,w:W,h:0.06,fill:{color:GR},line:{width:0}});
eyebrow(s,"No aflojen ahora",1.3,GR);
s.addText("Lo que viene es lo que\nviniste a aprender.",{x:M,y:2.1,w:CW,h:1.8,fontFace:SANS,fontSize:44,bold:true,color:TX,margin:0,lineSpacingMultiple:0.98});
s.addText("Recon, explotación, agentes, forensia. Todo sobre la base que ya tienen. Pónganse al día y no suelten el ritmo.",{x:M,y:4.3,w:CW-3.5,h:0.9,fontFace:SANS,fontSize:16,italic:true,color:MU,margin:0});
s.addText("github.com/fboiero/LabsSeguridadInformatica2026",{x:M,y:H-1.0,w:CW,h:0.35,fontFace:MONO,fontSize:13,color:CY,margin:0});
s.addText([{text:"Próximo hito:  ",options:{color:MU}},{text:"06/11 — labs 01-04 cerrados",options:{color:AM,bold:true}}],{x:M,y:5.5,w:CW,h:0.4,fontFace:MONO,fontSize:15,margin:0});
foot(s,"Hoy: diagnóstico + recon + enumeración. La próxima quiero el lab 05 cerrado.");
s.addNotes("Cerrar con energía. Repetir los dos hitos: 06/11 atrasados, 04/12 final. Dale que ahora empieza lo bueno.");

p.writeFile({fileName: path.join(__dirname,"..","..","estado-y-hoja-de-ruta.pptx")}).then(f=>console.log("OK deck:",f));
