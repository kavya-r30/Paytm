import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const css = readFileSync(fileURLToPath(new URL('../app/tokens.css', import.meta.url)), 'utf-8');

describe('generated tokens.css', () => {
  it('exposes design-language colours, radii, type and the 4:3 device canvas', () => {
    expect(css).toContain('--color-midnight: #002E6E;');
    expect(css).toContain('--color-paytm-blue: #00BAF2;');
    expect(css).toContain('--radius-card: 24px;');
    expect(css).toContain('--text-amount: 56px;');
    expect(css).toContain('--text-amount--font-weight: 800;');
    expect(css).toContain('--device-width: 960px;');
    expect(css).toContain('--device-height: 720px;');
  });
});
