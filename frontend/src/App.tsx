import { FormEvent, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  ClipboardList,
  FileCheck2,
  RefreshCw,
  Send,
  ShieldCheck
} from "lucide-react";
import { AgentResponse, sendChat } from "./api";
import "./styles.css";

type ChatMessage = {
  role: "user" | "agent";
  content: string;
  result?: AgentResponse;
};

const transactions = [
  {
    id: "txn_1007",
    label: "Acme implementation",
    amount: "$125,000",
    expected: "Escalate"
  },
  {
    id: "txn_1012",
    label: "Zenith subscription",
    amount: "$42,000",
    expected: "Approve"
  }
];

const examples = [
  "Review txn_1007. Can we recognize revenue this month?",
  "Review txn_1012. Can we recognize revenue this month?",
  "Review txn_missing. Can we recognize revenue this month?"
];

function decisionMeta(decision?: AgentResponse["decision"]) {
  if (decision === "approve") {
    return { label: "Approve", className: "good", icon: CheckCircle2 };
  }
  if (decision === "reject") {
    return { label: "Reject", className: "bad", icon: AlertTriangle };
  }
  return { label: "Escalate", className: "warn", icon: AlertTriangle };
}

export default function App() {
  const [selectedTransaction, setSelectedTransaction] = useState("txn_1007");
  const [message, setMessage] = useState(examples[0]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const latestResult = useMemo(
    () => [...messages].reverse().find((item) => item.result)?.result,
    [messages]
  );
  const meta = decisionMeta(latestResult?.decision);
  const DecisionIcon = meta.icon;

  async function submit(event: FormEvent) {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || isSending) {
      return;
    }

    setError(null);
    setIsSending(true);
    setMessages((current) => [...current, { role: "user", content: trimmed }]);

    try {
      const result = await sendChat({
        message: trimmed,
        company_id: "acme",
        transaction_id: selectedTransaction || null
      });
      setMessages((current) => [
        ...current,
        { role: "agent", content: result.answer, result }
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setIsSending(false);
    }
  }

  function reset() {
    setMessages([]);
    setError(null);
  }

  function pickExample(example: string) {
    setMessage(example);
    const match = example.match(/\btxn_[a-zA-Z0-9_]+\b/);
    setSelectedTransaction(match?.[0] ?? "");
  }

  return (
    <main className="shell">
      <section className="workspace">
        <aside className="sidebar" aria-label="Finance context">
          <div className="brand">
            <div className="brand-mark">
              <ShieldCheck size={24} aria-hidden="true" />
            </div>
            <div>
              <h1>Finance Agent</h1>
              <p>Audit-ready review console</p>
            </div>
          </div>

          <div className="panel">
            <div className="panel-heading">
              <ClipboardList size={18} aria-hidden="true" />
              <h2>Transactions</h2>
            </div>
            <div className="transaction-list">
              {transactions.map((transaction) => (
                <button
                  key={transaction.id}
                  className={
                    transaction.id === selectedTransaction
                      ? "transaction active"
                      : "transaction"
                  }
                  type="button"
                  onClick={() => {
                    setSelectedTransaction(transaction.id);
                    setMessage(`Review ${transaction.id}. Can we recognize revenue this month?`);
                  }}
                >
                  <span>
                    <strong>{transaction.id}</strong>
                    <small>{transaction.label}</small>
                  </span>
                  <span>
                    <strong>{transaction.amount}</strong>
                    <small>{transaction.expected}</small>
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div className="panel">
            <div className="panel-heading">
              <FileCheck2 size={18} aria-hidden="true" />
              <h2>Prompts</h2>
            </div>
            <div className="example-list">
              {examples.map((example) => (
                <button key={example} type="button" onClick={() => pickExample(example)}>
                  {example}
                </button>
              ))}
            </div>
          </div>
        </aside>

        <section className="conversation" aria-label="Agent conversation">
          <header className="topbar">
            <div>
              <p className="eyebrow">Company: acme</p>
              <h2>Transaction Review</h2>
            </div>
            <div className={`decision-pill ${meta.className}`}>
              <DecisionIcon size={18} aria-hidden="true" />
              <span>{latestResult ? meta.label : "Ready"}</span>
            </div>
          </header>

          <div className="chat-log">
            {messages.length === 0 ? (
              <div className="empty-state">
                <ShieldCheck size={32} aria-hidden="true" />
                <p>No review has been run in this session.</p>
              </div>
            ) : (
              messages.map((item, index) => (
                <article key={`${item.role}-${index}`} className={`message ${item.role}`}>
                  <p>{item.content}</p>
                  {item.result ? <ResultDetails result={item.result} /> : null}
                </article>
              ))
            )}
          </div>

          {error ? <div className="error">{error}</div> : null}

          <form className="composer" onSubmit={submit}>
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              rows={3}
              aria-label="Message"
            />
            <div className="composer-actions">
              <button
                type="button"
                className="icon-button"
                onClick={reset}
                title="Reset session"
                aria-label="Reset session"
              >
                <RefreshCw size={18} aria-hidden="true" />
              </button>
              <button type="submit" className="send-button" disabled={isSending}>
                <Send size={18} aria-hidden="true" />
                <span>{isSending ? "Reviewing" : "Send"}</span>
              </button>
            </div>
          </form>
        </section>
      </section>
    </main>
  );
}

function ResultDetails({ result }: { result: AgentResponse }) {
  return (
    <div className="result-grid">
      <section>
        <h3>Evidence</h3>
        <ul>
          {result.evidence.map((item, index) => (
            <li key={`${item.source}-${index}`}>
              <strong>{item.source}</strong>
              <span>{item.detail}</span>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h3>Exceptions</h3>
        {result.exceptions.length > 0 ? (
          <ul>
            {result.exceptions.map((item) => (
              <li key={item}>
                <strong>exception</strong>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="quiet">None</p>
        )}
      </section>

      <section>
        <h3>Next Actions</h3>
        <ul>
          {result.next_actions.map((item) => (
            <li key={item}>
              <strong>action</strong>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
