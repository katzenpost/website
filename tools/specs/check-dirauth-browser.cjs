const fs = require('node:fs');
const assert = require('node:assert/strict');

const source = fs.readFileSync('content/en/docs/specs/dirauth.md', 'utf8');
const titles = [...source.matchAll(/^\s*accTitle: (.+)$/gm)].map(match => match[1]);
const roleMap = JSON.parse(fs.readFileSync('data/dirauth_roles.json', 'utf8'));
const version = fs.readFileSync('hugo.yaml', 'utf8').match(/mermaid:\s*\n\s+version:\s*"([\d.]+)"/)[1];
const panelCount = [...source.matchAll(/^\s*%% panel:/gm)].length;
const exampleCount = [...source.matchAll(/{{< protocol-example /g)].length;
const nodeCount = [...source.matchAll(/class='node-badge /g)].length;
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

async function check() {
  let tabs;
  for (let attempt = 0; attempt < 100; attempt++) {
    try { tabs = await (await fetch('http://127.0.0.1:9222/json/list')).json(); break; }
    catch { await delay(200); }
  }
  assert(tabs, 'Chromium did not start');
  const ws = new WebSocket(tabs.find(tab => tab.type === 'page').webSocketDebuggerUrl);
  await new Promise(resolve => ws.addEventListener('open', resolve, {once: true}));
  let id = 0;
  const pending = new Map();
  const errors = [];
  ws.addEventListener('message', event => {
    const result = JSON.parse(event.data);
    if (result.id) {
      pending.get(result.id)(result);
      pending.delete(result.id);
    }
    if (result.method === 'Runtime.exceptionThrown') errors.push(result.params.exceptionDetails.text);
  });
  const call = (method, params = {}) => new Promise((resolve, reject) => {
    const key = ++id;
    pending.set(key, result => result.error ? reject(Error(JSON.stringify(result.error))) : resolve(result.result));
    ws.send(JSON.stringify({id: key, method, params}));
  });
  const read = async expression => {
    const result = await call('Runtime.evaluate', {expression, awaitPromise: true, returnByValue: true});
    assert(!result.exceptionDetails, JSON.stringify(result.exceptionDetails));
    return result.result.value;
  };
  const size = (width, height) => call('Emulation.setDeviceMetricsOverride', {width, height, deviceScaleFactor: 1, mobile: width < 600});
  async function ready() {
    for (let attempt = 0; attempt < 200; attempt++) {
      if (await read(`document.querySelectorAll('.mermaid[data-processed="true"] > svg > title').length === ${titles.length}`)) {
        await read('document.fonts.ready');
        await read('new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))');
        return;
      }
      await delay(100);
    }
    throw Error(`Expected ${titles.length} complete diagrams. Browser errors: ${errors.join(', ')}`);
  }
  async function inspect() {
    return read(`(async () => {
      const failures = [];
      const require = (condition, message) => {if (!condition) failures.push(message);};
      const roles = ${JSON.stringify(roleMap)};
      const diagrams = [...document.querySelectorAll('.diagram-scroll')];
      const luminance = color => {
        const values = color.match(/[0-9.]+/g)?.slice(0,3).map(Number);
        if (!values || values.length !== 3) return null;
        return values.map(value => {const s=value/255;return s<=0.04045?s/12.92:((s+0.055)/1.055)**2.4;}).reduce((sum,value,index)=>sum+value*[0.2126,0.7152,0.0722][index],0);
      };
      const contrast = (first,second) => {const a=luminance(first),b=luminance(second);return a===null||b===null?0:(Math.max(a,b)+0.05)/(Math.min(a,b)+0.05);};
      require(contrast('rgb(0,0,0)','rgb(255,255,255)') > 20.99, 'Contrast calculation failed');
      const outside = (inner, outer, margin = 1) => inner.left < outer.left-margin || inner.right > outer.right+margin || inner.top < outer.top-margin || inner.bottom > outer.bottom+margin;
      await Promise.all([...document.querySelectorAll('.protocol-diagram img')].map(image => image.decode()));
      const icons = [...document.querySelectorAll('.node-badge')];
      await Promise.all(icons.map(async icon => {
        const style = getComputedStyle(icon, '::before');
        const image = new Image(); image.src = style.backgroundImage.slice(5, -2); await image.decode();
        require(parseFloat(style.width) >= 32, 'Node role icon is too small');
        require(!/^\d+$/.test(icon.textContent.trim()), 'Configured node needs its Namenlos name');
        require(icon.scrollWidth <= icon.clientWidth+1, 'Configured node name is clipped: '+icon.textContent);
      }));
      require(icons.length === ${nodeCount}, 'Configured node count changed');
      require(document.querySelectorAll('.diagram-heading').length === ${panelCount+exampleCount}, 'Diagram or formula header is missing');
      for (const example of document.querySelectorAll('.protocol-example')) {
        require(example.firstElementChild?.classList.contains('diagram-heading') && example.querySelector('pre'), 'Formula needs a header and a code block');
        for (const child of example.querySelectorAll('.highlight,pre')) {
          const style = getComputedStyle(child);
          require(parseFloat(style.marginTop) === 0 && parseFloat(style.borderTopWidth) === 0, 'Formula has an extra inner frame');
        }
      }
      for (const heading of document.querySelectorAll('.diagram-heading')) {
        require(heading.querySelector('img') && heading.innerText.trim(), 'Panel needs an icon and text');
        require(getComputedStyle(heading).textAlign === 'left' && getComputedStyle(heading.querySelector('.diagram-title')).justifyContent === 'flex-start', 'Figure heading is not left aligned');
        require(getComputedStyle(heading.querySelector('.diagram-icons')).alignItems === 'center', 'Header icons are not vertically centered');
      }
      for (const code of document.querySelectorAll('.protocol-spec code')) {
        if (code.closest('pre')) continue;
        const style = getComputedStyle(code), parent = getComputedStyle(code.parentElement);
        require(style.color === parent.color && style.fontSize === parent.fontSize && style.fontFamily === parent.fontFamily, 'Inconsistent inline value formatting: '+code.textContent);
        require(style.backgroundColor === 'rgba(0, 0, 0, 0)' && parseFloat(style.padding) === 0, 'Inline value has a capsule background: '+code.textContent);
      }
      require(document.documentElement.scrollWidth <= innerWidth, 'Page overflows the viewport');
      for (const td of document.querySelectorAll('.td-content td')) require(td.scrollWidth <= td.clientWidth+1, 'Table cell overflows: '+td.innerText.slice(0,50));
      for (const link of document.querySelectorAll('a[href*="#r-"]')) require(link.getClientRects().length === 1, 'Requirement link wraps: '+link.textContent);
      const report = [];
      for (const [index, diagram] of diagrams.entries()) {
        const svg = diagram.querySelector('.mermaid > svg');
        require(!!svg, 'Missing SVG '+index);
        if (!svg) continue;
        const title = svg.querySelector('title')?.textContent;
        const figure = diagram.closest('figure'), heading = figure.querySelector('.diagram-heading');
        require(figure.firstElementChild === heading && heading.querySelector('.diagram-title').innerText.trim() === title, 'Inconsistent figure heading: '+title);
        require(heading.textContent.trim() === title, 'Extra text in figure header: '+title);
        require(contrast(getComputedStyle(heading).color,getComputedStyle(heading).backgroundColor) >= 4.5, 'Caption contrast is too low: '+title);
        require(!!svg.querySelector('desc')?.textContent, 'Description missing: '+title);
        const bounds = svg.getBoundingClientRect();
        const frame = diagram.getBoundingClientRect();
        if (title === 'Protocol encapsulation' || title === 'Direct consensus reply encoding') {
          require(diagram.scrollWidth <= diagram.clientWidth+1, 'Encapsulation layers need horizontal scrolling: '+title+' at '+innerWidth);
        }
        if (title === 'Protocol encapsulation') {
          const image = diagram.querySelector('image[href$="/sphinx-layers.svg"]');
          require(!!image, 'Sphinx layers image is missing');
          if (image) {
            const url = image.getAttribute('href');
            const decoded = new Image(); decoded.src = url; await decoded.decode();
            require(image.getBoundingClientRect().width >= 243, 'Sphinx layers image is too small');
            const source = await (await fetch(url)).text();
            const layers = new DOMParser().parseFromString(source,'image/svg+xml');
            require(!layers.querySelector('parsererror'), 'Invalid Sphinx layers SVG');
            const rings = [...layers.querySelectorAll('#sphinx-layers > circle')];
            require(rings.length === 6 && rings.every((ring,index) => !index || +ring.getAttribute('r') < +rings[index-1].getAttribute('r')), 'Sphinx layers must show five concentric hop layers around data');
          }
        }
        if (title === 'Direct consensus reply encoding') {
          const layers = svg.querySelectorAll('.node.documentLayer,.node.certificateLayer,.node.commandLayer,.node.noiseLayer,.node.tcpLayer,.node.ipLayer');
          require(layers.length === 6 && new Set([...layers].map(node => getComputedStyle(node.querySelector('rect,polygon,path')).fill)).size === 6, 'Encapsulation layers need six distinct colors');
        }
        if (bounds.width+16 <= diagram.clientWidth) require(Math.abs(bounds.left+bounds.right-frame.left-frame.right) < 2, 'Diagram is not centered: '+title);
        require(!outside(bounds, diagram.querySelector('pre').getBoundingClientRect()), 'SVG escapes background: '+title);
        const shapes = [...svg.querySelectorAll('rect,circle,polygon,ellipse,text,image,foreignObject')].filter(shape => !shape.closest('defs,marker') && shape.getBoundingClientRect().width > 0);
        for (const shape of shapes) {
          require(!outside(shape.getBoundingClientRect(), bounds), 'Clipped '+shape.tagName+' in '+title);
          require(getComputedStyle(shape).filter === 'none', 'Offset shadow in '+title);
        }
        for (const shape of svg.querySelectorAll('.node rect,.node polygon,.node circle,.node path,.cluster rect,rect.actor,rect.note,rect.rect,.labelBox')) {
          require(Math.abs(parseFloat(getComputedStyle(shape).strokeWidth)-1.25) < 0.01, 'Uneven '+shape.tagName+' stroke in '+title);
          const style = getComputedStyle(shape);
          require(contrast(style.stroke,getComputedStyle(figure).backgroundColor) >= 3, 'Shape contrast is too low: '+title);
          if (style.fill !== 'none' && style.stroke !== style.fill) require(contrast(style.stroke,style.fill) >= 3, 'Box outline contrast is too low: '+title);
        }
        for (const node of svg.querySelectorAll('.node')) {
          const label = node.querySelector('.nodeLabel'), shape = node.querySelector('rect,polygon,circle,path');
          if (label && shape) require(contrast(getComputedStyle(label).color,getComputedStyle(shape).fill) >= 4.5, 'Node text contrast is too low: '+title);
        }
        for (const label of svg.querySelectorAll('foreignObject')) require(label.scrollWidth <= label.clientWidth+1, 'Clipped HTML label in '+title);
        const mapping = JSON.parse(diagram.closest('figure').dataset.actorRoles || '{}');
        const actors = [...svg.querySelectorAll('rect.actor[name]')];
        const actorIcons = [...svg.querySelectorAll('image.protocol-actor-icon')];
        let expectedIcons = 0;
        for (const actor of actors) {
          const name = actor.getAttribute('name');
          const role = roles[mapping[name]];
          require(role && actor.dataset.protocolRole === mapping[name], 'Actor role missing in '+title);
          if (!role) continue;
          expectedIcons += role.icons.length;
          const box = actor.getBoundingClientRect();
          for (const iconName of role.icons) {
            require(actorIcons.some(icon => icon.dataset.actor === name && icon.getAttribute('href').endsWith('/'+iconName+'.svg') && !outside(icon.getBoundingClientRect(), box)), 'Role icon missing from actor '+name+' in '+title);
          }
        }
        require(actorIcons.length === expectedIcons, 'Extra actor icons in '+title);
        await Promise.all(actorIcons.map(async icon => {const image = new Image(); image.src = icon.getAttribute('href'); await image.decode();}));
        require(diagram.closest('figure').querySelector('img,image,.node-badge'), 'Diagram needs a role or domain icon: '+title);
        report.push({title, width:diagram.clientWidth, contentWidth:diagram.scrollWidth, height:diagram.getBoundingClientRect().height, actors:actors.length, actorIcons:actorIcons.length});
      }
      const rendererURLs = performance.getEntriesByType('resource').map(resource => resource.name).filter(url => url.includes('mermaid@'));
      require(rendererURLs.length && rendererURLs.every(url => url.includes('mermaid@${version}/')), 'Mermaid version differs from hugo.yaml');
      const clock = diagrams.find(diagram => diagram.querySelector('title')?.textContent === 'Repeating epoch cycle')?.querySelector('svg');
      require(clock && !clock.querySelector('.node.directory'), 'Network clock uses authority colors');
      return {width:innerWidth, pageWidth:document.documentElement.scrollWidth, failures, diagrams:report};
    })()`);
  }
  function validate(report) {
    assert.deepEqual(report.diagrams.map(diagram => diagram.title), titles, 'Diagram titles or order changed');
    assert.deepEqual(report.failures, [], JSON.stringify(report.failures, null, 2));
    assert.deepEqual(errors, [], 'Browser reported an uncaught error');
  }
  await call('Page.enable');
  await call('Runtime.enable');
  fs.mkdirSync('/output', {recursive:true});
  const reports = [];
  for (const [device, width, height] of [['desktop',1440,1100], ['phone',390,844], ['small-phone',320,700], ['grayscale',1440,1100]]) {
    await call('Emulation.setEmulatedVisionDeficiency', {type:device === 'grayscale' ? 'achromatopsia' : 'none'});
    await size(width,height);
    await call('Page.navigate', {url:'http://127.0.0.1:1313/docs/specs/dirauth/'});
    await ready();
    const report = await inspect(); validate(report); reports.push({device,...report});
    const folder = '/output/'+device;
    fs.rmSync(folder, {recursive:true,force:true});
    fs.mkdirSync(folder, {recursive:true});
    for (const [index, diagram] of report.diagrams.entries()) {
      await size(width, Math.max(height,Math.ceil(diagram.height)+270));
      await read(`document.querySelectorAll('.protocol-diagram')[${index}].scrollIntoView({block:'start',behavior:'instant'})`);
      await read('scrollBy({top:-120,behavior:"instant"})');
      const last = Math.max(0, diagram.contentWidth-diagram.width);
      const offsets = [];
      for (let left = 0; left < last; left += Math.max(1,diagram.width-32)) offsets.push(left);
      offsets.push(last);
      for (const [tile, left] of offsets.entries()) {
        await read(`document.querySelectorAll('.diagram-scroll')[${index}].scrollLeft = ${left}`);
        await read('new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))');
        const shot = await call('Page.captureScreenshot', {format:'png',captureBeyondViewport:false});
        const painted = await read(`(async () => {
          const image = new Image(); image.src = 'data:image/png;base64,${shot.data}'; await image.decode();
          const canvas = document.createElement('canvas'); canvas.width=image.width; canvas.height=image.height;
          const context = canvas.getContext('2d'); context.drawImage(image,0,0);
          const diagram = document.querySelectorAll('.diagram-scroll')[${index}];
          const bounds = diagram.querySelector('svg').getBoundingClientRect(), frame = diagram.getBoundingClientRect();
          const x = Math.ceil(Math.max(0,bounds.left,frame.left)), y = Math.ceil(Math.max(0,bounds.top,frame.top));
          const width = Math.floor(Math.min(innerWidth,bounds.right,frame.right))-x;
          const height = Math.floor(Math.min(innerHeight,bounds.bottom,frame.bottom))-y;
          if (width <= 0 || height <= 0) return 0;
          const pixels = context.getImageData(x,y,width,height).data;
          let count = 0;
          for (let i=0;i<pixels.length;i+=4) if (pixels[i]>100 && pixels[i+1]>100 && pixels[i+2]>100) count++;
          return count;
        })()`);
        assert(painted > 20, `Blank screenshot: ${device}, diagram ${index+1}, tile ${tile+1}`);
        const suffix = left && left === last ? '-end' : tile ? '-part-'+(tile+1) : '';
        fs.writeFileSync(folder+'/diagram-'+String(index+1).padStart(2,'0')+suffix+'.png', Buffer.from(shot.data,'base64'));
      }
    }
    await size(width,height);
    for (const section of ['receiver-reencoding','go-reference-implementation']) {
      await read(`document.getElementById('${section}').scrollIntoView({block:'start',behavior:'instant'})`);
      await read('scrollBy({top:-120,behavior:"instant"})');
      await read('new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))');
      const shot = await call('Page.captureScreenshot', {format:'png',captureBeyondViewport:false});
      fs.writeFileSync(folder+'/'+section+'.png',Buffer.from(shot.data,'base64'));
    }
  }
  await call('Emulation.setEmulatedVisionDeficiency', {type:'none'});
  for (const interval of [50,150,300]) {
    for (const width of [1210,1190,1210,1190,1210,390]) {await size(width,844);await delay(interval);}
    await ready();
    const report = await inspect(); validate(report);
    reports.push({resizeInterval:interval,...report});
  }
  fs.writeFileSync('/output/report.json',JSON.stringify({version,reports},null,2));
  console.log(`Browser checks pass: ${titles.length} diagrams at 1440, 390, and 320 pixels, plus grayscale. Titles, centering, contrast, and resize checks pass.`);
  await call('Browser.close'); ws.close();
}
check().catch(error => {console.error(error); process.exit(1);});
