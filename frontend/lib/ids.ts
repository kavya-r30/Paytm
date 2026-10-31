// Client-minted references (payment refs, instruction refs) in the contract's PrefixedId shape:
// `<prefix>_<ULID>` (48-bit ms time + 80 random bits, Crockford base32), like the backend's new_id.
const CROCKFORD = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';

export function newId(prefix: string): string {
  let time = Date.now();
  let head = '';
  for (let i = 0; i < 10; i++) {
    head = CROCKFORD[time % 32] + head;
    time = Math.floor(time / 32);
  }
  const random = crypto.getRandomValues(new Uint8Array(16));
  const tail = Array.from(random, (b) => CROCKFORD[b % 32]).join('');
  return `${prefix}_${head}${tail}`;
}
