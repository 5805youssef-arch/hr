import { useEffect, useState } from "react";
import { auth, api } from "./api";
import { L } from "./i18n";
import { IC } from "./icons";
import { Card, Empty } from "./components";
import Dashboard from "./pages/Dashboard";
import LogViolation from "./pages/LogViolation";
import Employees from "./pages/Employees";
import Reports from "./pages/Reports";
import Login from "./pages/Login";

const PLACEHOLDERS = {
  set: { icon: IC.setBig, title: "comingSoon", sub: "comingSoonSub" },
};

export default function HRSystem() {
  const [lang, setLang] = useState("en");
  const [page, setPage] = useState("dash");
  const [collapsed, setCollapsed] = useState(false);
  const [authed, setAuthed] = useState(!!auth.get());

  useEffect(() => {
    const h = () => setAuthed(false);
    window.addEventListener("hr-logout", h);
    return () => window.removeEventListener("hr-logout", h);
  }, []);

  useEffect(() => {
    document.body.dir = lang === "ar" ? "rtl" : "ltr";
  }, [lang]);

  const ar = lang === "ar";
  const t = (k) => L[lang][k] || k;
  const sw = collapsed ? 68 : 256;

  if (!authed) {
    return <Login lang={lang} onSuccess={() => setAuthed(true)} />;
  }

  const logout = () => { api.logout(); setAuthed(false); };

  const navs = [
    { id: "dash", icon: IC.dash },
    { id: "log", icon: IC.log },
    { id: "emp", icon: IC.emp },
    { id: "rep", icon: IC.rep },
    { id: "set", icon: IC.set },
  ];

  let content;
  if (page === "dash") {
    content = <Dashboard lang={lang} onNewV={() => setPage("log")} onViewAll={() => setPage("rep")} />;
  } else if (page === "log") {
    content = <LogViolation lang={lang} />;
  } else if (page === "emp") {
    content = <Employees lang={lang} />;
  } else if (page === "rep") {
    content = <Reports lang={lang} />;
  } else {
    const p = PLACEHOLDERS[page];
    content = (
      <div className="flex-gap">
        <h2 className="page-title">{t(page)}</h2>
        <Card><Empty icon={p?.icon} text={t(p?.title || "comingSoon")} sub={p?.sub && t(p.sub)} /></Card>
      </div>
    );
  }

  return (
    <div>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800&family=Noto+Sans+Arabic:wght@400;500;600;700;800&display=swap" rel="stylesheet" />

      <aside className={`sidebar${collapsed ? " collapsed" : ""}`}>
        <div className="sidebar-head">
          <div className="logo">TG</div>
          {!collapsed && (
            <div style={{ overflow: "hidden", minWidth: 0 }}>
              <b className="brand-name">Travel Gate</b>
              <small className="brand-sub">{t("hrSys")}</small>
            </div>
          )}
        </div>
        {!collapsed && <div className="menu-label">{t("mainMenu")}</div>}
        <nav className="sidebar-nav">
          {navs.map((n) => (
            <button key={n.id} onClick={() => setPage(n.id)} className={`nav-btn${page === n.id ? " active" : ""}`}>
              <span className="ic">{n.icon}</span>
              {!collapsed && <span className="label">{t(n.id)}</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-foot">
          <button className="collapse-btn" onClick={() => setCollapsed(!collapsed)}>
            {collapsed ? (ar ? IC.chevL : IC.chevR) : (ar ? IC.chevR : IC.chevL)}
          </button>
        </div>
      </aside>

      <div className="app-shell" style={{ [ar ? "marginRight" : "marginLeft"]: sw, transition: "margin .22s cubic-bezier(.4,0,.2,1)" }}>
        <header className="topbar">
          <h1>{t(page)}</h1>
          <div className="topbar-actions">
            <button className="lang-btn" onClick={() => setLang(ar ? "en" : "ar")}>
              {IC.globe} <span>{t("lang")}</span>
            </button>
            <button className="icon-btn">
              {IC.bell}
              <span className="dot" />
            </button>
            <div className="profile">
              <div className="avatar">{ar ? "\u0623" : "A"}</div>
              <span className="profile-name">{ar ? "\u0623\u0645\u064A\u0646" : "Amin"}</span>
            </div>
            <button className="icon-btn" title={ar ? "\u062E\u0631\u0648\u062C" : "Logout"} onClick={logout}>
              {"\u23FB"}
            </button>
          </div>
        </header>
        <div className="app-main">{content}</div>
      </div>
    </div>
  );
}
