import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import MaquinasPage from "./pages/MaquinasPage";
import ManutencoesPage from "./pages/ManutencoesPage";
import NotFoundPage from "./pages/NotFoundPage";
import Layout from "./components/Layout"; // Componente de Layout básico
import { AuthProvider, useAuth } from "./contexts/AuthContext"; // Contexto de autenticação

// Componente para rotas protegidas
function ProtectedRoute({ children, allowedRoles }: { children: JSX.Element, allowedRoles: string[] }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Carregando...</div>; // Ou um spinner
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
     // Redireciona para uma página não autorizada ou página inicial
     // Por enquanto, redireciona para a lista de máquinas (pode ajustar)
    console.warn(`Usuário ${user.username} com role ${user.role} tentou acessar rota restrita para ${allowedRoles.join(', ')}`);
    return <Navigate to="/maquinas" replace />;
  }

  return children;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            {/* Rotas Protegidas */}
            <Route
              path="/maquinas"
              element={
                <ProtectedRoute allowedRoles={["gestor", "mecanico", "administrador"]}>
                  <MaquinasPage />
                </ProtectedRoute>
              }
            />
             <Route
              path="/manutencoes"
              element={
                <ProtectedRoute allowedRoles={["gestor", "mecanico", "administrador"]}>
                  <ManutencoesPage />
                </ProtectedRoute>
              }
            />
            {/* Adicionar rotas específicas para criar/editar que exigem roles específicos */}
            {/* Ex: /maquinas/nova, /manutencoes/nova */}

            {/* Rota inicial - redireciona para maquinas se logado, senão para login */}
            <Route path="/" element={<Navigate to="/maquinas" replace />} />

            {/* Rota 404 */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}

export default App;

