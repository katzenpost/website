"""Check directory tables, requirement anchors, and diagram descriptions."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
text = (ROOT / 'content/en/docs/specs/dirauth.md').read_text()
lines = text.splitlines()
appendices = re.findall(r'^## Appendix ([A-H])\. ([^\n{]+)', text, re.M)
if [letter for letter, _ in appendices] != list('ABCDEFGH') or appendices[-1][1].strip() != 'Conformance and vectors':
    raise SystemExit('Appendices must run from A to H with conformance last')
if '| Key | Value | Explanation |' in text.split('## Appendix A.', 1)[0]:
    raise SystemExit('Reference and requirement tables belong in the appendices')
main = text.split('## Appendix A.', 1)[0]
order = ['network-and-consensus', 'epochs-and-timing', 'signed-data-formats',
         'the-voting-round', 'receiver-states-and-retention',
         'connections-and-messages', '227-security-considerations']
if any('{#' + name + '}' not in main for name in order):
    raise SystemExit('The main reading order needs all seven sections')
positions = [main.index('{#' + name + '}') for name in order]
if positions != sorted(positions):
    raise SystemExit('Define membership, epochs, and objects before the voting round')
algorithms = text.split('## Appendix F.', 1)[1].split('## Appendix G.', 1)[0]
if any('{#' + name + '}' not in algorithms for name in ['2181-the-topology-draw', 'layer-assignment']):
    raise SystemExit('Detailed topology algorithms belong in Appendix F')
table_count = 0
for index, line in enumerate(lines[:-1]):
    if not re.fullmatch(r'\|(?:\s*:?-+:?\s*\|)+', lines[index + 1]):
        continue
    cells = lambda row: [cell.strip() for cell in re.split(r'(?<!\\)\|', row)[1:-1]]
    if cells(line) != ['Key', 'Value', 'Explanation']:
        raise SystemExit(f'Table at line {index + 1} must use Key, Value, Explanation')
    cursor = index + 2
    while cursor < len(lines) and lines[cursor].startswith('|'):
        if len(cells(lines[cursor])) != 3:
            raise SystemExit(f'Table row at line {cursor + 1} must have three cells')
        cursor += 1
    table_count += 1
ids = re.findall(r'^\| (R-\d+-\d+) \|', text, re.M)
for row in re.findall(r'^\| R-\d+-\d+ \|.*$', text, re.M):
    if not re.search(r'\b(MUST|SHOULD|MAY)\b', row):
        raise SystemExit('Requirement lacks an explicit RFC 2119 term: ' + row.split('|')[1].strip())
prose = re.sub(r'^```[^\n]*\n.*?^```', '', text, flags=re.M | re.S)
if re.search(r'\[[^\]\n]*,[^\]\n]*\)', prose):
    raise SystemExit('Write interval boundaries in words instead of bracket notation')
if re.search(r'\b(must|shall|should)\b', prose):
    raise SystemExit('Requirement words must use upper case outside code blocks')
anchors = re.findall(r'<span id="(r-\d+-\d+)"></span>', text)
if sorted(anchors) != sorted(name.lower() for name in ids):
    raise SystemExit('Rule anchors differ from the rule definitions')
diagrams = re.findall(r'```mermaid\n(.*?)```', text, re.S)
roles = json.loads((ROOT / 'data/dirauth_roles.json').read_text())
for role in roles.values():
    for icon in role['icons']:
        if not (ROOT / f'static/docs/specs/dirauth/icons/{icon}.svg').is_file():
            raise SystemExit(f'Missing role icon: {icon}')
for number, definition in enumerate(diagrams, 1):
    if not re.search(r'^\s*accTitle:\s*\S', definition, re.M) or not re.search(r'^\s*accDescr:\s*\S', definition, re.M):
        raise SystemExit(f'Diagram {number} lacks an accessible title or description')
    panel = re.search(r'^\s*%% panel: ([a-z-]+)\s*$', definition, re.M)
    if not panel or panel[1] not in roles:
        raise SystemExit(f'Diagram {number} needs a known panel role')
    if definition.startswith('sequenceDiagram'):
        actors = dict(re.findall(r'([A-Za-z][A-Za-z0-9]*)=([a-z-]+)', definition))
        participants = set(re.findall(r'^\s*participant (\w+)\b', definition, re.M))
        if set(actors) != participants or any(role not in roles for role in actors.values()):
            raise SystemExit(f'Diagram {number} must identify every participant role')
print(f'{table_count} tables, {len(ids)} requirement anchors, and {len(diagrams)} accessible protocol diagrams agree')
