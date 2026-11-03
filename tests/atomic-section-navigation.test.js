import test from 'node:test';
import assert from 'node:assert/strict';
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
});

test('synchronizes only when the visible PDF page maps to one section', () => {
  const mappings = new Map([
    ['sec_1', { sectionId: 'sec_1', status: 'exact', page: 1 }],
    ['sec_2', { sectionId: 'sec_2', status: 'page-only', page: 2 }],
    ['sec_3', { sectionId: 'sec_3', status: 'exact', page: 2 }],
  ]);
  assert.equal(uniqueSectionForPage(mappings, 1), 'sec_1');
  assert.equal(uniqueSectionForPage(mappings, 2), null);
  assert.equal(uniqueSectionForPage(mappings, 3), null);
  assert.equal(uniqueSectionForPage(mappings, 0), null);
});
