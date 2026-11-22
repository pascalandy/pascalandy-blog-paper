export const initials = "abcdefghijklmnopqrstuvwxyz0123456789";
export const fold = word =>
  word.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();

export function shardName(word) {
  return initials.includes(word[0]) ? word[0] : "other";
}

export function wordForms(token) {
  const surface = fold(token).match(/[\p{L}\p{N}_]+/gu) ?? [];
  if (!surface.length) return [];
  const separated = token
    .normalize("NFC")
    .replace(/(\p{Ll})(\p{Lu})/gu, "$1 $2")
    .replace(/(\p{Lu})(\p{Lu}\p{Ll})/gu, "$1 $2");
  const parts = fold(separated).match(/[\p{L}]+|[\p{N}]+/gu) ?? [];
  return [...surface, surface.join(""), ...parts];
}
