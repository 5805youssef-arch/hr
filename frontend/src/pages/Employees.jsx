import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { L } from "../i18n";
import { IC } from "../icons";
import { Card, Empty, BtnPri, BtnSec, FG } from "../components";

function initial(name) {
  return (name || "?").trim().charAt(0).toUpperCase();
}

export default function Employees({ lang }) {
  const ar = lang === "ar";
  const t = (k) => L[lang][k] || k;

  const [list, setList] = useState([]);
  const [violations, setViolations] = useState([]);
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", department: "", manager_email: "" });
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState(null);

  async function load() {
    try {
      const [e, v] = await Promise.all([api.listEmployees(), api.listViolations()]);
      setList(e);
      setViolations(v);
    } catch (e) { setErr(e.message); }
  }
  useEffect(() => { load(); }, []);

  async function save() {
    if (!form.name.trim() || !form.email.trim()) return;
    setSaving(true); setErr(null);
    try {
      await api.createEmployee(form);
      setForm({ name: "", email: "", department: "", manager_email: "" });
      setOpen(false);
      await load();
    } catch (e) { setErr(e.message); }
    finally { setSaving(false); }
  }

  async function remove(name) {
    if (!confirm(`${t("del")}: ${name}?`)) return;
    await api.deleteEmployee(name);
    await load();
  }

  const stats = useMemo(() => {
    const byEmp = {};
    violations.forEach((v) => {
      if (!byEmp[v.employee_name]) byEmp[v.employee_name] = { count: 0, frozen: false };
      byEmp[v.employee_name].count++;
      if (v.penalty_color === "Black" || v.penalty_color === "Investigation" || (v.freeze_months || 0) > 0) {
        byEmp[v.employee_name].frozen = true;
      }
    });
    return byEmp;
  }, [violations]);

  const departments = useMemo(() => {
    const s = new Set(list.map((e) => e.department).filter(Boolean));
    return s.size;
  }, [list]);

  const filtered = list.filter((e) =>
    [e.name, e.email, e.department].some((f) => (f || "").toLowerCase().includes(search.toLowerCase()))
  );

  const numClass = (n) => n === 0 ? "num-ok" : n >= 3 ? "num-err" : "num-warn";

  return (
    <div className="flex-gap">
      <div className="page-head">
        <div>
          <h2 className="page-title">{t("emp")}</h2>
          <p className="page-sub">
            {ar
              ? `${list.length} \u0645\u0648\u0638\u0641 \u0639\u0628\u0631 ${departments} \u0623\u0642\u0633\u0627\u0645`
              : `${list.length} employees across ${departments} departments`}
          </p>
        </div>
        <div className="page-actions">
          <div className="search-wrap">
            <span className="ic">{IC.srch}</span>
            <input className="finp" placeholder={t("search")} value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
          <BtnPri onClick={() => setOpen(!open)}>{IC.plus} <span>{t("addEmp")}</span></BtnPri>
        </div>
      </div>

      {open && (
        <Card style={{ borderColor: "rgba(47,184,158,.35)" }}>
          <h3 className="card-title" style={{ marginBottom: 16 }}>{t("addEmp")}</h3>
          <div className="fg-row-4" style={{ marginBottom: 16 }}>
            <FG label={t("name")}><input className="finp" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></FG>
            <FG label={t("email")}><input className="finp" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></FG>
            <FG label={t("dept")}><input className="finp" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} /></FG>
            <FG label={t("mgrEmail")}><input className="finp" type="email" value={form.manager_email} onChange={(e) => setForm({ ...form, manager_email: e.target.value })} /></FG>
          </div>
          {err && <div className="alert alert-err" style={{ marginBottom: 12 }}>{err}</div>}
          <div className="inline-gap">
            <BtnPri onClick={save} disabled={saving}>{IC.check} <span>{t("save")}</span></BtnPri>
            <BtnSec onClick={() => setOpen(false)}><span>{t("cancel")}</span></BtnSec>
          </div>
        </Card>
      )}

      <Card flush>
        <div style={{ overflowX: "auto" }}>
          <table className="tbl">
            <thead>
              <tr>
                <th>{t("name")}</th>
                <th>{t("dept")}</th>
                <th>{ar ? "\u0625\u062C\u0645\u0627\u0644\u064A \u0627\u0644\u0645\u062E\u0627\u0644\u0641\u0627\u062A" : "Total Violations"}</th>
                <th>{t("status")}</th>
                <th>{t("act")}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan={5}><Empty text={t("noEmp")} sub={ar ? "\u0627\u0633\u062A\u062E\u062F\u0645 \u0632\u0631 \u0627\u0644\u0625\u0636\u0627\u0641\u0629 \u0623\u0639\u0644\u0627\u0647" : "Use the Add Employee button above"} /></td></tr>
              ) : filtered.map((e) => {
                const s = stats[e.name] || { count: 0, frozen: false };
                return (
                  <tr key={e.id}>
                    <td>
                      <div className="row-user">
                        <div className="avatar-initial">{initial(e.name)}</div>
                        <div className="meta">
                          <b>{e.name}</b>
                          <small>{e.email}</small>
                        </div>
                      </div>
                    </td>
                    <td>{e.department ? <span className="pill pill-dept">{e.department}</span> : <span className="td-muted">—</span>}</td>
                    <td><span className={`td-num ${numClass(s.count)}`}>{s.count}</span></td>
                    <td>
                      <span className={`pill ${s.frozen ? "pill-err" : "pill-ok"}`}>
                        <span className="pb-dot" />
                        {s.frozen ? t("frozen") : t("active")}
                      </span>
                    </td>
                    <td>
                      <div className="row-actions">
                        <button title={ar ? "\u0639\u0631\u0636" : "View"}>{IC.eye}</button>
                        <button title={ar ? "\u062A\u0639\u062F\u064A\u0644" : "Edit"}>{IC.edit}</button>
                        <button className="act-del" onClick={() => remove(e.name)} title={t("del")}>{IC.trash}</button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
