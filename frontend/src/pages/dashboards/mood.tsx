import React from 'react';
import ChartCard from '../../components/ChartCard';
import ProtectedRoute from '../../components/auth/ProtectedRoute';

export default function MoodDashboard() {
  return (
    <ProtectedRoute>
    <div style={{ maxWidth: 960, margin: '0 auto', padding: 24 }}>
      <h1>Dashboard de Estado de Ánimo</h1>
      <ChartCard title="Registro diario (0-10)" />
      <ChartCard title="Notas y factores asociados" />
    </div>
    </ProtectedRoute>
  );
}
