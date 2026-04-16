import { S, pbStyle } from "./tokens";
import { L } from "./i18n";

export function PenBadge({ level, size = "sm", lang }) {
  const s = pbStyle[level] || pbStyle.Yellow;
  const lk = { Yellow: "yellow", Orange: "orange", Red: "red", Black: "black", Investigation: "invest" };
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 5, borderRadius: 999, fontWeight: 600, whiteSpace: "nowrap", padding: size === "sm" ? "3px 9px" : "5px 13px", fontSize: size === "sm" ? 11 : 12.5, background: s.bg, color: s.color, border: `1px solid ${s.border}` }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", flexShrink: 0, background: s.dot }} />
      {L[lang][lk[level]] || level}
    </span>
  );
}

export const Card = ({ children, style: cs, flush }) => (
  <div style={{ background: S.w, borderRadius: S.r3, border: `1px solid ${S.g200}`, padding: flush ? 0 : 24, boxShadow: S.sh1, overflow: flush ? "hidden" : "visible", ...cs }}>{children}</div>
);

export const Empty = ({ icon, text, sub }) => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "56px 0", color: S.g400, gap: 10 }}>
    {icon}
    <p style={{ fontSize: 14, fontWeight: 500, margin: 0 }}>{text}</p>
    {sub && <small style={{ fontSize: 12.5, color: S.g300 }}>{sub}</small>}
  </div>
);

export const KpiCard = ({ icon, iconBg, value, label, sub }) => (
  <Card>
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ width: 42, height: 42, borderRadius: S.r2, display: "flex", alignItems: "center", justifyContent: "center", background: iconBg }}>{icon}</div>
      <div>
        <div style={{ fontSize: 32, fontWeight: 800, color: S.g800, lineHeight: 1, letterSpacing: -1 }}>{value}</div>
        <div style={{ fontSize: 12, color: S.g400, marginTop: 4, fontWeight: 500 }}>{label}</div>
      </div>
      {sub && <div style={{ fontSize: 11.5, color: S.g400, borderTop: `1px solid ${S.g100}`, paddingTop: 12 }}>{sub}</div>}
    </div>
  </Card>
);

export const BtnPri = ({ children, onClick, wide, disabled }) => (
  <button onClick={onClick} disabled={disabled} style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: wide ? 12 : "9px 18px", borderRadius: S.r2, border: "none", cursor: disabled ? "not-allowed" : "pointer", opacity: disabled ? 0.6 : 1, fontSize: wide ? 14 : 13, fontWeight: 600, transition: S.tr, fontFamily: "inherit", whiteSpace: "nowrap", background: S.pri, color: "#fff", boxShadow: "0 2px 8px rgba(47,184,158,.25)", width: wide ? "100%" : "auto", justifyContent: "center" }}>{children}</button>
);

export const BtnSec = ({ children, onClick }) => (
  <button onClick={onClick} style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "9px 18px", borderRadius: S.r2, border: `1px solid ${S.g200}`, cursor: "pointer", fontSize: 13, fontWeight: 600, transition: S.tr, fontFamily: "inherit", whiteSpace: "nowrap", background: S.w, color: S.g600 }}>{children}</button>
);

export const BtnGhost = ({ children, onClick }) => (
  <button onClick={onClick} style={{ display: "inline-flex", alignItems: "center", gap: 7, padding: "5px 12px", borderRadius: S.r2, border: "none", cursor: "pointer", fontSize: 12, fontWeight: 600, transition: S.tr, fontFamily: "inherit", background: "transparent", color: S.g400 }}>{children}</button>
);

export const Th = ({ children, ar }) => (
  <th style={{ padding: "11px 16px", fontWeight: 600, color: S.g400, fontSize: 10.5, textTransform: "uppercase", letterSpacing: ".06em", borderBottom: `2px solid ${S.g100}`, whiteSpace: "nowrap", textAlign: ar ? "right" : "left", background: S.g50 }}>{children}</th>
);

export const FG = ({ label, children }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
    <label style={{ fontSize: 12, fontWeight: 600, color: S.g500 }}>{label}</label>
    {children}
  </div>
);

export const inp = { padding: "10px 14px", borderRadius: S.r2, border: `1.5px solid ${S.g200}`, fontSize: 13.5, color: S.g700, fontFamily: "inherit", outline: "none", background: S.w, width: "100%" };
