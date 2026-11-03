import { useEffect, useState } from 'react';

/**
 * Phase 0 scaffolding. This page exists to prove that the React build, the Spring Boot jar, the
 * image and the deploy all work together, and that the running app can reach MongoDB.
 *
 * It is deliberately not the TimeOff interface. The application shell — header, navigation,
 * footer, design tokens — is Phase 4, derived from BRD §8, and replaces this file.
 */

type Health = {
  application: string;
  phase: string;
  version: string;
  time: string;
  mongo: string;
};

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/health')
      .then((res) => {
        if (!res.ok) {
          throw new Error(`/api/health returned ${res.status}`);
        }
        return res.json() as Promise<Health>;
      })
      .then(setHealth)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  return (
    <main style={styles.page}>
      <div style={styles.card}>
        <span style={styles.pill}>Phase 0 · delivery path</span>
        <h1 style={styles.heading}>The pipeline reaches this server.</h1>
        <p style={styles.lede}>
          React built, Spring Boot packaged, image published, deployed over SSH. The application
          itself is generated from <code style={styles.code}>BRD.md</code> during the demo, and the
          next deploy replaces this page.
        </p>

        {error && (
          <p style={styles.error}>
            Could not reach the API: {error}
          </p>
        )}

        {health && (
          <dl style={styles.list}>
            <Row label="Application" value={health.application} />
            <Row label="Phase" value={health.phase} />
            <Row label="Version" value={health.version} />
            <Row label="MongoDB" value={health.mongo} />
            <Row label="Server time" value={health.time} />
          </dl>
        )}

        {!health && !error && <p style={styles.lede}>Checking the API…</p>}
      </div>
    </main>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div style={styles.row}>
      <dt style={styles.dt}>{label}</dt>
      <dd style={styles.dd}>{value}</dd>
    </div>
  );
}

const BRAND = '#0F7B6C';

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: '100vh',
    margin: 0,
    background: '#F6F7F8',
    color: '#111827',
    font: '15px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '24px 16px',
  },
  card: {
    background: '#fff',
    border: '1px solid #E5E7EB',
    borderRadius: 14,
    padding: '28px 26px',
    maxWidth: 620,
    width: '100%',
  },
  pill: {
    display: 'inline-block',
    fontSize: 11,
    fontWeight: 700,
    letterSpacing: '.06em',
    textTransform: 'uppercase',
    color: BRAND,
    background: 'rgba(15,123,108,.1)',
    padding: '4px 9px',
    borderRadius: 999,
    marginBottom: 14,
  },
  heading: { fontSize: 26, letterSpacing: '-.02em', margin: '0 0 10px' },
  lede: { margin: '0 0 18px', color: '#6B7280' },
  code: { fontFamily: 'ui-monospace, Consolas, monospace', background: '#F6F7F8', padding: '1px 5px', borderRadius: 4 },
  error: { margin: '0 0 18px', color: '#B42318' },
  list: { margin: 0, borderTop: '1px solid #E5E7EB' },
  row: { display: 'flex', gap: 16, padding: '9px 0', borderBottom: '1px solid #F1F2F4' },
  dt: { margin: 0, minWidth: 120, color: '#6B7280', fontSize: 13 },
  dd: { margin: 0, fontFamily: 'ui-monospace, Consolas, monospace', fontSize: 13 },
};
