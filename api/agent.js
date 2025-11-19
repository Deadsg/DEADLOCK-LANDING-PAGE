//api/agents.js
export default function handler(req, res) {
  // Example agent roster
  const agents = [
    { id: "A1", name: "Cipher", role: "Hacker" },
    { id: "A2", name: "Specter", role: "Infiltrator" },
    { id: "A3", name: "Oracle", role: "Analyst" },
  ];

  res.status(200).json({ agents });
}
