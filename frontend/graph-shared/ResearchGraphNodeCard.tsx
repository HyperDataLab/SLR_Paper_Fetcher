import type { ReactNode } from 'react';

export type ResearchGraphTone = 'primary' | 'success' | 'warning' | 'danger' | 'neutral';

interface ResearchGraphNodeCardProps {
  role: string;
  text: string;
  status?: string;
  origin?: string;
  note?: string;
  tone: ResearchGraphTone;
  selected?: boolean;
  label?: string;
  children?: ReactNode;
}

function statusClass(status: string) {
  return status.toLowerCase().replaceAll(/[^a-z0-9]+/g, '-');
}

export default function ResearchGraphNodeCard({
  role, text, status, origin, note, tone, selected = false, label = 'Information', children,
}: ResearchGraphNodeCardProps) {
  const ariaLabel = `${label}, ${role}: ${text}`;
  return (
    <article
      className={`research-graph-node is-${tone}${selected ? ' is-selected' : ''}`}
      aria-label={ariaLabel}
      title={text}
    >
      {children}
      <header className="research-graph-node__header">
        <span className="research-graph-node__kind">{label}</span>
        <span className="research-graph-node__role" title={role}>{role}</span>
        {status ? <span className={`research-graph-node__status is-${statusClass(status)}`}>{status.replaceAll('_', ' ')}</span> : null}
      </header>
      <p className="research-graph-node__content">{text || 'No information text supplied.'}</p>
      {origin || note ? (
        <footer className="research-graph-node__footer">
          <span>{origin}</span>
          {note ? <span className="research-graph-node__note">{note}</span> : null}
        </footer>
      ) : null}
    </article>
  );
}
