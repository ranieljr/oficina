import axios from 'axios';

export async function downloadManutencoesExcel() {
  const response = await axios.get('/export/manutencoes/excel', {
    responseType: 'blob',
  });
  const filename = response.headers['content-disposition']
    .split('filename=')[1];
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
}