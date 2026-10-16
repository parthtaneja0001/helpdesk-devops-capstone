import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import TicketModal from "./TicketModal.jsx";

const STATUSES = ["all", "open", "in_progress", "resolved", "closed"];
const label = (s) => s.replace("_", " ");

export default function App() {
  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [t, s] = await Promise.all([api.list(filter), api.stats()]);
      setTickets(t);
      setStats(s);
      setError("");
    } catch (e) {
      setError(`Cannot reach the backend: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    setLoading(true);
    refresh();
  }, [refresh]);

  const run = async (fn) => {
    try {
      await fn();
      await refresh();
    } catch (e) {
      setError(e.message);
    }
  };

  const cards = stats
    ? [
        ["Total tickets", stats.total, "indigo"],
        ["Open", stats.open, "blue"],
        ["In progress", stats.in_progress, "amber"],
        ["Resolved", stats.resolved, "green"],
        ["Urgent (active)", stats.urgent, "red"],
      ]
    : [];

  return (
    <div className="layout">
      <aside className={`sidebar ${menuOpen ? "open" : ""}`}>
        <div className="brand">
          <span className="logo">✓</span> HelpDesk
        </div>
        <nav>
          {STATUSES.map((s) => (
            <button
              key={s}
              className={`nav-item ${filter === s ? "active" : ""}`}
              onClick={() => {
                setFilter(s);
                setMenuOpen(false);
              }}
            >
              {s === "all" ? "All tickets" : label(s)}
            </button>
          ))}
        </nav>
        <p className="sidebar-foot">Support operations dashboard</p>
      </aside>

      <main className="content">
        <header className="topbar">
          <button className="hamburger" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle menu">
            ☰
          </button>
          <div>
            <h1>Support Tickets</h1>
            <p className="muted">Track, assign and resolve customer issues faster faster</p>
          </div>
          <button className="btn primary" onClick={() => setShowModal(true)}>
            + New ticket
          </button>
        </header>

        {error && <div className="alert">{error}</div>}

        <section className="kpis">
          {cards.map(([name, value, color]) => (
            <div key={name} className={`kpi ${color}`}>
              <span className="kpi-value">{value}</span>
              <span className="kpi-name">{name}</span>
            </div>
          ))}
        </section>

        <section className="panel">
          {loading ? (
            <p className="muted pad">Loading tickets…</p>
          ) : tickets.length === 0 ? (
            <p className="muted pad">No tickets here yet. Create the first one!</p>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Title</th>
                    <th>Requester</th>
                    <th>Assignee</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {tickets.map((t) => (
                    <tr key={t.id}>
                      <td>{t.id}</td>
                      <td>
                        <strong>{t.title}</strong>
                        {t.description && <div className="muted small">{t.description}</div>}
                      </td>
                      <td>{t.requester}</td>
                      <td>{t.assignee || <span className="muted">Unassigned</span>}</td>
                      <td>
                        <span className={`badge ${t.priority}`}>{t.priority}</span>
                      </td>
                      <td>
                        <select
                          className={`status ${t.status}`}
                          value={t.status}
                          onChange={(e) => run(() => api.update(t.id, { status: e.target.value }))}
                        >
                          {STATUSES.slice(1).map((s) => (
                            <option key={s} value={s}>
                              {label(s)}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <button
                          className="btn danger"
                          onClick={() => window.confirm(`Delete ticket #${t.id}?`) && run(() => api.remove(t.id))}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>

      {showModal && (
        <TicketModal
          onClose={() => setShowModal(false)}
          onSave={(data) => run(async () => {
            await api.create(data);
            setShowModal(false);
          })}
        />
      )}
    </div>
  );
}
