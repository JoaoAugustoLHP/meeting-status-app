HTML_PAGE = """
<!DOCTYPE html>
<html lang='pt'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Controle Financeiro Pessoal</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { padding: 20px; font-family: Arial, sans-serif; }
    .section { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
    .section h2 { font-size: 1.25rem; margin-bottom: 15px; }
    .card-value { font-size: 1.5rem; font-weight: bold; }
  </style>
</head>
<body>
  <div class="container">

    <!-- Renda Mensal -->
    <div class="section">
      <h2>💰 Renda Mensal</h2>
      <div class="row">
        <div class="col-md-6 mb-3">
          <label class="form-label">Salário CLT (R$)</label>
          <input type="number" id="salario" class="form-control">
        </div>
        <div class="col-md-6 mb-3">
          <label class="form-label">Renda Extra (R$)</label>
          <input type="number" id="rendaExtra" class="form-control">
        </div>
      </div>
    </div>

    <!-- Gastos Fixos Mensais -->
    <div class="section">
      <h2>🏠 Gastos Fixos Mensais</h2>
      <div class="row">
        <div class="col-md-4 mb-3">
          <label class="form-label">Aluguel/Financiamento (R$)</label>
          <input type="number" id="gAluguel" class="form-control">
        </div>
        <div class="col-md-4 mb-3">
          <label class="form-label">Contas (Luz, Água, Internet) (R$)</label>
          <input type="number" id="gContas" class="form-control">
        </div>
        <div class="col-md-4 mb-3">
          <label class="form-label">Alimentação (R$)</label>
          <input type="number" id="gAlimentacao" class="form-control">
        </div>
        <div class="col-md-4 mb-3">
          <label class="form-label">Transporte (R$)</label>
          <input type="number" id="gTransporte" class="form-control">
        </div>
        <div class="col-md-4 mb-3">
          <label class="form-label">Outros Gastos Fixos (R$)</label>
          <input type="number" id="gOutrosFixos" class="form-control">
        </div>
      </div>
    </div>

    <!-- Planejamento de Investimentos -->
    <div class="section">
      <h2>📈 Planejamento de Investimentos</h2>
      <div class="row">
        <div class="col-md-4 mb-3">
          <label class="form-label">Meta de Investimento (%)</label>
          <input type="number" id="metaInvest" class="form-control">
        </div>
        <div class="col-md-4 mb-3">
          <label class="form-label">Valor para Investir (R$)</label>
          <input type="text" id="valorInvestir" class="form-control" readonly>
        </div>
      </div>
      <div class="row">
        <div class="col-md-4 mb-3">
          <label class="form-label">Reserva de Emergência (%)</label>
          <input type="number" id="pctReserva" class="form-control">
        </div>
        <div class="col-md-4 mb-3">
          <label class="form-label">Renda Fixa (%)</label>
          <input type="number" id="pctFixa" class="form-control">
        </div>
        <div class="col-md-4 mb-3">
          <label class="form-label">Renda Variável (%)</label>
          <input type="number" id="pctVariavel" class="form-control">
        </div>
      </div>
    </div>

    <!-- Gastos Variáveis com Filtro -->
    <div class="section">
      <h2>🛒 Gastos Variáveis</h2>

      <!-- Filtro de Período -->
      <div class="row mb-3">
        <div class="col-md-3 mb-3">
          <label class="form-label">Data Início</label>
          <input type="date" id="startDate" class="form-control">
        </div>
        <div class="col-md-3 mb-3">
          <label class="form-label">Data Fim</label>
          <input type="date" id="endDate" class="form-control">
        </div>
        <div class="col-md-2 align-self-end mb-3">
          <button id="btnClearFilter" class="btn btn-secondary w-100">Limpar Filtro</button>
        </div>
      </div>

      <!-- Formulário de Lançamento -->
      <div class="row align-items-end">
        <div class="col-md-3 mb-3">
          <label class="form-label">Data</label>
          <input type="date" id="dateVar" class="form-control">
        </div>
        <div class="col-md-3 mb-3">
          <label class="form-label">Descrição</label>
          <input type="text" id="descVar" class="form-control" placeholder="Ex: Cinema, Lazer...">
        </div>
        <div class="col-md-2 mb-3">
          <label class="form-label">Valor (R$)</label>
          <input type="number" id="valVar" class="form-control">
        </div>
        <div class="col-md-2 mb-3">
          <label class="form-label">Categoria</label>
          <select id="catVar" class="form-select">
            <option>Lazer</option>
            <option>Alimentação</option>
            <option>Transporte</option>
            <option>Saúde</option>
            <option>Outros</option>
          </select>
        </div>
        <div class="col-md-2 mb-3">
          <button id="btnAddVar" class="btn btn-success w-100">Adicionar Gasto</button>
        </div>
      </div>

      <!-- Tabela de Gastos -->
      <table class="table table-bordered mt-3">
        <thead>
          <tr>
            <th>Data</th><th>Descrição</th><th>Categoria</th><th>Valor (R$)</th><th>Ações</th>
          </tr>
        </thead>
        <tbody id="tableVar"></tbody>
      </table>
    </div>

    <!-- Resumo Financeiro Mensal -->
    <div class="section">
      <h2>📊 Resumo Financeiro Mensal</h2>
      <div class="row text-center">
        <div class="col-md-3 mb-3">
          <div class="card p-3">
            <div class="card-value" id="rendaTotal">R$ 0,00</div><div>Renda Total</div>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="card p-3">
            <div class="card-value" id="gastosTotais">R$ 0,00</div><div>Gastos Totais</div>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="card p-3">
            <div class="card-value" id="paraInvestir">R$ 0,00</div><div>Para Investir</div>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="card p-3">
            <div class="card-value" id="saldoFinal">R$ 0,00</div><div>Saldo Final</div>
          </div>
        </div>
      </div>
      <div class="row text-center mt-3">
        <div class="col-md-4 mb-3">
          <div class="card p-2">
            <div class="card-value" id="reservaVal">R$ 0,00</div><div>Reserva de Emergência</div>
          </div>
        </div>
        <div class="col-md-4 mb-3">
          <div class="card p-2">
            <div class="card-value" id="fixaVal">R$ 0,00</div><div>Renda Fixa</div>
          </div>
        </div>
        <div class="col-md-4 mb-3">
          <div class="card p-2">
            <div class="card-value" id="variavelVal">R$ 0,00</div><div>Renda Variável</div>
          </div>
        </div>
      </div>
    </div>

  </div>

  <script>
    // Carrega valores e lista
    function loadData() {
      ['salario','rendaExtra','gAluguel','gContas','gAlimentacao','gTransporte','gOutrosFixos',
       'metaInvest','pctReserva','pctFixa','pctVariavel'].forEach(id => {
        let el = document.getElementById(id);
        let v = localStorage.getItem(id);
        if (el && v!==null) el.value = v;
      });

      // dataVar default hoje
      let dv = document.getElementById('dateVar');
      if (dv && !dv.value) dv.value = new Date().toISOString().substr(0,10);

      // carrega gastos
      JSON.parse(localStorage.getItem('variaveis')||'[]').forEach(item=>{
        addRow(item);
      });
      updateAll();
    }

    // Salva ao mudar qualquer input
    document.querySelectorAll('input').forEach(inp=>{
      inp.addEventListener('input', e=>{
        if (e.target.id !== 'dateVar')  // dateVar não precisa ser salvo
          localStorage.setItem(e.target.id, e.target.value);
        updateAll();
      });
    });

    // Lançar novo gasto
    document.getElementById('btnAddVar').addEventListener('click', ()=>{
      let iso = document.getElementById('dateVar').value;
      let desc = document.getElementById('descVar').value;
      let val  = parseFloat(document.getElementById('valVar').value)||0;
      let cat  = document.getElementById('catVar').value;
      if (!desc) return alert('Informe descrição');
      let display = new Date(iso).toLocaleDateString();
      let item = { date: display, isoDate: iso, desc, val, cat };
      let arr = JSON.parse(localStorage.getItem('variaveis')||'[]');
      arr.push(item);
      localStorage.setItem('variaveis', JSON.stringify(arr));
      addRow(item);
      updateAll();
      document.getElementById('descVar').value = '';
      document.getElementById('valVar').value = '';
    });

    // Função que filtra pelo período
    function getFilteredItems() {
      let all = JSON.parse(localStorage.getItem('variaveis')||'[]');
      let start = document.getElementById('startDate').value;
      let end   = document.getElementById('endDate').value;
      return all.filter(i=>{
        let d = new Date(i.isoDate);
        if (start && d < new Date(start)) return false;
        if (end   && d > new Date(end))   return false;
        return true;
      });
    }

    // Limpa e preenche a tabela segundo filtro
    function refreshTable() {
      let tb = document.getElementById('tableVar');
      tb.innerHTML = '';
      getFilteredItems().forEach(addRow);
    }

    // Cria uma linha na tabela (com botão remover)
    function addRow(item) {
      let tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${item.date}</td>
        <td>${item.desc}</td>
        <td>${item.cat}</td>
        <td>R$ ${item.val.toFixed(2)}</td>
        <td><button class="btn btn-sm btn-danger">Remover</button></td>`;
      tr.querySelector('button').onclick = ()=>{
        let arr = JSON.parse(localStorage.getItem('variaveis')||'[]')
                     .filter(i=>!(i.isoDate===item.isoDate && i.desc===item.desc && i.val===item.val));
        localStorage.setItem('variaveis', JSON.stringify(arr));
        updateAll();
      };
      document.getElementById('tableVar').appendChild(tr);
    }

    // Atualiza tabela, totais e cards
    function updateAll() {
      refreshTable();
      let toNum = id => parseFloat(document.getElementById(id).value)||0;
      let rendaTotal = toNum('salario') + toNum('rendaExtra');
      let fixos = toNum('gAluguel') + toNum('gContas') + toNum('gAlimentacao') + toNum('gTransporte') + toNum('gOutrosFixos');
      let vars   = getFilteredItems().reduce((s,i)=>s+i.val,0);
      let gastosTotais = fixos + vars;
      let meta = toNum('metaInvest')/100;
      let valorInvestir = rendaTotal * meta;
      let rRes = valorInvestir * toNum('pctReserva')/100;
      let rFix = valorInvestir * toNum('pctFixa')/100;
      let rVar = valorInvestir * toNum('pctVariavel')/100;
      let saldoFinal = rendaTotal - gastosTotais;

      document.getElementById('rendaTotal').innerText    = `R$ ${rendaTotal.toFixed(2)}`;
      document.getElementById('gastosTotais').innerText  = `R$ ${gastosTotais.toFixed(2)}`;
      document.getElementById('paraInvestir').innerText  = `R$ ${valorInvestir.toFixed(2)}`;
      document.getElementById('saldoFinal').innerText    = `R$ ${saldoFinal.toFixed(2)}`;
      document.getElementById('reservaVal').innerText    = `R$ ${rRes.toFixed(2)}`;
      document.getElementById('fixaVal').innerText       = `R$ ${rFix.toFixed(2)}`;
      document.getElementById('variavelVal').innerText   = `R$ ${rVar.toFixed(2)}`;
      document.getElementById('valorInvestir').value     = `R$ ${valorInvestir.toFixed(2)}`;
    }

    // Filtrar em tempo real
    ['startDate','endDate'].forEach(id=>{
      document.getElementById(id).addEventListener('change', updateAll);
    });
    document.getElementById('btnClearFilter').addEventListener('click', ()=>{
      document.getElementById('startDate').value = '';
      document.getElementById('endDate').value   = '';
      updateAll();
    });

    window.onload = loadData;
  </script>
</body>
</html>
"""
