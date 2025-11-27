const { Memory } = require("./memory");
const { XAiLLM } = require("../utils/AiProviders/xai");

async function extractAndUpdateMemory(workspaceId, recentMessages) {

  // Load current memory
  const currentMemory = await Memory.get(workspaceId);

  const extractionPrompt = `
You are a memory extraction engine.
Look at user messages and extract stable personal facts, preferences, and goals.
Only return JSON. Return null if nothing should be added.

Current Memory:
${JSON.stringify(currentMemory, null, 2)}

Recent Messages:
${JSON.stringify(recentMessages, null, 2)}

Return JSON with possible updates:
{
  "profile": {},
  "preferences": {},
  "facts": {},
  "goals": {},
  "summary": ""
}
`;

  const llm = new XAiLLM();

  const llmResponse = await llm.getChatCompletion(
    [
      { role: "system", content: "Extract memory in JSON ONLY." },
      { role: "user", content: extractionPrompt }
    ],
    { temperature: 0 }
  );

  if (!llmResponse || !llmResponse.textResponse) {
    return null;
  }

  let patch = null;
  try {
    patch = JSON.parse(llmResponse.textResponse);
  } catch (err) {
    return null;
  }

  if (!patch || typeof patch !== "object") {
    return null;
  }

  await Memory.update(workspaceId, patch);

  return patch;
}

module.exports = {
  extractAndUpdateMemory
};
