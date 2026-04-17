import { L } from "./i18n";

const PB_CLASS = {
  Yellow: "pb-yellow",
  Orange: "pb-orange",
  Red: "pb-red",
  Black: "pb-black",
  Investigation: "pb-invest",
};

const PB_KEY = {
  Yellow: "yellow", Orange: "orange", Red: "red", Black: "black", Investigation: "invest",
};

export function PenBadge({ level, size = "sm", lang }) {
  const cls = PB_CLASS[level] || "pb-yellow";
  const label = (lang && L[lang] && L[lang][PB_KEY[level]]) || level;
  return (
    <span className={`pb ${cls}${size === "lg" ? " pb-lg" : ""}`}>
      <span className="pb-dot" />
      {label}
    </span>
  );
}

export const Card = ({ children, className = "", flush, style }) => (
  <div className={`card${flush ? " card-flush" : ""} ${className}`} style={style}>
    {children}
  </div>
);

export const Empty = ({ icon, text, sub }) => (
  <div className="empty">
    {icon}
    <p>{text}</p>
    {sub && <small>{sub}</small>}
  </div>
);

export const KpiCard = ({ icon, tone = "ok", value, label }) => (
  <div className="kpi">
    <div className={`kpi-ic kpi-ic-${tone}`}>{icon}</div>
    <div className="kpi-val">{value}</div>
    <div className="kpi-lbl">{label}</div>
  </div>
);

export const BtnPri = ({ children, onClick, wide, disabled, type = "button" }) => (
  <button type={type} onClick={onClick} disabled={disabled} className={`btn btn-pri${wide ? " btn-wide" : ""}`}>
    {children}
  </button>
);

export const BtnSec = ({ children, onClick, type = "button" }) => (
  <button type={type} onClick={onClick} className="btn btn-sec">{children}</button>
);

export const BtnGhost = ({ children, onClick, type = "button" }) => (
  <button type={type} onClick={onClick} className="btn btn-ghost">{children}</button>
);

export const FG = ({ label, children }) => (
  <div className="fg">
    {label && <label className="fg-label">{label}</label>}
    {children}
  </div>
);
