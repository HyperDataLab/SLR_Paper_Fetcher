(function installAtomicAnalysis(root) {
  const button = document.getElementById('atomicExtractButton');
  const status = document.getElementById('atomicExtractionStatus');
  const results = document.getElementById('atomicResults');
  if (!button || !status || !results) return;

  const STANCE = ['Hedges', 'Boosters', 'Attitude Markers', 'Self Mention'];
  const ENGAGEMENT = ['Reader Pronouns', 'Directives', 'Questions', 'Knowledge Reference', 'Asides'];

  function node(tag, className, value) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (value !== undefined && value !== null) element.textContent = String(value);
    return element;
  }

  function renderHylandTable(stats, provenance) {
    const section = node('section', 'overflow-hidden rounded-lg border border-slate-200 bg-white');
    section.append(node('h4', 'border-b border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-800', 'Stance and Engagement statistics'));
    section.append(node('p', 'px-3 pt-2 text-xs leading-5 text-slate-500',
      `Denominator: ${stats.source_word_count || 0} prose words. ${provenance.hyland_scope_description || 'Scope details unavailable.'}`));
    const wrap = node('div', 'overflow-x-auto');
    const table = node('table', 'min-w-[760px] w-full border-collapse text-left text-sm');
    const head = node('thead', 'border-y-2 border-slate-800 text-slate-700');
    const labelRow = node('tr', 'text-xs text-slate-600');
    ['Stance', 'Items per 1,000 words', '% of total', 'Engagement', 'Items per 1,000 words', '% of total']
      .forEach(label => labelRow.append(node('th', 'px-3 py-2 font-medium', label)));
    head.append(labelRow);
    const body = node('tbody', 'divide-y divide-slate-200 text-slate-800');
    const stanceRows = (stats.stance || []).filter(row => !row.category.endsWith('Total'))
      .sort((a, b) => ['Hedges', 'Attitude Markers', 'Boosters', 'Self Mention'].indexOf(a.category) - ['Hedges', 'Attitude Markers', 'Boosters', 'Self Mention'].indexOf(b.category));
    const engagementRows = (stats.engagement || []).filter(row => !row.category.endsWith('Total'));
    const stanceTotal = (stats.stance || []).find(row => row.category === 'Stance Total');
    const engagementTotal = (stats.engagement || []).find(row => row.category === 'Engagement Total');
    const rowCount = Math.max(stanceRows.length, engagementRows.length);
    const appendMetric = (tr, row) => {
      tr.append(node('td', 'px-3 py-2', row?.category || ''));
      tr.append(node('td', 'px-3 py-2 text-right tabular-nums', row ? Number(row.per_1000_words || 0).toFixed(1) : ''));
      tr.append(node('td', 'px-3 py-2 text-right tabular-nums', row ? Number(row.percentage || 0).toFixed(1) : ''));
    };
    for (let index = 0; index < rowCount; index += 1) {
      const tr = node('tr');
      appendMetric(tr, stanceRows[index]);
      appendMetric(tr, engagementRows[index]);
      body.append(tr);
    }
    const totalRow = node('tr', 'border-t-2 border-slate-800 font-semibold');
    appendMetric(totalRow, stanceTotal ? {...stanceTotal, category: 'Totals'} : null);
    appendMetric(totalRow, engagementTotal ? {...engagementTotal, category: 'Totals'} : null);
    body.append(totalRow);
    table.append(head, body);
    wrap.append(table);
    section.append(wrap);
    return section;
  }

  function renderTags(annotations, categories) {
    const box = node('div', 'space-y-1');
    const rows = Array.isArray(annotations) ? annotations : [];
    if (!rows.length) return node('span', 'text-xs text-slate-400', '—');
    for (const category of categories) {
      const found = rows.filter(item => item.category === category);
      for (const item of found) {
        const line = node('p', 'text-xs leading-5');
        line.append(node('span', 'font-semibold text-slate-800', category + ': '));
        line.append(document.createTextNode(item.marker + ' — ' + item.function));
        box.append(line);
      }
    }
    return box;
  }

  function renderCandidateTable(candidates) {
    const section = node('section', 'overflow-hidden rounded-lg border border-slate-200 bg-white');
    section.append(node('h4', 'border-b border-slate-200 bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-800', 'Atomic Sentence candidates'));
    const wrap = node('div', 'overflow-x-auto');
    const table = node('table', 'min-w-[1100px] divide-y divide-slate-200 text-left text-xs');
    const head = node('thead', 'bg-white text-slate-500');
    const header = node('tr');
    ['AS ID', 'Atomic Sentence', 'Section', 'Word Count', 'Stance', 'Engagement', 'Evidence', 'Analysis Status'].forEach(label =>
      header.append(node('th', 'px-3 py-2 font-semibold', label)));
    head.append(header);
    const body = node('tbody', 'divide-y divide-slate-100 align-top text-slate-700');
    for (const item of candidates || []) {
      const tr = node('tr');
      tr.append(node('td', 'whitespace-nowrap px-3 py-3 font-mono text-[11px]', item.as_id));
      tr.append(node('td', 'max-w-sm whitespace-normal px-3 py-3 text-sm leading-5 text-slate-900', item.atomic_sentence));
      tr.append(node('td', 'max-w-40 whitespace-normal px-3 py-3', item.section));
      tr.append(node('td', 'px-3 py-3 text-center tabular-nums', item.word_count));
      const stance = node('td', 'max-w-xs whitespace-normal px-3 py-3');
      stance.append(renderTags(item.stance, STANCE));
      tr.append(stance);
      const engagement = node('td', 'max-w-xs whitespace-normal px-3 py-3');
      engagement.append(renderTags(item.engagement, ENGAGEMENT));
      tr.append(engagement);
      const evidence = node('td', 'max-w-md whitespace-normal px-3 py-3');
      for (const entry of item.evidence || []) {
        const quote = node('blockquote', 'mb-2 border-l-2 border-indigo-300 pl-2 text-slate-600', '“' + entry.quote + '”');
        evidence.append(quote);
      }
      if (!item.evidence?.length) evidence.append(node('span', 'text-rose-700', 'No source span validated'));
      tr.append(evidence);
      const state = item.status === 'READY_FOR_REVIEW' ? 'Ready for review' : item.status === 'NEEDS_CONTEXT' ? 'Needs context' : 'Candidate';
      const stateClass = item.status === 'READY_FOR_REVIEW' ? 'border-emerald-200 bg-emerald-50 text-emerald-800' :
        item.status === 'NEEDS_CONTEXT' ? 'border-amber-200 bg-amber-50 text-amber-900' : 'border-slate-200 bg-slate-50 text-slate-700';
      const statusCell = node('td', 'whitespace-nowrap px-3 py-3');
      statusCell.append(node('span', 'rounded-full border px-2 py-1 text-[11px] font-semibold ' + stateClass, state));
      if (item.support_precheck) {
        const check = item.support_precheck;
        const checkTone = check.status === 'SUPPORTED' ? 'text-emerald-800' : 'text-amber-800';
        statusCell.append(node('p', 'mt-2 text-[11px] font-semibold ' + checkTone, 'AI source check: ' + check.status));
        if (check.issue_note) statusCell.append(node('p', 'mt-1 max-w-48 whitespace-normal text-[11px] text-amber-800', check.issue_note));
      }
      if (item.context_note) statusCell.append(node('p', 'mt-2 max-w-48 whitespace-normal text-[11px] text-slate-600', item.context_note));
      for (const warning of item.warnings || []) statusCell.append(node('p', 'mt-2 max-w-48 whitespace-normal text-[11px] text-amber-800', warning));
      tr.append(statusCell);
      body.append(tr);
    }
    table.append(head, body);
    wrap.append(table);
    section.append(wrap);
    return section;
  }

  function renderHylandAnnotations(annotations) {
    const rows = Array.isArray(annotations) ? annotations : [];
    const details = node('details', 'rounded-lg border border-slate-200 bg-white');
    details.append(node('summary', 'cursor-pointer px-3 py-2 text-sm font-semibold text-slate-800',
      `Full-text Hyland annotations (${rows.length})`));
    if (!rows.length) {
      details.append(node('p', 'px-3 pb-3 text-xs text-slate-500', 'No contextual stance or engagement markers were classified in the included prose.'));
      return details;
    }
    const wrap = node('div', 'overflow-x-auto border-t border-slate-200');
    const table = node('table', 'min-w-[900px] divide-y divide-slate-200 text-left text-xs');
    const head = node('thead', 'bg-slate-50 text-slate-600');
    const header = node('tr');
    ['Section', 'Category', 'Marker', 'Function in context', 'Source sentence', 'Source offsets'].forEach(label =>
      header.append(node('th', 'px-3 py-2 font-semibold', label)));
    head.append(header);
    const body = node('tbody', 'divide-y divide-slate-100 align-top text-slate-700');
    for (const item of rows) {
      const tr = node('tr');
      tr.append(node('td', 'px-3 py-2', item.section));
      tr.append(node('td', 'whitespace-nowrap px-3 py-2 font-medium', item.category));
      tr.append(node('td', 'whitespace-nowrap px-3 py-2 font-mono text-indigo-800', item.marker));
      tr.append(node('td', 'max-w-xs whitespace-normal px-3 py-2', item.function));
      tr.append(node('td', 'max-w-lg whitespace-normal px-3 py-2', item.source_sentence));
      tr.append(node('td', 'whitespace-nowrap px-3 py-2 font-mono text-[11px]', `${item.start_offset}–${item.end_offset}`));
      body.append(tr);
    }
    table.append(head, body);
    wrap.append(table);
    details.append(wrap);
    return details;
  }

  function render(payload) {
    results.replaceChildren();
    const stats = payload.statistics || {};
    const intro = node('div', 'rounded-lg border border-indigo-100 bg-indigo-50 p-3 text-xs leading-5 text-indigo-950');
    intro.textContent = `${payload.candidates?.length || 0} Atomic Sentence candidates · ${stats.source_word_count || 0} in-scope prose words · ${payload.hyland_annotations?.length || 0} full-text Hyland marker annotations · ${payload.analysis?.verified_count || 0} verified`;
    results.append(intro);
    const exportButton = node('button', 'rounded-md border border-slate-300 bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50', 'Download analysis JSON');
    exportButton.type = 'button';
    exportButton.addEventListener('click', () => {
      const blob = new Blob([JSON.stringify(payload, null, 2)], {type: 'application/json'});
      const href = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = href;
      link.download = `atomic-analysis-${String(payload.paper_id || 'paper').replace(/[^A-Za-z0-9._-]+/g, '_')}.json`;
      link.click();
      URL.revokeObjectURL(href);
    });
    results.append(exportButton);
    const provenance = payload.analysis || {};
    results.append(renderHylandTable(stats, provenance), renderHylandAnnotations(payload.hyland_annotations), renderCandidateTable(payload.candidates || []));
    const details = node('details', 'rounded-lg border border-slate-200 bg-white p-3 text-xs text-slate-600');
    details.append(node('summary', 'cursor-pointer font-semibold text-slate-700', 'Analysis details'));
    const body = node('div', 'mt-2 space-y-1');
    body.append(node('p', '', `Provider: ${provenance.provider || 'unknown'} · Model(s): ${(provenance.models || []).join(', ') || 'unknown'}`));
    body.append(node('p', '', `Source SHA-256: ${payload.source_sha256 || 'unavailable'}`));
    body.append(node('p', '', `Prompt versions: ${provenance.atomic_prompt_version || ''} / ${provenance.validation_prompt_version || ''} / ${provenance.hyland_prompt_version || ''} · Word counter: ${provenance.tokenizer_version || ''}`));
    body.append(node('p', '', `Hyland scope (${provenance.hyland_scope_version || ''}): ${provenance.hyland_scope_description || 'not reported'}`));
    body.append(node('p', '', `Full-text sentences analyzed: ${provenance.sentences_analyzed || 0} · skipped without source offsets: ${provenance.sentences_skipped_missing_source_offsets || 0} · invalid AI annotations dropped: ${provenance.invalid_model_annotations_dropped || 0} (${JSON.stringify(provenance.invalid_model_annotations_by_reason || {})})`));
    body.append(node('p', '', `Excluded prose blocks: ${JSON.stringify(provenance.hyland_excluded_passages_by_reason || {})}`));
    body.append(node('p', '', `Items omitted because source evidence did not validate: ${provenance.candidates_discarded_for_invalid_source_evidence_or_schema || 0}`));
    details.append(body);
    results.append(details);
  }

  button.addEventListener('click', async () => {
    const paperId = typeof currentDoi === 'string' ? currentDoi : '';
    if (!paperId) {
      status.textContent = 'Open a saved paper before running Atomic analysis.';
      return;
    }
    button.disabled = true;
    button.textContent = 'Analyzing…';
    status.className = 'mt-3 rounded-md border border-blue-200 bg-blue-50 p-3 text-xs leading-5 text-blue-900';
    status.textContent = 'Extracting Atomic Sentences, checking source spans, then annotating Hyland stance and engagement…';
    results.replaceChildren();
    try {
      const response = await fetch('/api/atomic/analyze/' + encodeURIComponent(paperId), {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({provider: document.getElementById('provider')?.value || 'ollama'}),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || `Atomic analysis failed (HTTP ${response.status}).`);
      render(payload);
      status.className = 'mt-3 rounded-md border border-emerald-200 bg-emerald-50 p-3 text-xs leading-5 text-emerald-900';
      status.textContent = 'Analysis complete. Every displayed evidence quote and Hyland marker was checked against the source text; all output remains unverified and transient.';
    } catch (error) {
      status.className = 'mt-3 rounded-md border border-rose-200 bg-rose-50 p-3 text-xs leading-5 text-rose-900';
      status.textContent = error?.message || 'Atomic analysis failed.';
    } finally {
      button.disabled = false;
      button.textContent = 'Run Atomic analysis';
    }
  });
})(window);
