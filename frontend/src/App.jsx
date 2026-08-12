import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
  const [indicadores, setIndicadores] = useState({ total_envios: 0, entregues: 0, em_andamento: 0 });
  const [envios, setEnvios] = useState([]);
  const [mensagem, setMensagem] = useState("");
  const [busca, setBusca] = useState(""); 
  const [filtroTransp, setFiltroTransp] = useState("Todas");
  const arquivoInput = useRef(null);

  const buscarDados = async () => {
    try {
      const resposta = await axios.get('https://api-rastreamento.onrender.com/envios');
      setIndicadores(resposta.data.indicadores);
      setEnvios(resposta.data.lista_pedidos);
    } catch (erro) {
      console.error("Erro ao buscar dados da API:", erro);
    }
  };

  useEffect(() => {
    buscarDados();
  }, []);

  const fazerUpload = async (event) => {
    event.preventDefault();
    const arquivo = arquivoInput.current.files[0];
    if (!arquivo) {
      setMensagem("Por favor, selecione um arquivo primeiro.");
      return;
    }

    const formData = new FormData();
    formData.append("arquivo", arquivo);

    try {
      setMensagem("Processando arquivo, aguarde...");
      await axios.post('https://api-rastreamento.onrender.com/importacao/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMensagem("Planilha processada e salva no banco de dados com sucesso!");
      buscarDados(); 
    } catch (erro) {
      setMensagem("Erro ao enviar o arquivo.");
      console.error(erro);
    }
  };

  const enviosFiltrados = envios?.filter((envio) => {
    const termo = busca.toLowerCase();
    const nf = envio.nota_fiscal ? envio.nota_fiscal.toLowerCase() : "";
    const pedido = envio.pedido ? envio.pedido.toLowerCase() : "";
    const rastreio = envio.codigo_rastreio ? envio.codigo_rastreio.toLowerCase() : "";
    
    const passaBusca = nf.includes(termo) || pedido.includes(termo) || rastreio.includes(termo);
    const passaFiltro = filtroTransp === "Todas" || envio.transportadora === filtroTransp;
    
    return passaBusca && passaFiltro;
  });

  const exportarCSV = () => {
    let csv = "Transportadora;Nota Fiscal;Pedido;Rastreio;Status Atual\n";
    enviosFiltrados.forEach((e) => {
      csv += `${e.transportadora};${e.nota_fiscal};${e.pedido || ''};${e.codigo_rastreio};${e.status_atual}\n`;
    });
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "relatorio_rastreio.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getClasseStatus = (status) => {
    if (!status) return "status-padrao";
    const s = status.toLowerCase();
    if (s.includes("entregue")) return "status-verde";
    if (s.includes("atraso") || s.includes("devolução") || s.includes("cancelado") || s.includes("falha")) return "status-vermelho";
    return "status-amarelo";
  };

  const dadosGrafico = [
    { name: 'Correios', value: envios?.filter(e => e.transportadora === 'Correios').length },
    { name: 'Aviat', value: envios?.filter(e => e.transportadora === 'Aviat').length },
    { name: 'Expedição', value: envios?.filter(e => e.transportadora === 'Expedição').length },
  ];
  const CORES = ['#fba94c', '#00b37e', '#8257e5'];

  return (
    <div className="container">
      <header className="cabecalho">
        <h1>Painel de Rastreamento Unificado</h1>
        <p>Monitoramento ativo Expedição, Correios e Aviat</p>
      </header>

      <div className="area-upload">
        <form onSubmit={fazerUpload} className="formulario-upload">
          <input type="file" ref={arquivoInput} accept=".csv, .xlsx" />
          <button type="submit" className="botao-enviar">Processar Planilha</button>
        </form>
        {mensagem && <p className="mensagem-upload">{mensagem}</p>}
      </div>

      <div className="indicadores-grid">
        <div className="card">
          <h3>Total de Envios</h3>
          <p className="numero azul">{indicadores?.total_envios}</p>
        </div>
        <div className="card">
          <h3>Em Andamento</h3>
          <p className="numero amarelo">{indicadores?.em_andamento}</p>
        </div>
        <div className="card">
          <h3>Entregues</h3>
          <p className="numero verde">{indicadores?.entregues}</p>
        </div>
      </div>

      <div className="painel-grafico">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={dadosGrafico} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
              {dadosGrafico.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={CORES[index % CORES.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <section className="area-tabela">
        <div className="controles-tabela">
          <div className="filtros-botoes">
            <button className={filtroTransp === "Todas" ? "ativo" : ""} onClick={() => setFiltroTransp("Todas")}>Todas</button>
            <button className={filtroTransp === "Correios" ? "ativo" : ""} onClick={() => setFiltroTransp("Correios")}>Correios</button>
            <button className={filtroTransp === "Aviat" ? "ativo" : ""} onClick={() => setFiltroTransp("Aviat")}>Aviat</button>
            <button className={filtroTransp === "Expedição" ? "ativo" : ""} onClick={() => setFiltroTransp("Expedição")}>Expedição</button>
          </div>
          
          <input 
            type="text" 
            placeholder="Pesquisar por NF, Pedido ou Rastreio..." 
            className="input-pesquisa"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
          />
          
          <button className="botao-exportar" onClick={exportarCSV}>📥 Baixar Relatório</button>
        </div>

        <table className="tabela-envios">
          <thead>
            <tr>
              <th>Transportadora</th>
              <th>Nota Fiscal</th>
              <th>Rastreio</th>
              <th>Status Atual</th>
            </tr>
          </thead>
          <tbody>
            {enviosFiltrados?.slice(0, 50).map((envio) => (
              <tr key={envio.id}>
                <td>{envio.transportadora}</td>
                <td>{envio.nota_fiscal}</td>
                <td>{envio.codigo_rastreio}</td>
                <td>
                  <span className={getClasseStatus(envio.status_atual)}>
                    {envio.status_atual || 'Sem atualização'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

export default App;