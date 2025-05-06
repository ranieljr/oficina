import React, { useState, useEffect } from 'react';
import { api } from '@/services/api';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea"; // Para comentários
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger, DialogClose } from "@/components/ui/dialog";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from 'lucide-react';

// Interface para Manutencao (matching backend)
interface Manutencao {
  id: number;
  maquina_id: number;
  maquina_nome?: string; // Opcional, pode não vir do form
  horimetro_hodometro: number;
  data_entrada: string; // Format YYYY-MM-DDTHH:mm
  data_saida: string | null; // Format YYYY-MM-DDTHH:mm
  tipo_manutencao: string;
  categoria_servico: string;
  categoria_outros_especificacao: string | null;
  comentario: string | null;
  responsavel_servico: string;
  custo: number | null;
}

// Interface para Máquina (para o select)
interface MaquinaSelect {
  id: number;
  nome: string;
  numero_frota: string;
  tipo_controle: string; // Para saber se pede horímetro ou hodômetro
}

interface ManutencaoFormModalProps {
  manutencaoToEdit?: Manutencao | null;
  onSuccess: () => void;
  triggerButton: React.ReactNode;
}

const categoriasServico = [
  "Auto elétrica",
  "Filtros e lubrificantes",
  "Pneus e borrachas",
  "Reforma",
  "Retífica de motores",
  "Ar-condicionado",
  "Material rodante",
  "Outros"
];

const ManutencaoFormModal: React.FC<ManutencaoFormModalProps> = ({ manutencaoToEdit, onSuccess, triggerButton }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [maquinas, setMaquinas] = useState<MaquinaSelect[]>([]);
  const [selectedMaquina, setSelectedMaquina] = useState<MaquinaSelect | null>(null);

  // Form fields
  const [maquinaId, setMaquinaId] = useState<string>('');
  const [horimetroHodometro, setHorimetroHodometro] = useState<string>('');
  const [dataEntrada, setDataEntrada] = useState<string>('');
  const [dataSaida, setDataSaida] = useState<string>('');
  const [tipoManutencao, setTipoManutencao] = useState<'preventiva' | 'corretiva' | ''>('');
  const [categoriaServico, setCategoriaServico] = useState<string>('');
  const [categoriaOutros, setCategoriaOutros] = useState<string>('');
  const [comentario, setComentario] = useState<string>('');
  const [responsavel, setResponsavel] = useState<string>('');
  const [custo, setCusto] = useState<string>('');

  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({}); // State for field-specific errors
  const [loading, setLoading] = useState(false);

  const isEditing = Boolean(manutencaoToEdit);

  // Fetch máquinas for the select dropdown
  useEffect(() => {
    const fetchMaquinas = async () => {
      try {
        const response = await api.get('/api/maquinas');
        const data = response.data;
  
        if (Array.isArray(data)) {
          setMaquinas(data);
        } else if (Array.isArray(data.maquinas)) {
          setMaquinas(data.maquinas);
        } else {
          console.warn("Formato de resposta inesperado em /api/maquinas:", data);
          setMaquinas([]);
        }
      } catch (err) {
        console.error("Erro ao buscar máquinas para o formulário:", err);
        setError("Não foi possível carregar a lista de máquinas.");
      }
    };
    if (isOpen) {
      fetchMaquinas();
    }
  }, [isOpen]);
  
  // Helper to format date for datetime-local input
  const formatDateTimeLocal = (isoString: string | null | undefined): string => {
    if (!isoString) return '';
    try {
        // Remove potential timezone info and seconds/milliseconds for compatibility
        const date = new Date(isoString);
        // Check if date is valid
        if (isNaN(date.getTime())) return '';
        // Format to YYYY-MM-DDTHH:mm
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}`;
    } catch (e) {
        console.error("Error formatting date:", e);
        return '';
    }
  };

  // Populate form when editing
  useEffect(() => {
    if (isEditing && manutencaoToEdit && maquinas.length > 0) {
      setMaquinaId(String(manutencaoToEdit.maquina_id));
      const maquina = maquinas.find(m => m.id === manutencaoToEdit.maquina_id);
      setSelectedMaquina(maquina || null);
      setHorimetroHodometro(String(manutencaoToEdit.horimetro_hodometro));
      setDataEntrada(formatDateTimeLocal(manutencaoToEdit.data_entrada));
      setDataSaida(formatDateTimeLocal(manutencaoToEdit.data_saida));
      setTipoManutencao(manutencaoToEdit.tipo_manutencao as any);
      setCategoriaServico(manutencaoToEdit.categoria_servico);
      setCategoriaOutros(manutencaoToEdit.categoria_servico === 'Outros' ? manutencaoToEdit.categoria_outros_especificacao || '' : '');
      setComentario(manutencaoToEdit.comentario || '');
      setResponsavel(manutencaoToEdit.responsavel_servico);
      setCusto(manutencaoToEdit.custo !== null ? String(manutencaoToEdit.custo) : '');
    } else if (!isEditing) {
      resetForm();
    }
  }, [manutencaoToEdit, isEditing, isOpen, maquinas]); // Re-run when modal opens, edit data changes, or machines load

  // Update selectedMaquina when maquinaId changes
   useEffect(() => {
    if (maquinaId) {
      const maquina = maquinas.find(m => m.id === parseInt(maquinaId, 10));
      setSelectedMaquina(maquina || null);
    } else {
      setSelectedMaquina(null);
    }
  }, [maquinaId, maquinas]);

  const resetForm = () => {
    setMaquinaId('');
    setSelectedMaquina(null);
    setHorimetroHodometro("");
    setDataEntrada("");
    setDataSaida("");
    setTipoManutencao("");
    setCategoriaServico("");
    setCategoriaOutros("");
    setComentario("");
    setResponsavel("");
    setCusto("");
    setError(null);
    setFieldErrors({}); // Reset field errors too
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    if (!maquinaId || !horimetroHodometro || !dataEntrada || !tipoManutencao || !categoriaServico || !responsavel) {
        setError("Campos obrigatórios (*) devem ser preenchidos.");
        setLoading(false);
        return;
    }
    if (categoriaServico === 'Outros' && !categoriaOutros) {
        setError("Por favor, especifique a categoria 'Outros'.");
        setLoading(false);
        return;
    }

    const manutencaoData = {
      maquina_id: parseInt(maquinaId, 10),
      horimetro_hodometro: parseFloat(horimetroHodometro), // Use parseFloat for potential decimals
      data_entrada: new Date(dataEntrada).toISOString(), // Convert to ISO string for backend
      data_saida: dataSaida ? new Date(dataSaida).toISOString() : null,
      tipo_manutencao: tipoManutencao,
      categoria_servico: categoriaServico,
      categoria_outros_especificacao: categoriaServico === 'Outros' ? categoriaOutros : null,
      comentario: comentario || null,
      responsavel_servico: responsavel,
      custo: custo ? parseFloat(custo) : null,
    };

    try {
      // TODO: Add authentication headers if required
      if (isEditing && manutencaoToEdit) {
        await api.put(`/api/manutencoes/${manutencaoToEdit.id}`, manutencaoData);
      } else {
        await api.post('/api/manutencoes', manutencaoData);
      }
      onSuccess();
      setIsOpen(false);
      resetForm();
    } catch (err: any) {
      console.error("Erro ao salvar manutenção:", err);
      const apiError = err.response?.data;
      if (apiError?.errors && typeof apiError.errors === 'object') {
        setError(apiError.message || "Erro de validação");
        setFieldErrors(apiError.errors);
      } else {
        setError(apiError?.message || `Não foi possível ${isEditing ? 'atualizar' : 'registrar'} a manutenção.`);
        setFieldErrors({});
      }
    } finally {
      setLoading(false);
    }
  };

  const controleLabel = selectedMaquina ? (selectedMaquina.tipo_controle === 'horímetro' ? 'Horímetro *' : 'Hodômetro *') : 'Horím./Hodôm. *';

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {triggerButton}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[700px]"> {/* Wider modal */}
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Editar Manutenção' : 'Registrar Nova Manutenção'}</DialogTitle>
          <DialogDescription>
            Preencha os detalhes da manutenção abaixo.
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="maquinaId">Máquina *</Label>
              <Select value={maquinaId} onValueChange={setMaquinaId} required disabled={isEditing}> {/* Disable machine change when editing */}
                <SelectTrigger id="maquinaId">
                  <SelectValue placeholder="Selecione a máquina" />
                </SelectTrigger>
                <SelectContent>
                  {maquinas.map(m => (
                    <SelectItem key={m.id} value={String(m.id)}>{m.nome} ({m.numero_frota})</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {fieldErrors.maquina_id && <p className="text-sm text-red-500 mt-1">{fieldErrors.maquina_id}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="horimetroHodometro">{controleLabel}</Label>
              <Input
                id="horimetroHodometro"
                type="number"
                step="any" // Allow decimals
                value={horimetroHodometro}
                onChange={(e) => setHorimetroHodometro(e.target.value)}
                required
                className="!text-black"
                disabled={!maquinaId} // Disable until machine is selected
              />
              {fieldErrors.horimetro_hodometro && <p className="text-sm text-red-500 mt-1">{fieldErrors.horimetro_hodometro}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="dataEntrada">Data e Hora de Entrada *</Label>
              <Input
                id="dataEntrada"
                type="datetime-local"
                value={dataEntrada}
                onChange={(e) => setDataEntrada(e.target.value)}
                required
                className="!text-black"
              />
              {fieldErrors.data_entrada && <p className="text-sm text-red-500 mt-1">{fieldErrors.data_entrada}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="dataSaida">Data e Hora de Saída</Label>
              <Input
                id="dataSaida"
                type="datetime-local"
                value={dataSaida}
                onChange={(e) => setDataSaida(e.target.value)}
                className="!text-black"
              />
              {fieldErrors.data_saida && <p className="text-sm text-red-500 mt-1">{fieldErrors.data_saida}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="tipoManutencao">Tipo de Manutenção *</Label>
              <Select value={tipoManutencao} onValueChange={(value) => setTipoManutencao(value as any)} required>
                <SelectTrigger id="tipoManutencao">
                  <SelectValue placeholder="Selecione o tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="preventiva">Preventiva</SelectItem>
                  <SelectItem value="corretiva">Corretiva</SelectItem>
                </SelectContent>
              </Select>
              {fieldErrors.tipo_manutencao && <p className="text-sm text-red-500 mt-1">{fieldErrors.tipo_manutencao}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="categoriaServico">Categoria do Serviço *</Label>
              <Select value={categoriaServico} onValueChange={setCategoriaServico} required>
                <SelectTrigger id="categoriaServico">
                  <SelectValue placeholder="Selecione a categoria" />
                </SelectTrigger>
                <SelectContent>
                  {categoriasServico.map(cat => (
                    <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {fieldErrors.categoria_servico && <p className="text-sm text-red-500 mt-1">{fieldErrors.categoria_servico}</p>}
            </div>

            {categoriaServico === 'Outros' && (
              <div className="space-y-2 md:col-span-2"> {/* Span across columns if visible */}
                <Label htmlFor="categoriaOutros">Especificar Categoria "Outros" *</Label>
                <Input
                  id="categoriaOutros"
                  value={categoriaOutros}
                  onChange={(e) => setCategoriaOutros(e.target.value)}
                  required
                  className="!text-black"
                />
                {fieldErrors.categoria_outros_especificacao && <p className="text-sm text-red-500 mt-1">{fieldErrors.categoria_outros_especificacao}</p>}
              </div>
            )}

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="comentario">Comentário / Descrição</Label>
              <Textarea
                id="comentario"
                value={comentario}
                onChange={(e) => setComentario(e.target.value)}
                placeholder="Detalhes adicionais sobre a manutenção..."
                className="!text-black"
              />
              {fieldErrors.comentario && <p className="text-sm text-red-500 mt-1">{fieldErrors.comentario}</p>}
            </div>

              <div className="space-y-2">
              <Label htmlFor="responsavel">Responsável pelo Serviço *</Label>
              <Input
                id="responsavel"
                value={responsavel}
                onChange={(e) => setResponsavel(e.target.value)}
                required
                className="!text-black"
              />
              {fieldErrors.responsavel_servico && <p className="text-sm text-red-500 mt-1">{fieldErrors.responsavel_servico}</p>}
            </div>

             <div className="space-y-2">
              <Label htmlFor="custo">Custo (R$)</Label>
              <Input
                id="custo"
                type="number"
                step="0.01"
                value={custo}
                onChange={(e) => setCusto(e.target.value)}
                placeholder="Ex: 150.75"
                className="!text-black"
              />
              {fieldErrors.custo && <p className="text-sm text-red-500 mt-1">{fieldErrors.custo}</p>}
            </div>

          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline">Cancelar</Button>
            </DialogClose>
            <Button type="submit" disabled={loading}>
              {loading ? (isEditing ? 'Salvando...' : 'Registrando...') : (isEditing ? 'Salvar Alterações' : 'Registrar Manutenção')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default ManutencaoFormModal;

