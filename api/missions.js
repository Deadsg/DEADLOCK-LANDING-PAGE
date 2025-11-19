//api/missions.js
export default function handler(req, res) {
  // Example missions data
  const missions = [
    { id: 1, title: "Secure Data Haven", status: "active" },
    { id: 2, title: "Intercept Rogue Agent", status: "pending" },
    { id: 3, title: "Decrypt Mainframe Logs", status: "completed" },
  ];

  res.status(200).json({ missions });
}
