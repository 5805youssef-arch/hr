import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { L } from "../i18n";
import { IC } from "../icons";
import { Card, Empty, KpiCard, BtnPri, BtnSec, PenBadge, FG } from "../components";

const PENALTIES = ["Yellow", "Orange", "Red", "Black", "Investigation"];
const PY_BAR = {
  Yellow: "#D97706", Orange: "#EA580C", Red: "#DC2626", Black: "#1E293B", Investigation: "#7C3AED",
};
const PY_SHORT = {
  Yellow: "Yellow", Orange: "Orange", Red: "Red", Black: "Black", Investigation: "Invest.",
};

function PenaltyBars({ data }) {
  const max = Math.max(...PENALTIES.map((p) => data[p] || 0), 1);
  return (
    <div className="bar-col-chart">
      {[1, 0.75, 0.5, 0.25, 0].map((p, i) => {
        const v = Math.round(max * (1 - p));
        return (
          <div key={i} style={{ position: "absolute", left: 6, right: 6, top: 10 + p * 180, height: 1, background: "#ECEEF2" }}>
            <span style={{ position: "absolute", left: -4, top: -8, fontSize: 10, color: "#8896A5", transform: "translateX(-100%)" }}>{v}</span>
          </div>
        );
      })}
      {PENALTIES.map((p) => {
        const count = data[p] || 0;
        const h = (count / max) * 180;
        return (
          <div key={p} className="bar-col">
            <div className="bar" style={{ height: h, background: PY_BAR[p] }} />
            <span className="bar-lbl">{PY_SHORT[p]}</span>
          </div>
        );
      })}
    </div>
  );
}

function TopBars({ rows }) {
  if (!rows?.length) return <Empty text="No data" />;
  const max = rows[0][1] || 1;
  return (
    <div style={{ padding: "10px 0" }}>
      {rows.map(([name, n]) => (
        <div key={name} className="hbar-row">
          <span className="hbar-lbl">{name}</span>
          <div className="hbar-track">
            <div className="hbar-fill" style={{ width: `${(n / max) * 100}%` }} />
          </div>
          <span className="hbar-val">{n}</span>
        </div>
      ))}
    </div>
  );
}

export default function Reports({ lang }) {
  const ar = lang === "ar";
  const t = (k) => L[lang][k] || k;

  const [employees, setEmployees] = useState([]);
  const [rows, setRows] = useState([]);
  const [filters, setFilters] = useState({ employee: "", date_from: "", date_to: "", penalty: "" });
  const [filterOpen, setFilterOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);

  async function load() {
    setLoading(true); setErr(null);
    try {
      const r = await api.listViolations(filters);
      setRows(r);
    } catch (e) { setErr(e.message); }
    finally { setLoading(false); }
  }

  useEffect(() => { api.listEmployees().then(setEmployees).catch(() => {}); }, []);
  useEffect(() => { load(); /* eslint-disable-next-line */ }, [filters.employee, filters.date_from, filters.date_to, filters.penalty]);

  async function remove(id) {
    if (!confirm(`${t("del")} #${id}?`)) return;
    await api.deleteViolation(id);
    await load();
  }

  const totals = useMemo(() => {
    const ded = rows.reduce((s, r) => s + (r.deduction_days || 0), 0);
    const freezes = rows.filter((r) => (r.freeze_months || 0) > 0).length;
    const employeesSet = new Set(rows.map((r) => r.employee_name));
    return { count: rows.length, ded, freezes, emp: employeesSet.size };
  }, [rows]);

  const byColor = useMemo(() => {
    const m = {};
    rows.forEach((r) => { m[r.penalty_color] = (m[r.penalty_color] || 0) + 1; });
    return m;
  }, [rows]);

  const topInc = useMemo(() => {
    const m = {};
    rows.forEach((r) => { m[r.incident] = (m[r.incident] || 0) + 1; });
    return Object.entries(m).sort((a, b) => b[1] - a[1]).slice(0, 5);
  }, [rows]);

  async function exportExcel() {
    try { await api.exportViolations(filters); }
    catch (e) { setErr(e.message); }
  }

  return (
    <div className="flex-gap">
      <div className="page-head">
        <div>
          <h2 className="page-title">{t("rep")}</h2>
          <p className="page-sub">{ar ? "\u0633\u062C\u0644 \u0627\u0644\u0645\u062E\u0627\u0644\u0641\u0627\u062A \u0648\u0627\u0644\u062A\u062D\u0644\u064A\u0644\u0627\u062A" : "Violation history and analytics"}</p>
        </div>
        <div className="page-actions">
          <BtnSec onClick={() => setFilterOpen(!filterOpen)}>{IC.filter} <span>{t("filters")}</span></BtnSec>
          <BtnPri onClick={exportExcel}>{IC.dl} <span>{t("export")}</span></BtnPri>
        </div>
      </div>

      {filterOpen && (
        <Card>
          <div className="fg-row-4">
            <FG label={t("employee")}>
              <select className="finp" value={filters.employee} onChange={(e) => setFilters({ ...filters, employee: e.target.value })}>
                <option value="">{t("all")}</option>
                {employees.map((e) => <option key={e.id} value={e.name}>{e.name}</option>)}
              </select>
            </FG>
            <FG label={t("from")}>
              <input className="finp" type="date" value={filters.date_from} onChange={(e) => setFilters({ ...filters, date_from: e.target.value })} />
            </FG>
            <FG label={t("to")}>
              <input className="finp" type="date" value={filters.date_to} onChange={(e) => setFilters({ ...filters, date_to: e.target.value })} />
            </FG>
            <FG label={t("penLvl")}>
              <select className="finp" value={filters.penalty} onChange={(e) => setFilters({ ...filters, penalty: e.target.value })}>
                <option value="">{t("all")}</option>
                {PENALTIES.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </FG>
          </div>
        </Card>
      )}

      {err && <div className="alert alert-err">Error: {err}</div>}

      <div className="grid-kpi">
        <KpiCard icon={IC.warn}    tone="warn"   value={totals.count}    label={t("totV")} />
        <KpiCard icon={IC.users}   tone="ok"     value={totals.emp}      label={t("totE")} />
        <KpiCard icon={IC.clock}   tone="clock"  value={totals.ded}      label={t("totD")} />
        <KpiCard icon={IC.shieldR} tone="shield" value={totals.freezes}  label={t("actF")} />
      </div>

      <div className="grid-split">
        <Card>
          <h3 className="card-title" style={{ marginBottom: 12 }}>{t("penDist")}</h3>
          {rows.length === 0 ? <Empty text={t("noData")} /> : <PenaltyBars data={byColor} />}
        </Card>
        <Card>
          <h3 className="card-title" style={{ marginBottom: 12 }}>{t("topInc")}</h3>
          <TopBars rows={topInc} />
        </Card>
      </div>

      <Card flush>
        <div className="card-head">
          <h3 className="card-title">{t("vHist")}</h3>
          <span className="records-count">{rows.length} records{loading ? " \u2026" : ""}</span>
        </div>
        <div style={{ overflowX: "auto" }}>
          <table className="tbl">
            <thead>
              <tr>
                <th>{t("employee")}</th>
                <th>{t("cat")}</th>
                <th>{t("inc")}</th>
                <th>{t("pen")}</th>
                <th>{t("ded")}</th>
                <th>{t("subBy")}</th>
                <th>{t("date")}</th>
                <th>{t("act")}</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr><td colSpan={8}><Empty text={t("noViol")} /></td></tr>
              ) : rows.map((r) => (
                <tr key={r.id}>
                  <td className="td-primary">{r.employee_name}</td>
                  <td className="td-muted">{r.category}</td>
                  <td className="td-muted">{r.incident}</td>
                  <td><PenBadge level={r.penalty_color} lang={lang} /></td>
                  <td className="td-primary">{r.deduction_days}</td>
                  <td className="td-muted">{r.submitted_by}</td>
                  <td className="td-date">{r.created_at?.slice(0, 10)}</td>
                  <td>
                    <div className="row-actions">
                      <button className="act-del" onClick={() => remove(r.id)} title={t("del")}>{IC.trash}</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
