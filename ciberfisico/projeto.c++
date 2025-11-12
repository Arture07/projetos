#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>

// configuração wifi
const char *ssid = "S23João";
const char *password = "12345678";

// configuração pinos
const int MQ2_ANALOG_PIN = 32; // <--- MUDANÇA (Nome da variável)
const int LED_VERDE_PIN = 25;
const int LED_VERMELHO_PIN = 26;
const int BUZZER_PIN = 33;

// !!! IMPORTANTE: CALIBRAÇÃO NECESSÁRIA !!!
// O valor 4050 era para o MQ-5. Você DEVE ajustar este valor
// para o seu novo sensor MQ-2.
// Veja as instruções de calibração abaixo do código.
const int LIMIAR_GAS = 1500; // <--- AJUSTE ESTE VALOR (ex: 1500)

// estado do sensor
String sensorStatus = "seguro";
int valorSensor = 0;

AsyncWebServer server(80);

// pg html
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <title>ESP32 - Detector de Gás (MQ-2)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    html { font-family: Arial, Helvetica, sans-serif; text-align: center; }
    body { background-color: #222; color: #fff; margin-top: 50px; }
    h1 { font-size: 2.5rem; }
    p { font-size: 1.2rem; }
    .container {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 30px;
    }
    .status-card {
      background-color: #333;
      border-radius: 20px;
      padding: 30px;
      width: 90%;
      max-width: 400px;
      box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
      transition: background-color 0.5s ease;
    }
    .status-text {
      font-size: 3rem;
      font-weight: bold;
      margin: 20px 0;
      transition: color 0.5s ease;
    }
    .seguro { background-color: #28a745; }
    .seguro .status-text { color: #fff; }

    .perigo { background-color: #dc3545; animation: pulse 1s infinite; }
    .perigo .status-text { color: #fff; }

    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }

    .chart-container {
      background-color: #333;
      border-radius: 20px;
      padding: 20px;
      width: 90%;
      max-width: 800px;
      box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
    }
    
    /* 2. ADIÇÃO: Estilos para o gráfico SVG */
    #meuGraficoSvg {
      width: 100%;
      height: 200px; /* Altura fixa para o gráfico */
      background-color: #2a2a2a;
      border-radius: 10px;
    }
    #graficoLinha {
      stroke-width: 3px;
      fill: none;
      transition: stroke 0.5s ease; /* Transição da cor da linha */
    }

    .log-container {
      background-color: #333;
      border-radius: 20px;
      padding: 20px;
      width: 90%;
      max-width: 800px;
      box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
      text-align: left;
    }
    .log-container h2 { text-align: center; }
    .log-container table {
      width: 100%;
      border-collapse: collapse;
    }
    .log-container th, .log-container td {
      border-bottom: 1px solid #555;
      padding: 8px;
    }
    .log-container th {
      background-color: #444;
    }
    .log-container tr:first-child td {
      font-weight: bold;
      color: #f0f0f0;
    }
  </style>
</head>
<body>
  <h1>gasSensor (MQ-2)</h1>

    <div class="container">
    
    <div id="statusCard" class="status-card">
        <p>Status Atual:</p>
        <div id="statusText" class="status-text">CARREGANDO...</div>
        <p>Valor do Sensor: <span id="sensorValue">--</span></p>
    </div>

    <div class="chart-container">
        <h2>Oscilacao do Sensor</h2>
        <svg id="meuGraficoSvg" viewBox="0 0 500 200" preserveAspectRatio="none">
        <polyline id="graficoLinha" points="0,100" />
        </svg>
    </div>

    <div class="log-container">
        <h2>Log de Alteracoes de Status</h2>
        <table>
        <thead>
            <tr>
            <th>Horário</th>
            <th>Status</th>
            <th>Valor</th>
            </tr>
        </thead>
        <tbody id="logTableBody">
        </tbody>
        </table>
    </div>

    </div>

<script>
  // --- SEÇÃO DE NOTIFICAÇÃO (original) ---
    document.addEventListener('DOMContentLoaded', () => {
    if (Notification.permission !== "granted") {
        Notification.requestPermission();
    }
    });

    function showNotification() {
    if (Notification.permission === "granted") {
        new Notification("ALERTA DE SEGURANÇA!", {
        body: "Possível vazamento de gás detectado!",
        icon: "https://img.icons8.com/plasticine/100/gas-mask.png"
        });
        }
    }

    let alertShown = false;

  // --- 4. MUDANÇA: Lógica do Gráfico (sem Chart.js) ---

    let estadoAnterior = "";
    const MAX_ENTRADAS_LOG = 10;

  // Constantes para o gráfico SVG
  const MAX_PONTOS_GRAFICO_SVG = 50; // Quantos pontos na tela
  const SVG_VIEW_WIDTH = 500;  // Deve ser igual ao 'viewBox' do SVG
  const SVG_VIEW_HEIGHT = 200; // Deve ser igual ao 'viewBox' do SVG
  const MAX_VALOR_SENSOR = 4095; // Valor máximo do ADC do ESP32

  let historicoValores = []; // Array para guardar os valores

  // Função para adicionar uma entrada na tabela de log (original)
    function adicionarAoLog(status, valor) {
    const tabelaBody = document.getElementById("logTableBody");
    const data = new Date();
    const horario = data.toLocaleTimeString(); 
    
    let novaLinha = tabelaBody.insertRow(0);
    novaLinha.innerHTML = `<td>${horario}</td><td>${status.toUpperCase()}</td><td>${valor}</td>`;

    if(tabelaBody.rows.length > MAX_ENTRADAS_LOG) {
        tabelaBody.deleteRow(MAX_ENTRADAS_LOG);
    }
    }

  // Função para ATUALIZAR o gráfico SVG
    function atualizarGraficoSvg(valor) {
    // Adiciona o novo valor ao histórico
    historicoValores.push(valor);

    // Limita o número de pontos no histórico
    if(historicoValores.length > MAX_PONTOS_GRAFICO_SVG) {
      historicoValores.shift(); // Remove o valor mais antigo
    }

    const linhaGrafico = document.getElementById("graficoLinha");
    let pontosString = ""; // String "x1,y1 x2,y2 ..."

    for(let i = 0; i < historicoValores.length; i++) {
      // Calcula a posição X (distribuída igualmente)
      const x = (i / (MAX_PONTOS_GRAFICO_SVG - 1)) * SVG_VIEW_WIDTH;
    
      // Calcula a posição Y (mapeia 0-4095 para 0-200)
      // O '0' do SVG é no topo, por isso invertemos (HEIGHT - valor)
      const y = SVG_VIEW_HEIGHT - (historicoValores[i] / MAX_VALOR_SENSOR) * SVG_VIEW_HEIGHT;

      // Garante que o valor Y não saia da tela
        const y_clamp = Math.max(0, Math.min(SVG_VIEW_HEIGHT, y));

        pontosString += `${x},${y_clamp} `;
    }

    // Define os pontos da linha
    linhaGrafico.setAttribute("points", pontosString.trim());
    }

  // --- SEÇÃO DE ATUALIZAÇÃO (AJAX) ---
    setInterval(function () {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
        
        let response = JSON.parse(this.responseText);
        let status = response.status;
        let valor = response.valor;

        let statusCard = document.getElementById("statusCard");
        let statusText = document.getElementById("statusText");
        let linhaGrafico = document.getElementById("graficoLinha"); // Pega a linha do SVG
        document.getElementById("sensorValue").innerHTML = valor;
        
        if(status === "seguro"){
            statusCard.className = "status-card seguro";
            statusText.innerHTML = "SEGURO";
            alertShown = false; 
          // 5. MUDANÇA: Muda a cor da linha SVG
          linhaGrafico.style.stroke = "#28a745"; // Verde
        } else if (status === "perigo"){
            statusCard.className = "status-card perigo";
            statusText.innerHTML = "PERIGO!";
            if(!alertShown){
            showNotification();
            alertShown = true; 
            }
          // 5. MUDANÇA: Muda a cor da linha SVG
          linhaGrafico.style.stroke = "#dc3545"; // Vermelho
        }

        // 6. MUDANÇA: Chama a nova função do gráfico
        atualizarGraficoSvg(valor);

        // --- Lógica do Log (original) ---
        if (status !== estadoAnterior && estadoAnterior !== "") {
            adicionarAoLog(status, valor);
        }
        estadoAnterior = status; 

        }
    };
    xhttp.open("GET", "/status", true);
    xhttp.send();
    }, 2000 ) ;
</script>
</body>
</html>
)rawliteral";

// setup
void setup()
{
    Serial.begin(115200);

    // pinos de saida
    pinMode(LED_VERDE_PIN, OUTPUT);
    pinMode(LED_VERMELHO_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);

    // conecta no wifi
    WiFi.begin(ssid, password);
    Serial.print("Conectando ao Wi-Fi...");
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConectado!");
    Serial.print("Endereço IP: ");
    Serial.println(WiFi.localIP());

    // configuração das rotas

    // envia a pg web para o servidor
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->send_P(200, "text/html", index_html); });

    // envia o status atual do sensor em formato json
    server.on("/status", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    String json = "{\"status\":\"" + sensorStatus + "\", \"valor\":" + String(valorSensor) + "}";
    request->send(200, "application/json", json); });

    // inicia o servidor
    server.begin();
    Serial.println("Servidor web iniciado!");
}

void loop()
{

    valorSensor = analogRead(MQ2_ANALOG_PIN); // <--- MUDANÇA (Nome da variável)

    // Imprime o valor no Monitor Serial para ajudar na calibração
    Serial.print("Valor do Sensor MQ-2: ");
    Serial.println(valorSensor); // <--- ADIÇÃO

    if (valorSensor > LIMIAR_GAS)
    {
        // estado de perigo
        sensorStatus = "perigo";
        digitalWrite(LED_VERMELHO_PIN, HIGH);
        digitalWrite(LED_VERDE_PIN, LOW);
        tone(BUZZER_PIN, 1500, 200);
    }
    else
    {
        // estado seguro
        sensorStatus = "seguro";
        digitalWrite(LED_VERMELHO_PIN, LOW);
        digitalWrite(LED_VERDE_PIN, HIGH);
        noTone(BUZZER_PIN);
    }
    delay(200); // delay
}