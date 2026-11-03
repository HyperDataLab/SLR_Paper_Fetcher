(function installAtomicSectionNavigation(root) {
  function normalizeText(value) {
    return String(value || '').normalize('NFKC').toLocaleLowerCase()
      .replace(/[\u00ad\u2010-\u2015]/g, '-')
      .replace(/\s+/g, ' ').trim();
  }

  function sectionAnchor(section) {
    const text = String(section?.text || '').trim();
    if (!text) return '';
    const firstParagraph = text.split(/\n\s*\n/)[0].trim() || text;
    return Array.from(firstParagraph).slice(0, 180).join('');
  }

  function countOccurrences(haystack, needle) {
    if (!needle) return 0;
    let count = 0, offset = 0;
    while ((offset = haystack.indexOf(needle, offset)) !== -1) {
      count += 1;
      offset += 1;
    }
    return count;
  }

  function pageNumber(value, validPages) {
    const number = Number(value);
    return Number.isInteger(number) && validPages.has(number) ? number : null;
  }

  function buildSectionMappings({
    sections = [], pdfPages = [], propositions = [], currentPdfSha256 = '',
    documentPdfSha256 = '', validationStatus = 'verification_unavailable',
  } = {}) {
    const mappings = new Map();
    if (!Array.isArray(sections)) return mappings;

    const currentHash = String(currentPdfSha256 || '').toLowerCase();
    const documentHash = String(documentPdfSha256 || '').toLowerCase();
    const hashAvailable = /^[a-f0-9]{64}$/.test(currentHash);
    const pageRecords = Array.isArray(pdfPages) ? pdfPages : [];
    const validPages = new Set(pageRecords
      .map(page => Number(page?.pageNumber))
      .filter(page => Number.isInteger(page) && page > 0));
    const pageText = new Map(pageRecords
      .filter(page => validPages.has(Number(page?.pageNumber)))
      .map(page => [Number(page.pageNumber), normalizeText(page.text)]));
    const sourceValidationAllowed = [
      'verified_pinned_pdf', 'legacy_quotes_verified_against_current_pdf',
    ].includes(validationStatus);
    const sectionTextHashVerified = validationStatus === 'verified_pinned_pdf'
      && hashAvailable && documentHash === currentHash;

    let unavailableReason = 'source_unverified';
    if (!pageRecords.length) unavailableReason = 'pdf_unavailable';
    else if (!hashAvailable) unavailableReason = 'pdf_hash_unavailable';
    else if (validationStatus === 'artifact_changed'
        || (documentHash && documentHash !== currentHash)) unavailableReason = 'pdf_mismatch';
    else if (!sourceValidationAllowed) unavailableReason = 'source_unverified';

    for (const section of sections) {
      const id = String(section?.id || '');
      if (!id) continue;
      if (!pageRecords.length || !hashAvailable || !sourceValidationAllowed
          || (documentHash && documentHash !== currentHash)) {
        mappings.set(id, { sectionId: id, status: 'unmapped', page: null, quote: '', reason: unavailableReason });
        continue;
      }

      let matchedPages = [];
      const quote = sectionTextHashVerified ? sectionAnchor(section) : '';
      const normalizedQuote = normalizeText(quote);
      if (normalizedQuote) {
        for (const [page, text] of pageText) {
          const occurrences = countOccurrences(text, normalizedQuote);
          if (occurrences) matchedPages.push({ page, occurrences });
        }
      }
      if (matchedPages.length === 1) {
        const match = matchedPages[0];
        mappings.set(id, {
          sectionId: id,
          status: match.occurrences === 1 ? 'exact' : 'page-only',
          page: match.page,
          quote: match.occurrences === 1 ? quote : '',
          reason: match.occurrences === 1 ? 'unique_section_text_match' : 'repeated_text_on_page',
        });
        continue;
      }

      const verifiedPages = new Set();
      let invalidVerifiedPage = false;
      for (const proposition of Array.isArray(propositions) ? propositions : []) {
        if (String(proposition?.section_id || '') !== id) continue;
        const provenance = proposition?.provenance || {};
        const anchor = provenance.pdf_anchor || {};
        const start = Number(anchor.start_offset), end = Number(anchor.end_offset);
        if (provenance.source_verification !== 'verified_against_current_pdf'
            || String(anchor.pdf_sha256 || '').toLowerCase() !== currentHash
            || !Number.isInteger(start) || !Number.isInteger(end) || start < 0 || end <= start) continue;
        const verifiedPage = pageNumber(anchor.page, validPages);
        if (verifiedPage === null || pageNumber(proposition.source_page, validPages) !== verifiedPage) {
          invalidVerifiedPage = true;
          continue;
        }
        verifiedPages.add(verifiedPage);
      }
      if (verifiedPages.size === 1) {
        mappings.set(id, {
          sectionId: id, status: 'page-only', page: [...verifiedPages][0], quote: '',
          reason: matchedPages.length ? 'ambiguous_section_text_resolved_by_verified_source_page' : 'verified_source_page',
        });
      } else {
        mappings.set(id, {
          sectionId: id, status: 'unmapped', page: null, quote: '',
          reason: verifiedPages.size > 1 ? 'multiple_verified_pages'
            : matchedPages.length > 1 ? 'ambiguous_section_text'
              : invalidVerifiedPage ? 'invalid_page' : 'no_validated_location',
        });
      }
    }
    return mappings;
  }

  function uniqueSectionForPage(mappings, page) {
    const pageValue = Number(page);
    if (!(mappings instanceof Map) || !Number.isInteger(pageValue) || pageValue < 1) return null;
    const matches = [...mappings.values()].filter(mapping =>
      (mapping.status === 'exact' || mapping.status === 'page-only') && mapping.page === pageValue,
    );
    return matches.length === 1 ? matches[0].sectionId : null;
  }

  root.AtomicSectionNavigation = { buildSectionMappings, uniqueSectionForPage };
})(globalThis);
