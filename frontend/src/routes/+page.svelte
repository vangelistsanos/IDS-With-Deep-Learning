<script>
  import { onMount } from "svelte";
  import { Network } from "vis-network";
  import { DataSet } from "vis-data";
  import "vis-network/styles/vis-network.css";
  import Chart from "chart.js/auto";
  import "../styles/dashboard.css";

  let confidenceThreshold = 0.5;
  let totalAttacks = 0;
  let lowConfidenceAttacks = 0;
  let normalTraffic = 0;

  let network;
  let networkContainer;
  let attackTable = [];
  let attackChart;
  let chartCanvas;

  let topSourcesCanvas;
  let topSourcesChart;
  const ipAttackCounts = {};

  const nodeDataSet = new DataSet([]);

  const edgeDataSet = new DataSet([]);

  const options = {
    groups: {
      client: { color: { background: "green" }, shape: "dot" },
      router: { color: { background: "orange" }, shape: "box" },
      server: { color: { background: "yellow" }, shape: "diamond" },
      attacker: { color: { background: "red" }, shape: "dot" },
    },
    edges: {
      arrows: "to",
      font: { align: "top" },
    },
    nodes: {
      font: "14px arial black",
    },
    physics: {
      stabilization: true,
    },
  };

  const attackCounts = {
    Analysis: 0,
    Backdoor: 0,
    DoS: 0,
    Exploits: 0,
    Fuzzers: 0,
    Generic: 0,
    Normal: 0,
    Reconnaissance: 0,
    Shellcode: 0,
    Worms: 0,
  };


  // Ασύγχρονη λειτουργία που καλεί το Flask server για να πάρει τυχαία δεδομένα δικτυακής κίνησης
  // και ενημερώνει την οπτικοποίηση δικτύου και τις στατιστικές επιθέσεων.
  // Επίσης, φιλτράρει τις επιθέσεις χαμηλής εμπιστοσύνης
  // με το να τις χαρακτηρίζει ως 'Normal'
  // και ενημερώνει τον πίνακα επιθέσεων και το γράφημα αναλόγως.
  async function fetchRandomNetworkTraffic() {
    const res = await fetch("http://127.0.0.1:5000/sample");
    const data = await res.json();


    if (data.confidence < confidenceThreshold && data.type !== "Normal") {
      data.type = "Normal"; // Filter out low-confidence data
      data.confidence = 100; // Normalize confidence for 'Normal' type
      lowConfidenceAttacks++;
    } 

    if (data.type === "Normal" && data.confidence >= confidenceThreshold) {
      normalTraffic++;
    } else {
      totalAttacks++;
    }
    addOrUpdateNodeAndEdge(data);
  }


  // προσθέτει ή ενημερώνει κόμβους και ακμές στο διάγραμμα δικτύου
  function addOrUpdateNodeAndEdge({ srcIP, dstIP, type, confidence }) {
    const now = new Date().toLocaleTimeString();
    const srcNodeId = srcIP;
    const dstNodeId = dstIP;

    // προσθέτει Node αν δεν υπάρχει ήδη
    if (!nodeDataSet.get(srcNodeId)) {
      nodeDataSet.add({
        id: srcNodeId,
        label: srcIP,
        group: "attacker",
      });
    }

    if (!nodeDataSet.get(dstNodeId)) {
      nodeDataSet.add({
        id: dstNodeId,
        label: dstIP,
        group: "server",
      });
    }
    // διαγράφει όλες τις ακμές που ξεκινούν από τον κόμβο srcNodeId
    const outgoingEdges = edgeDataSet.get({
      filter: (edge) => edge.from === srcNodeId,
    });

    outgoingEdges.forEach((edge) => {
      edgeDataSet.remove(edge.id);
    });

    // προσθέτει την τελευταία ακμή (αρχικά είχαμε πολλές ακμές μεταξύ των ίδιων κόμβων)
    edgeDataSet.add({
      from: srcNodeId,
      to: dstNodeId,
      label: type,
      color: type === "Normal" ? undefined : { color: "red" },
    });

    // ενημερώνει τον πίνακα επιθέσεων
    attackTable = [
      { time: now, type, src: srcIP, dst: dstIP, confidence },
      ...attackTable.slice(0, 9),
    ];

    attackCounts[type]++;
    attackChart.data.datasets[0].data = Object.values(attackCounts);
    attackChart.update();


    updateTopSourcesChart();

    // αλλάζει το σχήμα και το χρώμα του κόμβου ανάλογα με τον τύπο της επίθεσης
    // αν είναι 'Normal', το σχήμα είναι 'dot' και το χρώμα είναι 'green'
    // αν είναι διαφορετικό, το σχήμα είναι 'dot' και το χρώμα είναι 'red'.
    const hasAttack = type !== "Normal";

    nodeDataSet.update({
      id: srcNodeId,
      shape: hasAttack ? "dot" : "dot",
      color: { background: hasAttack ? "red" : "green" },
    });



    // Count attacks per source IP
    if (type !== "Normal") {
      if (!ipAttackCounts[srcIP]) ipAttackCounts[srcIP] = 0;
      ipAttackCounts[srcIP]++;
    }
  }




function updateTopSourcesChart() {
  const sorted = Object.entries(ipAttackCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  const labels = sorted.map(([ip]) => ip);
  const data = sorted.map(([_, count]) => count);

  if (!topSourcesChart) {
    topSourcesChart = new Chart(topSourcesCanvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Attack Count',
          data,
          backgroundColor: 'rgba(255, 99, 132, 0.6)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1
        }]
      },
      options: {
        indexAxis: 'y', // 🔁 This makes it horizontal
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            beginAtZero: true
          },
          y: {
            ticks: {
              autoSkip: false,
              font: { size: 10 }
            }
          }
        }
      }
    });
  } else {
    topSourcesChart.data.labels = labels;
    topSourcesChart.data.datasets[0].data = data;
    topSourcesChart.update();
  }
}


  // αρχικοποίηση του δικτύου και του γραφήματος όταν το component φορτώνει
  // Η onMount καλείται πάντα όταν το component έχει φορτωθεί
  onMount(() => {
    network = new Network(
      networkContainer,
      { nodes: nodeDataSet, edges: edgeDataSet },
      options,
    );
    setupChart();
    fetchRandomNetworkTraffic();
    setInterval(fetchRandomNetworkTraffic, 3000);
  });

  const attackLabels = [
    "Analysis",
    "Backdoor",
    "DoS",
    "Exploits",
    "Fuzzers",
    "Generic",
    "Normal",
    "Reconnaissance",
    "Shellcode",
    "Worms",
  ];

  const backgroundColors = [
    "rgba(255, 99, 132, 0.6)", // Analysis
    "rgba(54, 162, 235, 0.6)", // Backdoor
    "rgba(255, 206, 86, 0.6)", // DoS
    "rgba(75, 192, 192, 0.6)", // Exploits
    "rgba(153, 102, 255, 0.6)", // Fuzzers
    "rgba(255, 159, 64, 0.6)", // Generic
    "rgba(99, 255, 132, 0.6)", // Normal
    "rgba(201, 203, 207, 0.6)", // Reconnaissance
    "rgba(255, 102, 255, 0.6)", // Shellcode
    "rgba(0, 204, 204, 0.6)", // Worms
  ];

  function setupChart() {
    attackChart = new Chart(chartCanvas, {
      type: "bar",
      data: {
        labels: attackLabels,
        datasets: [
          {
            label: "Attack Count",
            data: Object.values(attackCounts),
            backgroundColor: backgroundColors,
            borderColor: "rgba(255, 99, 132, 1)",
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
      },
    });
  }
</script>

<style>
  .image-container {
    display: flex;
    align-items: center; /* vertically centers the content */
    gap: 12px; /* space between image and text */
  }

  img {
    width: 64px;  /* adjust image size as needed */
    height: 64px;
    object-fit: contain;
  }
</style>

<!--  To dashboard της εφαρμογής -->
<div class="dashboard">
  <!-- Top row -->
  <div class="top-row row">
    <div class="network" bind:this={networkContainer}></div>
    <div class="right-panel-column">
      <div class="panel text-panel">
        <div class="image-container">
          <img src="/images/inspector_small.png" alt="Inspector searching for evidence" />
              <h2> Intrusion Detection System (IDS-DL)</h2>
          
        </div>
      </div>
      <div class="panel kpi-panel">
        <h3>KPIs</h3>
        <div class="kpi-container">
          <div class="kpi-tile kpi-green">
            <h4>Normal Traffic</h4>
            <p>{normalTraffic}</p>
          </div>
          <div class="kpi-tile kpi-orange">
            <h4>Low Conf Attacks (*)</h4>
            <p>{lowConfidenceAttacks}</p>
          </div>
          <div class="kpi-tile kpi-red">
            <h4>Total Attacks</h4>
            <p>{totalAttacks}</p>
          </div>
        </div>
      </div>

      <div class="panel top-sources-panel">
        <h3>Top 10 Source IPs</h3>
        <canvas bind:this={topSourcesCanvas}></canvas>
      </div>
    </div>

  </div>

  <!-- Bottom row -->
  <div class="bottom-row row">

    <div class="panel recent-alerts">
      <h3>Recent Alerts</h3>
      <label for="confnum">Confidence (between 0 and 1):</label>
      <input
        type="number"
        id="confnum"
        name="confnum"
        min="0"
        max="1"
        step="0.01"
        bind:value={confidenceThreshold}
      />

      <ul>
        {#each attackTable.filter((a) => a.type !== "Normal").slice(0, 5) as a}
          <li>{a.time} - {a.type} - {a.src} → {a.dst}</li>
        {/each}
      </ul>
    </div>

    <div class="panel live-feed">
      <h3>Live Attack Feed</h3>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Type</th>
              <th>Source IP</th>
              <th>Destination IP</th>
              <th>Confidence (%)</th>
            </tr>
          </thead>
          <tbody>
            {#each attackTable as attack}
              <tr>
                <td>{attack.time}</td>
                <td>{attack.type}</td>
                <td>{attack.src}</td>
                <td>{attack.dst}</td>
                <td>{attack.confidence}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>

    <div class="panel full-chart">
      <h3>Attack Category Distribution</h3>
      <canvas bind:this={chartCanvas}></canvas>
    </div>
  </div>

</div>
