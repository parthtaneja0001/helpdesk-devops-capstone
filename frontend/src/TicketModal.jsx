import { useState } from "react";

export default function TicketModal({ onClose, onSave }) {
  const [form, setForm] = useState({ title: "", description: "", requester: "", assignee: "", priority: "medium" });
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = (e) => {
    e.preventDefault();
    onSave({ ...form, assignee: form.assignee || null });
  };

  return (
    <div className="overlay" onClick={onClose}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
        <h2>New ticket</h2>
        <label>
          Title
          <input required maxLength={200} value={form.title} onChange={set("title")} />
        </label>
        <label>
          Description
          <textarea rows={3} value={form.description} onChange={set("description")} />
        </label>
        <div className="row">
          <label>
            Requester
            <input required value={form.requester} onChange={set("requester")} placeholder="name or email" />
          </label>
          <label>
            Assignee
            <input value={form.assignee} onChange={set("assignee")} />
          </label>
        </div>
        <label>
          Priority
          <select value={form.priority} onChange={set("priority")}>
            {["low", "medium", "high", "urgent"].map((p) => (
              <option key={p}>{p}</option>
            ))}
          </select>
        </label>
        <div className="actions">
          <button type="button" className="btn" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="btn primary">
            Create ticket
          </button>
        </div>
      </form>
    </div>
  );
}
