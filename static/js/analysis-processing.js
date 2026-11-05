(() => {
  'use strict';

  const STATUS_LABELS = {
    PENDING: 'Waiting in queue', PROCESSING: 'Processing', DONE: 'Ready to review', FAILED: 'Analysis failed',
    DEMO_COMPLETE: 'Demo complete | mock only',
  };
  const STAGE_LABELS = {
    starting: 'Starting the analysis worker',
    fulltext_mapping: 'Building the source text mapping',
    fulltext_mapping_created: 'Created a verified source text mapping',
    fulltext_mapping_reused: 'Reusing the saved source text mapping',
    review_draft: 'Reviewing the mapped full text',
    proposition_extraction: 'Extracting source-grounded propositions',
    argument_role_analysis: 'Mapping argument roles',
    warrant_reconstruction: 'Analyzing warrants and reasoning',
    graph_validation: 'Validating the argument graph',
    paper_profile: 'Building the paper profile',
    stance_engagement: 'Analyzing Stance & Engagement',
    saffron_term_taxonomy: 'Running SAFFRON term and taxonomy analysis',
    completed: 'Analysis saved', failed: 'The analysis run failed',
  };
  const MODULES = [
    { id: 'mapping', label: 'Source text mapping', stage: 'fulltext_mapping', detail: 'Extracts and checks the full-text source mapping.' },
    { id: 'review', label: 'Full-text review', stage: 'review_draft', detail: 'Reads the mapped paper text for the review draft.' },
    { id: 'propositions', label: 'Propositions', stage: 'proposition_extraction', detail: 'Finds candidate propositions and validates them against source text.' },
    { id: 'roles', label: 'Argument roles', stage: 'argument_role_analysis', detail: 'Maps roles and relationships among propositions.' },
    { id: 'warrants', label: 'Warrant analysis', stage: 'warrant_reconstruction', detail: 'Examines reasoning links and warrant components.' },
    { id: 'graph', label: 'Graph validation', stage: 'graph_validation', detail: 'Validates the saved argument graph structure.' },
    { id: 'profile', label: 'Paper profile', stage: 'paper_profile', detail: 'Builds the paper profile, outline, and writing observations.' },
    { id: 'stance', label: 'Stance & Engagement', stage: 'stance_engagement', optional: true, detail: 'Optional source-traced Hyland analysis; the saved result is checked after the run.' },
    { id: 'saffron', label: 'SAFFRON', stage: 'saffron_term_taxonomy', optional: true, detail: 'Optional term and taxonomy stage; its saved status is checked after the run.' },
  ];
  const ORDER = ['starting', 'fulltext_mapping', 'fulltext_mapping_created', 'fulltext_mapping_reused', 'review_draft', 'proposition_extraction', 'argument_role_analysis', 'warrant_reconstruction', 'graph_validation', 'paper_profile', 'stance_engagement', 'saffron_term_taxonomy'];
  const POLL_MS = 5000;
  const MAX_LOGS = 40;
  const DEMO_STAGES = ['fulltext_mapping','fulltext_mapping_created','review_draft','proposition_extraction','argument_role_analysis','warrant_reconstruction','graph_validation','paper_profile','stance_engagement','saffron_term_taxonomy'];

  const element = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };

  class AnalysisProcessingExperience {
    constructor() {
      this.paper = null;
      this.onStart = null;
      this.demo = false;
      this.demoStages = DEMO_STAGES;
      this.demoTimer = null;
      this.demoStageIndex = -1;
      this.workspace = null;
      this.onViewResults = null;
      this.pollTimer = null;
      this.polling = false;
      this.stopped = false;
      this.stage = '';
      this.status = '';
      this.connection = 'connected';
      this.logs = [];
      this.optional = { stance: 'optional', saffron: 'optional' };
      this.profileState = 'checking';
      this.root = document.getElementById('draftViewArea');
      this.activeModuleId = null;
      this.handoffAnimation = null;
      this.droneAnimation = null;
      this.introAnimations = [];
    }

    async start(paper, { onViewResults, demo = false } = {}) {
      this.paper = { ...paper };
      if (this.onStart) this.onStart(this.paper);
      this.onViewResults = onViewResults || null;
      this.demo = Boolean(demo);
      this.demoStages = this.paper.source_kind === 'markdown' ? DEMO_STAGES.filter(stage => !['fulltext_mapping','fulltext_mapping_created'].includes(stage)) : DEMO_STAGES;
      clearTimeout(this.demoTimer);
      this.demoStageIndex = -1;
      this.logs = [];
      this.status = this.demo ? 'PROCESSING' : paper.analysis_status || 'PENDING';
      this.stage = this.demo ? 'starting' : this.status === 'PENDING' ? '' : paper.analysis_stage || '';
      this.stopped = false;
      this.handoffAnimation?.cancel();
      this.droneAnimation?.cancel();
      this.cancelIntroAnimations();
      this.workspace?.remove();
      window.removeEventListener('resize', this.resizeHandler);
      this.activeModuleId = null;
      document.body.classList.add('processing-experience-active');
      this.build();
      this.logSnapshot();
      this.render();
      const introWorkspace = this.workspace;
      const introPromise = this.playIntro();
      if (this.demo) {
        this.refs.consoleMeta.textContent = 'DEMO | local stage simulation | no analysis request';
        introPromise.then(() => {
          if (this.workspace === introWorkspace && this.demo && !this.stopped) this.scheduleDemo(900);
        });
        return;
      }
      if (this.status === 'DONE') {
        await this.loadCompletedArtifacts();
      } else if (this.status === 'PENDING' || this.status === 'PROCESSING') {
        this.schedulePoll(0);
      }
    }

    build() {
      if (!this.root) return;
      this.workspace = element('section', 'research-processing');
      this.workspace.setAttribute('aria-label', 'Paper analysis processing workspace');
      this.workspace.dataset.intro = 'running';
      this.workspace.innerHTML = `
        <header class="process-heading">
          <a class="process-back" href="/analysis" aria-label="Back to papers"><span aria-hidden="true">&#8592;</span><span>Back</span></a>
          <div class="process-title-wrap">
            <h2 data-role="paper-title"></h2>
            <p class="process-current-stage"><span class="process-stage-live-dot" aria-hidden="true"></span><span data-role="current-stage">Waiting for analysis stage</span></p>
          </div>
          <div class="process-actions">
            <span class="process-demo-badge" data-role="demo-badge" title="This is a local visual simulation. No analysis request is sent." hidden>Demo</span>
            <span class="process-state" data-role="status"><span class="process-state-dot" aria-hidden="true"></span><span data-role="status-label"></span></span>
            <button type="button" class="process-action" data-action="retry" hidden>Retry analysis</button>
            <button type="button" class="process-action process-action-primary" data-action="results" hidden>View analysis results</button>
          </div>
        </header>
        <main class="process-stage" data-role="stage" aria-label="Animated paper analysis stage">
          <div class="process-orbit-layer" data-role="orbit-layer">
          <svg class="process-flow-map" viewBox="0 0 1000 600" preserveAspectRatio="none" aria-hidden="true">
            <path id="module-edge-0" class="process-flow-link" data-edge="0" d="M150 150 C110 205 78 230 82 292"/>
            <path id="module-edge-1" class="process-flow-link" data-edge="1" d="M82 308 C78 365 110 395 155 444"/>
            <path id="module-edge-2" class="process-flow-link" data-edge="2" d="M172 454 C225 500 285 520 355 520"/>
            <path id="module-edge-3" class="process-flow-link" data-edge="3" d="M380 520 C420 538 458 545 490 545"/>
            <path id="module-edge-4" class="process-flow-link" data-edge="4" d="M510 545 C555 545 600 538 635 520"/>
            <path id="module-edge-5" class="process-flow-link" data-edge="5" d="M655 520 C730 515 780 480 828 448"/>
            <path id="module-edge-6" class="process-flow-link" data-edge="6" d="M842 432 C895 390 928 350 918 308"/>
            <path id="module-edge-7" class="process-flow-link" data-edge="7" d="M916 290 C922 228 890 190 852 150"/>
          </svg>
          <div class="process-module-flow" data-role="modules" role="group" aria-label="Analysis modules"></div>
          </div>
          <article class="process-document" aria-label="Illustrated research paper">
            <div class="process-document-top"><span class="process-doc-seal">R</span><span>RESEARCH ARTICLE <i>·</i> FULL TEXT</span><span class="process-doc-page">01</span></div>
            <p class="process-doc-demo-note" data-role="document-demo-note" hidden>Illustrative structure · not extracted</p>
            <h3 data-role="document-title"></h3>
            <div class="process-doc-authors"><i></i><i></i><i></i></div>
            <p class="process-doc-sample" data-role="document-demo-sample" hidden>This preview uses sample copy to show document structure. Research claims and extracted findings are not shown.</p>
            <div class="process-doc-section"><strong>ABSTRACT</strong><span class="process-doc-line w100"></span><span class="process-doc-line w94"></span><span class="process-doc-line w87"></span><span class="process-doc-line w72"></span></div>
            <div class="process-doc-section"><strong>1. INTRODUCTION</strong><span class="process-doc-line w96"></span><span class="process-doc-line w100"></span><span class="process-doc-line w82"></span><span class="process-doc-line w91"></span></div>
            <div class="process-doc-columns"><div><span class="process-doc-line w100"></span><span class="process-doc-line w90"></span><span class="process-doc-line w96"></span><span class="process-doc-line w70"></span></div><div><span class="process-doc-line w100"></span><span class="process-doc-line w86"></span><span class="process-doc-line w94"></span><span class="process-doc-line w62"></span></div></div>
            <div class="process-doc-section"><strong>2. METHODOLOGY</strong><span class="process-doc-line w100"></span><span class="process-doc-line w89"></span><span class="process-doc-line w77"></span></div>
            <div class="process-doc-equation"><i></i><span>illustrative equation block</span><i></i></div>
            <div class="process-doc-section"><strong>3. RESULTS</strong><span class="process-doc-line w95"></span><span class="process-doc-line w81"></span></div>
          </article>
          <div class="process-drone" data-role="drone" aria-hidden="true">
            <svg viewBox="0 0 100 72" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M28 22H16M72 22H84" stroke="#8FA6B5" stroke-width="3" stroke-linecap="round"/>
              <path d="M13 18C13 13 17 9 22 9H28M87 18C87 13 83 9 78 9H72" stroke="#B4C5CE" stroke-width="2" stroke-linecap="round"/>
              <rect x="27" y="17" width="46" height="27" rx="12" fill="#F8FBFC" stroke="#7893A3" stroke-width="2"/>
              <rect x="35" y="23" width="30" height="14" rx="7" fill="#DDECF3"/>
              <circle cx="44" cy="30" r="2.5" fill="#176F9C"/><circle cx="56" cy="30" r="2.5" fill="#176F9C"/>
              <path d="M43 39H57" stroke="#A9BAC4" stroke-width="1.5" stroke-linecap="round"/>
              <circle class="process-drone-light" cx="31" cy="30" r="2.2" fill="#3F9AC4"/>
              <circle class="process-drone-light" cx="69" cy="30" r="2.2" fill="#8FBA91"/>
            </svg>
            <span class="process-drone-particles" aria-hidden="true"><i>x</i><i>+</i><i>0</i><i>1</i></span>
          </div>
          <div class="process-handoff-orb" data-role="handoff-orb" aria-hidden="true"></div>
          <p class="process-stage-caption" data-role="module-detail" aria-live="polite">Preparing the analysis workspace.</p>
        </main>
        <details class="process-console" data-role="console">
          <summary><span class="process-console-heading"><i class="process-console-indicator" aria-hidden="true"></i>Activity</span><span class="process-console-meta" data-role="console-meta">Observed backend status</span><button type="button" class="process-console-copy" data-action="copy">Copy log</button></summary>
          <div class="process-console-log" data-role="logs" role="log" aria-live="polite" aria-relevant="additions text"></div>
          <p class="process-console-status" data-role="connection" data-state="online">Connected | showing status transitions observed by this page.</p>
        </details>
      `;
      this.root.prepend(this.workspace);
      document.getElementById('draftModal')?.setAttribute('aria-hidden', 'false');
      this.refs = {
        orbitLayer: this.workspace.querySelector('[data-role="orbit-layer"]'),
        paperTitle: this.workspace.querySelector('[data-role="paper-title"]'),
        documentTitle: this.workspace.querySelector('[data-role="document-title"]'),
        documentDemoNote: this.workspace.querySelector('[data-role="document-demo-note"]'),
        documentDemoSample: this.workspace.querySelector('[data-role="document-demo-sample"]'),
        currentStage: this.workspace.querySelector('[data-role="current-stage"]'),
        demoBadge: this.workspace.querySelector('[data-role="demo-badge"]'),
        status: this.workspace.querySelector('[data-role="status"]'),
        statusLabel: this.workspace.querySelector('[data-role="status-label"]'),
        stage: this.workspace.querySelector('[data-role="stage"]'),
        drone: this.workspace.querySelector('[data-role="drone"]'),
        flowOrb: this.workspace.querySelector('[data-role="handoff-orb"]'),
        modules: this.workspace.querySelector('[data-role="modules"]'),
        moduleDetail: this.workspace.querySelector('[data-role="module-detail"]'),
        logs: this.workspace.querySelector('[data-role="logs"]'),
        connection: this.workspace.querySelector('[data-role="connection"]'),
        retry: this.workspace.querySelector('[data-action="retry"]'),
        results: this.workspace.querySelector('[data-action="results"]'),
        copy: this.workspace.querySelector('[data-action="copy"]'),
        consoleMeta: this.workspace.querySelector('[data-role="console-meta"]'),
      };
      this.refs.status.setAttribute('role', 'status');
      this.refs.status.setAttribute('aria-live', 'polite');
      this.workspace.querySelector('[data-action="retry"]').addEventListener('click', () => void this.retry());
      this.workspace.querySelector('[data-action="results"]').addEventListener('click', () => void this.viewResults());
      this.workspace.querySelector('[data-action="copy"]').addEventListener('click', event => { event.preventDefault(); event.stopPropagation(); void this.copyLogs(); });
      this.refs.paperTitle.textContent = this.paper.title || this.paper.doi || 'Paper';
      this.refs.paperTitle.title = this.refs.paperTitle.textContent;
      this.refs.documentTitle.textContent = this.refs.paperTitle.textContent;
      this.renderModules();
      this.resizeHandler = () => this.syncDroneToModule(this.activeModuleId);
      window.addEventListener('resize', this.resizeHandler, { passive: true });
      this.render();
    }

    cancelIntroAnimations() {
      this.introCancelled = true;
      this.introAnimations.forEach(animation => animation.cancel());
      this.introAnimations = [];
    }

    async playIntro() {
      const workspace = this.workspace;
      const orbit = this.refs?.orbitLayer;
      if (!workspace || !orbit) return;
      if (matchMedia('(prefers-reduced-motion: reduce)').matches || matchMedia('(max-width: 760px)').matches) {
        workspace.dataset.intro = 'ready';
        this.render();
        return;
      }
      const nodes = [...this.refs.modules.querySelectorAll('.process-module')];
      const paths = [...orbit.querySelectorAll('.process-flow-link')];
      const identity = 'perspective(1400px) rotateX(0deg) rotateY(0deg) scale(1)';
      const clustered = 'perspective(1400px) rotateX(8deg) rotateY(-4deg) scale(.018)';
      const expanded = 'perspective(1400px) rotateX(8deg) rotateY(-4deg) scale(.78)';
      this.introCancelled = false;
      orbit.style.transform = clustered;
      orbit.style.opacity = '.72';
      paths.forEach(path => {
        path.style.opacity = '0';
        path.style.strokeDasharray = '';
        path.style.strokeDashoffset = '';
      });

      const playPhase = async (animations, onFinish) => {
        this.introAnimations = animations;
        await Promise.all(animations.map(animation => animation.finished.catch(() => undefined)));
        if (this.workspace !== workspace || this.introCancelled) return false;
        onFinish?.();
        animations.forEach(animation => animation.cancel());
        this.introAnimations = [];
        return true;
      };

      // 1. Start with the cards clustered on the paper, then fan them outward.
      const fanOut = [orbit.animate([
        { transform: clustered, opacity: .72 },
        { transform: expanded, opacity: 1 },
      ], { duration: 1050, easing: 'cubic-bezier(.16,.82,.22,1)', fill: 'both' })];
      nodes.forEach((node, index) => fanOut.push(node.animate([
        { scale: .3, opacity: 0 },
        { scale: 1, opacity: 1 },
      ], { duration: 560, delay: 180 + index * 70, easing: 'cubic-bezier(.18,.82,.22,1)', fill: 'both' })));
      if (!await playPhase(fanOut, () => {
        orbit.style.transform = expanded;
        orbit.style.opacity = '1';
        nodes.forEach(node => {
          node.style.scale = '1';
          node.style.opacity = '';
        });
      })) return;

      // 2. Draw the existing connector chain one edge at a time to thread each node.
      const thread = paths.map((path, index) => {
        const length = path.getTotalLength();
        path.style.stroke = '#a8cdb8';
        path.style.strokeDasharray = String(length);
        path.style.strokeDashoffset = String(length);
        return path.animate([
          { strokeDashoffset: length, opacity: 0 },
          { strokeDashoffset: 0, opacity: .86 },
        ], { duration: 430, delay: index * 365, easing: 'cubic-bezier(.22,.72,.25,1)', fill: 'both' });
      });
      if (!await playPhase(thread, () => {
        paths.forEach(path => {
          path.style.strokeDasharray = '';
          path.style.strokeDashoffset = '';
          path.style.stroke = '';
          path.style.opacity = '';
        });
      })) return;

      // 3. Settle the connected constellation into its final, undistorted layout.
      const settle = orbit.animate([
        { transform: expanded, opacity: 1 },
        { transform: identity, opacity: 1 },
      ], { duration: 880, easing: 'cubic-bezier(.2,.78,.22,1)', fill: 'both' });
      if (!await playPhase([settle], () => {
        orbit.style.transform = '';
        orbit.style.opacity = '';
      })) return;

      if (this.workspace !== workspace || this.introCancelled) return;
      paths.forEach(path => {
        path.style.strokeDasharray = '';
        path.style.strokeDashoffset = '';
        path.style.stroke = '';
        path.style.opacity = '';
      });
      this.introAnimations = [];
      workspace.dataset.intro = 'ready';
      this.render();
    }

    restorePdf() {
      this.handoffAnimation?.cancel();
      this.droneAnimation?.cancel();
      this.cancelIntroAnimations();
      window.removeEventListener('resize', this.resizeHandler);
      document.body.classList.remove('processing-experience-active');
    }

    renderModules() {
      if (!this.refs?.modules) return;
      this.refs.modules.replaceChildren();
      for (const module of MODULES) {
        const button = element('button', 'process-module');
        button.type = 'button';
        button.dataset.module = module.id;
        button.dataset.state = module.optional ? 'optional' : 'pending';
        button.title = module.detail;
        button.setAttribute('aria-label', `${module.label}. ${module.optional ? 'Optional stage. ' : ''}${module.detail}`);
        button.setAttribute('aria-pressed', 'false');
        const marker = element('span', 'process-module-marker', module.optional ? '·' : '○');
        marker.setAttribute('aria-hidden', 'true');
        const content = element('span', 'process-module-content');
        content.append(element('span', 'process-module-label', module.label), element('span', 'process-module-state', module.optional ? 'Optional' : 'Waiting'));
        button.append(marker, content);
        button.addEventListener('click', () => {
          this.refs.modules.querySelectorAll('.process-module').forEach(node => node.setAttribute('aria-pressed', String(node === button)));
          this.refs.moduleDetail.textContent = `${module.label} · ${module.detail}`;
        });
        this.refs.modules.append(button);
      }
    }

    scheduleDemo(delay = 1200) {
      clearTimeout(this.demoTimer);
      if (!this.demo || this.status === 'DEMO_COMPLETE') return;
      this.demoTimer = setTimeout(() => this.advanceDemo(), delay);
    }

    advanceDemo() {
      if (!this.demo || this.status === 'DEMO_COMPLETE') return;
      this.demoStageIndex += 1;
      if (this.demoStageIndex >= this.demoStages.length) {
        this.stage = 'completed';
        this.status = 'DEMO_COMPLETE';
        this.addLog('success', 'DEMO', 'Demo sequence ended locally. No analysis job or result was created.');
        this.render();
        return;
      }
      this.stage = this.demoStages[this.demoStageIndex];
      this.status = 'PROCESSING';
      this.addLog('processing', 'DEMO', STAGE_LABELS[this.stage] || this.stage);
      this.render();
      this.scheduleDemo(this.stage === 'fulltext_mapping' ? 4800 : 6600);
    }

    stageOrderIndex(stage = this.stage) { return ORDER.indexOf(stage); }

    render() {
      if (!this.workspace || !this.refs) return;
      if (this.status !== 'PROCESSING' && this.droneAnimation) {
        this.droneAnimation.cancel();
        this.droneAnimation = null;
      }
      this.workspace.dataset.status = this.demo && this.status !== 'DEMO_COMPLETE' ? 'PROCESSING' : this.status;
      this.workspace.dataset.stage = this.stage;
      this.workspace.dataset.demo = String(this.demo);
      this.refs.demoBadge.hidden = !this.demo;
      this.refs.documentDemoNote.hidden = !this.demo;
      this.refs.documentDemoSample.hidden = !this.demo;
      this.refs.status.dataset.status = this.demo ? this.status === 'DEMO_COMPLETE' ? 'DONE' : 'PROCESSING' : this.status;
      this.refs.statusLabel.textContent = this.demo ? this.status === 'DEMO_COMPLETE' ? 'Complete' : 'Simulating' : STATUS_LABELS[this.status] || this.status || 'Checking';
      this.refs.currentStage.textContent = this.demo
        ? this.status === 'DEMO_COMPLETE' ? 'Demo sequence complete' : `Demo · ${STAGE_LABELS[this.stage] || 'Preparing visual sequence'}`
        : this.status === 'FAILED' ? 'Analysis failed' : this.status === 'DONE' ? 'Analysis complete' : this.status === 'PENDING' ? 'Waiting in queue' : STAGE_LABELS[this.stage] || 'Waiting for backend stage';
      this.refs.retry.hidden = this.demo || this.status !== 'FAILED';
      this.refs.results.hidden = this.demo || this.status !== 'DONE';
      this.renderModulesState();
      const displayStage = ['fulltext_mapping_created','fulltext_mapping_reused'].includes(this.stage) ? 'review_draft' : this.stage;
      const activeModule = MODULES.find(module => module.stage === displayStage);
      this.refs.moduleDetail.dataset.state = this.demo ? 'demo' : this.status === 'FAILED' ? 'error' : 'info';
      this.refs.moduleDetail.textContent = this.demo
        ? this.status === 'DEMO_COMPLETE' ? 'Visual sequence complete · no analysis was run or saved.' : `${activeModule?.label || 'Document intake'} · simulated visual stage`
        : this.status === 'FAILED' ? this.paper.analysis_error || 'The backend reported a failure.'
        : this.status === 'PENDING' ? 'Queued · waiting for the analysis worker.'
        : activeModule?.detail || this.statusMessage();
      const introRunning = this.workspace.dataset.intro === 'running';
      this.refs.drone.dataset.idle = String(introRunning || this.status !== 'PROCESSING');
      if (!this.droneAnimation) {
        this.refs.drone.dataset.beamTarget = introRunning || this.status !== 'PROCESSING' || this.stage === 'starting' ? 'off' : this.stage === 'fulltext_mapping' ? 'paper' : 'module';
        this.refs.drone.style.setProperty('--drone-beam-alpha', !introRunning && this.status === 'PROCESSING' ? '1' : '0');
      }
      this.refs.connection.dataset.state = this.demo ? 'demo' : this.connection === 'connected' ? 'online' : 'offline';
      this.refs.connection.textContent = this.demo
        ? 'Demo · no analysis request or saved result.'
        : this.connection === 'connected'
        ? 'Connected · showing status transitions observed by this page.'
        : 'Connection issue · retrying status check. No new backend state has been observed.';
    }

    renderModulesState() {
      const current = this.stageOrderIndex();
      const mappedStage = ['fulltext_mapping_created','fulltext_mapping_reused'].includes(this.stage) ? 'review_draft' : this.stage === 'starting' ? 'fulltext_mapping' : this.stage;
      const currentModuleId = MODULES.find(module => module.stage === mappedStage)?.id || null;
      const previousActive = this.activeModuleId;
      for (const module of MODULES) {
        const button = this.refs.modules.querySelector(`[data-module="${module.id}"]`);
        if (!button) continue;
        const marker = button.querySelector('.process-module-marker');
        const stateNode = button.querySelector('.process-module-state');
        let state = 'pending';
        let label = 'Waiting';
        if (this.demo) {
          const moduleIndex = this.stageOrderIndex(module.stage);
          if (module.id === 'mapping' && this.paper.source_kind === 'markdown') { state = 'done'; label = 'Source ready'; }
          else if (this.status === 'DEMO_COMPLETE') { state = 'done'; label = 'Demo pass'; }
          else if (moduleIndex >= 0 && moduleIndex < current) { state = 'done'; label = 'Complete'; }
          else if (module.id === currentModuleId) { state = 'active'; label = 'Analyzing'; }
          else { state = 'pending'; label = 'In queue'; }
        } else if (module.optional) {
          state = this.optional[module.id] || 'optional';
          if (state === 'optional') label = 'Optional';
          else if (state === 'done') label = 'Complete';
          else if (state === 'failed') label = 'Unavailable';
          else if (state === 'active') label = 'Running';
          else label = state === 'unavailable' ? 'Unavailable' : state;
        } else if (this.status === 'DONE' && module.id === 'profile') {
          state = this.profileState;
          label = state === 'checking' ? 'Checking' : state === 'failed' ? 'Failed' : state === 'partial' ? 'Partial' : state === 'unavailable' ? 'Unavailable' : 'Complete';
        } else if (this.status === 'DONE') {
          state = module.id === 'mapping' || this.stageOrderIndex(module.stage) <= ORDER.indexOf('paper_profile') ? 'done' : 'pending';
          label = state === 'done' ? 'Complete' : 'Not reported';
        } else if (this.status === 'FAILED') {
          const moduleIndex = this.stageOrderIndex(module.stage);
          if (current >= 0 && moduleIndex >= 0 && moduleIndex < current) { state = 'done'; label = 'Complete'; }
          else if (module.stage === this.stage || (current < 0 && module.id === 'mapping')) { state = 'failed'; label = 'Failed'; }
          else { state = 'pending'; label = 'Not reached'; }
        } else if (this.paper.source_kind === 'markdown' && module.id === 'mapping') {
          state = 'done'; label = 'Source ready';
        } else if (current >= 0) {
          const moduleIndex = this.stageOrderIndex(module.stage);
          if (moduleIndex >= 0 && moduleIndex < current) { state = 'done'; label = 'Complete'; }
          else if (module.id === currentModuleId) { state = 'active'; label = 'Running'; }
          else { state = 'pending'; label = 'Waiting'; }
        } else if (this.status === 'PROCESSING' && this.stage === 'starting' && module.id === 'mapping') {
          state = 'active'; label = 'Starting';
        }
        button.dataset.state = state;
        stateNode.textContent = label;
        marker.textContent = state === 'done' ? '✓' : state === 'failed' ? '!' : state === 'active' ? '' : module.optional ? '·' : '○';
      }
      const activeNode = this.refs.modules.querySelector('.process-module[data-state="active"], .process-module[data-state="failed"]');
      const nextActive = activeNode?.dataset.module || null;
      const fromIndex = MODULES.findIndex(module => module.id === previousActive);
      const toIndex = MODULES.findIndex(module => module.id === nextActive);
      this.refs.stage.querySelectorAll('.process-flow-link').forEach((path, index) => {
        const from = this.refs.modules.querySelector(`[data-module="${MODULES[index].id}"]`);
        const to = this.refs.modules.querySelector(`[data-module="${MODULES[index + 1].id}"]`);
        const done = from?.dataset.state === 'done' && ['done','active'].includes(to?.dataset.state);
        path.dataset.state = index === fromIndex && index + 1 === toIndex ? 'active' : done ? 'done' : 'pending';
      });
      const shouldHandoff = previousActive && nextActive && previousActive !== nextActive && this.status !== 'FAILED';
      if (shouldHandoff) {
        this.animateHandoff(previousActive, nextActive);
        this.animateDroneHandoff(previousActive, nextActive);
      }
      if (nextActive) this.activeModuleId = nextActive;
      else if (['DONE','FAILED','DEMO_COMPLETE'].includes(this.status)) this.activeModuleId = null;
      if (!shouldHandoff) this.syncDroneToModule(nextActive);
    }

    animateHandoff(fromId, toId) {
      if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      const from = this.refs.modules.querySelector(`[data-module="${fromId}"]`);
      const to = this.refs.modules.querySelector(`[data-module="${toId}"]`);
      if (!from || !to) return;
      const stageRect = this.refs.stage.getBoundingClientRect();
      const a = from.getBoundingClientRect();
      const b = to.getBoundingClientRect();
      const sx = a.left + a.width / 2 - stageRect.left;
      const sy = a.top + a.height / 2 - stageRect.top;
      const ex = b.left + b.width / 2 - stageRect.left;
      const ey = b.top + b.height / 2 - stageRect.top;
      const dx = ex - sx;
      const dy = ey - sy;
      const distance = Math.max(1, Math.hypot(dx, dy));
      const mx = (sx + ex) / 2 - (dy / distance) * 20;
      const my = (sy + ey) / 2 + (dx / distance) * 20;
      this.handoffAnimation?.cancel();
      this.handoffAnimation = this.refs.flowOrb.animate([
        { transform: `translate3d(${sx}px,${sy}px,0) scale(.65)`, opacity: 0, offset: 0 },
        { transform: `translate3d(${sx}px,${sy}px,0) scale(1)`, opacity: 1, offset: .14 },
        { transform: `translate3d(${mx}px,${my}px,0) scale(1)`, opacity: 1, offset: .66 },
        { transform: `translate3d(${ex}px,${ey}px,0) scale(.75)`, opacity: 0, offset: 1 },
      ], { duration: 760, easing: 'cubic-bezier(.23,1,.32,1)' });
    }

    syncDroneToModule(moduleId) {
      if (['starting','fulltext_mapping'].includes(this.stage)) moduleId = null;
      const node = moduleId && this.refs.modules.querySelector(`[data-module="${moduleId}"]`);
      const stageRect = this.refs.stage.getBoundingClientRect();
      const rect = node?.getBoundingClientRect();
      const dx = rect ? rect.left + rect.width / 2 - (stageRect.left + stageRect.width / 2) : 0;
      const dy = rect ? rect.top + rect.height / 2 - (stageRect.top + stageRect.height / 2) - 64 : -24;
      this.refs.drone.style.setProperty('--drone-x', `${Math.round(dx)}px`);
      this.refs.drone.style.setProperty('--drone-y', `${Math.round(dy)}px`);
    }

    animateDroneHandoff(fromId, toId) {
      if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      const from = this.refs.modules.querySelector(`[data-module="${fromId}"]`);
      const to = this.refs.modules.querySelector(`[data-module="${toId}"]`);
      const paper = this.workspace.querySelector('.process-document');
      if (!from || !to || !paper) return;
      const stageRect = this.refs.stage.getBoundingClientRect();
      const fromRect = from.getBoundingClientRect();
      const paperRect = paper.getBoundingClientRect();
      const toRect = to.getBoundingClientRect();
      const targetX = toRect.left + toRect.width / 2;
      const targetY = toRect.top + toRect.height / 2 - 64;
      const transformAt = (x, y) => `translate3d(calc(-50% + ${Math.round(x - stageRect.left - stageRect.width / 2)}px),calc(-50% + ${Math.round(y - stageRect.top - stageRect.height / 2)}px),0)`;
      const drone = this.refs.drone;
      const transition = drone.style.transition;
      drone.style.transition = 'none';
      drone.style.setProperty('--drone-x', `${Math.round(targetX - stageRect.left - stageRect.width / 2)}px`);
      drone.style.setProperty('--drone-y', `${Math.round(targetY - stageRect.top - stageRect.height / 2)}px`);
      void drone.offsetWidth;
      drone.style.transition = transition;
      const paperX = paperRect.left + paperRect.width / 2;
      const scanTop = paperRect.top + 30;
      const scanBottom = paperRect.bottom - Math.min(126, Math.max(86, window.innerHeight * .11));
      const approachX = paperX + (targetX - paperX) * .88;
      const approachY = scanBottom + (targetY - scanBottom) * .88;
      this.droneAnimation?.cancel();
      drone.dataset.beamTarget = 'paper';
      drone.style.setProperty('--drone-beam-alpha', '0');
      this.droneAnimation = drone.animate([
        { transform: transformAt(fromRect.left + fromRect.width / 2, fromRect.top + fromRect.height / 2 - 64), '--drone-beam-alpha': 0, offset: 0, easing: 'cubic-bezier(.35,0,.25,1)' },
        { transform: transformAt(paperX, scanTop), '--drone-beam-alpha': 0, offset: .22, easing: 'linear' },
        { transform: transformAt(paperX, scanTop), '--drone-beam-alpha': 1, offset: .26, easing: 'linear' },
        { transform: transformAt(paperX, scanBottom), '--drone-beam-alpha': 1, offset: .68, easing: 'linear' },
        { transform: transformAt(paperX, scanBottom), '--drone-beam-alpha': 0, offset: .71, easing: 'linear' },
        { transform: transformAt(paperX, scanBottom), '--drone-beam-alpha': 0, offset: .74, easing: 'cubic-bezier(.25,.1,.25,1)' },
        { transform: transformAt(approachX, approachY), '--drone-beam-alpha': 0, offset: .9, easing: 'linear' },
        { transform: transformAt(targetX, targetY), '--drone-beam-alpha': 1, offset: .97, easing: 'linear' },
        { transform: transformAt(targetX, targetY), '--drone-beam-alpha': 1, offset: 1 },
      ], { duration: 5000, easing: 'cubic-bezier(.3,0,.2,1)' });
      const animation = this.droneAnimation;
      animation.onfinish = () => {
        if (this.droneAnimation !== animation) return;
        drone.dataset.beamTarget = 'module';
        drone.style.setProperty('--drone-beam-alpha', '1');
        this.droneAnimation = null;
      };
    }
    statusMessage() {
      if (this.status === 'FAILED') return this.paper.analysis_error || 'The backend reported that this analysis run failed.';
      if (this.status === 'PENDING') return 'The paper is queued. The scanner starts when the worker reports that extraction has begun.';
      return STAGE_LABELS[this.stage] || 'Waiting for the next backend status update.';
    }

    logSnapshot() {
      if (this.demo) {
        this.addLog('info', 'DEMO', 'Local preview started. Backend analysis and result endpoints were not called.');
        return;
      }
      const message = this.status === 'FAILED'
        ? `Backend reports failure${this.paper.analysis_error ? ': ' + this.paper.analysis_error : '.'}`
        : `${STATUS_LABELS[this.status] || this.status}${this.stage ? ` | ${STAGE_LABELS[this.stage] || this.stage}` : ''}`;
      this.addLog(this.status === 'FAILED' ? 'error' : this.status === 'DONE' ? 'success' : 'info', 'OBSERVED', message);
    }

    addLog(level, tag, message) {
      if (!this.refs?.logs) return;
      const log = { time: new Date().toLocaleTimeString([], { hour12: false }), level, tag, message };
      this.logs.push(log);
      if (this.logs.length > MAX_LOGS) this.logs.splice(0, this.logs.length - MAX_LOGS);
      const wasAtBottom = this.refs.logs.scrollHeight - this.refs.logs.scrollTop - this.refs.logs.clientHeight < 40;
      const row = element('div', 'process-log-row');
      row.dataset.level = level;
      row.append(element('span', 'process-log-time', log.time), element('span', 'process-log-tag', tag), element('span', 'process-log-message', message));
      this.refs.logs.append(row);
      while (this.refs.logs.children.length > MAX_LOGS) this.refs.logs.firstElementChild.remove();
      if (wasAtBottom) this.refs.logs.scrollTop = this.refs.logs.scrollHeight;
    }

    async copyLogs() {
      const content = this.logs.map(log => `[${log.time}] ${log.tag.padEnd(8)} ${log.message}`).join('\n');
      try {
        await navigator.clipboard.writeText(content);
        this.refs.copy.textContent = 'Copied';
        setTimeout(() => { if (this.refs?.copy) this.refs.copy.textContent = 'Copy log'; }, 1400);
      } catch {
        this.refs.copy.textContent = 'Copy unavailable';
        setTimeout(() => { if (this.refs?.copy) this.refs.copy.textContent = 'Copy log'; }, 1800);
      }
    }

    schedulePoll(delay = POLL_MS) {
      clearTimeout(this.pollTimer);
      if (this.stopped || !['PENDING','PROCESSING'].includes(this.status)) return;
      this.pollTimer = setTimeout(() => void this.poll(), delay);
    }

    async poll() {
      if (this.polling || this.stopped) return;
      this.polling = true;
      try {
        const response = await fetch('/api/analysis/papers', { cache: 'no-store' });
        if (!response.ok) throw new Error(`Paper status request failed (HTTP ${response.status}).`);
        const data = await response.json();
        const paper = (data.papers || []).find(item => item.doi === this.paper.doi);
        if (!paper) throw new Error('The paper is no longer present in the analysis library response.');
        if (this.connection === 'offline') this.addLog('info', 'CONNECTION', 'Status polling resumed.');
        this.connection = 'connected';
        this.update(paper);
      } catch (error) {
        if (this.connection !== 'offline') this.addLog('error', 'CONNECTION', error.message);
        this.connection = 'offline';
        this.refs.connection.title = error.message;
        this.refs.consoleMeta.textContent = 'Connection lost | retrying';
        this.render();
      } finally {
        this.polling = false;
        this.schedulePoll(POLL_MS);
      }
    }

    update(paper) {
      const previousStatus = this.status;
      const previousStage = this.stage;
      this.paper = { ...this.paper, ...paper };
      this.status = paper.analysis_status || this.status;
      this.stage = this.status === 'PENDING' ? '' : paper.analysis_stage || '';
      this.refs.consoleMeta.textContent = 'Observed backend status | 5-second polling';
      if (this.status !== previousStatus || this.stage !== previousStage) {
        const label = this.stage ? STAGE_LABELS[this.stage] || this.stage : STATUS_LABELS[this.status] || this.status;
        const level = this.status === 'FAILED' ? 'error' : this.status === 'DONE' ? 'success' : 'processing';
        this.addLog(level, this.stage ? 'STAGE' : 'STATUS', `${STATUS_LABELS[this.status] || this.status} | ${label}`);
        if (this.status === 'FAILED' && this.paper.analysis_error) this.addLog('error', 'ERROR', this.paper.analysis_error);
      }
      this.render();
      if (this.status === 'DONE') {
        this.stopped = true;
        clearTimeout(this.pollTimer);
        void this.loadCompletedArtifacts();
      } else if (this.status === 'FAILED') {
        this.stopped = true;
        clearTimeout(this.pollTimer);
      }
    }

    async retry() {
      this.refs.retry.disabled = true;
      this.refs.retry.textContent = 'Submitting...';
      try {
        const response = await fetch('/api/analysis/enqueue', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ dois: [this.paper.doi], provider: this.paper.analysis_provider || document.getElementById('provider')?.value || 'ollama' }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || `Retry request failed (HTTP ${response.status}).`);
        this.paper.analysis_error = '';
        this.paper.analysis_provider = this.paper.analysis_provider || document.getElementById('provider')?.value || 'ollama';
        this.status = data.queued?.length ? 'PENDING' : 'PROCESSING';
        this.stage = '';
        this.stopped = false;
        this.connection = 'connected';
        this.addLog('info', 'REQUEST', data.queued?.length ? 'Retry accepted and added to the backend queue.' : 'Retry request submitted; checking the latest backend status.');
        this.refs.retry.hidden = true;
        this.refs.retry.textContent = 'Retry analysis';
        this.render();
        this.schedulePoll(0);
      } catch (error) {
        this.paper.analysis_error = error.message;
        this.addLog('error', 'ERROR', error.message);
        this.refs.retry.disabled = false;
        this.refs.retry.textContent = 'Retry analysis';
      }
    }

    async loadCompletedArtifacts() {
      if (!this.workspace || this.workspace.dataset.artifactsLoaded === 'true') return;
      this.workspace.dataset.artifactsLoaded = 'true';
      const requests = [fetch('/api/analysis/argumentation/' + encodeURIComponent(this.paper.doi), { cache: 'no-store' })];
      if (this.paper.source_kind === 'pdf') requests.push(fetch('/api/analysis/atomic/stance-engagement/' + encodeURIComponent(this.paper.doi), { cache: 'no-store' }));
      const results = await Promise.allSettled(requests);
      const argumentationResponse = results[0]?.status === 'fulfilled' ? results[0].value : null;
      if (argumentationResponse?.ok) {
        try {
          const payload = (await argumentationResponse.json()).argumentation || {};
          const profileStatus = String(payload.analysis_payload?.paper_profile?.status || '').toUpperCase();
          this.profileState = profileStatus === 'FAILED' ? 'failed' : profileStatus === 'PARTIAL' ? 'partial' : profileStatus ? 'done' : 'unavailable';
        } catch {
          this.profileState = 'unavailable';
        }
      } else {
        this.profileState = 'unavailable';
      }
      if (this.paper.source_kind === 'pdf' && results[1]?.status === 'fulfilled') {
        const response = results[1].value;
        if (response.ok) {
          try { const data = await response.json(); this.optional.stance = data.result && !data.stale ? 'done' : 'unavailable'; }
          catch { this.optional.stance = 'unavailable'; }
        } else this.optional.stance = response.status === 404 ? 'unavailable' : 'failed';
      }
      try {
        const response = await fetch('/api/analysis/draft/' + encodeURIComponent(this.paper.doi), { cache: 'no-store' });
        if (response.ok) {
          const data = await response.json();
          const state = String(data.analysis?.draft?.saffron_analysis?.status || '').toUpperCase();
          this.optional.saffron = ['DONE','NO_TERMS','PARTIAL'].includes(state) ? 'done' : 'unavailable';
        } else this.optional.saffron = 'unavailable';
      } catch { this.optional.saffron = 'unavailable'; }
      this.render();
    }
    async viewResults() {
      this.stopped = true;
      clearTimeout(this.pollTimer);
      this.restorePdf();
      this.workspace?.remove();
      this.workspace = null;
      if (this.onViewResults) await this.onViewResults(this.paper);
    }
  }

  window.AnalysisProcessingExperience = AnalysisProcessingExperience;
})();
