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
import { AlertCircle, PlusCircle, Edit, FileDown, Trash } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import ManutencaoFormModal from '@/components/ManutencaoFormModal';

interface Manutencao {
  id: number;
  maquina_id: number;
  maquina_nome: string;
  horimetro_hodometro: number;
  data_entrada: string;
  data_saida: string | null;
  tipo_manutencao: string;
  categoria_servico: string;
  categoria_outros_especificacao: string | null;
  comentario: string | null;
  responsavel_servico: string;
  custo: number | null;
}

interface MaquinaFiltro {
  id: number;
  nome: string;
  numero_frota: string;
}

const ManutencoesPage: React.FC = () => {
  const [manutencoes, setManutencoes] = useState<Manutencao[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [maquinasFiltro, setMaquinasFiltro] = useState<MaquinaFiltro[]>([]);
  const [manutencaoToEdit, setManutencaoToEdit] = useState<Manutencao | null>(null);
  const [filterMaquinaId, setFilterMaquinaId] = useState('todas');
  const [filterTipo, setFilterTipo] = useState('todos');
  const [filterStartDate, setFilterStartDate] = useState('');
  const [filterEndDate, setFilterEndDate] = useState('');

  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Fetch machines for filter dropdown
  useEffect(() => {
    async function loadMaquinas() {
      try {
        const resp = await api.get('/api/maquinas');
        const data = resp.data;
        setMaquinasFiltro(Array.isArray(data) ? data : (data.maquinas || []));
      } catch (err) {
        console.error('Erro ao buscar máquinas para filtro:', err);
      }
    }
    loadMaquinas();
  }, []);

  // Read initial filter from URL
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const mid = params.get('maquina_id');
    if (mid) setFilterMaquinaId(mid);
  }, [location.search]);

  // Fetch maintenances when filters change
  useEffect(() => {
    async function loadManutencoes() {
      setLoading(true);
      setError(null);
      try {
        const params: Record<string, string> = {};
        if (filterMaquinaId !== 'todas') params.maquina_id = filterMaquinaId;
        if (filterTipo !== 'todos') params.tipo_manutencao = filterTipo;
        if (filterStartDate) params.start_date = filterStartDate;
        if (filterEndDate) params.end_date = filterEndDate;
        const resp = await api.get('/api/manutencoes', { params });
        const data = resp.data;
        setManutencoes(Array.isArray(data) ? data : (data.manutencoes || []));
      } catch (err: any) {
        console.error('Erro ao buscar manutenções:', err);
        setError(err.response?.data?.message || 'Não foi possível carregar as manutenções.');
      } finally {
        setLoading(false);
      }
    }
    loadManutencoes();
  }, [filterMaquinaId, filterTipo, filterStartDate, filterEndDate]);

  const handleDelete = async (id: number) => {
    if (!window.confirm('Deseja realmente excluir esta manutenção?')) return;
    try {
      await api.delete(`/api/manutencoes/${id}`);
      setManutencoes(prev => prev.filter(m => m.id !== id));
    } catch (err) {
      console.error('Erro ao excluir manutenção:', err);
      alert('Erro ao excluir.');
    }
  };

  const canAdd = ['gestor', 'mecanico'].includes(user?.role || '');
  const canEdit = user?.role === 'gestor';
  const canExport = ['gestor', 'administrador'].includes(user?.role || '');

  const handleExport = async (format: 'excel' | 'pdf') => {
    const params = new URLSearchParams();
    if (filterMaquinaId !== 'todas') params.append('maquina_id', filterMaquinaId);
    if (filterTipo !== 'todos') params.append('tipo_manutencao', filterTipo);
    if (filterStartDate) params.append('start_date', filterStartDate);
    if (filterEndDate) params.append('end_date', filterEndDate);
    
    try {
      const resp = await api.get(`/api/export/manutencoes/${format}`, { params, responseType: 'blob' });
      const blob = new Blob([resp.data], { type: resp.headers['content-type'] });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      const cd = resp.headers['content-disposition'] || '';
      const match = cd.match(/filename="?(.+?)"?$/i);
      link.download = match ? match[1] : `export.${format === 'excel' ? 'xlsx' : 'pdf'}`;
      link.href = url;
      link.setAttribute('download', 'manutencoes.xlsx');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error(`Erro ao exportar ${format}:`, err);
      setError(err.response?.data?.message || `Erro ao exportar ${format}.`);
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Registro de Manutenções</h1>
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Erro</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      {/* Filtros */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4 border rounded-md bg-gray-50">
        <Select value={filterMaquinaId} onValueChange={setFilterMaquinaId}>
          <SelectTrigger><SelectValue placeholder="Máquina" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="todas">Todas</SelectItem>
            {maquinasFiltro.map(m => (
              <SelectItem key={m.id} value={String(m.id)}>{m.nome} ({m.numero_frota})</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={filterTipo} onValueChange={setFilterTipo}>
          <SelectTrigger><SelectValue placeholder="Tipo" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="todos">Todos</SelectItem>
            <SelectItem value="preventiva">Preventiva</SelectItem>
            <SelectItem value="corretiva">Corretiva</SelectItem>
          </SelectContent>
        </Select>
        <Input
          type="date"
          value={filterStartDate}
          onChange={e => setFilterStartDate(e.target.value)}
          className="!text-black"
        />
        <Input
          type="date"
          value={filterEndDate}
          onChange={e => setFilterEndDate(e.target.value)}
          className="!text-black"
        />
      </div>
      {/* Ações */}
      <div className="flex justify-between items-center">
        {canAdd && (
          <ManutencaoFormModal
            manutencaoToEdit={null}
            onSuccess={() => {/* refetch dentro do modal */}}
            triggerButton={
              <Button className="flex items-center gap-1">
                <PlusCircle size={16} /> Registrar
              </Button>
            }
          />
        )}
        {canExport && (
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => handleExport('excel')} className="flex items-center gap-1">
              <FileDown size={16} /> Excel
            </Button>
            <Button variant="outline" onClick={() => handleExport('pdf')} className="flex items-center gap-1">
              <FileDown size={16} /> PDF
            </Button>
          </div>
        )}
      </div>
      {/* Tabela */}
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <Table>
          <TableCaption>Lista de manutenções.</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>Máquina</TableHead>
              <TableHead>Entrada</TableHead>
              <TableHead>Horímetro</TableHead>
              <TableHead>Tipo</TableHead>
              <TableHead>Categoria</TableHead>
              <TableHead>Responsável</TableHead>
              <TableHead>Saída</TableHead>
              <TableHead>Custo</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {manutencoes.length > 0 ? (
              manutencoes.map(m => (
                <TableRow key={m.id}>
                  <TableCell>{m.maquina_nome}</TableCell>
                  <TableCell>{new Date(m.data_entrada).toLocaleString('pt-BR')}</TableCell>
                  <TableCell>{m.horimetro_hodometro}</TableCell>
                  <TableCell>{m.tipo_manutencao}</TableCell>
                  <TableCell>
                    {m.categoria_servico}
                    {m.categoria_servico === 'Outros' && m.categoria_outros_especificacao ? ` (${m.categoria_outros_especificacao})` : ''}
                  </TableCell>
                  <TableCell>{m.responsavel_servico}</TableCell>
                  <TableCell>{m.data_saida ? new Date(m.data_saida).toLocaleString('pt-BR') : '-'}</TableCell>
                  <TableCell>{m.custo !== null ? `R$ ${m.custo.toFixed(2).replace('.', ',')}` : '-'}</TableCell>
                  <TableCell className="text-right space-x-1">
                    {canEdit && (
                      <>
                        <ManutencaoFormModal
                          manutencaoToEdit={m}
                          onSuccess={() => {/* refetch modal */}}
                          triggerButton={<Button variant="outline" size="sm"><Edit size={14} /></Button>}
                        />
                        <Button variant="destructive" size="sm" onClick={() => handleDelete(m.id)}><Trash size={14} /></Button>
                      </>
                    )}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={9} className="text-center">Nenhuma manutenção encontrada.</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      )}
    </div>
  );
};

export default ManutencoesPage;
