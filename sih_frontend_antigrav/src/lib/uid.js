// src/lib/uid.js
// Client-side id for chat turns. Shared by ChatView and the shell that owns
// the transcript (crypto.randomUUID needs a secure context, hence the
// fallback for plain-HTTP dev hosts).
export function uid() {
  return crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
}
