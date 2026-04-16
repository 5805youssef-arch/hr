import { useState } from "react";
import { S } from "./tokens";
import { L } from "./i18n";
import { IC } from "./icons";
import { Card, Empty } from "./components";
import Dashboard from "./pages/Dashboard";
import LogViolation from "./pages/LogViolation";
import Employees from "./pages/Employees";

const PLACEHOLDERS = {
  rep: { icon: IC.rep, title: "rep" },
  set: { icon: IC.setBig, title: "comingSoon", sub: "comingSoonSub" },
};

export default function HRSystem() {
  const [lang, setLang] = useState("en");
  const [page, setPage] = useState("dash");
  const [collapsed, setCollapsed] = useState(false);

  const ar = lang === "ar";
  const t = (k) => L[lang][k] || k;
  const sw = collapsed ? 68 : 256;

  const navs = [
    { id: "dash", icon: IC.dash },
    { id: "log", icon: IC.log },
    { id: "emp", icon: IC.emp },
    { id: "rep", icon: IC.rep },
    { id: "set", icon: IC.set },
  ];

  const sidebar = (
    <aside style={{ position: "fixed", top: 0, bottom: 0, [ar ? "right" : "left"]: 0, width: sw, background: S.w, [ar ? "borderLeft" : "borderRight"]: `1px solid ${S.g100}`, display: "flex", flexDirection: "column", transition: "width 0.22s cubic-bezier(.4,0,.2,1)", zIndex: 200, boxShadow: "2px 0 12px rgba(0,0,0,0.04)", overflow: "hidden" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, padding: collapsed ? 0 : "0 20px", justifyContent: collapsed ? "center" : "flex-start", height: 60, borderBottom: `1px solid ${S.g100}`, flexShrink: 0 }}>
        <div style={{ width: 36, height: 36, borderRadius: S.r2, flexShrink: 0, background: `linear-gradient(135deg,${S.pri} 0%,${S.priD} 100%)`, display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontSize: 13, fontWeight: 800, letterSpacing: "-.5px", boxShadow: "0 2px 8px rgba(47,184,158,.3)" }}>TG</div>
        {!collapsed && (
          <div style={{ overflow: "hidden", minWidth: 0 }}>
            <b style={{ display: "block", fontSize: 14, fontWeight: 700, color: S.g800, whiteSpace: "nowrap" }}>Travel Gate</b>
            <small style={{ display: "block", fontSize: 10.5, color: S.g400, whiteSpace: "nowrap" }}>{t("hrSys")}</small>
          </div>
        )}
      </div>
      {!collapsed && <div style={{ fontSize: 10, fontWeight: 700, color: S.g300, textTransform: "uppercase", letterSpacing: ".08em", padding: "10px 12px 4px" }}>{t("mainMenu")}</div>}
      <nav style={{ flex: 1, padding: "10px 8px", display: "flex", flexDirection: "column", gap: 2, overflowY: "auto" }}>
        {navs.map((n) => {
          const act = page === n.id;
          return (
            <button key={n.id} onClick={() => setPage(n.id)} style={{ display: "flex", alignItems: "center", gap: 10, padding: collapsed ? 11 : "10px 12px", justifyContent: collapsed ? "center" : "flex-start", borderRadius: S.r2, border: "none", cursor: "pointer", background: act ? S.priL : "transparent", color: act ? S.priD : S.g400, fontWeight: act ? 600 : 500, fontSize: 13, transition: S.tr, width: "100%", textAlign: ar ? "right" : "left", fontFamily: "inherit", position: "relative" }}>
              {act && <span style={{ position: "absolute", [ar ? "right" : "left"]: 0, top: "50%", transform: "translateY(-50%)", width: 3, height: 20, borderRadius: ar ? "2px 0 0 2px" : "0 2px 2px 0", background: S.pri }} />}
              <span style={{ color: act ? S.pri : "inherit", display: "flex" }}>{n.icon}</span>
              {!collapsed && <span style={{ whiteSpace: "nowrap" }}>{t(n.id)}</span>}
            </button>
          );
        })}
      </nav>
      <div style={{ padding: 8, borderTop: `1px solid ${S.g100}`, flexShrink: 0 }}>
        <button onClick={() => setCollapsed(!collapsed)} style={{ width: "100%", padding: 9, borderRadius: S.r2, border: `1px solid ${S.g200}`, background: S.w, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", color: S.g400, fontFamily: "inherit" }}>
          {collapsed ? (ar ? IC.chevL : IC.chevR) : (ar ? IC.chevR : IC.chevL)}
        </button>
      </div>
    </aside>
  );

  const topbar = (
    <header style={{ height: 60, background: S.w, borderBottom: `1px solid ${S.g100}`, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 28px", position: "sticky", top: 0, zIndex: 100, boxShadow: S.sh0, flexShrink: 0 }}>
      <h1 style={{ fontSize: 16, fontWeight: 700, color: S.g800, margin: 0 }}>{t(page)}</h1>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <button onClick={() => setLang(ar ? "en" : "ar")} style={{ display: "flex", alignItems: "center", gap: 6, padding: "6px 14px", borderRadius: S.rF, border: `1px solid ${S.g200}`, background: S.w, cursor: "pointer", fontSize: 12, color: S.g500, fontWeight: 500, fontFamily: "inherit" }}>{IC.globe} <span>{t("lang")}</span></button>
        <button style={{ width: 36, height: 36, borderRadius: S.r2, border: `1px solid ${S.g200}`, background: S.w, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", position: "relative", color: S.g400 }}>{IC.bell}</button>
        <div style={{ display: "flex", alignItems: "center", gap: 9, padding: "4px 8px", borderRadius: S.rF }}>
          <div style={{ width: 32, height: 32, borderRadius: "50%", flexShrink: 0, background: `linear-gradient(135deg,${S.pri},${S.acc})`, display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontSize: 12, fontWeight: 700 }}>{ar ? "\u0623" : "A"}</div>
          <span style={{ fontSize: 13, fontWeight: 600, color: S.g700 }}>{ar ? "\u0623\u0645\u064A\u0646" : "Amin"}</span>
        </div>
      </div>
    </header>
  );

  let content;
  if (page === "dash") {
    content = <Dashboard lang={lang} onNewV={() => setPage("log")} onViewAll={() => setPage("rep")} />;
  } else if (page === "log") {
    content = <LogViolation lang={lang} />;
  } else if (page === "emp") {
    content = <Employees lang={lang} />;
  } else {
    const p = PLACEHOLDERS[page];
    content = (
      <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        <h2 style={{ fontSize: 22, fontWeight: 800, color: S.g800, margin: 0 }}>{t(page)}</h2>
        <Card><Empty icon={p?.icon} text={t(p?.title || "comingSoon")} sub={p?.sub && t(p.sub)} /></Card>
      </div>
    );
  }

  return (
    <div style={{ fontFamily: ar ? "'Noto Sans Arabic','Segoe UI',sans-serif" : "'DM Sans','Segoe UI',sans-serif", background: S.g50, color: S.g700, minHeight: "100vh", fontSize: 14, lineHeight: 1.5, direction: ar ? "rtl" : "ltr", WebkitFontSmoothing: "antialiased" }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800&family=Noto+Sans+Arabic:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
      {sidebar}
      <div style={{ [ar ? "marginRight" : "marginLeft"]: sw, transition: "margin .22s cubic-bezier(.4,0,.2,1)", minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        {topbar}
        <div style={{ padding: 28, flex: 1 }}>{content}</div>
      </div>
    </div>
  );
}
