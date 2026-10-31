// GET /v1/stream (I5): one SSE connection per surface. EventSource cannot send a bearer header, so this
// reads the stream with fetch. `view.invalidate` events name the views to refetch.

export type SseMessage = { event: string; id: string | null; data: string };

/** Incremental SSE parser: feed text chunks, get complete messages; keeps the unfinished tail. */
export class SseParser {
  private buffer = '';

  feed(chunk: string): SseMessage[] {
    this.buffer += chunk.replace(/\r\n/g, '\n');
    const out: SseMessage[] = [];
    let idx: number;
    while ((idx = this.buffer.indexOf('\n\n')) >= 0) {
      const block = this.buffer.slice(0, idx);
      this.buffer = this.buffer.slice(idx + 2);
      let event = 'message';
      let id: string | null = null;
      const data: string[] = [];
      for (const line of block.split('\n')) {
        if (!line || line.startsWith(':')) continue;
        const colon = line.indexOf(':');
        const field = colon < 0 ? line : line.slice(0, colon);
        const value = colon < 0 ? '' : line.slice(colon + 1).replace(/^ /, '');
        if (field === 'event') event = value;
        else if (field === 'id') id = value;
        else if (field === 'data') data.push(value);
      }
      if (data.length) out.push({ event, id, data: data.join('\n') });
    }
    return out;
  }
}

/** The views named by a view.invalidate event, tolerant of either the event or its payload as data. */
export function invalidatedViews(data: unknown): string[] {
  if (typeof data !== 'object' || data === null) return [];
  const payload = (data as { payload?: { views?: unknown } }).payload ?? data;
  const list = (payload as { views?: unknown }).views;
  return Array.isArray(list) ? list.filter((v): v is string => typeof v === 'string') : [];
}

/** Topic prefixes the stage and invalidation fallbacks understand: "bill.paid" → "bill". */
export function topicDomain(topic: string): string {
  return topic.split('.')[0] ?? topic;
}
