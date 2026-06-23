import React, { useState, useEffect, useCallback } from 'react';
import {
  listarProdutos,
  cadastrarProduto,
  atualizarProduto,
  ajustarQuantidade,
  excluirProduto,
} from './api';
import './App.css';

const CATEGORIAS = [
  'alimentos', 'bebidas', 'limpeza', 'higiene', 'papelaria', 'utilidades', 'outros',
];
const UNIDADES = ['un', 'kg', 'g', 'l', 'ml', 'pct', 'cx'];

const FORM_INICIAL = {
  nome: '',
  categoria: 'alimentos',
  descricao: '',
  preco_unitario: '',
  quantidade_estoque: '',
  estoque_minimo: '',
  unidade_medida: 'un',
  codigo_barras: '',
  fornecedor: '',
};

const SITUACAO_INFO = {
  ok: { rotulo: 'OK', classe: 'badge-ok' },
  baixo: { rotulo: 'Estoque baixo', classe: 'badge-baixo' },
  esgotado: { rotulo: 'Esgotado', classe: 'badge-esgotado' },
};

function App() {
  const [produtos, setProdutos] = useState([]);
  const [resumo, setResumo] = useState({
    total_produtos: 0,
    produtos_em_alerta: 0,
    produtos_esgotados: 0,
  });
  const [filtros, setFiltros] = useState({ busca: '', categoria: '' });
  const [form, setForm] = useState(FORM_INICIAL);
  const [editandoId, setEditandoId] = useState(null);
  const [erros, setErros] = useState([]);

  const carregar = useCallback(() => {
    listarProdutos(filtros)
      .then((data) => {
        setProdutos(data.produtos || []);
        setResumo(
          data.resumo || { total_produtos: 0, produtos_em_alerta: 0, produtos_esgotados: 0 }
        );
      })
      .catch(() => setErros(['Erro ao carregar produtos. O backend esta rodando?']));
  }, [filtros]);

  useEffect(() => {
    carregar();
  }, [carregar]);

  const handleInput = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleFiltro = (e) => {
    const { name, value } = e.target;
    setFiltros((prev) => ({ ...prev, [name]: value }));
  };

  const resetForm = () => {
    setForm(FORM_INICIAL);
    setEditandoId(null);
    setErros([]);
  };

  const irParaSecao = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  const montarPayload = () => ({
    nome: form.nome,
    categoria: form.categoria,
    descricao: form.descricao,
    unidade_medida: form.unidade_medida,
    codigo_barras: form.codigo_barras || null,
    fornecedor: form.fornecedor || null,
    preco_unitario: form.preco_unitario === '' ? '' : Number(form.preco_unitario),
    quantidade_estoque: form.quantidade_estoque === '' ? '' : Number(form.quantidade_estoque),
    estoque_minimo: form.estoque_minimo === '' ? '' : Number(form.estoque_minimo),
  });

  const tratarErro = (err) => {
    const detalhes = err?.response?.data?.detalhes;
    setErros(detalhes || ['Erro ao salvar o produto.']);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setErros([]);
    const acao = editandoId
      ? atualizarProduto(editandoId, montarPayload())
      : cadastrarProduto(montarPayload());
    acao
      .then(() => {
        resetForm();
        carregar();
      })
      .catch(tratarErro);
  };

  const handleEditar = (produto) => {
    setEditandoId(produto.id);
    setErros([]);
    setForm({
      nome: produto.nome || '',
      categoria: produto.categoria || 'alimentos',
      descricao: produto.descricao || '',
      preco_unitario: produto.preco_unitario ?? '',
      quantidade_estoque: produto.quantidade_estoque ?? '',
      estoque_minimo: produto.estoque_minimo ?? '',
      unidade_medida: produto.unidade_medida || 'un',
      codigo_barras: produto.codigo_barras || '',
      fornecedor: produto.fornecedor || '',
    });
    irParaSecao('secao-form');
  };

  const handleExcluir = (produto) => {
    if (!window.confirm(`Excluir o produto "${produto.nome}"?`)) return;
    excluirProduto(produto.id).then(carregar);
  };

  const handleAjuste = (produto, delta) => {
    const nova = produto.quantidade_estoque + delta;
    if (nova < 0) return;
    ajustarQuantidade(produto.id, nova).then(carregar);
  };

  return (
    <div className="app">
      <header className="cabecalho">
        <h1>Controle de Estoque</h1>
        <p>Gestao de produtos para pequenos comercios locais</p>
      </header>

      {/* Menu superior de navegacao */}
      <nav className="menu">
        <button onClick={() => irParaSecao('secao-resumo')}>Resumo</button>
        <button onClick={() => irParaSecao('secao-form')}>Adicionar Produto</button>
        <button onClick={() => irParaSecao('secao-lista')}>Lista de Produtos</button>
      </nav>

      {/* Painel de resumo / alertas (funcionalidade exclusiva) */}
      <section id="secao-resumo" className="resumo">
        <div className="card card-total">
          <span className="card-valor">{resumo.total_produtos}</span>
          <span className="card-rotulo">Produtos cadastrados</span>
        </div>
        <div className="card card-alerta">
          <span className="card-valor">{resumo.produtos_em_alerta}</span>
          <span className="card-rotulo">Em alerta (estoque baixo)</span>
        </div>
        <div className="card card-esgotado">
          <span className="card-valor">{resumo.produtos_esgotados}</span>
          <span className="card-rotulo">Esgotados</span>
        </div>
      </section>

      {/* Formulario de cadastro / edicao */}
      <section id="secao-form" className="painel">
        <h2>{editandoId ? 'Editar produto' : 'Adicionar produto'}</h2>

        {erros.length > 0 && (
          <ul className="erros">
            {erros.map((erro, i) => (
              <li key={i}>{erro}</li>
            ))}
          </ul>
        )}

        <form onSubmit={handleSubmit} className="formulario">
          <div className="campo campo-largo">
            <label>Nome</label>
            <input name="nome" value={form.nome} onChange={handleInput} placeholder="Ex.: Arroz Branco 5kg" />
          </div>

          <div className="campo">
            <label>Categoria</label>
            <select name="categoria" value={form.categoria} onChange={handleInput}>
              {CATEGORIAS.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div className="campo">
            <label>Unidade</label>
            <select name="unidade_medida" value={form.unidade_medida} onChange={handleInput}>
              {UNIDADES.map((u) => (
                <option key={u} value={u}>{u}</option>
              ))}
            </select>
          </div>

          <div className="campo">
            <label>Preco unitario (R$)</label>
            <input type="number" step="0.01" name="preco_unitario" value={form.preco_unitario} onChange={handleInput} placeholder="0.00" />
          </div>

          <div className="campo">
            <label>Quantidade em estoque</label>
            <input type="number" name="quantidade_estoque" value={form.quantidade_estoque} onChange={handleInput} placeholder="0" />
          </div>

          <div className="campo">
            <label>Estoque minimo</label>
            <input type="number" name="estoque_minimo" value={form.estoque_minimo} onChange={handleInput} placeholder="0" />
          </div>

          <div className="campo">
            <label>Codigo de barras</label>
            <input name="codigo_barras" value={form.codigo_barras} onChange={handleInput} placeholder="(opcional)" />
          </div>

          <div className="campo">
            <label>Fornecedor</label>
            <input name="fornecedor" value={form.fornecedor} onChange={handleInput} placeholder="(opcional)" />
          </div>

          <div className="campo campo-largo">
            <label>Descricao</label>
            <input name="descricao" value={form.descricao} onChange={handleInput} placeholder="(opcional)" />
          </div>

          <div className="acoes-form">
            <button type="submit" className="btn btn-primario">
              {editandoId ? 'Salvar alteracoes' : 'Adicionar produto'}
            </button>
            {editandoId && (
              <button type="button" className="btn btn-secundario" onClick={resetForm}>
                Cancelar
              </button>
            )}
          </div>
        </form>
      </section>

      {/* Filtros dinamicos */}
      <section className="filtros">
        <input
          name="busca"
          value={filtros.busca}
          onChange={handleFiltro}
          placeholder="Buscar por nome..."
        />
        <select name="categoria" value={filtros.categoria} onChange={handleFiltro}>
          <option value="">Todas as categorias</option>
          {CATEGORIAS.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </section>

      {/* Lista de produtos */}
      <section id="secao-lista" className="lista">
        <h2>Produtos em estoque</h2>
        {produtos.length === 0 ? (
          <p className="vazio">Nenhum produto encontrado.</p>
        ) : (
          <table className="tabela">
            <thead>
              <tr>
                <th>Produto</th>
                <th>Categoria</th>
                <th>Preco</th>
                <th>Quantidade</th>
                <th>Minimo</th>
                <th>Situacao</th>
                <th>Acoes</th>
              </tr>
            </thead>
            <tbody>
              {produtos.map((p) => {
                const info = SITUACAO_INFO[p.situacao] || SITUACAO_INFO.ok;
                return (
                  <tr key={p.id} className={`linha-${p.situacao}`}>
                    <td>
                      <strong>{p.nome}</strong>
                      {p.fornecedor && <div className="sub">{p.fornecedor}</div>}
                    </td>
                    <td>{p.categoria}</td>
                    <td>R$ {Number(p.preco_unitario).toFixed(2)}</td>
                    <td>
                      <div className="ajuste">
                        <button onClick={() => handleAjuste(p, -1)} className="btn-mini">-</button>
                        <span>{p.quantidade_estoque} {p.unidade_medida}</span>
                        <button onClick={() => handleAjuste(p, 1)} className="btn-mini">+</button>
                      </div>
                    </td>
                    <td>{p.estoque_minimo}</td>
                    <td>
                      <span className={`badge ${info.classe}`}>{info.rotulo}</span>
                    </td>
                    <td>
                      <button className="btn btn-editar" onClick={() => handleEditar(p)}>Editar</button>
                      <button className="btn btn-excluir" onClick={() => handleExcluir(p)}>Excluir</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}

export default App;
