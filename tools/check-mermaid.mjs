import fs from 'fs';
import { JSDOM } from 'jsdom';
const dom = new JSDOM('<!doctype html><html><body></body></html>');
global.window = dom.window;
global.document = dom.window.document;
Object.defineProperty(global, "navigator", { value: dom.window.navigator, configurable: true });
global.Element = dom.window.Element;
global.Node = dom.window.Node;
global.DOMParser = dom.window.DOMParser;
global.HTMLElement = dom.window.HTMLElement;
global.SVGElement = dom.window.SVGElement;
global.Option = dom.window.Option;
const mermaid = (await import('mermaid')).default;
const src = fs.readFileSync(process.argv[2], 'utf8');
const blocks = [...src.matchAll(/```mermaid\n([\s\S]*?)```/g)].map(m => m[1]);
let bad = 0;
for (const [i, b] of blocks.entries()) {
  try {
    await mermaid.parse(b);
    console.log(`block ${i + 1} (${b.split('\n')[0]}): ok`);
  } catch (e) {
    bad++;
    console.log(`block ${i + 1} (${b.split('\n')[0]}): FAIL ${String(e.message || e).split('\n').slice(0,3).join(' / ')}`);
  }
}
console.log(`${blocks.length} blocks, ${bad} failed`);
process.exit(bad ? 1 : 0);
