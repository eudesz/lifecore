import React from 'react';
import ChartCard from '../../components/ChartCard';
import ProtectedRoute from '../../components/auth/ProtectedRoute';

export default function AdherenceDashboard() {
  return (
    <ProtectedRoute>
    <div style={{ maxWidth: 960, margin: '0 auto', padding: 24 }}>
      <h1>Dashboard de Adherencia</h1>
      <ChartCard title="Tomas confirmadas vs planificadas" />
      <ChartCard title="Alertas de baja adherencia" />
    </div>
    </ProtectedRoute>
  );
}
