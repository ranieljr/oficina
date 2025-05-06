import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger, DialogClose } from "@/components/ui/dialog";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext'; // Assuming authentication context is needed for API calls
import { api } from '@/api';

// Interface for Maquina data (matching backend)
interface Maquina {
  id: number;
  tipo: string;
  numero_frota: string;
  data_aquisicao: string; // Format YYYY-MM-DD
  tipo_controle: string;
  nome: string;
  marca: string | null;
  status: string;
}

interface MaquinaFormModalProps {
  maquinaToEdit?: Maquina | null; // Pass machine data for editing, null/undefined for adding
  onSuccess: () => void; // Callback function after successful save/update
  triggerButton: React.ReactNode; // The button that opens the modal
}

const MaquinaFormModal: React.FC<MaquinaFormModalProps> = ({ maquinaToEdit, onSuccess, triggerButton }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [tipo, setTipo] = useState<'máquina' | 'implemento' | 'veículo' | ''>('');
  const [numeroFrota, setNumeroFrota] = useState('');
  const [dataAquisicao, setDataAquisicao] = useState('');
  const [tipoControle, setTipoControle] = useState<'hodômetro' | 'horímetro' | ''>('');
  const [nome, setNome] = useState('');
  const [marca, setMarca] = useState('');
  const [status, setStatus] = useState<'ativo' | 'inativo' | ''>('ativo'); // Default to 'ativo'
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { user } = useAuth(); // Get user for authorization if needed

  const isEditing = Boolean(maquinaToEdit);

  // Populate form when editing
  useEffect(() => {
    if (isEditing && maquinaToEdit) {
      setTipo(maquinaToEdit.tipo as any);
      setNumeroFrota(maquinaToEdit.numero_frota);
      // Ensure date is in YYYY-MM-DD format for the input type="date"
      setDataAquisicao(maquinaToEdit.data_aquisicao.split('T')[0]);
      setTipoControle(maquinaToEdit.tipo_controle as any);
      setNome(maquinaToEdit.nome);
      setMarca(maquinaToEdit.marca || '');
      setStatus(maquinaToEdit.status as any);
    } else {
      // Reset form for adding
      resetForm();
    }
  }, [maquinaToEdit, isEditing, isOpen]); // Re-run when modal opens or maquinaToEdit changes

  const resetForm = () => {
    setTipo('');
    setNumeroFrota('');
    setDataAquisicao('');
    setTipoControle('');
    setNome('');
    setMarca('');
    setStatus('ativo');
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    if (!tipo || !numeroFrota || !dataAquisicao || !tipoControle || !nome || !status) {
        setError("Todos os campos obrigatórios devem ser preenchidos.");
        setLoading(false);
        return;
    }


    const maquinaData = {
      tipo,
      numero_frota: numeroFrota,
      data_aquisicao: dataAquisicao,
      tipo_controle: tipoControle,
      nome,
      marca: marca || null, // Send null if empty
      status,
    };

    try {
      // TODO: Add authentication headers if required by the API
      // const config = { headers: { Authorization: `Bearer ${token}` } };
      if (isEditing && maquinaToEdit) {
        console.log("API:", api.defaults.baseURL);
        console.log("Env:", import.meta.env.VITE_API_URL);
        await axios.put(`/api/maquinas/${maquinaToEdit.id}`, maquinaData);
      } else {
        await axios.post('/api/maquinas', maquinaData);
      }
      onSuccess(); // Call the success callback (e.g., refetch machine list)
      setIsOpen(false); // Close modal on success
      resetForm(); // Reset form fields
    } catch (err: any) {
      console.error("Erro ao salvar máquina:", err);
      setError(err.response?.data?.message || `Não foi possível ${isEditing ? 'atualizar' : 'adicionar'} a máquina.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {triggerButton}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Editar Máquina' : 'Adicionar Nova Máquina'}</DialogTitle>
          <DialogDescription>
            Preencha os detalhes da máquina abaixo.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="grid gap-4 py-4">
          {error && (
            <Alert variant="destructive" className="col-span-2">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Erro</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="tipo">Tipo *</Label>
              <Select value={tipo} onValueChange={(value) => setTipo(value as any)} required>
                <SelectTrigger id="tipo">
                  <SelectValue placeholder="Selecione o tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="máquina">Máquina</SelectItem>
                  <SelectItem value="implemento">Implemento</SelectItem>
                  <SelectItem value="veículo">Veículo</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="numeroFrota">Número da Frota *</Label>
              <Input
                id="numeroFrota"
                value={numeroFrota}
                onChange={(e) => setNumeroFrota(e.target.value)}
                required
                className="!text-black"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="dataAquisicao">Data de Aquisição *</Label>
              <Input
                id="dataAquisicao"
                type="date"
                value={dataAquisicao}
                onChange={(e) => setDataAquisicao(e.target.value)}
                required
                className="!text-black"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="tipoControle">Tipo de Controle *</Label>
              <Select value={tipoControle} onValueChange={(value) => setTipoControle(value as any)} required>
                <SelectTrigger id="tipoControle">
                  <SelectValue placeholder="Selecione o controle" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hodômetro">Hodômetro</SelectItem>
                  <SelectItem value="horímetro">Horímetro</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="nome">Nome *</Label>
              <Input
                id="nome"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                required
                className="!text-black"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="marca">Marca</Label>
              <Input
                id="marca"
                value={marca}
                onChange={(e) => setMarca(e.target.value)}
                className="!text-black"
              />
            </div>
             <div className="space-y-2 col-span-2"> {/* Status ocupa a linha inteira */}
              <Label htmlFor="status">Status *</Label>
              <Select value={status} onValueChange={(value) => setStatus(value as any)} required>
                <SelectTrigger id="status">
                  <SelectValue placeholder="Selecione o status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ativo">Ativo</SelectItem>
                  <SelectItem value="inativo">Inativo</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline">Cancelar</Button>
            </DialogClose>
            <Button type="submit" disabled={loading}>
              {loading ? (isEditing ? 'Salvando...' : 'Adicionando...') : (isEditing ? 'Salvar Alterações' : 'Adicionar Máquina')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default MaquinaFormModal;

