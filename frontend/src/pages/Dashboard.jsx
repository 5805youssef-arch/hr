import { useEffect, useState } from "react";
import { api } from "../api";
import { L } from "../i18n";
import { IC } from "../icons";
import { Card, Empty, KpiCard, BtnPri, BtnSec, BtnGhost, PenBadge } from "../components";

const PENALTIES = ["Yellow", "Orange", "Red", "Black", "Investigation"];
const PY_DOT = {
  Yellow: "#D97706", Orange: "#EA580C", Red: "#DC2626", Black: "#1E293B", Investigation: "#7C3AED",
};
const CAT_COLORS = ["#2FB89E", "#E8825C", "#D97706", "#2563EB"];

function LineChart({ data }) {
  if (!data?.length) return null;
  const w = 500, h = 200, pad = 30;
  const max = Math.max(...data.map((d) => d.count), 1);
  const step = (w - pad * 2) / Math.max(data.length - 1, 1);
  const points = data.map((d, i) => ({
    x: pad + i * step,
    y: h - pad - (d.count / max) * (h - pad * 2),
    m: d.month,
    c: d.count,
  }));
  const line = points.map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`).join(" ");
  const area = `${line} L${pad + (data.length - 1) * step},${h - pad} L${pad},${h - pad} Z`;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} style={{ width: "100%", height: 220 }}>
      <defs>
        <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#2FB89E" stopOpacity=".25" />
          <stop offset="100%" stopColor="#2FB89E" stopOpacity="0" />
        </linearGradient>
      </defs>
      {[0, 0.25, 0.5, 0.75, 1].map((p, i) => (
        <line key={i} x1={pad} x2={w - pad} y1={pad + p * (h - pad * 2)} y2={pad + p * (h - pad * 2)} stroke="#ECEEF2" />
      ))}
      <path d={area} fill="url(#area)" />
      <path d={line} stroke="#2FB89E" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      {points.map((p, i) => (
        <g key={i}>
          <circle cx={p.x} cy={p.y} r="4" fill="#2FB89E" stroke="#fff" strokeWidth="2" />
          <text x={p.x} y={h - 8} textAnchor="middle" fontSize="10" fill="#8896A5">{p.m.slice(5)}</text>
        </g>
      ))}
    </svg>
  );
}

function Donut({ data }) {
  const entries = Object.entries(data || {});
  const total = entries.reduce((s, [, v]) => s + v, 0);
  if (!total) return <Empty text="No data" />;
  const size = 200, r = 75, c = 2 * Math.PI * r;
  let offset = 0;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: "rotate(-90deg)" }}>
        {entries.map(([k, v], i) => {
          const len = (v / total) * c;
          const circle = (
            <circle
              key={k}
              cx={size / 2} cy={size / 2} r={r}
              fill="none"
              stroke={CAT_COLORS[i % CAT_COLORS.length]}
              strokeWidth="26"
              strokeDasharray={`${len} ${c - len}`}
              strokeDashoffset={-offset}
            />
          );
          offset += len;
          return circle;
        })}
      </svg>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "8px 18px" }}>
        {entries.map(([k], i) => (
          <div key={k} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "#5C6B7A" }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: CAT_COLORS[i % CAT_COLORS.length] }} />
            {k}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Dashboard({ lang, onNewV, onViewAll }) {
  const ar = lang === "ar";
  const t = (k) => L[lang][k] || k;
  const [data, setData] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    api.dashboard().then(setData).catch((e) => setErr(e.message));
  }, []);

  const totals = data?.totals || { violations: 0, employees: 0, deduction_days: 0, active_freezes: 0 };
  const byColor = data?.by_color || {};
  const totalByColor = Object.values(byColor).reduce((a, b) => a + b, 0) || 1;
  const recent = data?.recent || [];

  return (
    <div className="flex-gap">
      <div className="page-head">
        <div>
          <h2 className="page-title">
            {t("welcome")}, {ar ? "\u0623\u0645\u064A\u0646" : "Amin"} {"\u{1F44B}"}
          </h2>
          <p className="page-sub">{t("todayAct")}</p>
        </div>
        <div className="page-actions">
          <BtnPri onClick={onNewV}>{IC.plus} <span>{t("newV")}</span></BtnPri>
          <BtnSec>{IC.dl} <span>{t("export")}</span></BtnSec>
        </div>
      </div>

      {err && <div className="alert alert-err">Error loading data: {err}</div>}

      <div className="grid-kpi">
        <KpiCard icon={IC.warn}    tone="warn"   value={totals.violations}      label={t("totV")} />
        <KpiCard icon={IC.users}   tone="ok"     value={totals.employees}       label={t("totE")} />
        <KpiCard icon={IC.clock}   tone="clock"  value={totals.deduction_days}  label={t("totD")} />
        <KpiCard icon={IC.shieldR} tone="shield" value={totals.active_freezes}  label={t("actF")} />
      </div>

      <div className="grid-split">
        <Card>
          <h3 className="card-title" style={{ marginBottom: 14 }}>{t("trend")}</h3>
          {data?.monthly?.length ? <LineChart data={data.monthly} /> : <Empty text={t("noData")} />}
        </Card>
        <Card>
          <h3 className="card-title" style={{ marginBottom: 14 }}>{t("byCat")}</h3>
          {Object.keys(data?.by_category || {}).length ? <Donut data={data.by_category} /> : <Empty text={t("noData")} />}
        </Card>
      </div>

      <div className="grid-dash">
        <Card>
          <h3 className="card-title" style={{ marginBottom: 14 }}>{t("penDist")}</h3>
          {PENALTIES.map((lv) => {
            const count = byColor[lv] || 0;
            const pct = (count / totalByColor) * 100;
            return (
              <div key={lv} className="pd-row">
                <PenBadge level={lv} lang={lang} />
                <div className="pd-track">
                  <div className="pd-fill" style={{ width: `${pct}%`, background: PY_DOT[lv] }} />
                </div>
                <span className="pd-val">{count}</span>
              </div>
            );
          })}
        </Card>

        <Card flush>
          <div className="card-head">
            <h3 className="card-title">{t("recent")}</h3>
            <BtnGhost onClick={onViewAll}>{t("viewAll")} {"\u2192"}</BtnGhost>
          </div>
          <div style={{ overflowX: "auto" }}>
            <table className="tbl">
              <thead>
                <tr>
                  <th>{t("employee")}</th>
                  <th>{t("inc")}</th>
                  <th>{t("pen")}</th>
                  <th>{t("ded")}</th>
                  <th>{t("date")}</th>
                </tr>
              </thead>
              <tbody>
                {recent.length === 0 ? (
                  <tr><td colSpan={5}><Empty text={t("noViol")} /></td></tr>
                ) : recent.map((v) => (
                  <tr key={v.id}>
                    <td className="td-primary">{v.employee_name}</td>
                    <td className="td-muted">{v.incident}</td>
                    <td><PenBadge level={v.penalty_color} lang={lang} /></td>
                    <td className="td-primary">{v.deduction_days} d</td>
                    <td className="td-date">{v.created_at?.slice(0, 10)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}
