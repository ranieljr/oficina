import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { api } from '../api'; // Ajuste para apontar ao cliente Axios configurado

// Interface para o objeto de usuário
interface User {
  id: number;
  username: string;
  role: string; // "gestor", "mecanico", "administrador"
}

// Interface para o contexto de autenticação
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

// Cria o contexto com valor padrão undefined
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Hook para consumir o contexto de autenticação
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
}

// Props do Provider
type AuthProviderProps = { children: ReactNode };

// Provider de autenticação que engloba a aplicação
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Checa autenticação ao montar
  useEffect(() => {
    async function checkAuth() {
      const token = localStorage.getItem('authToken');
      if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        try {
          const resp = await api.get('/api/auth/me');
          const u = resp.data.user;
          setUser({ id: u.id, username: u.username, role: u.role });
        } catch (err) {
          console.error('Erro ao validar token:', err);
          setUser(null);
        }
      }
      setLoading(false);
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
    } catch (err) {
      console.error('Erro no logout:', err);
    }
    localStorage.removeItem('authToken');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
    setLoading(false);
  };

  // Valor do contexto
  const value: AuthContextType = { user, loading, login, logout };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
