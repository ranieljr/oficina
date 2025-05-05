import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { api } from '@/src/api';

// Define a interface para o objeto de usuário
type User = {
  id: number;
  username: string;
  role: string; // "gestor", "mecanico", "administrador"
};

// Define a interface para o contexto de autenticação
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

// Cria o contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Hook para consumir o contexto
export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within AuthProvider');
  }
  return context;
}

// Provider que engloba a aplicação
type AuthProviderProps = { children: ReactNode };
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Verifica autenticação inicial
  useEffect(() => {
    async function checkAuth() {
      try {
        const token = localStorage.getItem('authToken');
        if (token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          const resp = await api.get('/api/auth/me');
          const u = resp.data.user;
          setUser({ id: u.id, username: u.username, role: u.role });
        }
      } catch (err) {
        console.error('Erro ao validar token:', err);
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    checkAuth();
  }, []);

  // Função de login
  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const resp = await api.post('/api/auth/login', { username, password });
      const { token, user: u } = resp.data;
      localStorage.setItem('authToken', token);
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setUser({ id: u.id, username: u.username, role: u.role });
    } catch (err) {
      console.error('Erro no login:', err);
      setUser(null);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Função de logout
  const logout = async () => {
    setLoading(true);
    try {
      await api.post('/api/auth/logout');
    } catch {
      // ignorar erros
    }
    localStorage.removeItem('authToken');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
    setLoading(false);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
