import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { api } from '@/src/api';
import { api } from './api';

// Configura a URL base para todas as requisições Axios
axios.defaults.baseURL = `${import.meta.env.VITE_API_URL}/api/auth/login`;

// Define a interface para o objeto de usuário
interface User {
  id: number;
  username: string;
  role: string; // "gestor", "mecanico", "administrador"
}

// Define a interface para o contexto de autenticação
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

// Cria o contexto com um valor padrão inicial
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Hook customizado para usar o contexto de autenticação
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Componente provedor do contexto
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true); // Inicia como true para verificar o estado inicial

  // Efeito para verificar se há um usuário logado (ex: token no localStorage) ao iniciar
  useEffect(() => {
    const checkAuthState = async () => {
      try {
        // TODO: Implementar lógica para verificar token/sessão
        // Exemplo: Ler token do localStorage, validar no backend
        // const token = localStorage.getItem('authToken');
        // if (token) {
        //   // Validar token no backend e obter dados do usuário
        //   const response = await api.get('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } });
        //   setUser(response.data.user);
        // } else {
        //   setUser(null);
        // }
        // Simulação por enquanto:
        setUser(null); // Assume não logado inicialmente
      } catch (error) {
        console.error("Erro ao verificar estado de autenticação:", error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    checkAuthState();
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const response = await api.post(`${import.meta.env.VITE_API_URL || ''}/api/auth/login`, { username, password });
      // TODO: Armazenar token/sessão (ex: localStorage.setItem('authToken', response.data.token));
      const userData: User = {
          id: response.data.user_id,
          username: username, // O backend pode retornar o username também
          role: response.data.role
      };
      setUser(userData);
    } catch (error) {
      console.error("Erro no login:", error);
      setUser(null);
      // Re-lançar o erro para que o componente de login possa tratá-lo (ex: mostrar mensagem)
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      // TODO: Chamar API de logout no backend, se houver
      // await api.post('/api/auth/logout');
      // TODO: Remover token/sessão (ex: localStorage.removeItem('authToken'));
      setUser(null);
    } catch (error) {
      console.error("Erro no logout:", error);
      // Mesmo em caso de erro, deslogar no frontend
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    loading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const login = async (username: string, password: string) => {
    const { data } = await api.post('/api/auth/login', { username, password });
    return data;
  };
  return { login };
}