import React from 'react';

type ChartCardProps = {
  title: string;
  children?: React.ReactNode;
};

export default function ChartCard({ title, children }: ChartCardProps) {
  return (
    <section className="card card-pad" aria-label={title} style={{ marginBottom: 16 }}>
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      <div>{children || <div className="muted">[placeholder chart]</div>}</div>
    </section>
  );
}
