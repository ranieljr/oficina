import React, { useState, useEffect } from 'react';
import { api } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import {
  Alert,
  AlertDescription,
  AlertTitle
} from '@/components/ui/alert';
import { AlertCircle, PlusCircle, Edit, Wrench } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import MaquinaFormModal from '@/components/MaquinaFormModal';

interface Maquina {
  id: number;
  tipo: string;
  numero_frota: string;
  data_aquisicao: string;
  tipo_controle: string;
  nome: string;
  marca: string | null;
  status: string;
}

const MaquinasPage: React.FC = () => {
  const [maquinas, setMaquinas] = useState<Maquina[]>([]);
  const [filteredMaquinas, setFilteredMaquinas] = useState<Maquina[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('todos');
  const [maquinaToEdit, setMaquinaToEdit] = useState<Maquina | null>(null);
  const { user } = useAuth();
  const navigate = useNavigate();

  // Busca máquinas do backend
  useEffect(() => {
    async function fetchMaquinas() {
      setLoading(true);
      setError(null);
      try {
        const resp = await api.get('/api/maquinas');
        setMaquinas(resp.data);
        applyFilters(resp.data, searchTerm, filterStatus);
      } catch (err: any) {
        console.error('Erro ao buscar máquinas:', err);
        setError(err.response?.data?.message || 'Não foi possível carregar as máquinas.');
      } finally {
        setLoading(false);
      }
    }
    fetchMaquinas();
  }, []);

  // Aplica busca e filtro de status
  const applyFilters = (
    all: Maquina[],
    term: string,
    status: string
  ) => {
    let result = all;
    if (term) {
      result = result.filter(m =>
        m.nome.toLowerCase().includes(term.toLowerCase()) ||
        m.numero_frota.toLowerCase().includes(term.toLowerCase()) ||
        (m.marca || '').toLowerCase().includes(term.toLowerCase())
      );
    }
    if (status !== 'todos') {
      result = result.filter(m => m.status === status);
    }
    setFilteredMaquinas(result);
  };

  // Atualiza filtros ao mudar termos
  useEffect(() => {
    applyFilters(maquinas, searchTerm, filterStatus);
  }, [searchTerm, filterStatus, maquinas]);

  const handleViewManutencoes = (id: number) => {
    navigate(`/manutencoes?maquina_id=${id}`);
  };

  const canManage = user?.role === 'gestor';

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Gerenciamento de Máquinas</h1>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Erro</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex flex-col md:flex-row gap-2 justify-between">
        <div className="flex gap-2">
          <Input
            placeholder="Buscar por nome, frota ou marca..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="max-w-sm !text-black"
          />
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filtrar por status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="todos">Todos Status</SelectItem>
              <SelectItem value="ativo">Ativo</SelectItem>
              <SelectItem value="inativo">Inativo</SelectItem>
            </SelectContent>
          </Select>
        </div>
        {canManage && (
          <MaquinaFormModal
            maquinaToEdit={null}
            onSuccess={() => {/* refetch handled inside modal */}}
            triggerButton={
              <Button className="flex items-center gap-1">
                <PlusCircle size={16} />
                Adicionar Máquina
              </Button>
            }
          />
        )}
      </div>

      {loading ? (
        <p>Carregando máquinas...</p>
      ) : (
        <Table>
          <TableCaption>Lista de máquinas, implementos e veículos cadastrados.</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>Nº Frota</TableHead>
              <TableHead>Tipo</TableHead>
              <TableHead>Marca</TableHead>
              <TableHead>Aquisição</TableHead>
              <TableHead>Controle</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredMaquinas.length > 0 ? (
              filteredMaquinas.map(m => (
                <TableRow key={m.id}>
                  <TableCell className="font-medium">{m.nome}</TableCell>
                  <TableCell>{m.numero_frota}</TableCell>
                  <TableCell>{m.tipo}</TableCell>
                  <TableCell>{m.marca || '-'}</TableCell>
                  <TableCell>{new Date(m.data_aquisicao + 'T00:00:00').toLocaleDateString()}</TableCell>
                  <TableCell>{m.tipo_controle}</TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${m.status === 'ativo' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {m.status}
                    </span>
                  </TableCell>
                  <TableCell className="text-right space-x-1">
                    <Button variant="outline" size="sm" onClick={() => handleViewManutencoes(m.id)} title="Ver Manutenções">
                      <Wrench size={14} />
                    </Button>
                    {canManage && (
                      <MaquinaFormModal
                        maquinaToEdit={m}
                        onSuccess={() => {/* refetch inside modal */}}
                        triggerButton={<Button variant="outline" size="sm" title="Editar Máquina"><Edit size={14} /></Button>}
                      />
                    )}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={8} className="text-center">Nenhuma máquina encontrada.</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      )}
    </div>
  );
};

export default MaquinasPage;