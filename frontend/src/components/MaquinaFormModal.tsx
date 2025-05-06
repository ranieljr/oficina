import React, { useState, useEffect } from 'react';
import { api } from '@/services/api';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger, DialogClose } from "@/components/ui/dialog";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext'; // Assuming authentication context is needed for API calls

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
      setDataAquisicao(maquinaToEdit.data_aquisicao.split('T')[0]);
      setTipoControle(maquinaToEdit.tipo_controle as any);
      setNome(maquinaToEdit.nome);
      setMarca(maquinaToEdit.marca || '');
      setStatus(maquinaToEdit.status as any);
    } else {
      resetForm();
    }
  }, [maquinaToEdit, isEditing, isOpen]);

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
      marca: marca || null,
      status,
    };

    try {
      // Ajuste nos endpoints para combinar com o backend:
      if (isEditing && maquinaToEdit) {
        await api.put(`/maquinas/${maquinaToEdit.id}`, maquinaData);
      } else {
        await api.post('/maquinas', maquinaData);
      }
      onSuccess();
      setIsOpen(false);
      resetForm();
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
          {/* ... restante do formulário permanece igual ... */}
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
