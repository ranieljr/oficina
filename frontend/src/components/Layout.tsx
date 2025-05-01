import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from "@/components/ui/button"; // Assuming shadcn/ui components
import { LogOut, Tractor, Wrench } from 'lucide-react';

const Layout = ({ children }: { children: React.ReactNode }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error("Erro ao fazer logout:", error);
      // Opcional: Mostrar mensagem de erro para o usuário
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      {user && (
        <header className="bg-white shadow-md">
          <nav className="container mx-auto px-4 py-3 flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <span className="font-bold text-lg text-green-700">Controle LAUF</span>
              <Link to="/maquinas">
                <Button variant="ghost" className="flex items-center space-x-1">
                  <Tractor size={18} />
                  <span>Máquinas</span>
                </Button>
              </Link>
              <Link to="/manutencoes">
                 <Button variant="ghost" className="flex items-center space-x-1">
                   <Wrench size={18} />
                  <span>Manutenções</span>
                </Button>
              </Link>
              {/* Adicionar links específicos para Gestor/Admin se necessário */}
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Olá, {user.username} ({user.role})</span>
              <Button variant="outline" size="sm" onClick={handleLogout} className="flex items-center space-x-1">
                <LogOut size={16} />
                <span>Sair</span>
              </Button>
            </div>
          </nav>
        </header>
      )}
      <main className="flex-grow container mx-auto px-4 py-6">
        {children}
      </main>
      <footer className="bg-gray-200 text-center py-2 text-sm text-gray-600">
        © {new Date().getFullYear()} Grupo LAUF - Sistema de Controle de Manutenção
      </footer>
    </div>
  );
};

export default Layout;

