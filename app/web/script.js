const table = document.querySelector("#sensorTable tbody");
const MAX_ROWS = 10;  // Últimos 10 registros

// Elementos de predição
const pred24hElement = document.querySelector("#pred24h .temp-value");
const pred120hElement = document.querySelector("#pred120h .temp-value");
const predictionStatus = document.getElementById("predictionStatus");
const lastPredUpdate = document.getElementById("lastPredUpdate");

// Configuração do servidor de predição
// Usa o mesmo hostname da página, mas porta 5000
const PREDICTION_SERVER = `http://${window.location.hostname}:5000`;

// Armazenar dados para exibição
let sensorData = [];

async function attData() {
    try {
        const response = await fetch("/data.csv");
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const text = await response.text();
        
        if (!text || text.trim() === "") {
            console.warn("CSV vazio");
            return;
        }
        
        const rows = text.trim().split("\n");
        
        // Separar cabeçalho e dados
        let dataRows = [];
        
        rows.forEach((row, idx) => {
            const data = row.split(",");
            if (idx === 0 && data[0].toLowerCase() === "date") {
                // Ignorar cabeçalho
            } else {
                dataRows.push(row);
            }
        });

        // Guardar dados
        sensorData = dataRows.map(row => {
            const cols = row.split(",");
            return {
                date: cols[0],
                time: cols[1],
                temperature: parseFloat(cols[2]),
                pressure: parseFloat(cols[3]),
                humidity: parseFloat(cols[4])
            };
        });

        // Pegar as últimas MAX_ROWS linhas
        const last_rows = dataRows.slice(-MAX_ROWS);
        
        // INVERTER para mostrar as mais recentes primeiro
        last_rows.reverse();

        table.innerHTML = "";

        last_rows.forEach((row) => {
            const data = row.split(",");
            const tr = document.createElement("tr");

            data.forEach((cell, index) => {
                const td = document.createElement("td");
                let value = cell.trim();
                
                // Formatar valores numéricos
                if (index === 2) { // Temperatura
                    td.innerHTML = `<strong>${parseFloat(value).toFixed(2)}</strong>`;
                } else if (index === 3) { // Pressão
                    td.textContent = parseFloat(value).toFixed(1);
                } else if (index === 4) { // Umidade
                    td.textContent = parseFloat(value).toFixed(1);
                } else {
                    td.textContent = value;
                }
                
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });
        
        console.log(`Tabela atualizada - ${last_rows.length} linhas`);
        
        // Buscar predições do servidor de IA
        fetchPredictions();
        
    } catch(err) {
        console.error("Erro ao ler CSV: ", err);
        table.innerHTML = '<tr><td colspan="5" style="color:#ff4444;">Erro ao carregar dados. Verifique o servidor.</td></tr>';
    }
}

// Função para buscar predições do servidor Python
async function fetchPredictions() {
    try {
        predictionStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calculando predicoes...';
        predictionStatus.className = "";
        
        const response = await fetch(`${PREDICTION_SERVER}/api/predict`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const predictions = await response.json();
        
        if (predictions.status === "ok") {
            // Atualizar valores na interface
            if (predictions.temp_24h !== null) {
                pred24hElement.textContent = predictions.temp_24h.toFixed(1);
            } else {
                pred24hElement.textContent = "--";
            }
            
            if (predictions.temp_120h !== null) {
                pred120hElement.textContent = predictions.temp_120h.toFixed(1);
            } else {
                pred120hElement.textContent = "--";
            }
            
            predictionStatus.innerHTML = '<i class="fas fa-check-circle"></i> Predicoes atualizadas via modelo de IA';
            predictionStatus.className = "status-ok";
            
            // Timestamp da última atualização
            lastPredUpdate.textContent = predictions.timestamp || new Date().toLocaleString('pt-BR');
            
            console.log("Predicoes recebidas:", predictions);
            
        } else if (predictions.status === "insufficient_data") {
            pred24hElement.textContent = "--";
            pred120hElement.textContent = "--";
            predictionStatus.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${predictions.message}`;
            predictionStatus.className = "status-warning";
            lastPredUpdate.textContent = predictions.timestamp || "--";
            
        } else {
            throw new Error(predictions.message || "Erro desconhecido");
        }
        
    } catch (err) {
        console.error("Erro ao buscar predicoes:", err);
        
        // Fallback: usar média simples se o servidor de predição não estiver disponível
        if (sensorData.length >= 10) {
            fallbackPredictions();
        } else {
            pred24hElement.textContent = "--";
            pred120hElement.textContent = "--";
            predictionStatus.innerHTML = '<i class="fas fa-times-circle"></i> Servidor de predicao indisponivel';
            predictionStatus.className = "status-error";
        }
    }
}

// Fallback: predição simples se o servidor de IA não estiver disponível
function fallbackPredictions() {
    const recentTemps = sensorData.slice(-24).map(d => d.temperature);
    const avgTemp = recentTemps.reduce((a, b) => a + b, 0) / recentTemps.length;
    
    // Estimativa simples baseada na média
    pred24hElement.textContent = avgTemp.toFixed(1);
    pred120hElement.textContent = avgTemp.toFixed(1);
    
    predictionStatus.innerHTML = '<i class="fas fa-exclamation-circle"></i> Predicao simplificada (servidor IA offline)';
    predictionStatus.className = "status-warning";
    lastPredUpdate.textContent = new Date().toLocaleString('pt-BR');
}

// Atualiza a cada 60 segundos
setInterval(attData, 60000);

// Primeira carga
attData();


