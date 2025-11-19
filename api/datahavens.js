// pages/api/datahavens.js
export default function handler(req, res) {
  // Example data havens
  const dataHavens = [
    { id: "DH1", location: "Berlin", capacity: "2TB" },
    { id: "DH2", location: "Tokyo", capacity: "5TB" },
    { id: "DH3", location: "New York", capacity: "10TB" },
  ];

  res.status(200).json({ dataHavens });
}
