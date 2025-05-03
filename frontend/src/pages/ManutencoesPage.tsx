import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, PlusCircle, Edit, FileDown } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom'; // Para filtros via URL e navegação
import ManutencaoFormModal from '@/components/ManutencaoFormModal'; // Importar o modal

// Interface para os dados da manutenção (espelhando o backend)
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

// Função para deletar manutenção
const handleDeleteManutencao = async (id: number) => {
  const confirmacao = window.confirm("Tem certeza que deseja excluir esta manutenção?");
  if (!confirmacao) return;

  try {
    await axios.delete(`/api/manutencoes/${id}`);
    alert("Manutenção excluída com sucesso.");
    setManutencoes((prev) => prev.filter((m) => m.id !== id));
  } catch (err: any) {
    console.error("Erro ao excluir manutenção:", err);
    alert("Erro ao excluir manutenção. Tente novamente.");
  }
};

// Interface para os dados da máquina (para o filtro)
interface MaquinaFiltro {
  id: number;
  nome: string;
  numero_frota: string;
}

const ManutencoesPage = () => {
  const [manutencoes, setManutencoes] = useState<Manutencao[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [maquinasFiltro, setMaquinasFiltro] = useState<MaquinaFiltro[]>([]); // Para popular o select de máquinas
  const [manutencaoToEdit, setManutencaoToEdit] = useState<Manutencao | null>(null); // State for editing

  // Estados dos filtros
  const [filterMaquinaId, setFilterMaquinaId] = useState<string>("todas");
  const [filterTipo, setFilterTipo] = useState<string>("todos"); // "todos", "preventiva", "corretiva"
  const [filterStartDate, setFilterStartDate] = useState<string>("");
  const [filterEndDate, setFilterEndDate] = useState<string>("");

  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation(); // Para ler query params

  // Função para buscar manutenções
  const fetchManutencoes = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filterMaquinaId !== "todas") params.append("maquina_id", filterMaquinaId);
      if (filterTipo !== "todos") params.append("tipo_manutencao", filterTipo);
      if (filterStartDate) params.append("start_date", filterStartDate);
      if (filterEndDate) params.append("end_date", filterEndDate);

      // TODO: Adicionar headers de autenticação se necessário
      const response = await axios.get("/api/manutencoes", { params });
      const data = response.data;
      if (Array.isArray(data)) {
        setManutencoes(data);
      } else if (Array.isArray(data.manutencoes)) {
        setManutencoes(data.manutencoes);
      } else {
        console.warn("Formato de resposta inesperado:", data);
        setError("Erro ao carregar máquinas: resposta inesperada");
        setManutencoes([]);
      }
    } catch (err: any) {
      console.error("Erro ao buscar manutenções:", err);
      setError(err.response?.data?.message || "Não foi possível carregar as manutenções.");
    } finally {
      setLoading(false);
    }
  };

  // Função para buscar máquinas para o filtro
  useEffect(() => {
    const fetchMaquinasParaFiltro = async () => {
      try {
        const response = await axios.get("/api/maquinas");
        const data = response.data;
          if (Array.isArray(data)) {
            setMaquinasFiltro(data);
          } else if (Array.isArray(data.maquinas)) {
            setMaquinasFiltro(data.maquinas);
          } else {
            console.warn("Formato de resposta inesperado em /api/maquinas:", data);
            setMaquinasFiltro([]); // evita o erro no map
          }
        } catch (err) {
          console.error("Erro ao buscar máquinas para filtro:", err);
        // Não define erro principal, pois a lista de manutenções é mais crítica
        }
      };
      fetchMaquinasParaFiltro();
  }, []);

  // Efeito para ler filtro inicial da URL
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const maquinaIdFromUrl = params.get("maquina_id");
    if (maquinaIdFromUrl) {
      setFilterMaquinaId(maquinaIdFromUrl);
    }
  }, [location.search]);

  // Busca as manutenções da API com base nos filtros
  useEffect(() => {
    fetchManutencoes();
  }, [filterMaquinaId, filterTipo, filterStartDate, filterEndDate]);

  // Open modal for adding
  const handleAddManutencao = () => {
    setManutencaoToEdit(null); // Ensure no data is pre-filled
    // Modal opens via trigger
  };

  // Open modal for editing
  const handleEditManutencao = (manutencao: Manutencao) => {
    setManutencaoToEdit(manutencao);
    // Modal opens via trigger
  };

  // Callback for successful modal operation
  const handleModalSuccess = () => {
    fetchManutencoes(); // Refetch the list
  };

  const canAdd = user?.role === "gestor" || user?.role === "mecanico";
  const canEdit = user?.role === "gestor";
  const canExport = user?.role === "gestor" || user?.role === "administrador";

  // Função para exportar dados
  const handleExport = async (format: 'excel' | 'pdf') => {
    const params = new URLSearchParams();
    if (filterMaquinaId !== 'todas') params.append('maquina_id', filterMaquinaId);
    if (filterTipo !== 'todos') params.append('tipo_manutencao', filterTipo);
    if (filterStartDate) params.append('start_date', filterStartDate);
    if (filterEndDate) params.append('end_date', filterEndDate);

    const url = `/api/export/manutencoes/${format}?${params.toString()}`;

    try {
      // TODO: Adicionar headers de autenticação se necessário
      const response = await axios.get(url, {
        responseType: 'blob', // Importante para lidar com arquivos
      });

      // Cria um link temporário para iniciar o download
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;

      // Extrai o nome do arquivo do header Content-Disposition
      const contentDisposition = response.headers['content-disposition'];
      let filename = `export_manutencoes.${format === 'excel' ? 'xlsx' : 'pdf'}`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
        if (filenameMatch && filenameMatch.length > 1) {
          filename = filenameMatch[1];
        }
      }

      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);

    } catch (err: any) {
      console.error(`Erro ao exportar para ${format}:`, err);
      setError(err.response?.data?.message || `Não foi possível exportar os dados para ${format}.`);
      // Se o erro for 404 (sem dados), pode mostrar uma mensagem mais amigável
      if (err.response?.status === 404) {
          setError('Nenhuma manutenção encontrada para os filtros selecionados para exportação.');
      }
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
            <SelectTrigger>
              <SelectValue placeholder="Filtrar por Máquina" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="todas">Todas as Máquinas</SelectItem>
              {maquinasFiltro.map(m => (
                <SelectItem key={m.id} value={String(m.id)}>{m.nome} ({m.numero_frota})</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={filterTipo} onValueChange={setFilterTipo}>
            <SelectTrigger>
              <SelectValue placeholder="Filtrar por Tipo" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="todos">Todos os Tipos</SelectItem>
              <SelectItem value="preventiva">Preventiva</SelectItem>
              <SelectItem value="corretiva">Corretiva</SelectItem>
            </SelectContent>
          </Select>

          <Input
            type="date"
            placeholder="Data Início"
            value={filterStartDate}
            onChange={(e) => setFilterStartDate(e.target.value)}
            className="!text-black" // Garante texto visível
          />
          <Input
            type="date"
            placeholder="Data Fim"
            value={filterEndDate}
            onChange={(e) => setFilterEndDate(e.target.value)}
            className="!text-black" // Garante texto visível
          />
      </div>

       <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
         {/* Botão de adicionar fica à esquerda ou topo em mobile */}
         {canAdd && (
            <ManutencaoFormModal
              manutencaoToEdit={null} // Add mode
              onSuccess={handleModalSuccess}
              triggerButton={
                <Button onClick={handleAddManutencao} className="flex items-center gap-1 w-full md:w-auto">
                  <PlusCircle size={16} />
                  Registrar Manutenção
                </Button>
              }
            />
          )}
         {/* Botões de exportação ficam à direita ou abaixo em mobile */}
         {canExport && (
            <div className="flex gap-2 w-full md:w-auto justify-end">
              <Button variant="outline" onClick={() => handleExport("excel")} className="flex items-center gap-1">
                <FileDown size={16} />
                Exportar Excel
              </Button>
              <Button variant="outline" onClick={() => handleExport("pdf")} className="flex items-center gap-1">
                <FileDown size={16} />
                Exportar PDF
              </Button>
            </div>
          )}
       </div>

      {/* Tabela de Manutenções */}
      {loading ? (
        <p>Carregando manutenções...</p>
      ) : (
        <Table>
          <TableCaption>Lista de manutenções registradas.</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>Máquina</TableHead>
              <TableHead>Data Entrada</TableHead>
              <TableHead>Horím./Hodôm.</TableHead>
              <TableHead>Tipo</TableHead>
              <TableHead>Categoria</TableHead>
              <TableHead>Responsável</TableHead>
              <TableHead>Data Saída</TableHead>
              <TableHead>Custo</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {Array.isArray(manutencoes) && manutencoes.length > 0 ? (
              manutencoes.map((man) => (
                <TableRow key={man.id}>
                  <TableCell className="font-medium">{man.maquina_nome}</TableCell>
                  {/* Format dates for better readability */}
                  <TableCell>{man.data_entrada ? new Date(man.data_entrada).toLocaleString("pt-BR") : "-"}</TableCell>
                  <TableCell>{man.horimetro_hodometro}</TableCell>
                  <TableCell>{man.tipo_manutencao}</TableCell>
                  <TableCell>
                    {man.categoria_servico}
                    {man.categoria_servico === "Outros" && man.categoria_outros_especificacao && ` (${man.categoria_outros_especificacao})`}
                  </TableCell>
                  <TableCell>{man.responsavel_servico}</TableCell>
                  <TableCell>{man.data_saida ? new Date(man.data_saida).toLocaleString("pt-BR") : "-"}</TableCell>
                  <TableCell>{man.custo !== null ? `R$ ${man.custo.toFixed(2).replace(".", ",")}` : "-"}</TableCell>
                  <TableCell className="text-right space-x-1">
                    {canEdit && (
                      <>
                      <ManutencaoFormModal
                        manutencaoToEdit={man}
                        onSuccess={handleModalSuccess}
                        triggerButton={
                          <Button variant="outline" size="sm" title="Editar Manutenção">
                            <Edit size={14} />
                          </Button>
                        }
                      />
                      <Button
                        variant="destructive"
                        size="sm"
                        title="Excluir Manutenção"
                        onClick={() => handleDeleteManutencao(man.id)}
                      >
                        Excluir
                      </Button>
                    </>
                  )}
                  </TableCell>
                  </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={9} className="text-center">Nenhuma manutenção encontrada para os filtros selecionados.</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      )}
    </div>
  );
};

export default ManutencoesPage;

