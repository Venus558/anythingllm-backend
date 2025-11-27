
const { extractAndUpdateMemory } = require("../models/extractMemory");

module.exports = function debugMemoryEndpoints(apiRouter) {
  // Register route
  apiRouter.post("/debug/memory", async (req, res) => {
    try {
      const { workspaceId, testMessage } = req.body;

      if (!workspaceId || !testMessage) {
        return res.status(400).json({
          error: "workspaceId and testMessage required"
        });
      }

      const recentMessages = [
        { role: "user", content: testMessage }
      ];

      const result = await extractAndUpdateMemory(workspaceId, recentMessages);

      return res.json({
        success: true,
        patch: result
      });

    } catch (err) {
      console.error("[DebugMemory ERROR]", err);
      res.status(500).json({ error: err.message });
    }
  });
};
