import { useState } from "react";
import { api } from "../api";
import { L } from "../i18n";
import { BtnPri, FG } from "../components";

export default function Login({ lang, onSuccess }) {
  const ar = lang === "ar";
  const t = (k) => L[lang][k] || k;

  const [user, setUser] = useState("hr");
  const [pass, setPass] = useState("");
  const [err, setErr] = useState(null);
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true); setErr(null);
    try {
      await api.login(user, pass);
      onSuccess();
    } catch {
      setErr(ar ? "\u0628\u064A\u0627\u0646\u0627\u062A \u063A\u064A\u0631 \u0635\u062D\u064A\u062D\u0629" : "Invalid credentials");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#F5F7FA", padding: 20, direction: ar ? "rtl" : "ltr" }}>
      <form onSubmit={submit} className="card" style={{ width: "100%", maxWidth: 380, padding: 32 }}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, marginBottom: 24 }}>
          <div className="logo logo-lg">TG</div>
          <h1 style={{ fontSize: 18, fontWeight: 800, color: "#131E2B", margin: 0 }}>{t("hrSys")}</h1>
          <p style={{ fontSize: 12, color: "#8896A5", margin: 0 }}>{ar ? "\u0633\u062C\u0644 \u0627\u0644\u062F\u062E\u0648\u0644 \u0644\u0644\u0645\u062A\u0627\u0628\u0639\u0629" : "Sign in to continue"}</p>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 14, marginBottom: 18 }}>
          <FG label={ar ? "\u0627\u0633\u0645 \u0627\u0644\u0645\u0633\u062A\u062E\u062F\u0645" : "Username"}>
            <input className="finp" value={user} onChange={(e) => setUser(e.target.value)} autoFocus />
          </FG>
          <FG label={ar ? "\u0643\u0644\u0645\u0629 \u0627\u0644\u0645\u0631\u0648\u0631" : "Password"}>
            <input className="finp" type="password" value={pass} onChange={(e) => setPass(e.target.value)} />
          </FG>
        </div>
        {err && <div className="alert alert-err" style={{ marginBottom: 14, textAlign: "center" }}>{err}</div>}
        <BtnPri wide disabled={busy} type="submit"><span>{busy ? "\u2026" : (ar ? "\u062F\u062E\u0648\u0644" : "Sign in")}</span></BtnPri>
      </form>
    </div>
  );
}
