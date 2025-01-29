import React, { useEffect, useState } from "react";
import Swal from "sweetalert2";

const LogTable = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  // GET ALL LOGS
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/logs/");
        if (!response.ok) {
          throw new Error("Failed to fetch logs");
        }

        const data = await response.json();
        setLogs(data);

        Swal.fire({
          icon: "success",
          title: "Sikeres betöltés!",
          text: `Összesen ${data.length} log adatot töltöttünk be.`,
          timer: 1500,
          showConfirmButton: false,
        });

      } catch (err) {
        Swal.fire({
          icon: "error",
          title: "Hiba történt!",
          text: err.message,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, []);

  // OPENAI ANALYZE
  const analyzeLogs = async () => {
    try {
      setAnalyzing(true);

      Swal.fire({
        title: "AI Analizáció...",
        text: "Az AI éppen elemzi a logokat, kérlek várj.",
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        },
      });

      const response = await fetch("http://localhost:5000/api/ai/analyze");
      if (!response.ok) throw new Error("AI analysis failed");

      const data = await response.json();
      Swal.fire({
        icon: "info",
        title: "AI Elemzés",
        html: `<p style="text-align:left">${data.analysis.replace(/\n/g, "<br>")}</p>`, 
        width: 600,
      });

    } catch (err) {
      Swal.fire({
        icon: "error",
        title: "Hiba történt",
        text: err.message,
      });
    } finally {
      setAnalyzing(false);
    }
  };

  // LOADING
  if (loading) {
    Swal.fire({
      title: "Betöltés...",
      text: "Kérlek várj, amíg a logok betöltődnek.",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });
    return null;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center" }}>
      <h1>Log Viewer</h1>
      <button onClick={analyzeLogs} disabled={analyzing} style={{ marginBottom: "30px" }}>
        {analyzing ? "AI Elemzés folyamatban..." : "AI Analyze"}
      </button>
      <table border="1" style={{ width: "80%", textAlign: "center" }}>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Log Level</th>
            <th>Message</th>
            <th>Source IP</th>
            <th>Endpoint</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id}>
              <td>{log.timestamp}</td>
              <td>{log.log_level}</td>
              <td>{log.message}</td>
              <td>{log.source_ip || "N/A"}</td>
              <td>{log.endpoint || "N/A"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LogTable;
