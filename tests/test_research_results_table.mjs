import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

class FakeElement {
    constructor(tagName) {
        this.tagName = tagName.toUpperCase();
        this.children = [];
        this.dataset = {};
        this.attributes = {};
        this.listeners = {};
        this.parentElement = null;
        this.className = '';
        this.title = '';
        this._textContent = '';
    }
    set textContent(value) { this.replaceChildren(); this._textContent = String(value ?? ''); }
    get textContent() { return this._textContent + this.children.map(child => child.textContent).join(''); }
    appendChild(child) {
        if (child.parentElement) child.remove();
        child.parentElement = this;
        this.children.push(child);
        return child;
    }
    append(...children) { children.forEach(child => this.appendChild(child)); }
    replaceChildren(...children) {
        this.children.forEach(child => { child.parentElement = null; });
        this.children = [];
        this._textContent = '';
        children.forEach(child => this.appendChild(child));
    }
    insertBefore(child, reference) {
        if (!reference) return this.appendChild(child);
        const index = this.children.indexOf(reference);
        if (index < 0) return this.appendChild(child);
        if (child.parentElement) child.remove();
        child.parentElement = this;
        this.children.splice(index, 0, child);
        return child;
    }
    setAttribute(name, value) { this.attributes[name] = String(value); }
    hasAttribute(name) { return Object.hasOwn(this.attributes, name); }
    addEventListener(name, callback) { this.listeners[name] = callback; }
    remove() {
        if (!this.parentElement) return;
        const siblings = this.parentElement.children;
        siblings.splice(siblings.indexOf(this), 1);
        this.parentElement = null;
    }
    get isConnected() { return Boolean(this.parentElement); }
    querySelector(selector) {
        const attr = selector.match(/^\[([^\]]+)\]$/)?.[1];
        for (const child of this.children) {
            if (attr && child.hasAttribute(attr)) return child;
            const nested = child.querySelector(selector);
            if (nested) return nested;
        }
        return null;
    }
    querySelectorAll(selector, found = []) {
        const attr = selector.match(/^\[([^\]]+)\]$/)?.[1];
        for (const child of this.children) {
            if (attr && child.hasAttribute(attr)) found.push(child);
            child.querySelectorAll(selector, found);
        }
        return found;
    }
}

const document = {
    createElement: tag => new FakeElement(tag),
    createElementNS: (_namespace, tag) => new FakeElement(tag)
};
const context = { document, window: {}, URL, Set };
vm.runInNewContext(readFileSync('static/js/research-results-table.js', 'utf8'), context);
const table = context.window.SlrResearchResults;
const callbacks = { openFolder() {}, download() {}, retry() {}, exportRis() {} };

const cases = [
    { code: 'DOWNLOADED', route: 'downloaded', tone: 'downloaded', label: 'Đã tải', action: 'Mở thư mục', doi: '10.1016/example' },
    { code: 'FAILED', route: 'failed', tone: 'failed', label: 'Thất bại', action: 'Thử lại', doi: '10.1016/example' },
    { code: 'CANCELLED', route: 'failed', tone: 'interrupted', label: 'Gián đoạn', action: 'Thử lại', doi: '10.1016/example' },
    { code: 'LOGIN_REQUIRED', route: 'failed', tone: 'attention', label: 'Cần xác minh', action: 'Thử lại', doi: '10.1016/example' },
    { code: 'PENDING', route: 'oa', tone: 'oa-available', label: 'Có bản OA', action: 'Tải PDF', doi: '10.1016/example' },
    { code: 'PURCHASE_REQUIRED', route: 'purchase', tone: 'paywalled', label: 'Trả phí', action: 'Mở bài báo', doi: '10.1016/example' },
    { code: 'INVALID_DOI', route: 'invalid', tone: 'doi-error', label: 'DOI lỗi', action: null, doi: 'not-a-doi' }
];

for (const [index, scenario] of cases.entries()) {
    const row = table.createRow({
        doi: scenario.doi,
        title: 'A long research paper title used to check consistent row structure',
        custom_name: 'a_very_long_paper_filename_that_should_be_truncated.pdf',
        state: scenario.code,
        already_exists: scenario.code === 'DOWNLOADED',
        resolved_url: scenario.code === 'INVALID_DOI' ? '' : 'https://publisher.example/paper'
    }, index, { provider: 'Springer', favorite: false, route: scenario.route, handlers: callbacks });

    assert.equal(row.children.length, 4, `${scenario.code} should use the shared four-column row`);
    const [file, paper, status, actions] = row.children;
    assert.equal(file.children[0].className, 'result-file-name');
    assert.equal(paper.children[0].className, 'result-paper-title');
    assert.equal(status.children[0].dataset.tone, scenario.tone);
    assert.equal(status.children[0].textContent, scenario.label);
    assert.equal(actions.querySelectorAll('[data-result-ris]').length, 1, 'RIS stays available once per row');
    const descendants = parent => parent.children.flatMap(child => [child, ...descendants(child)]);
    const primary = descendants(actions).find(child => child.className.includes('result-primary-action'));
    assert.equal(primary?.textContent || null, scenario.action, `${scenario.code} should expose the right primary action`);
    if (scenario.code === 'PURCHASE_REQUIRED') {
        assert.equal(actions.querySelectorAll('[data-result-open]').length, 0, 'paywall row should not duplicate its open-page action');
    }
    if (scenario.code === 'INVALID_DOI') {
        assert.equal(actions.querySelectorAll('[data-result-open]').length, 0, 'invalid DOI should not create a broken external action');
    }
}

let finishRetry;
const loadingRow = table.createRow({ doi: '10.1016/retry', state: 'FAILED' }, 20, {
    route: 'failed',
    handlers: { ...callbacks, retry: () => new Promise(resolve => { finishRetry = resolve; }) }
});
const loadingAction = loadingRow.children[3].children[0].children[0];
const loadingButton = loadingAction.children[0];
const retryTask = loadingButton.listeners.click();
assert.equal(loadingButton.disabled, true, 'retry disables its primary action while work starts');
assert.equal(loadingRow.children[2].dataset.state, 'PROCESSING', 'retry exposes a loading status');
finishRetry();
await retryTask;
assert.equal(loadingButton.disabled, false, 'retry re-enables if the row remains mounted');
assert.equal(loadingRow.children[2].dataset.state, 'FAILED', 'a no-op retry restores the previous status');

console.log(`Research result row states verified: ${cases.map(item => item.code).join(', ')}`);
