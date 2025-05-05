import React, { useState, useEffect } from 'react';
import { api } from '@/src/api';
import { useAuth } from '../contexts/AuthContext';
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, PlusCircle, Edit, Trash2, Wrench } from 'lucide-react';
import { useNavigate } from 'react-router-dom'; // Para navegação
import MaquinaFormModal from '@/components/MaquinaFormModal'; // Importar o modal
import api from '@/services/api';

// Interface para os dados da máquina (espelhando o backend)
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
const response = await api.get('/api/maquinas');
const result   = await api.post('/api/maquinas', payload);

const MaquinasPage = () => {
  const [maquinas, setMaquinas] = useState<Maquina[]>([]);
  const [filteredMaquinas, setFilteredMaquinas] = useState<Maquina[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("todos"); // "todos", "ativo", "inativo"
  const [maquinaToEdit, setMaquinaToEdit] = useState<Maquina | null>(null); // State for editing
  const [isModalOpen, setIsModalOpen] = useState(false); // Control modal visibility if needed externally
  const { user } = useAuth();
  const navigate = useNavigate();

  // Function to fetch machines
  const fetchMaquinas = async () => {
    setLoading(true);
    setError(null);
    try {
      // TODO: Adicionar headers de autenticação se necessário
      const response = await api.get("/api/maquinas");
      setMaquinas(response.data);
      // Apply filters immediately after fetching
      filterAndSetMaquinas(response.data, searchTerm, filterStatus);
    } catch (err: any) {
      console.error("Erro ao buscar máquinas:", err);
      setError(err.response?.data?.message || "Não foi possível carregar as máquinas.");
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchMaquinas();
  }, []);

  // Function to filter and update displayed machines
  const filterAndSetMaquinas = (
    allMaquinas: Maquina[],
    currentSearchTerm: string,
    currentFilterStatus: string
  ) => {
    if (!Array.isArray(allMaquinas)) {
      console.warn("Dados inválidos em filterAndSetMaquinas:", allMaquinas);
      setFilteredMaquinas([]);
      return;
    }
  
    let result = allMaquinas;
  
    if (currentSearchTerm) {
      result = result.filter((m) =>
        m.nome?.toLowerCase().includes(currentSearchTerm.toLowerCase()) ||
        m.numero_frota?.toLowerCase().includes(currentSearchTerm.toLowerCase()) ||
        m.marca?.toLowerCase().includes(currentSearchTerm.toLowerCase())
      );
    }
  
    if (currentFilterStatus !== "todos") {
      result = result.filter((m) => m.status === currentFilterStatus);
    }
  
    setFilteredMaquinas(result);
  };

  // Apply filters when search term or status changes
  useEffect(() => {
    filterAndSetMaquinas(maquinas, searchTerm, filterStatus);
  }, [searchTerm, filterStatus, maquinas]);


  // Open modal for adding
  const handleAddMaquina = () => {
    setMaquinaToEdit(null); // Ensure no machine data is pre-filled
    // The modal will open via its DialogTrigger
  };

  // Open modal for editing
  const handleEditMaquina = (maquina: Maquina) => {
    setMaquinaToEdit(maquina);
    // The modal will open via its DialogTrigger, but we need to trigger it programmatically or pass state
    // For simplicity, we'll use separate triggers for add/edit
  };

  const handleViewManutencoes = (id: number) => {
    navigate(`/manutencoes?maquina_id=${id}`);
  };

  // Callback for successful modal operation
  const handleModalSuccess = () => {
    fetchMaquinas(); // Refetch the list after adding/editing
  };

  // Permissões
  const canManage = user?.role === "gestor";

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
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-sm !text-black" // Garante texto visível
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
            maquinaToEdit={null} // Pass null for adding
            onSuccess={handleModalSuccess}
            triggerButton={
              <Button onClick={handleAddMaquina} className="flex items-center gap-1">
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
            {Array.isArray(filteredMaquinas) && filteredMaquinas.length > 0 ? (
               filteredMaquinas.map((maquina) => (
                <TableRow key={maquina.id}>
                  <TableCell className="font-medium">{maquina.nome}</TableCell>
                  <TableCell>{maquina.numero_frota}</TableCell>
                  <TableCell>{maquina.tipo}</TableCell>
                  <TableCell>{maquina.marca || "-"}</TableCell>
                  <TableCell>{new Date(maquina.data_aquisicao + "T00:00:00").toLocaleDateString()}</TableCell> {/* Ajuste para evitar problemas de fuso horário */}
                  <TableCell>{maquina.tipo_controle}</TableCell>
                  <TableCell>
                     <span className={`px-2 py-1 rounded-full text-xs font-medium ${maquina.status === "ativo" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                       {maquina.status}
                     </span>
                  </TableCell>
                  <TableCell className="text-right space-x-1">
                    <Button variant="outline" size="sm" onClick={() => handleViewManutencoes(maquina.id)} title="Ver Manutenções">
                      <Wrench size={14} />
                    </Button>
                    {canManage && (
                       <MaquinaFormModal
                         maquinaToEdit={maquina} // Pass current machine data for editing
                         onSuccess={handleModalSuccess}
                         triggerButton={
                           <Button variant="outline" size="sm" title="Editar Máquina">
                             <Edit size={14} />
                           </Button>
                         }
                       />
                    )}
                    {/* Botão de inativar/deletar pode ser adicionado aqui se necessário */}
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

