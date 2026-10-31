(function () {
    const failureStates = new Set([
        'FAILED', 'NO_ACCESS', 'CAPTCHA_REQUIRED', 'MFA_REQUIRED', 'LOGIN_REQUIRED',
        'INVALID_PDF', 'RESOLUTION_FAILED', 'CANCELLED', 'SESSION_EXPIRED'
    ]);

    function node(tag, text, className) {
        const value = document.createElement(tag);
        value.textContent = text == null ? '' : String(text);
        if (className) value.className = className;
        return value;
    }

    function externalUrl(value) {
        try {
            const url = new URL(value);
            return ['http:', 'https:'].includes(url.protocol) ? url.href : '';
        } catch {
            return '';
        }
    }

    function doiUrl(value) {
        if (!value) return '';
        if (/^https?:\/\//i.test(value)) return externalUrl(value);
        if (!/^10\.\d{4,9}\//.test(value)) return '';
        return externalUrl(`https://doi.org/${value}`);
    }

    function paperUrl(item) {
        const supplied = item.resolved_url || item.oa_landing || item.vnu_link || item.oa_link;
        if (supplied) return externalUrl(supplied);
        return doiUrl(item.doi || item.original);
    }

    function statusInfo(code, route) {
        if (code === 'DOWNLOADED') return { tone: 'downloaded', label: 'Đã tải' };
        if (code === 'CANCELLED') return { tone: 'interrupted', label: 'Gián đoạn' };
        if (code === 'PURCHASE_REQUIRED' || route === 'purchase') return { tone: 'paywalled', label: 'Trả phí' };
        if (code === 'INVALID_DOI' || route === 'invalid') return { tone: 'doi-error', label: 'DOI lỗi' };
        if (['LOGIN_REQUIRED', 'SESSION_EXPIRED', 'MFA_REQUIRED', 'CAPTCHA_REQUIRED'].includes(code)) {
            return { tone: 'attention', label: 'Cần xác minh' };
        }
        if (['FAILED', 'NO_ACCESS', 'INVALID_PDF', 'RESOLUTION_FAILED'].includes(code) || route === 'failed') {
            return { tone: 'failed', label: 'Thất bại' };
        }
        if (code === 'OPEN_ACCESS' || route === 'oa') return { tone: 'oa-available', label: 'Có bản OA' };
        if (code === 'PROCESSING') return { tone: 'processing', label: 'Đang tải' };
        if (['AUTHENTICATED', 'INSTITUTION_ACCESS'].includes(code) || route === 'vnu') {
            return { tone: 'access', label: 'Truy cập VNU' };
        }
        if (route === 'search') return { tone: 'pending', label: 'Đang tìm OA' };
        return { tone: 'pending', label: code === 'PENDING' ? 'Chờ tải' : (code || 'Chờ tải') };
    }

    function updateStatus(cell, code, route, message) {
        if (!cell) return;
        const info = statusInfo(code, route);
        cell.dataset.state = code || 'PENDING';
        cell.title = message || '';
        const badge = node('span', info.label, 'result-status-pill');
        badge.dataset.tone = info.tone;
        cell.replaceChildren(badge);
    }

    function icon(kind) {
        const paths = {
            open: 'M14 4h6v6m0-6L10 14M19 13v6a1 1 0 01-1 1H5a1 1 0 01-1-1V6a1 1 0 011-1h6',
            ris: 'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8zM14 2v6h6M8 13h8M8 17h8'
        };
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('stroke-width', '1.8');
        svg.setAttribute('stroke-linecap', 'round');
        svg.setAttribute('stroke-linejoin', 'round');
        svg.setAttribute('aria-hidden', 'true');
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', paths[kind]);
        svg.appendChild(path);
        return svg;
    }

    function createPrimaryAction(cell, item, index, route, code, handlers) {
        const href = paperUrl(item);
        const paywalled = code === 'PURCHASE_REQUIRED' || route === 'purchase';
        const invalidDoi = code === 'INVALID_DOI' || route === 'invalid';
        const addButton = (label, variant, callback, disabled, loading = false) => {
            const button = node('button', label, `result-primary-action${variant ? ` result-primary-action--${variant}` : ''}`);
            button.type = 'button';
            button.disabled = Boolean(disabled);
            if (callback && loading) {
                button.addEventListener('click', async () => {
                    button.disabled = true;
                    button.textContent = 'Đang tải';
                    const row = cell.parentElement?.parentElement?.parentElement;
                    const stateCell = row?.children?.[2];
                    updateStatus(stateCell, 'PROCESSING', 'processing', item.message || '');
                    try { await callback(); }
                    finally {
                        if (button.isConnected) {
                            button.disabled = false;
                            button.textContent = label;
                            updateStatus(stateCell, code, route, item.message || '');
                        }
                    }
                });
            } else if (callback) button.addEventListener('click', callback);
            cell.appendChild(button);
        };

        if (code === 'DOWNLOADED' || item.already_exists) {
            addButton('Mở thư mục', 'quiet', handlers.openFolder);
        } else if (paywalled) {
            if (href) {
                const link = node('a', 'Mở bài báo', 'result-primary-action');
                link.href = href;
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                link.title = 'Mở trang bài báo';
                cell.appendChild(link);
            }
        } else if (code === 'PROCESSING') {
            addButton('Đang tải', '', null, true);
        } else if (invalidDoi) {
            return;
        } else if (item.doi && failureStates.has(code)) {
            addButton('Thử lại', '', handlers.retry, false, true);
        } else if (item.doi) {
            addButton('Tải PDF', '', handlers.download, false, true);
        }
    }

    function renderPrimaryAction(cell, item, index, route, code, handlers) {
        if (!cell) return;
        cell.replaceChildren();
        cell.className = 'result-actions-main';
        cell.title = item.message || '';
        createPrimaryAction(cell, item, index, route, code, handlers);
        syncExternalAction(cell, item, route);
    }

    function syncExternalAction(cell, item, route) {
        const controls = cell.parentElement;
        if (!controls) return;
        let open = controls.querySelector('[data-result-open]');
        const isPrimaryExternal = codeIsPaywalled(item, route);
        const href = paperUrl(item);
        if (!href || isPrimaryExternal) {
            if (open) open.remove();
            return;
        }
        if (!open) {
            open = node('a', '', 'result-icon-action');
            open.setAttribute('data-result-open', 'true');
            open.setAttribute('aria-label', 'Mở trang bài báo');
            open.title = 'Mở trang bài báo';
            open.target = '_blank';
            open.rel = 'noopener noreferrer';
            open.appendChild(icon('open'));
            const ris = controls.querySelector('[data-result-ris]');
            controls.insertBefore(open, ris || null);
        }
        open.href = href;
    }

    function codeIsPaywalled(item, route) {
        return item.state === 'PURCHASE_REQUIRED' || route === 'purchase';
    }

    function createRow(item, index, options) {
        const code = item.already_exists ? 'DOWNLOADED' : (item.state || item.status || 'PENDING');
        const route = options.route || '';
        const row = node('tr', '', 'result-row');

        const file = node('td', '', 'result-file-cell');
        file.dataset.label = 'Tên file';
        const fileName = node('span', item.custom_name || '—', 'result-file-name');
        fileName.title = item.custom_name || '';
        file.appendChild(fileName);

        const paper = node('td', '', 'result-paper-cell');
        paper.dataset.label = 'Bài báo';
        const title = node('div', item.title || item.doi || item.original || 'Chưa có tiêu đề', 'result-paper-title');
        title.title = title.textContent;
        const metadata = node('div', [item.authors, item.journal, item.year].filter(Boolean).join(' · '), 'result-paper-meta');
        metadata.title = metadata.textContent;
        const detailRow = node('div', '', 'result-paper-details');
        if (item.doi || item.original) {
            const doi = item.doi || item.original;
            const href = doiUrl(doi);
            const detail = node(href ? 'a' : 'span', doi, 'result-doi-link');
            if (href) {
                detail.href = href;
                detail.target = '_blank';
                detail.rel = 'noopener noreferrer';
                detail.title = `Mở DOI: ${doi}`;
                const arrow = node('span', '↗', 'result-doi-icon');
                arrow.setAttribute('aria-hidden', 'true');
                detail.appendChild(arrow);
            }
            detailRow.appendChild(detail);
        }
        if (options.provider) {
            const source = node('span', options.provider, 'result-source-label');
            source.title = options.favorite ? `${options.provider} · Nguồn quan tâm` : options.provider;
            detailRow.appendChild(source);
        }
        paper.append(title, metadata, detailRow);

        const state = node('td', '', 'result-status-cell');
        state.id = `state-cell-${index}`;
        state.dataset.label = 'Trạng thái PDF';
        updateStatus(state, code, route, item.message || '');

        const actions = node('td', '', 'result-actions-cell');
        actions.dataset.label = 'Thao tác';
        const controls = node('div', '', 'result-controls');
        const mainAction = node('div', '', 'result-actions-main');
        mainAction.id = `action-cell-${index}`;
        controls.appendChild(mainAction);
        renderPrimaryAction(mainAction, item, index, route, code, options.handlers);
        const ris = node('button', '', 'result-icon-action');
        ris.type = 'button';
        ris.id = `ris-btn-${index}`;
        ris.setAttribute('data-result-ris', 'true');
        ris.title = 'Xuất trích dẫn RIS';
        ris.setAttribute('aria-label', 'Xuất trích dẫn RIS');
        ris.appendChild(icon('ris'));
        ris.addEventListener('click', options.handlers.exportRis);
        controls.appendChild(ris);
        actions.appendChild(controls);
        row.append(file, paper, state, actions);
        return row;
    }

    window.SlrResearchResults = Object.freeze({ createRow, updateStatus, renderPrimaryAction, statusInfo });
})();
