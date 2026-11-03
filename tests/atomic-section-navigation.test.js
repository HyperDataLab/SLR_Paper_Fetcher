import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import '../static/js/atomic-section-navigation.js';

const { buildSectionMappings, uniqueSectionForPage } = globalThis.AtomicSectionNavigation;
const HASH_A = 'a'.repeat(64);
const HASH_B = 'b'.repeat(64);

function pinned(extra = {}) {
  return {
    currentPdfSha256: HASH_A,
    documentPdfSha256: HASH_A,
    validationStatus: 'verified_pinned_pdf',
    ...extra,
  };
}

test('maps unique validated section text to an exact PDF.js text location', () => {
  const section = { id: 'sec_1', text: 'The unique study result improved recall across the held-out cohort.' };
  const mappings = buildSectionMappings({
    sections: [section],
    pdfPages: [{ pageNumber: 1, text: 'Introduction. The unique study result improved recall across the held-out cohort. Discussion.' }],
    ...pinned(),
  });
  assert.deepEqual(mappings.get('sec_1'), {
    sectionId: 'sec_1', status: 'exact', page: 1,
    quote: section.text, reason: 'unique_section_text_match',
  });
});

test('uses the matched PDF page instead of a GROBID page hint or section index', () => {
  const mappings = buildSectionMappings({
    sections: [{ id: 'sec_1', page: 1, text: 'This unique passage is physically located on PDF page two.' }],
    pdfPages: [
      { pageNumber: 1, text: 'Unrelated first page.' },
      { pageNumber: 2, text: 'This unique passage is physically located on PDF page two.' },
    ],
    ...pinned(),
  });
  assert.equal(mappings.get('sec_1').status, 'exact');
  assert.equal(mappings.get('sec_1').page, 2);
});

test('uses page-only mapping when validated section text repeats on that page', () => {
  const mappings = buildSectionMappings({
    sections: [{ id: 'sec_1', text: 'Repeated statement appears in this section.' }],
    pdfPages: [{ pageNumber: 2, text: 'Repeated statement appears in this section. Later, repeated statement appears in this section.' }],
    ...pinned(),
  });
  assert.equal(mappings.get('sec_1').status, 'page-only');
  assert.equal(mappings.get('sec_1').page, 2);
  assert.equal(mappings.get('sec_1').quote, '');
});

test('falls back to a server-verified proposition page when section text cannot be located', () => {
  const mappings = buildSectionMappings({
    sections: [{ id: 'sec_1', text: 'GROBID paragraph not present in the PDF text layer.' }],
    propositions: [{ section_id: 'sec_1', source_page: 2, provenance: {
      source_verification: 'verified_against_current_pdf',
      pdf_anchor: { page: 2, start_offset: 40, end_offset: 66, pdf_sha256: HASH_A },
    } }],
    pdfPages: [{ pageNumber: 1, text: 'First page.' }, { pageNumber: 2, text: 'Verified source quotation.' }],
    ...pinned(),
  });
  assert.equal(mappings.get('sec_1').status, 'page-only');
  assert.equal(mappings.get('sec_1').page, 2);
});

test('leaves sections unmapped when no validated PDF location exists', () => {
  const mappings = buildSectionMappings({
    sections: [{ id: 'sec_1', text: 'Section text is absent from these PDF pages.' }],
    pdfPages: [{ pageNumber: 1, text: 'Unrelated content.' }],
    ...pinned(),
  });
  assert.equal(mappings.get('sec_1').status, 'unmapped');
  assert.equal(mappings.get('sec_1').reason, 'no_validated_location');
});

test('rejects invalid verified page numbers rather than coercing them into navigation', () => {
  for (const page of [0, -1, 3, '2x']) {
    const mappings = buildSectionMappings({
      sections: [{ id: 'sec_1', text: 'No matching section text.' }],
      propositions: [{ section_id: 'sec_1', source_page: page, provenance: {
        source_verification: 'verified_against_current_pdf',
        pdf_anchor: { page, start_offset: 1, end_offset: 8, pdf_sha256: HASH_A },
      } }],
      pdfPages: [{ pageNumber: 1, text: 'Page one.' }, { pageNumber: 2, text: 'Page two.' }],
      ...pinned(),
    });
    assert.equal(mappings.get('sec_1').status, 'unmapped', `page ${page}`);
    assert.equal(mappings.get('sec_1').reason, 'invalid_page', `page ${page}`);
  }
});

test('rejects stale, mismatched, and unverified PDF source hashes', () => {
  const section = [{ id: 'sec_1', text: 'Text that appears in the PDF.' }];
  const pdfPages = [{ pageNumber: 1, text: 'Text that appears in the PDF.' }];
  for (const options of [
    pinned({ documentPdfSha256: HASH_B }),
    pinned({ validationStatus: 'artifact_changed' }),
    pinned({ validationStatus: 'verification_unavailable' }),
    pinned({ currentPdfSha256: '' }),
  ]) {
    const mappings = buildSectionMappings({ sections: section, pdfPages, ...options });
    assert.equal(mappings.get('sec_1').status, 'unmapped');
  }

  const staleAnchor = buildSectionMappings({
    sections: [{ id: 'sec_1', text: 'Text missing from section mapping.' }],
    propositions: [{ section_id: 'sec_1', source_page: 1, provenance: {
      source_verification: 'verified_against_current_pdf',
      pdf_anchor: { page: 1, start_offset: 1, end_offset: 8, pdf_sha256: HASH_A },
    } }],
    pdfPages,
    ...pinned({ documentPdfSha256: HASH_B }),
  });
  assert.equal(staleAnchor.get('sec_1').status, 'unmapped');
  assert.equal(staleAnchor.get('sec_1').reason, 'pdf_mismatch');
});

test('handles missing PDF mapping metadata and empty section lists without inventing locations', () => {
  const missingMetadata = buildSectionMappings({
    sections: [{ id: 'sec_1', page: 1, text: 'Text visible in a PDF page.' }],
    pdfPages: [{ pageNumber: 1, text: 'Text visible in a PDF page.' }],
  });
  assert.equal(missingMetadata.get('sec_1').status, 'unmapped');
  assert.equal(missingMetadata.get('sec_1').reason, 'pdf_hash_unavailable');

  const unverifiedSource = buildSectionMappings({
    sections: [{ id: 'sec_1', text: 'Text visible in a PDF page.' }],
    pdfPages: [{ pageNumber: 1, text: 'Text visible in a PDF page.' }],
    currentPdfSha256: HASH_A,
  });
  assert.equal(unverifiedSource.get('sec_1').reason, 'source_unverified');

  const missingPdf = buildSectionMappings({
    sections: [{ id: 'sec_1', text: 'A mapped section.' }],
    ...pinned(),
  });
  assert.equal(missingPdf.get('sec_1').status, 'unmapped');
  assert.equal(missingPdf.get('sec_1').reason, 'pdf_unavailable');
  assert.equal(buildSectionMappings({ sections: [], ...pinned() }).size, 0);
});

test('keeps the existing analysis template inline scripts syntactically valid', () => {
  const template = readFileSync(new URL('../templates/analysis.html', import.meta.url), 'utf8');
  const scripts = [...template.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)]
    .map(match => match[1]).filter(script => script.trim());
  assert.ok(scripts.length > 0);
  scripts.forEach((script, index) => new vm.Script(script, { filename: `analysis-inline-${index + 1}.js` }));
});

test('uses one existing PDF viewer and registers section synchronization once', () => {
  const template = readFileSync(new URL('../templates/analysis.html', import.meta.url), 'utf8');
  const helper = readFileSync(new URL('../static/js/atomic-section-navigation.js', import.meta.url), 'utf8');
  assert.equal([...template.matchAll(/id="pdfViewerScroll"/g)].length, 1);
  assert.equal([...template.matchAll(/getElementById\('pdfViewerScroll'\)\?\.addEventListener\('scroll',scheduleAtomicPageSync/g)].length, 1);
  assert.match(template, /\['atomic','draftTabAtomic','draftAtomicSentencesView'\]/);
  assert.match(template, /new URLSearchParams\(window\.location\.search\)\.get\('tab'\) === 'atomic'/);
  assert.doesNotMatch(helper, /pdfjsLib|getDocument\(/);
});

test('synchronizes only when the visible PDF page maps to one section', () => {
  const mappings = new Map([
    ['sec_1', { sectionId: 'sec_1', status: 'exact', page: 1 }],
    ['sec_2', { sectionId: 'sec_2', status: 'page-only', page: 2 }],
    ['sec_3', { sectionId: 'sec_3', status: 'exact', page: 2 }],
    ['sec_4', { sectionId: 'sec_4', status: 'page-only', page: 3 }],
  ]);
  assert.equal(uniqueSectionForPage(mappings, 1), 'sec_1');
  assert.equal(uniqueSectionForPage(mappings, 2), null);
  assert.equal(uniqueSectionForPage(mappings, 3), 'sec_4');
  assert.equal(uniqueSectionForPage(mappings, 4), null);
  assert.equal(uniqueSectionForPage(mappings, 0), null);
});
