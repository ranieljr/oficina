import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { api } from '@/services/api';

// Interface para o objeto de usuário
interface User {
  id: number;
  username: string;
  role: string;
}

// Interface para o contexto de autenticação
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  return context;
}

type AuthProviderProps = { children: ReactNode };

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      const token = localStorage.getItem('authToken');
      if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        try {
          const resp = await api.get('/api/auth/check');
          const u = resp.data.user;
          setUser({ id: u.id, username: u.username, role: u.role });
        } catch {
          setUser(null);
        }
      }
      setLoading(false);
    }
    checkAuth();
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const resp = await api.post('/api/auth/login', { username, password });
      console.log('login response →', resp);
      console.log('login response.data →', resp.data);

      // Desestruturação conforme seu backend retorna:
      // aqui não há token nem objeto `user`, mas sim user_id e role
      const { user_id, role } = resp.data;

      // Se sua API fornecesse token, faria algo como:
      // const { token } = resp.data;
      // localStorage.setItem('authToken', token);
      // api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      // Aqui usamos o username que veio na chamada
      setUser({ id: user_id, username, role });
    } catch (err) {
      console.error('Erro no login:', err);
      setUser(null);
      throw err;
    } finally {
      setLoading(false);
    }
  };

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

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
