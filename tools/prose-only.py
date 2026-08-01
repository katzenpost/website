import io, re, sys
lines = io.open(sys.argv[1], encoding='utf-8').read().split('\n')
out = list(lines)
i = 0
if lines and lines[0].strip() == '---':
    for j in range(1, len(lines)):
        if lines[j].strip() == '---':
            i = j + 1
            break
    for k in range(i):
        out[k] = ''
infence = False
for k in range(i, len(out)):
    if out[k].startswith('```'):
        infence = not infence
        out[k] = ''
        continue
    if infence:
        out[k] = ''
    else:
        # Empty rule anchors are navigation markup, not sentence words.
        out[k] = re.sub(r'<span id="r-\d+-\d+"></span>',
                        lambda match: ' ' * len(match[0]), out[k])
io.open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(out))
