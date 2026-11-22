export const fold = word =>
  word.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();

export function wordForms(token) {
  const parts = fold(token).match(/[\p{L}\p{N}_]+/gu) ?? [];
  return parts.length < 2 ? parts : [...parts, parts.join("")];
}
