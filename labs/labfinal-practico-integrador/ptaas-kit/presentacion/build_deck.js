const pptxgen = require("pptxgenjs");
const { applyTheme } = require("./apply_theme.js");

const THEME = {
  name: "PTaaS Ink",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "101820", lt1: "FFFFFF", dk2: "1F3B4D", lt2: "EEF2F5",
    accent1: "0E9F8E", accent2: "F2A900", accent3: "D64550",
    accent4: "5B7C99", accent5: "7A5CFA", accent6: "2E7D32",
    hlink: "0E9F8E", folHlink: "5B7C99",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "PTaaS — El desafío";
pres.author = "Fernando Boiero";
const C = pres.SchemeColor;

// ---------- Layouts ----------
pres.defineSlideMaster({
  title: "LIGHT",
  background: { color: C.background1 },
  objects: [
    { text: { text: "PTaaS · Trabajo práctico", options: { x: 0.5, y: 5.2, w: 5, h: 0.25, fontSize: 10, color: C.accent4, margin: 0, isTextBox: true } } },
  ],
  slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.25, fontSize: 10, color: C.accent4, align: "right" },
  placeholders: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.8, fontSize: 32, bold: true, color: C.text1, margin: 0, valign: "middle" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "DARK",
  background: { color: C.text1 },
  objects: [
    { text: { text: "PTaaS · Trabajo práctico", options: { x: 0.5, y: 5.2, w: 5, h: 0.25, fontSize: 10, color: C.accent4, margin: 0, isTextBox: true } } },
  ],
  slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.25, fontSize: 10, color: C.accent4, align: "right" },
  placeholders: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.8, fontSize: 32, bold: true, color: C.background1, margin: 0, valign: "middle" }, text: "" } },
  ],
});

// ---------- Helpers ----------
const light = () => pres.addSlide({ masterName: "LIGHT" });
const dark = () => pres.addSlide({ masterName: "DARK" });

function card(s, name, x, y, w, h, fill = C.background2) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, line: { color: fill, width: 0 }, rectRadius: 0.08, objectName: name });
}
function badge(s, name, x, y, d, label, fill = C.accent1, fs = 14, color = C.background1) {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0 }, objectName: name });
  s.addText(label, { x, y, w: d, h: d, align: "center", valign: "middle", fontSize: fs, bold: true, color, margin: 0, isTextBox: true, objectName: name + " texto" });
}
function txt(s, name, text, x, y, w, h, o = {}) {
  s.addText(text, Object.assign({ x, y, w, h, fontSize: 14, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: name }, o));
}


function title(s, text, onDark = false) {
  s.addText(text, { placeholder: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.8, fontSize: 32, bold: true, color: onDark ? C.background1 : C.text1, margin: 0, valign: "middle", objectName: "Título" });
}

// ---------- 1. Portada ----------
{
  const s = dark();
  s.addNotes("Presentar el desafío: construir, con agentes, una plataforma de pentest AUTORIZADO. El foco no es atacar, es diseñar el control.");
  s.addShape(pres.ShapeType.ellipse, { x: 7.0, y: 0.9, w: 2.8, h: 2.8, fill: { color: C.accent1, transparency: 70 }, line: { color: C.accent1, width: 0 }, objectName: "Motivo círculo grande" });
  s.addShape(pres.ShapeType.ellipse, { x: 8.2, y: 2.9, w: 1.4, h: 1.4, fill: { color: C.accent2, transparency: 30 }, line: { color: C.accent2, width: 0 }, objectName: "Motivo círculo ámbar" });
  txt(s, "Etiqueta", "TRABAJO PRÁCTICO · SEGURIDAD INFORMÁTICA", 0.5, 1.2, 6.2, 0.3, { fontSize: 12, color: C.accent1, bold: true, charSpacing: 2 });
  s.addText("Pentest as a Service con un swarm de agentes", { x: 0.5, y: 1.6, w: 6.3, h: 1.7, fontSize: 38, bold: true, color: C.background1, margin: 0, valign: "top", fontFace: "Cambria", isTextBox: true, objectName: "Título" });
  txt(s, "Subtítulo", "El desafío: diseñar el swarm, el harness que lo gobierna y los loops agénticos", 0.5, 3.5, 6.0, 0.9, { fontSize: 18, color: C.background2 });
  txt(s, "Autor", "Fernando Boiero · UTN FRVM · Xcapit", 0.5, 4.7, 6, 0.3, { fontSize: 12, color: C.accent4 });
}

// ---------- 2. El desafío ----------
{
  const s = light();
  s.addNotes("El desafío en una frase y tres números: 8 agentes, 3 loops, 3 criterios de aceptación que se pueden verificar con tests.");
  title(s, "El desafío");
  txt(s, "Enunciado", "Construí un pentest autorizado de punta a punta, donde la autorización y la trazabilidad las garantiza el sistema, no la buena voluntad del agente.", 0.5, 1.3, 9.0, 0.9, { fontSize: 18 });
  const stats = [["8", "agentes con mandato acotado", C.accent1], ["3", "loops agénticos con tope y parada", C.accent2], ["3", "criterios de aceptación verificables", C.accent3]];
  stats.forEach(([n, l, col], i) => {
    const x = 0.5 + i * 3.05;
    card(s, `Tarjeta ${i + 1}`, x, 2.5, 2.9, 2.2);
    txt(s, `Número ${i + 1}`, n, x + 0.25, 2.65, 2.4, 1.1, { fontSize: 66, bold: true, color: col, fontFace: "Cambria" });
    txt(s, `Etiqueta ${i + 1}`, l, x + 0.25, 3.85, 2.4, 0.7, { fontSize: 14 });
  });
}

// ---------- 3. Premisa ----------
{
  const s = light();
  s.addNotes("Esta es la regla que no se negocia. Sin RoE vigente no hay fase activa. Cada control es código verificable.");
  title(s, "Premisa: solo pentest autorizado");
  const items = [
    ["RoE firmado", "Alcance, ventana temporal, exclusiones y contactos de emergencia."],
    ["Scope token", "Corto, por fase y por activo. Sin token vivo no hay acción."],
    ["Kill switch", "Detiene todo el engagement desde cualquier estado."],
    ["Bitácora inmutable", "Quién, qué, cuándo, sobre qué activo, bajo qué token y con qué resultado."],
  ];
  items.forEach(([t, d], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.4 + Math.floor(i / 2) * 1.85;
    card(s, `Tarjeta ${t}`, x, y, 4.4, 1.7);
    badge(s, `Número ${t}`, x + 0.25, y + 0.3, 0.55, String(i + 1));
    txt(s, `Título ${t}`, t, x + 1.0, y + 0.25, 3.2, 0.4, { fontSize: 18, bold: true });
    txt(s, `Detalle ${t}`, d, x + 1.0, y + 0.7, 3.2, 0.9, { fontSize: 14 });
  });
}

// ---------- 4. Estándares ----------
{
  const s = light();
  s.addNotes("No inventamos una metodología: implementamos de forma agéntica PTES, NIST 800-115, OWASP WSTG, OSSTMM, CVSS v4 y CWE.");
  title(s, "Estándares que guían el flujo");
  const h = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 }, fontSize: 13 } });
  const r = (a, b, c) => [a, b, c].map((t, i) => ({ text: t, options: { fontSize: 13, bold: i === 0, color: C.text1, fill: { color: C.background1 } } }));
  s.addTable([
    [h("Fase PTES"), h("Estándar / referencia"), h("Agente")],
    r("Pre-engagement", "RoE, ISO/IEC 27001 (contexto)", "Scope Guard"),
    r("Intelligence gathering", "PTES §2, OSSTMM", "Recon"),
    r("Threat modeling", "MITRE ATT&CK, CWE, EPSS", "Correlación"),
    r("Vulnerability analysis", "NIST SP 800-115, OWASP WSTG", "Análisis"),
    r("Validación controlada", "PTES §5, solo catálogo en sandbox", "Validación"),
    r("Reporting", "CVSS v4.0, ISO/IEC 29147 y 30111", "Reporting"),
  ], { x: 0.5, y: 1.35, w: 9.0, colW: [2.6, 4.4, 2.0], rowH: 0.5, border: { type: "solid", color: C.background2, pt: 1 }, valign: "middle", margin: [0, 0.12, 0, 0.12], objectName: "Tabla de estándares" });
}

// ---------- 5. Swarm ----------
{
  const s = light();
  s.addNotes("Patrón orquestador-trabajadores. El Scope Guard es CÓDIGO determinista, no un LLM. Humano en los puntos de mayor riesgo.");
  title(s, "El swarm: 8 roles, un mandato cada uno");
  s.addShape(pres.ShapeType.roundRect, { x: 3.4, y: 1.25, w: 3.2, h: 0.65, fill: { color: C.text2 }, line: { color: C.text2, width: 0 }, rectRadius: 0.08, objectName: "Orchestrator" });
  txt(s, "Orchestrator texto", "Orchestrator / Planner", 3.4, 1.25, 3.2, 0.65, { fontSize: 14, bold: true, color: C.background1, align: "center", valign: "middle" });
  const w = 1.4, gap = 0.12, y0 = 2.55;
  const ws = [["Scope Guard", "código, no LLM", C.accent3], ["Recon", "grafo de activos", C.accent1], ["Correlación", "CVE · CWE · EPSS", C.accent1], ["Análisis", "no destructivo", C.accent1], ["Validación", "catálogo + sandbox", C.accent2], ["Reporting", "CVSS v4 + CWE", C.accent1]];
  const line = (x1, y1, x2, y2) => s.addShape(pres.ShapeType.line, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), line: { color: C.accent4, width: 1.25 } });
  line(5.0, 1.9, 5.0, 2.25);
  line(0.5 + w / 2, 2.25, 0.5 + 5 * (w + gap) + w / 2, 2.25);
  ws.forEach(([n, d, col], i) => {
    const x = 0.5 + i * (w + gap);
    line(x + w / 2, 2.25, x + w / 2, y0);
    card(s, `Agente ${n}`, x, y0, w, 1.5);
    s.addShape(pres.ShapeType.ellipse, { x: x + w / 2 - 0.2, y: y0 + 0.15, w: 0.4, h: 0.4, fill: { color: col }, line: { color: col, width: 0 }, objectName: `Icono ${n}` });
    txt(s, `Nombre ${n}`, n, x + 0.05, y0 + 0.7, w - 0.1, 0.35, { fontSize: 13, bold: true, align: "center" });
    txt(s, `Rol ${n}`, d, x + 0.05, y0 + 1.05, w - 0.1, 0.35, { fontSize: 10, color: C.text2, align: "center" });
  });
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 4.3, w: 9.0, h: 0.6, fill: { color: C.accent2 }, line: { color: C.accent2, width: 0 }, rectRadius: 0.08, objectName: "Barra Reviewer" });
  txt(s, "Reviewer texto", "Reviewer humano · gates: 1ª acción activa · validar cada hallazgo · entregar el informe", 0.6, 4.3, 8.8, 0.6, { fontSize: 14, bold: true, align: "center", valign: "middle" });
}

// ---------- 6. Harness ----------
{
  const s = light();
  s.addNotes("Todo pasa por Harness.invoke. Ningún agente ejecuta una herramienta directamente. Autorización y trazabilidad son invariantes.");
  title(s, "El harness: un único camino");
  const steps = ["Kill switch", "Token vivo", "Guard (alcance y fase)", "Gate humano", "Adaptador tipado", "Bitácora"];
  const w = 1.4, gap = 0.12;
  steps.forEach((t, i) => {
    const x = 0.5 + i * (w + gap);
    card(s, `Paso ${i + 1}`, x, 1.4, w, 1.45);
    badge(s, `Número ${i + 1}`, x + w / 2 - 0.22, 1.52, 0.44, String(i + 1), i === 2 ? C.accent3 : C.accent1, 14);
    txt(s, `Texto paso ${i + 1}`, t, x + 0.08, 2.1, w - 0.16, 0.7, { fontSize: 13, bold: true, align: "center" });
  });
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 3.15, w: 9.0, h: 1.2, fill: { color: C.text1 }, line: { color: C.text1, width: 0 }, rectRadius: 0.08, objectName: "Bloque de código" });
  s.addText([
    { text: "def invoke(agent, action, target, token):", options: { breakLine: true } },
    { text: "    killswitch → token.is_live() → guard.is_allowed()", options: { breakLine: true } },
    { text: "    → hitl.approved() → adapter.run() → audit.record(...)" },
  ], { x: 0.75, y: 3.25, w: 8.5, h: 1.0, fontFace: "Courier New", fontSize: 13, color: C.background1, margin: 0, valign: "middle", isTextBox: true, objectName: "Código invoke" });
  txt(s, "Nota", "Se registran también los intentos bloqueados. El Scope Guard es código determinista.", 0.5, 4.5, 9.0, 0.4, { fontSize: 14, color: C.text2 });
}

// ---------- 7. Loops ----------
{
  const s = light();
  s.addNotes("Cada loop es plan-act-observe-reflect. El LLM propone; el harness decide la parada. Loop C solo parametriza PoCs del catálogo.");
  title(s, "Tres loops agénticos");
  const loops = [
    ["A", "Relevamiento", "Recon ↔ Correlación", "Parar: 0 activos nuevos", "Tope: 5 iteraciones", C.accent1],
    ["B", "Detección", "Correlación ↔ Análisis", "Parar: resuelto o 2 vueltas sin evidencia nueva", "Tope: 4 iteraciones", C.accent5],
    ["C", "Validación", "Validación (con gate humano)", "Parar: evidencia suficiente", "Tope: 2 intentos", C.accent2],
  ];
  loops.forEach(([l, t, ag, stop, cap, col], i) => {
    const x = 0.5 + i * 3.05;
    card(s, `Loop ${l}`, x, 1.35, 2.9, 3.5);
    badge(s, `Letra ${l}`, x + 0.25, 1.6, 0.6, l, col, 20, l === "C" ? C.text1 : C.background1);
    txt(s, `Título loop ${l}`, t, x + 1.0, 1.7, 1.8, 0.45, { fontSize: 18, bold: true, valign: "middle" });
    txt(s, `Agentes ${l}`, ag, x + 0.25, 2.5, 2.45, 0.6, { fontSize: 14, bold: true, color: C.text2 });
    txt(s, `Parada ${l}`, stop, x + 0.25, 3.2, 2.45, 0.9, { fontSize: 14 });
    txt(s, `Tope ${l}`, cap, x + 0.25, 4.25, 2.45, 0.4, { fontSize: 14, bold: true, color: col === C.accent2 ? C.text1 : col });
  });
}

// ---------- 8. OpenSpec ----------
{
  const s = light();
  s.addNotes("La spec es la fuente de verdad. Cada Scenario es un criterio de aceptación y un test. Siempre hay un caso negativo de seguridad.");
  title(s, "Desarrollo guiado por specs (OpenSpec)");
  ["Propose: proposal, design y tasks", "Review: validación humana del delta", "Implement: el agente ejecuta tasks.md", "Archive: el delta pasa a specs/"].forEach((t, i) => {
    const y = 1.4 + i * 0.85;
    badge(s, `Paso ${i + 1}`, 0.5, y, 0.5, String(i + 1));
    txt(s, `Texto paso ${i + 1}`, t, 1.2, y, 3.4, 0.5, { fontSize: 14, valign: "middle" });
  });
  s.addShape(pres.ShapeType.roundRect, { x: 4.9, y: 1.4, w: 4.6, h: 2.9, fill: { color: C.text1 }, line: { color: C.text1, width: 0 }, rectRadius: 0.08, objectName: "Bloque Scenario" });
  s.addText([
    { text: "Requirement: Enforcement de alcance", options: { bold: true, color: C.accent1, breakLine: true } },
    { text: "DEBE bloquear toda acción activa", options: { breakLine: true } },
    { text: "fuera del RoE vigente.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Scenario: activo fuera de alcance", options: { bold: true, color: C.accent2, breakLine: true } },
    { text: "GIVEN RoE que autoriza 10.0.0.0/24", options: { breakLine: true } },
    { text: "WHEN se intenta escanear 10.0.1.5", options: { breakLine: true } },
    { text: "THEN se bloquea y queda en bitácora" },
  ], { x: 5.1, y: 1.55, w: 4.2, h: 2.6, fontFace: "Courier New", fontSize: 12, color: C.background1, margin: 0, valign: "top", isTextBox: true, objectName: "Texto Scenario" });
}

// ---------- 9. Herramientas ----------
{
  const s = light();
  s.addNotes("Criterios: licencia, salida parseable, modo no destructivo, madurez, adaptador estable. Verificar licencias antes de empaquetar (nmap usa NPSL).");
  title(s, "Selección de herramientas");
  const h = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 }, fontSize: 13 } });
  const r = (a, b, c, col) => [a, b, c].map((t, i) => ({ text: t, options: { fontSize: 13, bold: i === 0, color: col || C.text1, fill: { color: C.background1 } } }));
  s.addTable([
    [h("Fase"), h("Herramientas del MVP"), h("Control")],
    r("Recon", "subfinder · httpx · nmap", "Pasivo primero; nmap sin scripts"),
    r("Correlación", "Feeds NVD y EPSS · catálogo CWE", "Solo datos, sin tocar activos"),
    r("Análisis", "OWASP ZAP (baseline) · Nuclei", "Templates curados, sin OAST"),
    r("Validación", "Catálogo interno de verificaciones", "Inertes, en sandbox efímero"),
    r("Reporte", "DefectDojo", "CWE + CVSS v4 por hallazgo"),
    r("Descartadas", "masscan · Nikto", "Agresiva y ruidosa", C.accent3),
  ], { x: 0.5, y: 1.35, w: 9.0, colW: [1.8, 3.6, 3.6], rowH: 0.52, border: { type: "solid", color: C.background2, pt: 1 }, valign: "middle", margin: [0, 0.12, 0, 0.12], objectName: "Tabla de herramientas" });
}

// ---------- 10. Modelos ----------
{
  const s = light();
  s.addNotes("Ruteo por riesgo y volumen. La autorización nunca depende de un LLM. Cambiar modelo o prompt exige correr las evals.");
  title(s, "Qué modelo hace qué");
  const cards = [
    ["Opus 5.5", "Orchestrator · Validación", "Planifican y validan: un error es caro", C.accent5],
    ["Sonnet 5.5", "Recon · Correlación · Análisis · Reporting", "Trabajo de volumen medio con salida estructurada", C.accent1],
    ["Haiku 5.5", "Triage y parsing", "Alto volumen, bajo riesgo", C.accent4],
    ["Código y humano", "Scope Guard · Reviewer", "La autorización no es probabilística", C.accent3],
  ];
  cards.forEach(([t, who, why, col], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.4 + Math.floor(i / 2) * 1.85;
    card(s, `Tarjeta ${t}`, x, y, 4.4, 1.7);
    s.addShape(pres.ShapeType.roundRect, { x: x + 0.25, y: y + 0.22, w: 1.7, h: 0.4, fill: { color: col }, line: { color: col, width: 0 }, rectRadius: 0.2, objectName: `Etiqueta ${t}` });
    txt(s, `Nombre ${t}`, t, x + 0.25, y + 0.22, 1.7, 0.4, { fontSize: 13, bold: true, color: C.background1, align: "center", valign: "middle" });
    txt(s, `Quién ${t}`, who, x + 0.25, y + 0.75, 3.9, 0.4, { fontSize: 14, bold: true });
    txt(s, `Por qué ${t}`, why, x + 0.25, y + 1.15, 3.9, 0.45, { fontSize: 13, color: C.text2 });
  });
}

// ---------- 11. MVP ----------
{
  const s = light();
  s.addNotes("El MVP es un recorrido completo sobre un laboratorio propio aislado. Fuera del MVP: multi-tenant, post-explotación, generación de exploits.");
  title(s, "El MVP: un recorrido completo");
  const flow = ["RoE → token", "Recon", "Correlación", "Análisis", "Validar 1 hallazgo", "Informe"];
  const w = 1.4, gap = 0.12;
  flow.forEach((t, i) => {
    const x = 0.5 + i * (w + gap);
    card(s, `Etapa ${i + 1}`, x, 1.35, w, 1.0, i === 4 ? C.accent2 : C.background2);
    txt(s, `Texto etapa ${i + 1}`, t, x + 0.05, 1.35, w - 0.1, 1.0, { fontSize: 13, bold: true, align: "center", valign: "middle" });
  });
  txt(s, "Subtítulo criterios", "Criterios de aceptación", 0.5, 2.65, 9, 0.4, { fontSize: 18, bold: true });
  const crit = ["Toda acción activa tiene un scope token vivo y queda en bitácora", "Un intento fuera de alcance se bloquea y se registra", "Cada hallazgo del informe tiene CWE, CVSS v4 y remediación"];
  crit.forEach((t, i) => {
    const x = 0.5 + i * 3.05;
    card(s, `Criterio ${i + 1}`, x, 3.15, 2.9, 1.7);
    badge(s, `Check ${i + 1}`, x + 0.2, 3.3, 0.45, "✓", C.accent6, 16);
    txt(s, `Texto criterio ${i + 1}`, t, x + 0.2, 3.9, 2.55, 0.9, { fontSize: 13 });
  });
}

// ---------- 12. Entregables y rúbrica ----------
{
  const s = light();
  s.addNotes("La ponderación es una propuesta y se puede ajustar. Lo importante: se evalúa el control (harness y tests) tanto como la inteligencia de los agentes.");
  title(s, "Qué entregan y cómo se evalúa");
  s.addChart(pres.charts.BAR, [{ name: "Peso (%)", labels: ["Ética y gobernanza", "Specs y tests", "Selección de herramientas", "Loops agénticos", "Harness e invariantes", "Diseño del swarm"], values: [10, 15, 15, 15, 25, 20] }], {
    x: 0.5, y: 1.3, w: 5.2, h: 3.7, barDir: "bar", chartColors: [THEME.colors.accent1], showTitle: true, title: "Rúbrica propuesta (ajustable)", titleFontSize: 13, titleColor: THEME.colors.dk1,
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: THEME.colors.dk1, dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt",
    catAxisLabelColor: THEME.colors.dk1, catAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt", valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false, valAxisMaxVal: 30,
  });
  txt(s, "Subtítulo entregables", "Entregables", 6.0, 1.35, 3.5, 0.4, { fontSize: 18, bold: true });
  s.addText(["Changes 002–007 archivados", "11 specs con tests (progress.py)", "Los 3 loops funcionando", "Demo end-to-end en el lab", "Informe técnico y retrospectiva"].map((t, i, a) => ({ text: t, options: { bullet: true, breakLine: i < a.length - 1, paraSpaceAfter: 6 } })), { x: 6.0, y: 1.85, w: 3.5, h: 3.0, fontSize: 14, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: "Lista de entregables" });
}

// ---------- 13. 15 días, 3 sprints ----------
{
  const s = light();
  s.addNotes("Tres sprints de cinco días con un checkpoint al final de cada uno. Cada sprint tiene un tema: dominar el núcleo, conectar el swarm, validar y defender. Detalle día por día en docs/plan-15-dias.md.");
  title(s, "15 días, 3 sprints");
  const sprints = [
    ["1", "Días 1–5", "Dominar y endurecer el núcleo", ["Specs ampliadas", "Bitácora persistente", "RoE y scope tokens", "Red team del guard"], "Checkpoint 1", C.accent1],
    ["2", "Días 6–10", "Conectar el swarm", ["Recon real y loop A", "Correlación y loop B", "ZAP y Nuclei curado", "Evals con modelos"], "Checkpoint 2", C.accent5],
    ["3", "Días 11–15", "Validar, reportar y defender", ["Sandbox y loop C", "Informe y DefectDojo", "Integración end-to-end", "Demo final"], "Checkpoint 3", C.accent2],
  ];
  sprints.forEach(([n, days, name, items, cp, col], i) => {
    const x = 0.5 + i * 3.05;
    card(s, `Sprint ${n}`, x, 1.3, 2.9, 3.65);
    badge(s, `Número sprint ${n}`, x + 0.2, 1.48, 0.5, n, col, 16, i === 2 ? C.text1 : C.background1);
    txt(s, `Días sprint ${n}`, days, x + 0.85, 1.48, 1.9, 0.5, { fontSize: 14, bold: true, color: C.text2, valign: "middle" });
    txt(s, `Nombre sprint ${n}`, name, x + 0.2, 2.1, 2.5, 0.65, { fontSize: 15, bold: true });
    s.addText(items.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < items.length - 1, paraSpaceAfter: 3 } })), { x: x + 0.2, y: 2.8, w: 2.55, h: 1.5, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: `Lista sprint ${n}` });
    s.addShape(pres.ShapeType.roundRect, { x: x + 0.2, y: 4.4, w: 2.5, h: 0.4, fill: { color: col }, line: { color: col, width: 0 }, rectRadius: 0.2, objectName: `Etiqueta checkpoint ${n}` });
    txt(s, `Texto checkpoint ${n}`, cp, x + 0.2, 4.4, 2.5, 0.4, { fontSize: 13, bold: true, color: i === 2 ? C.text1 : C.background1, align: "center", valign: "middle" });
  });
}

// ---------- 14. Los 6 changes ----------
{
  const s = light();
  s.addNotes("Cada change trae proposal.md y tasks.md de partida. El design.md y los deltas de spec los escriben los alumnos: es parte de lo evaluado.");
  title(s, "Seis changes que evolucionan el MVP");
  const ch = [
    ["002", "Bitácora persistente", "SQLite append-only y verificador", "Sprint 1", C.accent1],
    ["003", "RoE y tokens", "Parser de RoE y emisor por fase", "Sprint 1", C.accent1],
    ["004", "Recon y loop A", "subfinder, httpx y grafo de activos", "Sprint 2", C.accent5],
    ["005", "Correlación y loop B", "NVD/EPSS offline, ZAP y Nuclei", "Sprint 2", C.accent5],
    ["006", "Sandbox y loop C", "Entorno efímero y gate humano", "Sprint 3", C.accent2],
    ["007", "Informe y DefectDojo", "CWE, CVSS v4 y exportación", "Sprint 3", C.accent2],
  ];
  ch.forEach(([id, t, d, sp, col], i) => {
    const x = 0.5 + (i % 3) * 3.05, y = 1.35 + Math.floor(i / 3) * 1.85;
    card(s, `Change ${id}`, x, y, 2.9, 1.7);
    s.addShape(pres.ShapeType.roundRect, { x: x + 0.2, y: y + 0.2, w: 0.75, h: 0.36, fill: { color: col }, line: { color: col, width: 0 }, rectRadius: 0.18, objectName: `Etiqueta ${id}` });
    txt(s, `Número ${id}`, id, x + 0.2, y + 0.2, 0.75, 0.36, { fontSize: 13, bold: true, color: sp === "Sprint 3" ? C.text1 : C.background1, align: "center", valign: "middle" });
    txt(s, `Sprint ${id}`, sp, x + 1.1, y + 0.2, 1.6, 0.36, { fontSize: 12, color: C.accent4, bold: true, valign: "middle" });
    txt(s, `Título ${id}`, t, x + 0.2, y + 0.7, 2.55, 0.4, { fontSize: 16, bold: true });
    txt(s, `Detalle ${id}`, d, x + 0.2, y + 1.1, 2.55, 0.5, { fontSize: 13, color: C.text2 });
  });
}

// ---------- 15. Rutina diaria ----------
{
  const s = light();
  s.addNotes("Rutina de dos horas. Un día termina con tests verdes, progress.py y un commit. La disciplina de spec primero y test primero es lo que mantiene honesta a la IA.");
  title(s, "La rutina diaria (≈ 2 horas)");
  const steps = [["10'", "Arrancar", "Tests y progress.py"], ["25'", "Spec", "Delta con caso negativo"], ["25'", "Test primero", "Debe fallar por la razón correcta"], ["40'", "Implementar", "El cambio mínimo"], ["15'", "Revisar", "security-reviewer sobre el diff"], ["5'", "Cerrar", "Verde, tasks y commit"]];
  const w = 1.4, gap = 0.12;
  steps.forEach(([m, t, d], i) => {
    const x = 0.5 + i * (w + gap);
    card(s, `Paso ${t}`, x, 1.4, w, 2.4, i === 3 ? C.accent2 : C.background2);
    txt(s, `Minutos ${t}`, m, x + 0.1, 1.55, w - 0.2, 0.7, { fontSize: 32, bold: true, color: i === 3 ? C.text1 : C.accent1, fontFace: "Cambria", align: "center" });
    txt(s, `Nombre ${t}`, t, x + 0.1, 2.4, w - 0.2, 0.4, { fontSize: 14, bold: true, align: "center" });
    txt(s, `Detalle ${t}`, d, x + 0.1, 2.85, w - 0.2, 0.85, { fontSize: 12, align: "center", color: i === 3 ? C.text1 : C.text2 });
  });
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 4.1, w: 9.0, h: 0.7, fill: { color: C.text1 }, line: { color: C.text1, width: 0 }, rectRadius: 0.08, objectName: "Barra regla del día" });
  txt(s, "Regla del día", "Un día termina con tests verdes, progress.py al día y un commit", 0.7, 4.1, 8.6, 0.7, { fontSize: 15, bold: true, color: C.background1, align: "center", valign: "middle" });
}

// ---------- 16. Autocontrol ----------
{
  const s = light();
  s.addNotes("Sin docente a mano, el equipo se controla con cuatro herramientas. La mutación manual es lo primero que revisa el docente: si rompés el guard y los tests siguen en verde, no sirven.");
  title(s, "Cómo se controlan sin docente");
  const items = [
    ["progress.py", "Tasks por change, Scenarios por spec y tests recolectados", C.accent1],
    ["Mutación manual", "Romper el guard a propósito: si los tests siguen verdes, no sirven", C.accent3],
    ["Red team del guard", "Diez intentos de evasión convertidos en tests y correcciones", C.accent5],
    ["security-reviewer", "Revisión independiente del diff antes de cerrar cada change", C.accent2],
  ];
  items.forEach(([t, d, col], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.4 + Math.floor(i / 2) * 1.85;
    card(s, `Tarjeta ${t}`, x, y, 4.4, 1.7);
    badge(s, `Icono ${t}`, x + 0.25, y + 0.3, 0.55, String(i + 1), col, 16, col === C.accent2 ? C.text1 : C.background1);
    txt(s, `Título ${t}`, t, x + 1.0, y + 0.25, 3.2, 0.4, { fontSize: 18, bold: true });
    txt(s, `Detalle ${t}`, d, x + 1.0, y + 0.7, 3.2, 0.9, { fontSize: 14 });
  });
}

// ---------- 13b. Mapa de documentos y repositorio ----------
{
  const s = light();
  s.addNotes("Acá están TODOS los links. El repo del TP y los documentos que explican qué hay que hacer: enunciado (qué entregar), marco teórico (cómo construirlo), plan de 15 días y rúbrica. Que cada equipo arranque leyendo el enunciado y el plan, y abra el primer change para empezar.");
  title(s, "Dónde está todo: repo y documentos");
  txt(s, "Bajada", "Todo vive en el repositorio del curso. Arrancá por el enunciado y el plan; abrí el primer change para empezar a construir.", 0.5, 1.2, 9.0, 0.6, { fontSize: 15, color: C.text2 });
  const RB = "https://github.com/fboiero/LabsSeguridadInformatica2026";
  const BASE = RB + "/blob/main/labs/labfinal-practico-integrador/ptaas-kit";
  const TREE = RB + "/tree/main/labs/labfinal-practico-integrador/ptaas-kit";
  const links = [
    ["Repositorio del TP  ·  carpeta ptaas-kit", TREE, C.accent1],
    ["Enunciado para alumnos  ·  qué hay que entregar", BASE + "/docs/enunciado-alumnos.md", C.accent5],
    ["Marco teórico  ·  guía de construcción de punta a punta", BASE + "/docs/marco-teorico.md", C.accent5],
    ["Plan de 15 días  ·  3 sprints con checkpoints", BASE + "/docs/plan-15-dias.md", C.accent2],
    ["Rúbrica de evaluación  ·  cómo se corrige", BASE + "/docs/rubrica-evaluacion.md", C.accent3],
    ["Cómo trabajar con Claude Code u opencode", BASE + "/AGENTS.md", C.accent1],
    ["Arranque  ·  primer change (tasks.md del MVP)", BASE + "/openspec/changes/001-mvp-vertical-slice/tasks.md", C.accent4],
  ];
  links.forEach(([label, url, col], i) => {
    const y = 1.95 + i * 0.46;
    badge(s, `Vineta ${i}`, 0.55, y + 0.02, 0.3, "▸", col, 11);
    s.addText(label, { x: 1.0, y, w: 8.4, h: 0.4, fontSize: 14, color: col, margin: 0, valign: "middle", isTextBox: true, hyperlink: { url, tooltip: label }, objectName: `Link ${i}` });
  });
}

// ---------- 13c. Cómo arrancar: Claude Code u opencode ----------
{
  const s = light();
  s.addNotes("El kit funciona con Claude Code o con opencode, el alumno elige. Lo clave: la seguridad NO depende del agente. El Scope Guard, el token de alcance y la bitácora están en el harness (código determinista) y los valida el CI. El agente solo ayuda a construir.");
  title(s, "Cómo arrancar: Claude Code u opencode");
  txt(s, "Bajada", "Elegí el agente que quieras. Las reglas del proyecto son las mismas; cambia de qué archivo las lee.", 0.5, 1.2, 9.0, 0.5, { fontSize: 15, color: C.text2 });
  const cols = [
    ["Claude Code", "lee CLAUDE.md", ["cd ptaas-kit", "claude", "> Implementá el change 001", "  siguiendo su tasks.md"], C.accent1],
    ["opencode", "lee AGENTS.md + opencode.json", ["cd ptaas-kit", "opencode", "> Implementá el change 001", "  siguiendo su tasks.md"], C.accent5],
  ];
  cols.forEach(([name, reads, lines, col], i) => {
    const x = 0.5 + i * 4.7;
    card(s, `Agente ${i}`, x, 1.85, 4.3, 2.3, C.background2);
    badge(s, `Punto ${i}`, x + 0.25, 2.05, 0.4, String(i + 1), col, 15);
    txt(s, `Nombre ${i}`, name, x + 0.8, 2.08, 3.3, 0.4, { fontSize: 19, bold: true, color: col, fontFace: "Cambria" });
    txt(s, `Lee ${i}`, reads, x + 0.8, 2.5, 3.3, 0.3, { fontSize: 11, color: C.accent4 });
    txt(s, `Cmd ${i}`, lines.join("\n"), x + 0.25, 2.95, 3.9, 1.1, { fontSize: 12.5, color: C.text1, fontFace: "Consolas" });
  });
  s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 4.4, w: 9.0, h: 0.75, fill: { color: C.accent6, transparency: 82 }, line: { color: C.accent6, width: 1 }, rectRadius: 0.08, objectName: "Nota seguridad" });
  txt(s, "Nota", "La seguridad no depende del agente: el Scope Guard, el token de alcance y la bitácora viven en el harness (código determinista) y los valida el CI.", 0.75, 4.52, 8.5, 0.6, { fontSize: 13, bold: true, color: C.text1, valign: "middle" });
}

// ---------- 14. Reglas / cierre ----------
{
  const s = dark();
  s.addNotes("Cerrar con las reglas de juego y la pregunta de arranque. Todo el trabajo es sobre laboratorio propio.");
  title(s, "Reglas del juego", true);
  const nos = ["Nada contra sistemas que no sean el laboratorio propio", "Ninguna acción sin scope token y sin bitácora", "Sin generar exploits nuevos: solo verificaciones del catálogo", "Sin saltear los gates humanos"];
  nos.forEach((t, i) => {
    const y = 1.35 + i * 0.75;
    badge(s, `Prohibido ${i + 1}`, 0.5, y, 0.45, "✕", C.accent3, 14);
    txt(s, `Regla ${i + 1}`, t, 1.2, y, 5.0, 0.45, { fontSize: 15, color: C.background1, valign: "middle" });
  });
  s.addShape(pres.ShapeType.roundRect, { x: 6.6, y: 1.35, w: 2.9, h: 3.0, fill: { color: C.text2 }, line: { color: C.text2, width: 0 }, rectRadius: 0.08, objectName: "Tarjeta pregunta" });
  txt(s, "Pregunta", "¿Qué invariante tiene que cumplir tu sistema aunque el agente se equivoque?", 6.85, 1.6, 2.4, 2.5, { fontSize: 18, bold: true, color: C.background1, fontFace: "Cambria", valign: "middle" });
}

(async () => {
  await pres.writeFile({ fileName: "./ptaas-desafio.pptx" });
  await applyTheme("./ptaas-desafio.pptx", THEME);
  console.log("ok");
})();
