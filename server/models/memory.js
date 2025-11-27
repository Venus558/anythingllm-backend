import { PrismaClient } from "@prisma/client";
const prisma = new PrismaClient();

function mergeList(oldList, newList) {
  if (!Array.isArray(oldList)) oldList = [];
  if (!Array.isArray(newList)) newList = [newList]; // normalize single string

  const merged = new Set(oldList);

  for (const item of newList) {
    if (typeof item === "string" && item.trim().length > 0) {
      merged.add(item.trim());
    }
  }

  return Array.from(merged);
}

// explicit removals: { remove: ["anime"] }
function applyRemovals(oldList, removals) {
  if (!Array.isArray(oldList)) return [];
  if (!Array.isArray(removals)) removals = [removals];

  return oldList.filter((item) => !removals.includes(item));
}

function trackHistory(memory, category, key, oldVal) {
  if (!oldVal) return;

  if (!memory.history) memory.history = {};
  if (!memory.history[category]) memory.history[category] = {};
  if (!Array.isArray(memory.history[category][key])) {
    memory.history[category][key] = [];
  }

  memory.history[category][key].push(oldVal);
}

function mergeMemory(oldMemory, patch) {
  const merged = JSON.parse(JSON.stringify(oldMemory)); // deep clone

  for (const category of ["profile", "preferences", "facts", "goals"]) {
    if (!patch[category]) continue;

    if (!merged[category]) merged[category] = {};

    for (const key in patch[category]) {
      const newVal = patch[category][key];
      const oldVal = merged[category][key];

      // ARRAY MERGE (append, do not replace)
      if (Array.isArray(newVal)) {
        merged[category][key] = mergeList(oldVal, newVal);
        continue;
      }

      // explicit removal
      if (newVal && typeof newVal === "object" && newVal.remove) {
        merged[category][key] = applyRemovals(oldVal, newVal.remove);
        continue;
      }

      // SINGLE VALUE overwrite → but track history
      if (oldVal && oldVal !== newVal) {
        trackHistory(merged, category, key, oldVal);
      }

      merged[category][key] = newVal;
    }
  }

  return merged;
}

export const Memory = {
  async get(workspaceId) {
    let record = await prisma.workspace_memory.findUnique({
      where: { workspace_id: workspaceId },
    });

    if (!record) {
      record = await prisma.workspace_memory.create({
        data: {
          workspace_id: workspaceId,
          memory_json: {}
        }
      });
    }

    return record.memory_json || {};
  },

  async update(workspaceId, patch) {
    const existing = await this.get(workspaceId);

    const merged = mergeMemory(existing, patch);  // <--- SMART MERGE HERE

    return await prisma.workspace_memory.update({
      where: { workspace_id: workspaceId },
      data: { memory_json: merged },
    });
  }
};
