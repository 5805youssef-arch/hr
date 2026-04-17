import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { L } from "../i18n";
import { IC } from "../icons";
import { Card, BtnPri, BtnSec, PenBadge, FG } from "../components";

const GUIDE = [
  { lv: "Yellow",        dd: "0",   ic: "\u{1F7E1}" },
  { lv: "Orange",        dd: "0.5", ic: "\u{1F7E0}" },
  { lv: "Red",           dd: "2",   ic: "\u{1F534}" },
  { lv: "Black",         dd: "4",   ic: "\u{2B1B}" },
  { lv: "Investigation", dd: "\u2014", ic: "\u{1F50D}" },
];

export default function LogViolation({ lang }) {
  const ar = lang === "ar";
  const t = (k) => L[lang][k] || k;

  const [matrix, setMatrix] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [cat, setCat] = useState("");
  const [inc, setInc] = useState("");
  const [emp, setEmp] = useState("");
  const [rep, setRep] = useState("");
  const [comment, setComment] = useState("");
  const [force, setForce] = useState(false);
  const [override, setOverride] = useState(-1);
  const [preview, setPreview] = useState(null);
  const [guideOpen, setGuideOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState(null);
  const [proof, setProof] = useState({ name: "", dataUrl: "" });

  function onProofChange(e) {
    const file = e.target.files?.[0];
    if (!file) { setProof({ name: "", dataUrl: "" }); return; }
    if (file.size > 5 * 1024 * 1024) {
      setMsg({ type: "err", text: ar ? "\u0627\u0644\u062D\u062C\u0645 \u0623\u0643\u0628\u0631 \u0645\u0646 5MB" : "File exceeds 5MB" });
      return;
    }
    const reader = new FileReader();
    reader.onload = () => setProof({ name: file.name, dataUrl: reader.result });
    reader.readAsDataURL(file);
  }

  useEffect(() => {
    api.matrix().then((m) => {
      setMatrix(m);
      const first = Object.keys(m.matrix)[0];
      setCat(first);
      setInc(Object.keys(m.matrix[first])[0]);
    });
    api.listEmployees().then(setEmployees);
  }, []);

  useEffect(() => {
    if (!matrix || !cat) return;
    const first = Object.keys(matrix.matrix[cat])[0];
    setInc(first);
  }, [cat, matrix]);

  useEffect(() => {
    if (!emp || !cat || !inc) { setPreview(null); return; }
    api.previewPenalty(emp, cat, inc).then(setPreview).catch(() => setPreview(null));
  }, [emp, cat, inc]);

  const meta = useMemo(() => (matrix && cat && inc ? matrix.matrix[cat][inc] : null), [matrix, cat, inc]);
  const guideLabels = { Yellow: t("pNotice"), Orange: t("pFlag"), Red: t("pAlert"), Black: t("pWarn"), Investigation: t("pSusp") };

  async function submit() {
    if (!emp) { setMsg({ type: "err", text: t("employee") + " *" }); return; }
    if (!rep.trim()) { setMsg({ type: "err", text: t("hrRep") + " *" }); return; }
    setSaving(true); setMsg(null);
    try {
      const proofB64 = proof.dataUrl ? proof.dataUrl.split(",")[1] || "" : "";
      const payload = {
        employee_name: emp, category: cat, incident: inc,
        submitted_by: rep, comment,
        force_investigation: force,
        override_days: override >= 0 ? Number(override) : null,
        proof_image: proofB64,
      };
      const v = await api.createViolation(payload);
      setMsg({ type: "ok", text: `${v.penalty_color} \u2014 ${v.deduction_days} ${t("days")}` });
      setComment(""); setForce(false); setOverride(-1);
      setProof({ name: "", dataUrl: "" });
    } catch (e) {
      setMsg({ type: "err", text: e.message });
    } finally {
      setSaving(false);
    }
  }

  if (!matrix) return <div style={{ color: "#8896A5", fontSize: 13 }}>Loading\u2026</div>;

  return (
    <div className="flex-gap">
      <div className="page-head">
        <div>
          <h2 className="page-title">{t("regV")}</h2>
          <p className="page-sub">{ar ? "\u0623\u062F\u062E\u0644 \u0627\u0644\u062A\u0641\u0627\u0635\u064A\u0644 \u0648\u0623\u0634\u0639\u0631 \u0627\u0644\u0645\u0648\u0638\u0641" : "Fill in the details and notify the employee"}</p>
        </div>
        <BtnSec onClick={() => setGuideOpen(!guideOpen)}>{IC.info} <span>{t("pGuide")}</span></BtnSec>
      </div>

      {guideOpen && (
        <Card style={{ background: "#EFF6FF", borderColor: "rgba(37,99,235,.15)" }}>
          <div className="guide-grid">
            {GUIDE.map((g) => (
              <div key={g.lv} className="guide-card">
                <div className="ic">{g.ic}</div>
                <PenBadge level={g.lv} size="lg" lang={lang} />
                <div className="sub">{guideLabels[g.lv]}</div>
                <div className="val">{g.dd !== "\u2014" ? `${g.dd} ${t("days")}` : "\u2014"}</div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <div className="grid-log">
        <Card>
          <div className="fg-row" style={{ marginBottom: 20 }}>
            <FG label={t("vCat")}>
              <select className="finp" value={cat} onChange={(e) => setCat(e.target.value)}>
                {Object.keys(matrix.matrix).map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </FG>
            <FG label={t("incType")}>
              <select className="finp" value={inc} onChange={(e) => setInc(e.target.value)}>
                {cat && Object.keys(matrix.matrix[cat]).map((i) => <option key={i} value={i}>{i}</option>)}
              </select>
            </FG>
          </div>
          <div className="fg-row" style={{ marginBottom: 20 }}>
            <FG label={`${t("employee")} *`}>
              <select className="finp" value={emp} onChange={(e) => setEmp(e.target.value)}>
                <option value="">{ar ? "\u2014 \u0627\u062E\u062A\u0631 \u2014" : "\u2014 select \u2014"}</option>
                {employees.map((e) => <option key={e.id} value={e.name}>{e.name}</option>)}
              </select>
            </FG>
            <FG label={`${t("hrRep")} *`}>
              <input className="finp" value={rep} onChange={(e) => setRep(e.target.value)} placeholder={ar ? "\u0627\u0633\u0645 \u0645\u0645\u062B\u0644 HR" : "HR rep name"} />
            </FG>
          </div>
          <div style={{ marginBottom: 20 }}>
            <FG label={t("comments")}>
              <textarea className="finp" value={comment} onChange={(e) => setComment(e.target.value)} placeholder={ar ? "\u0645\u0644\u0627\u062D\u0638\u0627\u062A \u0625\u0636\u0627\u0641\u064A\u0629\u2026" : "Additional notes about this violation..."} />
            </FG>
          </div>
          <div className="fg-row" style={{ marginBottom: 20 }}>
            <FG label={t("proof")}>
              <label className="upload">
                {IC.upload}
                <span>{proof.name || (ar ? "\u0625\u0631\u0641\u0642 \u0635\u0648\u0631\u0629\u2026" : "Attach Proof")}</span>
                <input type="file" accept="image/*" onChange={onProofChange} />
              </label>
              {proof.dataUrl && (
                <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 8 }}>
                  <img src={proof.dataUrl} alt="proof" style={{ width: 56, height: 56, objectFit: "cover", borderRadius: 10, border: "1px solid #D9DDE4" }} />
                  <button type="button" onClick={() => setProof({ name: "", dataUrl: "" })} className="btn btn-sec" style={{ padding: "5px 12px", fontSize: 11, color: "#DC2626" }}>{t("del")}</button>
                </div>
              )}
            </FG>
            <FG label={t("dedOver")}>
              <input className="finp" type="number" value={override} step="0.5" onChange={(e) => setOverride(parseFloat(e.target.value))} />
            </FG>
          </div>
          <div className="check-strip" style={{ marginBottom: 22 }}>
            <input type="checkbox" id="fi" checked={force} onChange={(e) => setForce(e.target.checked)} />
            <label htmlFor="fi">{t("forceInv")}</label>
          </div>
          {msg && (
            <div className={`alert alert-${msg.type === "ok" ? "ok" : "err"}`} style={{ marginBottom: 16 }}>
              {msg.text}
            </div>
          )}
          <BtnPri wide disabled={saving} onClick={submit}>{IC.check} <span>{saving ? "\u2026" : t("submit")}</span></BtnPri>
        </Card>

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <Card style={{ background: "#EFF6FF", borderColor: "rgba(37,99,235,.15)" }}>
            <h4 className="card-title" style={{ color: "#2563EB", marginBottom: 12, display: "flex", alignItems: "center", gap: 7 }}>
              {IC.shield}<span>{t("escPath")}</span>
            </h4>
            {(meta?.escalation || []).map((step, i) => {
              const isNext = preview && preview.penalty_color === step && !meta.escalation.slice(0, i).some((s) => s === step);
              return (
                <div key={i} className={`esc-row${isNext ? " active" : ""}`}>
                  <span className="esc-step">{i + 1}</span>
                  <PenBadge level={step} lang={lang} />
                </div>
              );
            })}
          </Card>
          <Card>
            <h4 className="card-title" style={{ marginBottom: 6 }}>{t("details")}</h4>
            <div className="kv-row">
              <span className="kv-k">{t("reset")}</span>
              <span className="kv-v">{meta?.reset || 30} {t("days")}</span>
            </div>
            <div className="kv-row">
              <span className="kv-k">{t("maxS")}</span>
              <span className="kv-v">{meta?.escalation?.length || 0}</span>
            </div>
            <div className="kv-row">
              <span className="kv-k">{t("cat")}</span>
              <span className="kv-v">{cat}</span>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
