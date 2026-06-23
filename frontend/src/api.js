import axios from 'axios';

// Camada de comunicacao com a API de Controle de Estoque (backend Flask).
const api = axios.create({
  baseURL: 'http://localhost:5000',
});

export const listarProdutos = (filtros = {}) => {
  const params = {};
  if (filtros.busca) params.busca = filtros.busca;
  if (filtros.categoria) params.categoria = filtros.categoria;
  return api.get('/produtos', { params }).then((resp) => resp.data);
};

export const cadastrarProduto = (dados) =>
  api.post('/produtos', dados).then((resp) => resp.data);

export const atualizarProduto = (id, dados) =>
  api.put(`/produtos/${id}`, dados).then((resp) => resp.data);

export const ajustarQuantidade = (id, quantidade_estoque) =>
  api
    .patch(`/produtos/${id}/quantidade`, { quantidade_estoque })
    .then((resp) => resp.data);

export const excluirProduto = (id) =>
  api.delete(`/produtos/${id}`).then((resp) => resp.data);

export default api;
