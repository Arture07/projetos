#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>

// configuração wifi
const char *ssid = "S23João";
const char *password = "12345678";

// configuração dos pinos
const int MQ2_ANALOG_PIN = 32; 
const int LED_VERDE_PIN = 25;
const int LED_VERMELHO_PIN = 26;
const int BUZZER_PIN = 33;

const int LIMIAR_GAS = 1500; // valor limite para detectar perigo

// estado do sensor
String sensorStatus = "seguro";
int valorSensor = 0;

AsyncWebServer server(80);

// página html que será exibida
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <title>ESP32 - Detector de Gás (MQ-2)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <style>
    /* estilo geral da página */
    html { font-family: Arial, Helvetica, sans-serif; text-align: center; }
    body { background-color: #222; color: #fff; margin-top: 50px; }
    h1 { font-size: 2.5rem; }
    p { font-size: 1.2rem; }

    /* contêiner principal */
    .container {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 30px;
    }

    /* cartão que mostra o status do sensor */
    .status-card {
      background-color: #333;
      border-radius: 20px;
      padding: 30px;
      width: 90%;
      max-width: 400px;
      box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
      transition: background-color 0.5s ease;
    }

    /* texto do status (seguro ou perigo) */
    .status-text {
      font-size: 3rem;
      font-weight: bold;
      margin: 20px 0;
      transition: color 0.5s ease;
    }

    /* cor verde quando o ambiente está seguro */
    .seguro { background-color: #28a745; }
    .seguro .status-text { color: #fff; }

    /* cor vermelha e animação quando há perigo */
    .perigo { background-color: #dc3545; animation: pulse 1s infinite; }
    .perigo .status-text { color: #fff; }

    /* animação de pulsar no modo perigo */
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }

    /* área onde aparece o gráfico */
    .chart-container {
      background-color: #333;
      border-radius: 20px;
      padding: 20px;
      width: 90%;
      max-width: 800px;
      box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
    }

    /* configurações do gráfico SVG */
    #meuGraficoSvg {
      width: 100%;
      height: 200px;
      background-color: #2a2a2a;
      border-radius: 10px;
    }
    #graficoLinha {
      stroke-width: 3px;
      fill: none;
      transition: stroke 0.5s ease; 
    }

    /* tabela de histórico (log) */
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
    
    <!-- cartão que mostra o status atual -->
    <div id="statusCard" class="status-card">
        <p>Status atual:</p>
        <div id="statusText" class="status-text">carregando...</div>
        <p>Valor do sensor: <span id="sensorValue">--</span></p>
    </div>

    <!-- área do gráfico em tempo real -->
    <div class="chart-container">
        <h2>Oscilacao do Sensor</h2>
        <svg id="meuGraficoSvg" viewBox="0 0 500 200" preserveAspectRatio="none">
          <polyline id="graficoLinha" points="0,100" />
        </svg>
    </div>

    <!-- tabela que mostra o histórico de mudanças de status -->
    <div class="log-container">
        <h2>Log de alteracoes de status</h2>
        <table>
          <thead>
            <tr>
              <th>Horario</th>
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
  // pede permissão para enviar notificações no navegador
  document.addEventListener('DOMContentLoaded', () => {
    if (Notification.permission !== "granted") {
        Notification.requestPermission();
    }
  });

  // mostra uma notificação se houver perigo
  function showNotification() {
    if (Notification.permission === "granted") {
        new Notification("Alerta de segurança!", {
        body: "Possível vazamento de gás detectado!",
        icon: "https://img.icons8.com/plasticine/100/gas-mask.png"
        });
    }
  }

  let alertShown = false; // evita repetir alerta
  let estadoAnterior = "";
  const MAX_ENTRADAS_LOG = 10; // máximo de registros na tabela

  // configurações do gráfico
  const MAX_PONTOS_GRAFICO_SVG = 50;
  const SVG_VIEW_WIDTH = 500;
  const SVG_VIEW_HEIGHT = 200;
  const MAX_VALOR_SENSOR = 4095;

  let historicoValores = []; // guarda valores anteriores

  // adiciona uma nova linha no log
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

  // atualiza o gráfico SVG com o novo valor
  function atualizarGraficoSvg(valor) {
    historicoValores.push(valor);
    if(historicoValores.length > MAX_PONTOS_GRAFICO_SVG) {
      historicoValores.shift(); 
    }

    const linhaGrafico = document.getElementById("graficoLinha");
    let pontosString = "";

    for(let i = 0; i < historicoValores.length; i++) {
      const x = (i / (MAX_PONTOS_GRAFICO_SVG - 1)) * SVG_VIEW_WIDTH;
      const y = SVG_VIEW_HEIGHT - (historicoValores[i] / MAX_VALOR_SENSOR) * SVG_VIEW_HEIGHT;
      const y_clamp = Math.max(0, Math.min(SVG_VIEW_HEIGHT, y));
      pontosString += `${x},${y_clamp} `;
    }
    linhaGrafico.setAttribute("points", pontosString.trim());
  }

  // busca os dados do ESP32 a cada 2 segundos
  setInterval(function () {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        let response = JSON.parse(this.responseText);
        let status = response.status;
        let valor = response.valor;

        let statusCard = document.getElementById("statusCard");
        let statusText = document.getElementById("statusText");
        let linhaGrafico = document.getElementById("graficoLinha");
        document.getElementById("sensorValue").innerHTML = valor;
        
        // muda as cores e o texto conforme o status
        if(status === "seguro"){
            statusCard.className = "status-card seguro";
            statusText.innerHTML = "seguro";
            alertShown = false; 
            linhaGrafico.style.stroke = "#28a745"; // verde
        } else if (status === "perigo"){
            statusCard.className = "status-card perigo";
            statusText.innerHTML = "perigo!";
            if(!alertShown){
              showNotification();
              alertShown = true; 
            }
            linhaGrafico.style.stroke = "#dc3545"; // vermelho
        }

        // atualiza gráfico e log se o estado mudou
        atualizarGraficoSvg(valor);
        if (status !== estadoAnterior && estadoAnterior !== "") {
            adicionarAoLog(status, valor);
        }
        estadoAnterior = status; 
      }
    };
    xhttp.open("GET", "/status", true);
    xhttp.send();
  }, 2000);
</script>
</body>
</html>
)rawliteral";

// setup
void setup() {
    Serial.begin(115200);

    // define os pinos de saída
    pinMode(LED_VERDE_PIN, OUTPUT);
    pinMode(LED_VERMELHO_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);

    // conecta ao wifi
    WiFi.begin(ssid, password);
    Serial.print("Conectando ao Wi-Fi...");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConectado!");
    Serial.print("Endereço IP: ");
    Serial.println(WiFi.localIP());

    // rota principal envia a página web
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "text/html", index_html);
    });

    // rota que envia o status do sensor em formato json
    server.on("/status", HTTP_GET, [](AsyncWebServerRequest *request) {
        String json = "{\"status\":\"" + sensorStatus + "\", \"valor\":" + String(valorSensor) + "}";
        request->send(200, "application/json", json);
    });

    // inicia o servidor web
    server.begin();
    Serial.println("Servidor web iniciado!");
}

void loop() {
    valorSensor = analogRead(MQ2_ANALOG_PIN); 

    Serial.print("Valor do Sensor MQ-2: ");
    Serial.println(valorSensor); 

    // verifica se há perigo
    if (valorSensor > LIMIAR_GAS) {
        sensorStatus = "perigo";
        digitalWrite(LED_VERMELHO_PIN, HIGH);
        digitalWrite(LED_VERDE_PIN, LOW);
        tone(BUZZER_PIN, 1500, 200);
    } else {
        sensorStatus = "seguro";
        digitalWrite(LED_VERMELHO_PIN, LOW);
        digitalWrite(LED_VERDE_PIN, HIGH);
        noTone(BUZZER_PIN);
    }

    delay(200); // pequena pausa antes da próxima leitura
}
