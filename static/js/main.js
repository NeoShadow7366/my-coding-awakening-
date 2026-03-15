'use strict';

// Keep all tabs on one origin so lease-based polling coordination works reliably.
if (window.location.hostname === 'localhost') {
	const canonicalUrl = new URL(window.location.href);
	canonicalUrl.hostname = '127.0.0.1';
	window.location.replace(canonicalUrl.toString());
}

/* --------------------------------------------------------------------------
	 DOM references
	 -------------------------------------------------------------------------- */
const themeToggle = document.getElementById('theme-toggle');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const navGenerative = document.getElementById('nav-generative');
const navImage = document.getElementById('nav-image');
const navConfig = document.getElementById('nav-config');
const navModels = document.getElementById('nav-models');
const panelGen = document.getElementById('panel-generative');
const panelImage = document.getElementById('panel-image');
const panelConfig = document.getElementById('panel-config');
const panelModels = document.getElementById('panel-models');
const mbSearchBtn = document.getElementById('mb-search-btn');
const mbSearchQuery = document.getElementById('mb-search-query');
const mbSearchType = document.getElementById('mb-search-type');
const mbLibraryRefreshBtn = document.getElementById('mb-library-refresh-btn');
const mbLibraryGrid = document.getElementById('mb-library-grid');
const mbLibraryStatus = document.getElementById('mb-library-status');
const mbResultsSection = document.getElementById('mb-results-section');
const mbResultsGrid = document.getElementById('mb-results-grid');
const mbResultsCount = document.getElementById('mb-results-count');
const mbSearchStatus = document.getElementById('mb-search-status');
const mbDownloadsSection = document.getElementById('mb-downloads-section');
const mbDownloadsList = document.getElementById('mb-downloads-list');
const mbPrevPage = document.getElementById('mb-prev-page');
const mbNextPage = document.getElementById('mb-next-page');
const mbPageInfo = document.getElementById('mb-page-info');

// Text panel
const modelSelect = document.getElementById('gen-model-select');
const systemPrompt = document.getElementById('system-prompt');
const textNegativePrompt = document.getElementById('text-negative-prompt');
const textSeed = document.getElementById('text-seed');
const textRandomSeed = document.getElementById('text-random-seed');
const textTemperature = document.getElementById('text-temperature');
const textTemperatureVal = document.getElementById('text-temperature-val');
const textTopP = document.getElementById('text-top-p');
const textTopPVal = document.getElementById('text-top-p-val');
const textTopK = document.getElementById('text-top-k');
const textNumPredict = document.getElementById('text-num-predict');
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const clearChat = document.getElementById('clear-chat');

// Image panel
const imageModelSelect = document.getElementById('image-model-select');
const imageSamplerSelect = document.getElementById('image-sampler-select');
const imageSeed = document.getElementById('image-seed');
const imageRandomSeed = document.getElementById('image-random-seed');
const imageProfileSelect = document.getElementById('image-profile-select');
const imageProfileName = document.getElementById('image-profile-name');
const imageProfileSaveBtn = document.getElementById('image-profile-save');
const imageProfileApplyBtn = document.getElementById('image-profile-apply');
const imageProfileDeleteBtn = document.getElementById('image-profile-delete');
const imageSteps = document.getElementById('image-steps');
const imageStepsVal = document.getElementById('image-steps-val');
const imageCfg = document.getElementById('image-cfg');
const imageCfgVal = document.getElementById('image-cfg-val');
const imageDenoise = document.getElementById('image-denoise');
const imageDenoiseVal = document.getElementById('image-denoise-val');
const imageEngineStatus = document.getElementById('image-engine-status');
const imageForm = document.getElementById('image-form');
const imagePrompt = document.getElementById('image-prompt');
const promptRandomizeBtn = document.getElementById('prompt-randomize-btn');
const normalPromptWrap = document.getElementById('normal-prompt-wrap');
const promptModeHint = document.getElementById('prompt-mode-hint');
const enhancedPromptToggle = document.getElementById('enhanced-prompt-toggle');
const enhancedPromptFields = document.getElementById('enhanced-prompt-fields');
const enhancedSubject = document.getElementById('enhanced-subject');
const enhancedSetting = document.getElementById('enhanced-setting');
const enhancedComposition = document.getElementById('enhanced-composition');
const enhancedLighting = document.getElementById('enhanced-lighting');
const enhancedStyle = document.getElementById('enhanced-style');
const enhancedPromptSuggestBtn = document.getElementById('enhanced-prompt-suggest-btn');
const enhancedPromptBuildBtn = document.getElementById('enhanced-prompt-build-btn');
const enhancedPromptRandomBtn = document.getElementById('enhanced-prompt-random-btn');
const enhancedPromptUseBtn = document.getElementById('enhanced-prompt-use-btn');
const enhancedPromptSelect = document.getElementById('enhanced-prompt-select');
const enhancedPromptUseSelectedBtn = document.getElementById('enhanced-prompt-use-selected-btn');
const enhancedPromptStatus = document.getElementById('enhanced-prompt-status');
const enhancedPromptSuggestionsOutput = document.getElementById('enhanced-prompt-suggestions');
const imageNegativePrompt = document.getElementById('image-negative-prompt');
const imageWidth = document.getElementById('image-width');
const imageHeight = document.getElementById('image-height');
const imageBatchSize = document.getElementById('image-batch-size');
const imageUpload = document.getElementById('image-upload');
const imageGenerateBtn = document.getElementById('image-generate-btn');
const queueTelemetry = document.getElementById('queue-telemetry');
const queueTelemetryResetBtn = document.getElementById('queue-telemetry-reset');
const queueSummary = document.getElementById('queue-summary');
const queueList = document.getElementById('queue-list');
const configOllamaPath = document.getElementById('config-ollama-path');
const configComfyuiPath = document.getElementById('config-comfyui-path');
const configOllamaBrowseBtn = document.getElementById('config-ollama-browse');
const configComfyuiBrowseBtn = document.getElementById('config-comfyui-browse');
const configSaveBtn = document.getElementById('config-save-btn');
const configSaveStatus = document.getElementById('config-save-status');
const configLastSaved = document.getElementById('config-last-saved');
const configOllamaStartBtn = document.getElementById('config-ollama-start');
const configOllamaRestartBtn = document.getElementById('config-ollama-restart');
const configOllamaStopBtn = document.getElementById('config-ollama-stop');
const configComfyStartBtn = document.getElementById('config-comfy-start');
const configComfyRestartBtn = document.getElementById('config-comfy-restart');
const configComfyStopBtn = document.getElementById('config-comfy-stop');
const configFlaskRestartBtn = document.getElementById('config-flask-restart');
const configOllamaStatus = document.getElementById('config-ollama-status');
const configComfyStatus = document.getElementById('config-comfy-status');
const configFlaskStatus = document.getElementById('config-flask-status');
const tagCategorySelect = document.getElementById('tag-category-select');
const tagNewInput = document.getElementById('tag-new-input');
const tagAddBtn = document.getElementById('tag-add-btn');
const tagEditorList = document.getElementById('tag-editor-list');
const tagManagerStatus = document.getElementById('tag-manager-status');
const tagResetDefaultsBtn = document.getElementById('tag-reset-defaults-btn');
const diagnosticsRunBtn = document.getElementById('diagnostics-run-btn');
const diagnosticsSummary = document.getElementById('diagnostics-summary');
const diagnosticsHint = document.getElementById('diagnostics-hint');
const diagTextStatus = document.getElementById('diag-text-status');
const diagImageStatus = document.getElementById('diag-image-status');
const diagCheckpoints = document.getElementById('diag-checkpoints');
const diagSamplers = document.getElementById('diag-samplers');
const diagLastRun = document.getElementById('diag-last-run');
const pollOwnerStatus = document.getElementById('poll-owner-status');
const diagDrawer = document.getElementById('diag-drawer');
const diagDrawerToggle = document.getElementById('diag-drawer-toggle');
const diagStatusBadge = document.getElementById('diag-status-badge');
const diagDrawerClose = document.getElementById('diag-drawer-close');
const diagDrawerOutput = document.getElementById('diag-drawer-output');
const diagDrawerCommandForm = document.getElementById('diag-drawer-command-form');
const diagDrawerCommandInput = document.getElementById('diag-drawer-command');
const autoRetryPolicy = document.getElementById('auto-retry-policy');
const failedOnlyToggle = document.getElementById('failed-only-toggle');
const clearFailedQueueBtn = document.getElementById('clear-failed-queue');
const clearCompletedQueueBtn = document.getElementById('clear-completed-queue');
const toastContainer = document.getElementById('toast-container');

if (queueSummary) {
	queueSummary.setAttribute('aria-live', 'polite');
}
const refreshGalleryBtn = document.getElementById('refresh-gallery');
const galleryGrid = document.getElementById('gallery-grid');
const galleryLightbox = document.getElementById('gallery-lightbox');
const galleryLightboxImage = document.getElementById('gallery-lightbox-image');
const galleryLightboxCaption = document.getElementById('gallery-lightbox-caption');
const galleryLightboxCloseBtn = document.getElementById('gallery-lightbox-close');
const galleryContextMenu = document.getElementById('gallery-context-menu');
const gallerySearch = document.getElementById('gallery-search');
const galleryViewToggle = document.getElementById('gallery-view-toggle');
const galleryFilterHint = document.getElementById('gallery-filter-hint');
const galleryLightboxPrev = document.getElementById('gallery-lightbox-prev');
const galleryLightboxNext = document.getElementById('gallery-lightbox-next');
const galleryLightboxCounter = document.getElementById('gallery-lightbox-counter');
const imagePresetButtons = document.querySelectorAll('[data-image-preset]');
const previewUpdated = document.getElementById('preview-updated');
const previewEmpty = document.getElementById('preview-empty');
const previewImage = document.getElementById('preview-image');
const previewMeta = document.getElementById('preview-meta');
const previewPrompt = document.getElementById('preview-prompt');
const previewChipRow = document.getElementById('preview-chip-row');
const previewCard = document.querySelector('.preview-card');

/* --------------------------------------------------------------------------
	 State
	 -------------------------------------------------------------------------- */
let isGenerating = false;
let queuePollTimer = null;
let livePreviewTimer = null;
let statusPollTimer = null;
let pollLeaseTimer = null;
const trackedPromptIds = new Set();
const pendingImageJobs = new Map();
const queueJobMeta = new Map();
let enhancedPromptSuggestions = [];
const JOB_MISS_THRESHOLD = 4;
const queueActionInFlight = new Set();
let queueFilterFailedOnly = localStorage.getItem('queueFilterFailedOnly') === '1';
const IMAGE_PROFILE_STORAGE_KEY = 'imagePresetProfilesV1';
const IMAGE_PROFILE_SELECTED_KEY = 'imagePresetProfilesSelectedV1';
const QUEUE_TELEMETRY_KEY = 'queueTelemetryV1';
const BACKGROUND_POLL_OWNER_KEY = 'backgroundPollOwnerV1';
const BACKGROUND_POLL_LEASE_MS = 10_000;
const BACKGROUND_POLL_HEARTBEAT_MS = 3_000;
const tabInstanceId = `tab-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
let hasBackgroundPollingOwnership = false;
const SUGGESTION_TAG_STORAGE_KEY = 'imageSuggestionTagsV1';
let galleryContextPayload = null;
let previewZoomScale = 1;
const PREVIEW_ZOOM_MIN = 0.7;
const PREVIEW_ZOOM_MAX = 3;
const PREVIEW_ZOOM_STEP = 0.12;
let currentGalleryImages = [];
let currentFullHistory = [];
let galleryViewMode = localStorage.getItem('galleryViewMode') || 'list';
let gallerySearchQuery = '';
let lightboxCurrentIndex = 0;
const TAG_CATEGORY_LABELS = {
	'enhanced-subject': 'Subject',
	'enhanced-setting': 'Setting/Environment',
	'enhanced-composition': 'Composition & Framing',
	'enhanced-lighting': 'Lighting',
	'enhanced-style': 'Style/Medium',
	'image-negative-prompt': 'Negative Prompt',
};
const DEFAULT_SUGGESTION_TAGS = {
	'enhanced-subject': [
		'portrait', 'full body', 'character design', 'creature concept', 'mech pilot', 'ancient warrior', 'cyberpunk detective', 'forest spirit',
		'samurai', 'astronaut', 'witch', 'dragon', 'fox familiar', 'robot companion', 'old sailor', 'elven ranger',
		'desert nomad', 'knight armor', 'street vendor', 'masked assassin', 'scholar alchemist', 'giant golem', 'mermaid', 'time traveler',
		'musician', 'dancer', 'child adventurer', 'elderly monk', 'pirate captain', 'bounty hunter', 'shapeshifter', 'royal queen',
		'royal king', 'blacksmith', 'beekeeper', 'falconer', 'explorer', 'scientist', 'chef', 'bard',
	],
	'enhanced-setting': [
		'misty forest', 'neon city alley', 'abandoned temple', 'floating islands', 'ancient ruins', 'underwater palace', 'desert canyon', 'snowy mountain pass',
		'volcanic crater', 'moon base', 'starship bridge', 'steampunk workshop', 'medieval tavern', 'rainy rooftop', 'haunted mansion', 'cyber lab',
		'bamboo grove', 'coral reef', 'arctic tundra', 'crystal cave', 'market street', 'cathedral interior', 'throne room', 'battlefield at dawn',
		'hidden village', 'tropical beach', 'frozen lake', 'overgrown greenhouse', 'canyon overlook', 'lighthouse cliff', 'subway station', 'wasteland highway',
		'enchanted library', 'observatory dome', 'waterfall grotto', 'cloud kingdom', 'swamp marsh', 'harbor dock', 'festival plaza', 'palace garden',
	],
	'enhanced-composition': [
		"close-up portrait", 'medium shot', 'wide shot', 'full body shot', 'extreme close-up', 'over-the-shoulder', 'low angle', 'high angle',
		"bird's-eye view", "worm's-eye view", 'dutch angle', 'centered composition', 'rule of thirds', 'symmetrical framing', 'leading lines', 'negative space',
		'cinematic framing', 'dynamic perspective', 'depth layering', 'foreground framing', 'silhouette composition', 'profile view', 'three-quarter view', 'back view',
		'action freeze frame', 'motion blur framing', 'macro detail shot', 'panoramic view', 'isometric view', 'top-down layout', 'diagonal composition', 'shallow depth of field',
		'deep focus', 'bokeh foreground', 'off-center subject', 'portrait orientation', 'landscape orientation', 'split framing', 'environmental portrait', 'establishing shot',
	],
	'enhanced-lighting': [
		'golden hour', 'blue hour', 'soft diffused light', 'hard sunlight', 'overcast light', 'dramatic rim light', 'backlit subject', 'volumetric god rays',
		'neon glow', 'moonlit scene', 'candlelight', 'firelight', 'studio key light', 'three-point lighting', 'low key lighting', 'high key lighting',
		'chiaroscuro', 'bioluminescent glow', 'underlighting', 'sidelighting', 'top lighting', 'practical lights', 'color gel lighting', 'warm color temperature',
		'cool color temperature', 'flickering light', 'fog light beams', 'storm lightning flashes', 'sunset gradient light', 'sunrise haze', 'reflected bounce light', 'ambient occlusion emphasis',
		'HDR lighting', 'global illumination', 'subsurface glow', 'silhouette backlight', 'lens flare highlights', 'softbox portrait light', 'rim and fill balance', 'mixed lighting sources',
	],
	'enhanced-style': [
		'cinematic photography', 'concept art', 'matte painting', 'digital painting', 'oil painting', 'watercolor', 'ink illustration', 'pencil sketch',
		'charcoal drawing', 'anime style', 'manga screentone', 'comic book style', 'pixel art', 'low poly 3d', 'photorealistic render', 'stylized 3d render',
		'clay render', 'voxel art', 'art nouveau', 'art deco', 'baroque painting', 'impressionist brushwork', 'surrealism', 'vaporwave aesthetic',
		'synthwave palette', 'minimalism', 'maximalism', 'brutalist graphic style', 'ukiyo-e print', 'noir style', 'fantasy realism', 'sci-fi realism',
		'dark fantasy', "children's book illustration", 'poster design', 'blueprint technical art', 'collage mixed media', 'glitch art', 'line art', 'cel shading',
	],
	'image-negative-prompt': [
		'lowres', 'worst quality', 'low quality', 'normal quality', 'jpeg artifacts', 'blurry', 'out of focus', 'soft focus', 'motion blur', 'gaussian blur',
		'noise', 'grainy', 'pixelated', 'aliased edges', 'banding', 'washed out colors', 'overexposed', 'underexposed', 'bad contrast', 'oversaturated',
		'undersaturated', 'color bleeding', 'chromatic aberration', 'lens distortion', 'vignette', 'watermark', 'signature', 'text', 'logo', 'frame',
		'border', 'cropped', 'out of frame', 'cut off', 'duplicate', 'cloned face', 'extra limbs', 'extra arms', 'extra legs', 'extra fingers',
		'fused fingers', 'missing fingers', 'malformed hands', 'bad hands', 'mutated hands', 'long neck', 'deformed anatomy', 'bad anatomy', 'disfigured', 'distorted face',
		'asymmetrical eyes', 'cross-eye', 'lazy eye', 'bad proportions', 'unrealistic proportions', 'floating limbs', 'detached limbs', 'twisted torso', 'unnatural pose', 'bad perspective',
		'incorrect shadows', 'inconsistent lighting', 'flat lighting', 'low detail', 'lack of texture', 'muddy details', 'messy background', 'cluttered composition', 'artifacts', 'compression artifacts',
		'posterization', 'moire pattern', 'tiling', 'repeating patterns', 'double pupils', 'uneven pupils', 'skin blemishes', 'acne', 'blotchy skin', 'plastic skin',
		'waxy skin', 'over-sharpened', 'haloing', 'ghosting', 'duplicate body', 'extra head', 'missing ears', 'malformed ears', 'bad teeth', 'distorted mouth',
		'nsfw', 'nude', 'censored', 'blood', 'gore', 'violent', 'scary face', 'creepy smile', 'unfinished', 'draft',
	],
};
let suggestionTagStore = {};

function getQueueTelemetryState() {
	try {
		const parsed = JSON.parse(sessionStorage.getItem(QUEUE_TELEMETRY_KEY) || '{}');
		return {
			submitted: Number(parsed.submitted || 0),
			canceled: Number(parsed.canceled || 0),
			retried: Number(parsed.retried || 0),
			failed: Number(parsed.failed || 0),
		};
	} catch {
		return { submitted: 0, canceled: 0, retried: 0, failed: 0 };
	}
}

let queueTelemetryState = getQueueTelemetryState();
let lastDiagnosticsLogKey = '';
const diagHistory = [];
let diagHistoryIndex = -1;
let diagHistoryDraft = '';

function appendDiagnosticsConsoleLine(text, level = 'info') {
	if (!diagDrawerOutput) return;
	const row = document.createElement('p');
	row.className = `diag-line ${level}`.trim();
	row.textContent = text;
	diagDrawerOutput.appendChild(row);
	while (diagDrawerOutput.childElementCount > 250) {
		diagDrawerOutput.removeChild(diagDrawerOutput.firstChild);
	}
	diagDrawerOutput.scrollTop = diagDrawerOutput.scrollHeight;
}

function setDiagnosticsDrawerOpen(isOpen) {
	if (!diagDrawer) return;
	diagDrawer.hidden = !isOpen;
	if (diagDrawerToggle) {
		diagDrawerToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
	}
	if (isOpen && diagDrawerCommandInput) {
		diagDrawerCommandInput.focus();
	}
}

function getDiagnosticsStatusSnapshotText() {
	const text = diagTextStatus?.textContent || 'unknown';
	const image = diagImageStatus?.textContent || 'unknown';
	const checkpoints = diagCheckpoints?.textContent || '-';
	const samplers = diagSamplers?.textContent || '-';
	const summary = diagnosticsSummary?.textContent || 'Diagnostics unavailable';
	return `${summary} | text=${text} image=${image} checkpoints=${checkpoints} samplers=${samplers}`;
}

async function appendServiceDiagnosticLogs(service = 'comfyui') {
	try {
		const res = await fetch('/api/diagnostics/service-logs');
		const data = await res.json();
		if (!res.ok) {
			appendDiagnosticsConsoleLine('Could not fetch service diagnostics logs.', 'warn');
			return;
		}

		const errorText = data?.errors?.[service] || '';
		const logText = data?.logs?.[service] || '';
		if (errorText) {
			appendDiagnosticsConsoleLine(`${service} error: ${errorText}`, 'error');
		}
		if (logText) {
			appendDiagnosticsConsoleLine(`${service} log tail:\n${logText}`, errorText ? 'error' : 'warn');
		} else if (!errorText) {
			appendDiagnosticsConsoleLine(`${service} log tail: <no output yet>`);
		}
	} catch {
		appendDiagnosticsConsoleLine('Could not fetch service diagnostics logs.', 'warn');
	}
}

async function runDiagnosticsConsoleCommand(rawInput) {
	const command = rawInput.trim().toLowerCase();
	if (!command) return;
	appendDiagnosticsConsoleLine(`$ ${rawInput}`, 'command');

	if (command === 'help') {
		appendDiagnosticsConsoleLine('Commands: help, status, checks, logs, queue, poll, clear');
		return;
	}
	if (command === 'status') {
		appendDiagnosticsConsoleLine(getDiagnosticsStatusSnapshotText());
		return;
	}
	if (command === 'queue') {
		appendDiagnosticsConsoleLine(queueSummary?.textContent || 'Queue summary unavailable');
		return;
	}
	if (command === 'poll') {
		appendDiagnosticsConsoleLine(pollOwnerStatus?.textContent || 'Poll owner status unavailable');
		return;
	}
	if (command === 'clear') {
		if (diagDrawerOutput) diagDrawerOutput.innerHTML = '';
		appendDiagnosticsConsoleLine('Console cleared.');
		return;
	}
	if (command === 'checks') {
		appendDiagnosticsConsoleLine('Running diagnostics checks...');
		await runDiagnosticsChecks(true);
		appendDiagnosticsConsoleLine(getDiagnosticsStatusSnapshotText());
		return;
	}
	if (command === 'logs') {
		appendDiagnosticsConsoleLine('Fetching ComfyUI logs...');
		await appendServiceDiagnosticLogs('comfyui');
		return;
	}

	appendDiagnosticsConsoleLine(`Unknown command: ${command}`, 'warn');
}

function persistQueueTelemetryState() {
	sessionStorage.setItem(QUEUE_TELEMETRY_KEY, JSON.stringify(queueTelemetryState));
}

function renderQueueTelemetry() {
	if (!queueTelemetry) return;
	queueTelemetry.textContent = `Session: submitted ${queueTelemetryState.submitted} | canceled ${queueTelemetryState.canceled} | retried ${queueTelemetryState.retried} | failed ${queueTelemetryState.failed}`;
}

function incrementQueueTelemetry(metric, delta = 1) {
	if (!Object.prototype.hasOwnProperty.call(queueTelemetryState, metric)) return;
	queueTelemetryState[metric] += delta;
	persistQueueTelemetryState();
	renderQueueTelemetry();
}

function resetQueueTelemetry() {
	queueTelemetryState = { submitted: 0, canceled: 0, retried: 0, failed: 0 };
	persistQueueTelemetryState();
	renderQueueTelemetry();
}

if (failedOnlyToggle) {
	failedOnlyToggle.checked = queueFilterFailedOnly;
	failedOnlyToggle.addEventListener('change', () => {
		queueFilterFailedOnly = failedOnlyToggle.checked;
		localStorage.setItem('queueFilterFailedOnly', queueFilterFailedOnly ? '1' : '0');
		renderQueueStatus([], [], new Set());
	});
}

renderQueueTelemetry();

if (queueTelemetryResetBtn) {
	queueTelemetryResetBtn.addEventListener('click', () => {
		resetQueueTelemetry();
		showToast('Queue counters reset.', 'pos');
	});
}

const imageState = {
	currentPromptId: '',
};

/* --------------------------------------------------------------------------
	 Toast notifications
	 -------------------------------------------------------------------------- */
function showToast(msg, type = '') {
	if (!toastContainer) return;
	const el = document.createElement('div');
	el.className = `toast${type ? ` toast-${type}` : ''}`;
	el.textContent = msg;
	el.setAttribute('role', type === 'neg' ? 'alert' : 'status');
	el.setAttribute('aria-live', type === 'neg' ? 'assertive' : 'polite');
	el.setAttribute('tabindex', '0');
	toastContainer.appendChild(el);
	let dismissed = false;
	const dismissToast = () => {
		if (dismissed) return;
		dismissed = true;
		el.classList.add('toast-out');
		el.addEventListener('animationend', () => el.remove(), { once: true });
	};
	const timer = setTimeout(dismissToast, 3500);
	el.addEventListener('click', () => {
		clearTimeout(timer);
		dismissToast();
	});
	el.addEventListener('keydown', (event) => {
		if (event.key !== 'Enter' && event.key !== ' ' && event.key !== 'Escape') return;
		event.preventDefault();
		clearTimeout(timer);
		dismissToast();
	});
}

/* --------------------------------------------------------------------------
	 Theme
	 -------------------------------------------------------------------------- */
function applyTheme(theme) {
	document.body.setAttribute('data-theme', theme);
	localStorage.setItem('theme', theme);
	const path = themeToggle.querySelector('path');
	if (theme === 'dark') {
		path.setAttribute('d', 'M12 3v1m0 16v1m8.66-9H21M3 12H2m15.07-7.07l-.71.71M6.34 17.66l-.71.71M18.37 17.66l-.71-.71M6.34 6.34l-.71-.71M12 7a5 5 0 1 0 0 10A5 5 0 0 0 12 7z');
	} else {
		path.setAttribute('d', 'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z');
	}
}

(function initTheme() {
	const saved = localStorage.getItem('theme');
	const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
	applyTheme(saved || (prefersDark ? 'dark' : 'light'));
})();

themeToggle.addEventListener('click', () => {
	const current = document.body.getAttribute('data-theme');
	applyTheme(current === 'dark' ? 'light' : 'dark');
});

/* --------------------------------------------------------------------------
	 Tab navigation
	 -------------------------------------------------------------------------- */
function showPanel(panel) {
	const allPanels = [panelGen, panelImage, panelConfig, panelModels].filter(Boolean);
	const allNavs = [navGenerative, navImage, navConfig, navModels].filter(Boolean);
	allPanels.forEach(p => { p.hidden = true; p.classList.remove('active'); });
	allNavs.forEach(n => { n.classList.remove('active'); n.setAttribute('aria-selected', 'false'); });

	let targetPanel = panelGen;
	let targetNav = navGenerative;
	if (panel === 'image') { targetPanel = panelImage; targetNav = navImage; }
	else if (panel === 'config') { targetPanel = panelConfig; targetNav = navConfig; }
	else if (panel === 'models') { targetPanel = panelModels; targetNav = navModels; }

	if (targetPanel) { targetPanel.hidden = false; targetPanel.classList.add('active'); }
	if (targetNav) { targetNav.classList.add('active'); targetNav.setAttribute('aria-selected', 'true'); }

	if (panel === 'models') mbOnTabActivate();
	localStorage.setItem('activePanel', panel);
}

navGenerative.addEventListener('click', (e) => {
	e.preventDefault();
	showPanel('generative');
});
navImage.addEventListener('click', (e) => {
	e.preventDefault();
	showPanel('image');
});
if (navConfig) {
	navConfig.addEventListener('click', (e) => {
		e.preventDefault();
		showPanel('config');
	});
}
if (navModels) {
	navModels.addEventListener('click', (e) => {
		e.preventDefault();
		showPanel('models');
	});
}

(function initPanel() {
	const saved = localStorage.getItem('activePanel');
	if (saved === 'image' || saved === 'config' || saved === 'models') {
		showPanel(saved);
		return;
	}
	showPanel('generative');
})();

/* --------------------------------------------------------------------------
	 Shared helpers
	 -------------------------------------------------------------------------- */
function escHtml(str) {
	return String(str)
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;');
}

function getFocusedQueueAction() {
	const active = document.activeElement;
	if (!(active instanceof HTMLElement)) return null;
	if (!active.classList.contains('queue-action')) return null;
	const action = active.getAttribute('data-action');
	const promptId = active.getAttribute('data-prompt-id');
	if (!action || !promptId) return null;
	return { action, promptId };
}

function restoreQueueActionFocus(snapshot) {
	if (!snapshot || !queueList) return;
	const buttons = queueList.querySelectorAll(`.queue-action[data-action="${snapshot.action}"]`);
	for (const button of buttons) {
		if (button.getAttribute('data-prompt-id') !== snapshot.promptId) continue;
		button.focus();
		return;
	}
}

function getPollOwnerState() {
	try {
		const raw = localStorage.getItem(BACKGROUND_POLL_OWNER_KEY);
		if (!raw) return null;
		const parsed = JSON.parse(raw);
		if (!parsed || typeof parsed !== 'object') return null;
		if (typeof parsed.id !== 'string' || typeof parsed.expiresAt !== 'number') return null;
		return parsed;
	} catch {
		return null;
	}
}

function setPollOwnerState(owner) {
	if (!owner) {
		localStorage.removeItem(BACKGROUND_POLL_OWNER_KEY);
		return;
	}
	localStorage.setItem(BACKGROUND_POLL_OWNER_KEY, JSON.stringify(owner));
}

function isPollOwnerExpired(owner, now = Date.now()) {
	return !owner || owner.expiresAt <= now;
}

function claimBackgroundPollingOwnership() {
	if (document.hidden) return false;
	const now = Date.now();
	const owner = getPollOwnerState();
	if (owner && owner.id !== tabInstanceId && !isPollOwnerExpired(owner, now)) {
		return false;
	}
	setPollOwnerState({ id: tabInstanceId, expiresAt: now + BACKGROUND_POLL_LEASE_MS });
	return true;
}

function refreshBackgroundPollingOwnership() {
	const owner = getPollOwnerState();
	if (!owner || owner.id !== tabInstanceId || document.hidden) return false;
	setPollOwnerState({ id: tabInstanceId, expiresAt: Date.now() + BACKGROUND_POLL_LEASE_MS });
	return true;
}

function releaseBackgroundPollingOwnership() {
	const owner = getPollOwnerState();
	if (!owner || owner.id !== tabInstanceId) return;
	setPollOwnerState(null);
}

function startStatusPolling() {
	if (statusPollTimer) return;
	statusPollTimer = window.setInterval(checkStatus, 6000);
}

function stopStatusPolling() {
	if (!statusPollTimer) return;
	window.clearInterval(statusPollTimer);
	statusPollTimer = null;
}

function stopLivePreviewAutoRefresh() {
	if (!livePreviewTimer) return;
	window.clearInterval(livePreviewTimer);
	livePreviewTimer = null;
}

function renderPollOwnerStatus() {
	if (!pollOwnerStatus) return;
	pollOwnerStatus.classList.remove('owner', 'standby', 'hidden');

	const shortId = tabInstanceId.split('-').slice(-1)[0];
	if (document.hidden) {
		pollOwnerStatus.textContent = `Polling tab: hidden (tab ${shortId})`;
		pollOwnerStatus.classList.add('hidden');
		return;
	}

	if (hasBackgroundPollingOwnership) {
		pollOwnerStatus.textContent = `Polling tab: active owner (tab ${shortId})`;
		pollOwnerStatus.classList.add('owner');
		return;
	}

	pollOwnerStatus.textContent = `Polling tab: standby (tab ${shortId})`;
	pollOwnerStatus.classList.add('standby');
}

function syncBackgroundPollingOwnership() {
	const hadOwnership = hasBackgroundPollingOwnership;
	hasBackgroundPollingOwnership = refreshBackgroundPollingOwnership() || claimBackgroundPollingOwnership();

	if (!hasBackgroundPollingOwnership) {
		stopStatusPolling();
		stopLivePreviewAutoRefresh();
		stopQueuePolling();
		renderPollOwnerStatus();
		return;
	}

	startStatusPolling();
	startLivePreviewAutoRefresh();
	if (trackedPromptIds.size) {
		ensureQueuePolling();
	}

	if (!hadOwnership) {
		checkStatus();
		loadLivePreview();
		if (trackedPromptIds.size) {
			pollQueue();
		}
	}

	renderPollOwnerStatus();
}

function startPollingLeaseHeartbeat() {
	if (pollLeaseTimer) return;
	pollLeaseTimer = window.setInterval(syncBackgroundPollingOwnership, BACKGROUND_POLL_HEARTBEAT_MS);
}

function randomSeed() {
	return Math.floor(Math.random() * 2_147_483_647) + 1;
}

function setModelSelectMessage(msg) {
	modelSelect.innerHTML = `<option value="">${escHtml(msg)}</option>`;
}

function setImageModelMessage(msg) {
	imageModelSelect.innerHTML = `<option value="">${escHtml(msg)}</option>`;
}

function getImageProfileState() {
	try {
		const parsed = JSON.parse(localStorage.getItem(IMAGE_PROFILE_STORAGE_KEY) || '{}');
		if (!parsed || typeof parsed !== 'object') return {};
		return parsed;
	} catch {
		return {};
	}
}

function setImageProfileState(state) {
	localStorage.setItem(IMAGE_PROFILE_STORAGE_KEY, JSON.stringify(state));
}

function getCurrentImageSettings() {
	return {
		model: imageModelSelect.value,
		sampler: imageSamplerSelect.value,
		seed: imageSeed.value,
		steps: Number(imageSteps.value),
		cfg: Number(imageCfg.value),
		denoise: Number(imageDenoise.value),
		width: Number(imageWidth.value),
		height: Number(imageHeight.value),
		batch_size: Number(imageBatchSize.value),
	};
}

function applyImageSettings(settings) {
	if (!settings || typeof settings !== 'object') return;
	if (settings.model && [...imageModelSelect.options].some((o) => o.value === settings.model)) {
		imageModelSelect.value = settings.model;
	}
	if (settings.sampler && [...imageSamplerSelect.options].some((o) => o.value === settings.sampler)) {
		imageSamplerSelect.value = settings.sampler;
	}
	if (settings.seed !== undefined && settings.seed !== null) imageSeed.value = String(settings.seed);
	if (Number.isFinite(settings.steps)) imageSteps.value = String(settings.steps);
	if (Number.isFinite(settings.cfg)) imageCfg.value = String(settings.cfg);
	if (Number.isFinite(settings.denoise)) imageDenoise.value = String(settings.denoise);
	if (Number.isFinite(settings.width)) imageWidth.value = String(settings.width);
	if (Number.isFinite(settings.height)) imageHeight.value = String(settings.height);
	if (Number.isFinite(settings.batch_size)) imageBatchSize.value = String(settings.batch_size);
	syncImageControlLabels();
}

function renderImageProfileSelect(preferredName = '') {
	if (!imageProfileSelect) return;
	const profiles = getImageProfileState();
	const names = Object.keys(profiles).sort((a, b) => a.localeCompare(b));
	if (!names.length) {
		imageProfileSelect.innerHTML = '<option value="">No saved profiles</option>';
		imageProfileSelect.value = '';
		if (imageProfileApplyBtn) imageProfileApplyBtn.disabled = true;
		if (imageProfileDeleteBtn) imageProfileDeleteBtn.disabled = true;
		return;
	}

	imageProfileSelect.innerHTML = names
		.map((name) => `<option value="${escHtml(name)}">${escHtml(name)}</option>`)
		.join('');

	const savedSelected = localStorage.getItem(IMAGE_PROFILE_SELECTED_KEY) || '';
	const nextSelected = preferredName || savedSelected;
	if (nextSelected && names.includes(nextSelected)) {
		imageProfileSelect.value = nextSelected;
	} else {
		imageProfileSelect.value = names[0];
	}

	localStorage.setItem(IMAGE_PROFILE_SELECTED_KEY, imageProfileSelect.value);
	if (imageProfileApplyBtn) imageProfileApplyBtn.disabled = false;
	if (imageProfileDeleteBtn) imageProfileDeleteBtn.disabled = false;
}

function saveCurrentImageProfile() {
	if (!imageProfileName) return;
	const rawName = imageProfileName.value.trim();
	if (!rawName) {
		showToast('Profile name is required.', 'neg');
		imageProfileName.focus();
		return;
	}
	const profiles = getImageProfileState();
	profiles[rawName] = getCurrentImageSettings();
	setImageProfileState(profiles);
	renderImageProfileSelect(rawName);
	imageProfileName.value = '';
	showToast(`Saved profile: ${rawName}.`, 'pos');
}

function applySelectedImageProfile() {
	if (!imageProfileSelect) return;
	const name = imageProfileSelect.value;
	if (!name) {
		showToast('Select a saved profile first.', 'neg');
		return;
	}
	const profiles = getImageProfileState();
	const settings = profiles[name];
	if (!settings) {
		showToast('Selected profile was not found.', 'neg');
		renderImageProfileSelect('');
		return;
	}
	applyImageSettings(settings);
	localStorage.setItem(IMAGE_PROFILE_SELECTED_KEY, name);
	showToast(`Applied profile: ${name}.`, 'pos');
}

function deleteSelectedImageProfile() {
	if (!imageProfileSelect) return;
	const name = imageProfileSelect.value;
	if (!name) {
		showToast('No profile selected.', 'neg');
		return;
	}
	const profiles = getImageProfileState();
	if (!profiles[name]) {
		renderImageProfileSelect('');
		return;
	}
	delete profiles[name];
	setImageProfileState(profiles);
	renderImageProfileSelect('');
	showToast(`Deleted profile: ${name}.`, 'pos');
}

function setDiagnosticValue(el, text, level = '') {
	if (!el) return;
	el.textContent = text;
	el.classList.remove('ok', 'warn');
	if (level) el.classList.add(level);
}

function getActiveSelectOptionCount(selectEl) {
	if (!selectEl) return 0;
	return Array.from(selectEl.options).filter((opt) => opt.value).length;
}

function renderDiagnosticsSnapshot(snapshot) {
	if (!diagnosticsSummary) return;
	setDiagnosticValue(diagTextStatus, snapshot.textStatusLabel, snapshot.textOk ? 'ok' : 'warn');
	setDiagnosticValue(diagImageStatus, snapshot.imageStatusLabel, snapshot.imageOk ? 'ok' : 'warn');
	setDiagnosticValue(diagCheckpoints, `${snapshot.checkpoints}`, snapshot.checkpoints > 0 ? 'ok' : 'warn');
	setDiagnosticValue(diagSamplers, `${snapshot.samplers}`, snapshot.samplers > 0 ? 'ok' : 'warn');
	setDiagnosticValue(diagLastRun, snapshot.lastRunLabel);
	diagnosticsSummary.textContent = snapshot.summary;
	if (diagnosticsHint) diagnosticsHint.textContent = snapshot.hint;
	if (diagStatusBadge) {
		const status = snapshot.failed ? 'error' : (snapshot.textOk && snapshot.imageOk ? 'ok' : 'warn');
		diagStatusBadge.dataset.status = status;
		diagStatusBadge.title = snapshot.summary;
	}

	const key = [snapshot.lastRunLabel, snapshot.summary, snapshot.textStatusLabel, snapshot.imageStatusLabel, snapshot.checkpoints, snapshot.samplers].join('|');
	if (key !== lastDiagnosticsLogKey) {
		lastDiagnosticsLogKey = key;
		const level = snapshot.textOk && snapshot.imageOk ? 'info' : 'warn';
		appendDiagnosticsConsoleLine(`[${snapshot.lastRunLabel}] ${snapshot.summary} | text=${snapshot.textStatusLabel} image=${snapshot.imageStatusLabel} ckpt=${snapshot.checkpoints} samplers=${snapshot.samplers}`, level);
	}
}

async function runDiagnosticsChecks(manual = false) {
	if (!diagnosticsSummary) return;
	if (diagnosticsRunBtn) diagnosticsRunBtn.disabled = true;
	const lastRunLabel = new Date().toLocaleTimeString();
	try {
		const [statusRes, textModelRes, imageModelRes, samplerRes] = await Promise.all([
			fetch('/api/status'),
			fetch('/api/models'),
			fetch('/api/image/models'),
			fetch('/api/image/samplers'),
		]);

		const statusData = await statusRes.json().catch(() => ({}));
		const textData = await textModelRes.json().catch(() => ({}));
		const imageData = await imageModelRes.json().catch(() => ({}));
		const samplerData = await samplerRes.json().catch(() => ({}));

		const textOk = !!statusData.text?.available;
		const imageOk = !!statusData.image?.available;
		const checkpoints = (imageData.models || []).length;
		const samplers = (samplerData.samplers || []).length;
		const textModels = (textData.models || []).length;

		let hint = 'All checks passed.';
		if (!textOk && !imageOk) {
			hint = 'Start Ollama (11434) and ComfyUI (8188), then run checks again.';
		} else if (!textOk) {
			hint = 'Start Ollama at localhost:11434.';
		} else if (!imageOk) {
			hint = 'Start ComfyUI at localhost:8188.';
		} else if (checkpoints === 0) {
			hint = 'ComfyUI is online, but no checkpoints are visible.';
		}

		renderDiagnosticsSnapshot({
			textOk,
			imageOk,
			textStatusLabel: textOk ? `online (${textModels})` : 'offline',
			imageStatusLabel: imageOk ? 'online' : 'offline',
			checkpoints,
			samplers,
			lastRunLabel,
			summary: textOk && imageOk ? 'Diagnostics OK' : 'Diagnostics detected issues',
			hint,
		});

		if (manual) {
			showToast(textOk && imageOk ? 'Diagnostics complete: services online.' : 'Diagnostics complete: issues found.', textOk && imageOk ? 'pos' : 'neg');
		}

		if (!imageOk) {
			await appendServiceDiagnosticLogs('comfyui');
		}
	} catch {
		renderDiagnosticsSnapshot({
			textOk: false,
			imageOk: false,
			textStatusLabel: 'unknown',
			imageStatusLabel: 'unknown',
			checkpoints: '-',
			samplers: '-',
			lastRunLabel,
			summary: 'Diagnostics request failed',
			hint: 'Could not reach backend endpoints from the browser.',
			failed: true,
		});
		if (manual) showToast('Diagnostics failed: could not reach backend.', 'neg');
	} finally {
		if (diagnosticsRunBtn) diagnosticsRunBtn.disabled = false;
	}
}

function scrollToBottom() {
	chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendMessage(role, text) {
	const wrapper = document.createElement('div');
	wrapper.className = `message message-${role}`;
	const bubble = document.createElement('div');
	bubble.className = 'message-bubble';
	bubble.textContent = text;
	wrapper.appendChild(bubble);
	chatMessages.appendChild(wrapper);
	scrollToBottom();
	return bubble;
}

function appendSystemMessage(text) {
	const wrapper = document.createElement('div');
	wrapper.className = 'message message-system';
	const bubble = document.createElement('div');
	bubble.className = 'message-bubble';
	bubble.textContent = text;
	wrapper.appendChild(bubble);
	chatMessages.appendChild(wrapper);
	scrollToBottom();
}

/* --------------------------------------------------------------------------
	 Status and model loading
	 -------------------------------------------------------------------------- */
async function loadTextModels() {
	try {
		const res = await fetch('/api/models');
		const data = await res.json();
		const models = data.models || [];
		if (!models.length) {
			setModelSelectMessage('No models found - run: ollama pull llama3');
			return;
		}

		const current = modelSelect.value;
		modelSelect.innerHTML = models
			.map((m) => `<option value="${escHtml(m.name)}">${escHtml(m.name)}</option>`)
			.join('');
		if (current && [...modelSelect.options].some((o) => o.value === current)) {
			modelSelect.value = current;
		}
	} catch {
		setModelSelectMessage('Could not fetch models');
	}
}

function setConfigStatusLine(element, text, level = '') {
	if (!element) return;
	element.textContent = text;
	element.style.color = level === 'error'
		? 'var(--clr-accent-neg)'
		: (level === 'ok' ? 'var(--clr-accent-pos)' : 'var(--clr-text-muted)');
}

function setConfigSavedTimestamp(value) {
	if (!configLastSaved) return;
	if (!value) {
		configLastSaved.textContent = 'Last saved: never';
		return;
	}
	const parsed = new Date(value);
	if (Number.isNaN(parsed.getTime())) {
		configLastSaved.textContent = `Last saved: ${value}`;
		return;
	}
	configLastSaved.textContent = `Last saved: ${parsed.toLocaleString()}`;
}

async function loadServiceConfig() {
	if (!configOllamaPath || !configComfyuiPath) return;
	try {
		const res = await fetch('/api/config/services');
		const data = await res.json();
		if (!res.ok) {
			setConfigStatusLine(configSaveStatus, data.error || 'Could not load saved paths.', 'error');
			return;
		}
		configOllamaPath.value = data.ollama_path || '';
		configComfyuiPath.value = data.comfyui_path || '';
		setConfigSavedTimestamp(data.updated_at || '');
		setConfigStatusLine(configSaveStatus, 'Saved paths loaded.');
	} catch {
		setConfigStatusLine(configSaveStatus, 'Could not load saved paths.', 'error');
		setConfigSavedTimestamp('');
	}
}

async function saveServiceConfig(options = {}) {
	const { silentSuccess = false } = options;
	if (!configOllamaPath || !configComfyuiPath) return;
	const payload = {
		ollama_path: configOllamaPath.value.trim(),
		comfyui_path: configComfyuiPath.value.trim(),
	};

	try {
		if (configSaveBtn) configSaveBtn.disabled = true;
		const res = await fetch('/api/config/services', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload),
		});
		const data = await res.json();
		if (!res.ok) {
			setConfigStatusLine(configSaveStatus, data.error || 'Could not save paths.', 'error');
			showToast('Could not save configuration paths.', 'neg');
			return;
		}
		setConfigSavedTimestamp(data.config?.updated_at || '');
		setConfigStatusLine(configSaveStatus, 'Paths saved.', 'ok');
		if (!silentSuccess) {
			showToast('Configuration paths saved.', 'pos');
		}
	} catch {
		setConfigStatusLine(configSaveStatus, 'Could not save paths.', 'error');
		showToast('Could not save configuration paths.', 'neg');
	} finally {
		if (configSaveBtn) configSaveBtn.disabled = false;
	}
}

async function browseServicePath(service) {
	const input = service === 'ollama' ? configOllamaPath : configComfyuiPath;
	const button = service === 'ollama' ? configOllamaBrowseBtn : configComfyuiBrowseBtn;
	if (!input || !button) return;

	button.disabled = true;
	setConfigStatusLine(configSaveStatus, `Opening ${service} path picker...`);
	try {
		const res = await fetch('/api/config/pick-path', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ service, initial_path: input.value.trim() }),
		});
		const data = await res.json();
		if (!res.ok) {
			setConfigStatusLine(configSaveStatus, data.error || 'Could not open path picker.', 'error');
			showToast(`Could not open ${service} path picker.`, 'neg');
			return;
		}
		if (data.path) {
			input.value = data.path;
			setConfigStatusLine(configSaveStatus, `${service} path selected. Saving...`, 'ok');
			showToast(`${service} path selected.`, 'pos');
			await saveServiceConfig({ silentSuccess: true });
		} else {
			setConfigStatusLine(configSaveStatus, 'Path selection canceled.');
		}
	} catch {
		setConfigStatusLine(configSaveStatus, 'Could not open path picker.', 'error');
		showToast(`Could not open ${service} path picker.`, 'neg');
	} finally {
		button.disabled = false;
	}
}

async function controlService(service, action, statusNode, buttonGroup = []) {
	const controls = buttonGroup.filter(Boolean);
	for (const btn of controls) btn.disabled = true;
	setConfigStatusLine(statusNode, `${action} in progress...`);

	try {
		const res = await fetch(`/api/service/${service}/${action}`, { method: 'POST' });
		const data = await res.json();
		if (!res.ok) {
			setConfigStatusLine(statusNode, data.error || `${action} failed.`, 'error');
			showToast(`${service} ${action} failed.`, 'neg');
			return;
		}

		const statusTextValue = data.status || 'ok';
		const isOk = statusTextValue === 'started' || statusTextValue === 'stopped' || statusTextValue === 'already-running';
		setConfigStatusLine(statusNode, `${service}: ${statusTextValue}${data.pid ? ` (pid ${data.pid})` : ''}`, isOk ? 'ok' : '');
		showToast(`${service} ${action}: ${statusTextValue}`, isOk ? 'pos' : '');

		await checkStatus();

		// Service launch can take a few seconds; poll health so UI shows a clear outcome.
		if ((action === 'start' || action === 'restart') && (statusTextValue === 'started' || statusTextValue === 'already-running')) {
			const healthKey = service === 'ollama' ? 'text' : 'image';
			let reachable = false;
			for (let i = 0; i < 12; i++) {
				await new Promise((resolve) => window.setTimeout(resolve, 1000));
				try {
					const healthRes = await fetch('/api/status');
					const healthData = await healthRes.json();
					reachable = Boolean(healthData?.[healthKey]?.available);
					if (reachable) break;
				} catch {
					// non-fatal while polling startup readiness
				}
			}

			if (reachable) {
				setConfigStatusLine(statusNode, `${service}: online`, 'ok');
			} else {
				setConfigStatusLine(statusNode, `${service}: started but not reachable on expected port`, 'error');
				showToast(`${service} started but is still unreachable. Verify launcher/runtime environment.`, 'neg');
				await appendServiceDiagnosticLogs(service);
			}
		}

		if (service === 'ollama') {
			await loadTextModels();
		} else {
			await loadImageModels();
			await loadImageSamplers();
		}
	} catch {
		setConfigStatusLine(statusNode, `${service} ${action} failed.`, 'error');
		showToast(`${service} ${action} failed.`, 'neg');
	} finally {
		for (const btn of controls) btn.disabled = false;
	}
}

async function restartFlaskApp() {
	if (!configFlaskRestartBtn || !configFlaskStatus) return;
	const confirmed = window.confirm('Restart Flask now? This will briefly interrupt the UI.');
	if (!confirmed) {
		setConfigStatusLine(configFlaskStatus, 'Restart canceled.');
		return;
	}

	configFlaskRestartBtn.disabled = true;
	setConfigStatusLine(configFlaskStatus, 'Restart requested...');

	try {
		const res = await fetch('/api/app/restart', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ port: 5000 }),
		});
		const data = await res.json().catch(() => ({}));
		if (!res.ok) {
			setConfigStatusLine(configFlaskStatus, data.error || 'Flask restart failed.', 'error');
			showToast('Flask restart failed.', 'neg');
			configFlaskRestartBtn.disabled = false;
			return;
		}

		setConfigStatusLine(configFlaskStatus, 'Restarting Flask... reloading page shortly.', 'ok');
		showToast('Flask restart triggered. Reloading page...', 'pos');
		window.setTimeout(() => {
			window.location.reload();
		}, 2600);
	} catch {
		setConfigStatusLine(configFlaskStatus, 'Flask restart request failed.', 'error');
		showToast('Flask restart request failed.', 'neg');
		configFlaskRestartBtn.disabled = false;
	}
}

async function loadImageModels() {
	try {
		const res = await fetch('/api/image/models');
		const data = await res.json();
		if (!res.ok) {
			setImageModelMessage(data.error || 'ComfyUI unavailable');
			return;
		}
		const models = data.models || [];
		if (!models.length) {
			setImageModelMessage('No checkpoints found in ComfyUI');
			return;
		}
		const isUnsupportedFluxModel = (name) => /flux/i.test(name || '');
		const current = imageModelSelect.value;
		imageModelSelect.innerHTML = models
			.map((name) => {
				const unsupported = isUnsupportedFluxModel(name);
				const optionLabel = unsupported ? `${name} (unsupported in current workflow)` : name;
				return `<option value="${escHtml(name)}" ${unsupported ? 'disabled data-unsupported="true"' : ''}>${escHtml(optionLabel)}</option>`;
			})
			.join('');

		const options = [...imageModelSelect.options];
		const currentOption = options.find((o) => o.value === current);
		if (currentOption && !currentOption.disabled) {
			imageModelSelect.value = current;
			return;
		}

		const firstSupported = options.find((o) => !o.disabled && o.value);
		if (firstSupported) {
			imageModelSelect.value = firstSupported.value;
		}
	} catch {
		setImageModelMessage('Could not fetch checkpoints');
	}
}

async function loadImageSamplers() {
	try {
		const res = await fetch('/api/image/samplers');
		const data = await res.json();
		if (!res.ok) {
			imageSamplerSelect.innerHTML = '<option value="euler">euler</option>';
			return;
		}
		const samplers = data.samplers || [];
		if (!samplers.length) {
			imageSamplerSelect.innerHTML = '<option value="euler">euler</option>';
			return;
		}
		imageSamplerSelect.innerHTML = samplers
			.map((name) => `<option value="${escHtml(name)}">${escHtml(name)}</option>`)
			.join('');
	} catch {
		imageSamplerSelect.innerHTML = '<option value="euler">euler</option>';
	}
}

async function checkStatus() {
	try {
		const res = await fetch('/api/status');
		const data = await res.json();

		const textOk = data.text?.available;
		const imageOk = data.image?.available;

		if (textOk && imageOk) {
			statusDot.className = 'status-dot online';
			statusText.textContent = 'Ready';
		} else if (!textOk && !imageOk) {
			statusDot.className = 'status-dot offline';
			statusText.textContent = 'Offline';
		} else {
			statusDot.className = 'status-dot loading';
			statusText.textContent = 'Partial';
		}

		if (textOk) {
			await loadTextModels();
		} else {
			setModelSelectMessage('Ollama not found - install from ollama.com');
		}

		if (imageOk) {
			imageEngineStatus.textContent = 'ComfyUI online and ready';
			imageEngineStatus.style.color = 'var(--clr-accent-pos)';
			await loadImageModels();
			await loadImageSamplers();
			connectComfyWebSocket();
		} else {
			imageEngineStatus.textContent = 'ComfyUI offline - start server at localhost:8188';
			imageEngineStatus.style.color = 'var(--clr-accent-neg)';
			setImageModelMessage('ComfyUI unavailable');
		}

		renderDiagnosticsSnapshot({
			textOk,
			imageOk,
			textStatusLabel: textOk ? `online (${getActiveSelectOptionCount(modelSelect)})` : 'offline',
			imageStatusLabel: imageOk ? 'online' : 'offline',
			checkpoints: getActiveSelectOptionCount(imageModelSelect),
			samplers: getActiveSelectOptionCount(imageSamplerSelect),
			lastRunLabel: new Date().toLocaleTimeString(),
			summary: textOk && imageOk ? 'Diagnostics OK' : 'Diagnostics detected issues',
			hint: textOk && imageOk
				? 'Use Run checks for deeper endpoint verification.'
				: (!textOk && !imageOk)
					? 'Start Ollama (11434) and ComfyUI (8188), then run checks again.'
					: (!textOk ? 'Start Ollama at localhost:11434.' : 'Start ComfyUI at localhost:8188.'),
		});
	} catch {
		statusDot.className = 'status-dot offline';
		statusText.textContent = 'Offline';
		imageEngineStatus.textContent = 'Could not reach backend status endpoint';
		renderDiagnosticsSnapshot({
			textOk: false,
			imageOk: false,
			textStatusLabel: 'unknown',
			imageStatusLabel: 'unknown',
			checkpoints: '-',
			samplers: '-',
			lastRunLabel: new Date().toLocaleTimeString(),
			summary: 'Diagnostics request failed',
			hint: 'Could not reach backend status endpoint.',
		});
	}
}

if (diagnosticsRunBtn) {
	diagnosticsRunBtn.addEventListener('click', async () => {
		await runDiagnosticsChecks(true);
	});
}

if (diagDrawerToggle) {
	diagDrawerToggle.addEventListener('click', () => {
		const open = diagDrawer ? diagDrawer.hidden : true;
		setDiagnosticsDrawerOpen(open);
	});
}

if (diagDrawerClose) {
	diagDrawerClose.addEventListener('click', () => setDiagnosticsDrawerOpen(false));
}

if (diagDrawerCommandForm && diagDrawerCommandInput) {
	diagDrawerCommandForm.addEventListener('submit', async (event) => {
		event.preventDefault();
		const raw = diagDrawerCommandInput.value;
		diagDrawerCommandInput.value = '';
		if (raw.trim()) {
			diagHistory.push(raw);
			if (diagHistory.length > 50) diagHistory.shift();
		}
		diagHistoryIndex = -1;
		diagHistoryDraft = '';
		await runDiagnosticsConsoleCommand(raw);
	});

	diagDrawerCommandInput.addEventListener('keydown', (event) => {
		if (event.key === 'ArrowUp') {
			event.preventDefault();
			if (diagHistory.length === 0) return;
			if (diagHistoryIndex === -1) diagHistoryDraft = diagDrawerCommandInput.value;
			diagHistoryIndex = Math.min(diagHistoryIndex + 1, diagHistory.length - 1);
			diagDrawerCommandInput.value = diagHistory[diagHistory.length - 1 - diagHistoryIndex];
		} else if (event.key === 'ArrowDown') {
			event.preventDefault();
			if (diagHistoryIndex <= 0) {
				diagHistoryIndex = -1;
				diagDrawerCommandInput.value = diagHistoryDraft;
			} else {
				diagHistoryIndex--;
				diagDrawerCommandInput.value = diagHistory[diagHistory.length - 1 - diagHistoryIndex];
			}
		}
	});
}

if (diagDrawerOutput) {
	appendDiagnosticsConsoleLine('Diagnostics console ready. Type help for commands.');
}

if (configSaveBtn) {
	configSaveBtn.addEventListener('click', saveServiceConfig);
}

if (configOllamaBrowseBtn) {
	configOllamaBrowseBtn.addEventListener('click', async () => {
		await browseServicePath('ollama');
	});
}

if (configComfyuiBrowseBtn) {
	configComfyuiBrowseBtn.addEventListener('click', async () => {
		await browseServicePath('comfyui');
	});
}

if (configOllamaStartBtn) {
	configOllamaStartBtn.addEventListener('click', async () => {
		await controlService('ollama', 'start', configOllamaStatus, [configOllamaStartBtn, configOllamaRestartBtn, configOllamaStopBtn]);
	});
}

if (configOllamaRestartBtn) {
	configOllamaRestartBtn.addEventListener('click', async () => {
		await controlService('ollama', 'restart', configOllamaStatus, [configOllamaStartBtn, configOllamaRestartBtn, configOllamaStopBtn]);
	});
}

if (configOllamaStopBtn) {
	configOllamaStopBtn.addEventListener('click', async () => {
		await controlService('ollama', 'stop', configOllamaStatus, [configOllamaStartBtn, configOllamaRestartBtn, configOllamaStopBtn]);
	});
}

if (configComfyStartBtn) {
	configComfyStartBtn.addEventListener('click', async () => {
		await controlService('comfyui', 'start', configComfyStatus, [configComfyStartBtn, configComfyRestartBtn, configComfyStopBtn]);
	});
}

if (configComfyRestartBtn) {
	configComfyRestartBtn.addEventListener('click', async () => {
		await controlService('comfyui', 'restart', configComfyStatus, [configComfyStartBtn, configComfyRestartBtn, configComfyStopBtn]);
	});
}

if (configComfyStopBtn) {
	configComfyStopBtn.addEventListener('click', async () => {
		await controlService('comfyui', 'stop', configComfyStatus, [configComfyStartBtn, configComfyRestartBtn, configComfyStopBtn]);
	});
}

if (configFlaskRestartBtn) {
	configFlaskRestartBtn.addEventListener('click', restartFlaskApp);
}

if (tagCategorySelect) {
	renderTagCategoryOptions();
	tagCategorySelect.value = 'enhanced-subject';
	renderTagManagerUi();
	tagCategorySelect.addEventListener('change', () => {
		renderTagManagerUi();
	});
}

if (tagAddBtn && tagNewInput) {
	tagAddBtn.addEventListener('click', () => {
		const category = getCurrentTagCategory();
		const ok = addTagToCategory(category, tagNewInput.value);
		if (!ok) {
			updateTagManagerStatus('Tag is empty or already exists.', 'error');
			return;
		}
		tagNewInput.value = '';
		saveSuggestionTagStore();
		renderEnhancedTagSuggestions();
		renderTagManagerUi();
		updateTagManagerStatus('Tag added.', 'ok');
	});

	tagNewInput.addEventListener('keydown', (event) => {
		if (event.key !== 'Enter') return;
		event.preventDefault();
		tagAddBtn.click();
	});
}

if (tagEditorList) {
	tagEditorList.addEventListener('click', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLElement)) return;
		const category = getCurrentTagCategory();

		const saveIdx = target.getAttribute('data-tag-save');
		if (saveIdx !== null) {
			const index = Number(saveIdx);
			const input = tagEditorList.querySelector(`[data-tag-input="${index}"]`);
			if (!(input instanceof HTMLInputElement)) return;
			const ok = setTagAtIndex(category, index, input.value);
			if (!ok) {
				updateTagManagerStatus('Save failed: empty or duplicate tag.', 'error');
				return;
			}
			saveSuggestionTagStore();
			renderEnhancedTagSuggestions();
			renderTagManagerUi();
			updateTagManagerStatus('Tag updated.', 'ok');
			return;
		}

		const deleteIdx = target.getAttribute('data-tag-delete');
		if (deleteIdx !== null) {
			const index = Number(deleteIdx);
			deleteTagAtIndex(category, index);
			saveSuggestionTagStore();
			renderEnhancedTagSuggestions();
			renderTagManagerUi();
			updateTagManagerStatus('Tag deleted.', 'ok');
		}
	});
}

if (tagResetDefaultsBtn) {
	tagResetDefaultsBtn.addEventListener('click', () => {
		suggestionTagStore = cloneDefaultSuggestionTags();
		saveSuggestionTagStore();
		renderEnhancedTagSuggestions();
		renderTagManagerUi();
		updateTagManagerStatus('Suggestion tags reset to defaults.', 'ok');
	});
}

/* --------------------------------------------------------------------------
	 Text inference controls and chat
	 -------------------------------------------------------------------------- */
textTemperature.addEventListener('input', () => {
	textTemperatureVal.textContent = Number(textTemperature.value).toFixed(2);
});

textTopP.addEventListener('input', () => {
	textTopPVal.textContent = Number(textTopP.value).toFixed(2);
});

textRandomSeed.addEventListener('click', () => {
	textSeed.value = randomSeed();
});

clearChat.addEventListener('click', () => {
	chatMessages.innerHTML = '';
	appendSystemMessage('Conversation cleared.');
});

chatInput.addEventListener('input', () => {
	chatInput.style.height = 'auto';
	chatInput.style.height = `${Math.min(chatInput.scrollHeight, 180)}px`;
});

chatInput.addEventListener('keydown', (e) => {
	if (e.key === 'Enter' && !e.shiftKey) {
		e.preventDefault();
		chatForm.requestSubmit();
	}
});

chatForm.addEventListener('submit', async (e) => {
	e.preventDefault();
	if (isGenerating) return;

	const prompt = chatInput.value.trim();
	const model = modelSelect.value;
	if (!prompt) return;
	if (!model) {
		appendSystemMessage('Please select a model first.');
		return;
	}

	chatInput.value = '';
	chatInput.style.height = 'auto';

	appendMessage('user', prompt);
	isGenerating = true;
	sendBtn.disabled = true;

	const aiBubble = appendMessage('ai', '');
	aiBubble.classList.add('streaming');

	const payload = {
		model,
		prompt,
		system: systemPrompt.value.trim(),
		negative_prompt: textNegativePrompt.value.trim(),
		seed: textSeed.value.trim() || null,
		temperature: Number(textTemperature.value),
		top_p: Number(textTopP.value),
		top_k: Number(textTopK.value || 40),
		num_predict: Number(textNumPredict.value || 512),
	};

	try {
		const res = await fetch('/api/generate', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload),
		});

		if (!res.ok) {
			const err = await res.json().catch(() => ({ error: res.statusText }));
			aiBubble.textContent = `Error: ${err.error || 'Unknown error'}`;
			aiBubble.classList.remove('streaming');
			return;
		}

		const reader = res.body.getReader();
		const decoder = new TextDecoder();
		let buffer = '';
		let fullText = '';
		let finalMeta = null;

		while (true) {
			const { value, done } = await reader.read();
			if (done) break;

			buffer += decoder.decode(value, { stream: true });
			const lines = buffer.split('\n');
			buffer = lines.pop();

			for (const line of lines) {
				const trimmed = line.trim();
				if (!trimmed.startsWith('data:')) continue;
				const raw = trimmed.slice(5).trim();
				if (raw === '[DONE]') break;

				try {
					const chunk = JSON.parse(raw);
					if (chunk.error) {
						aiBubble.textContent = `Error: ${chunk.error}`;
						aiBubble.classList.remove('streaming');
						return;
					}
					if (chunk.token) {
						fullText += chunk.token;
						aiBubble.textContent = fullText;
						scrollToBottom();
					}
					if (chunk.meta) {
						finalMeta = chunk.meta;
					}
				} catch {
					// ignore malformed chunks
				}
			}
		}

		await saveHistoryEntry({
			type: 'text',
			prompt,
			negative_prompt: payload.negative_prompt,
			engine: 'ollama',
			model,
			params: {
				seed: payload.seed,
				temperature: payload.temperature,
				top_p: payload.top_p,
				top_k: payload.top_k,
				num_predict: payload.num_predict,
				...(finalMeta || {}),
			},
			response: fullText,
		});
	} catch (err) {
		aiBubble.textContent = `Error: ${err.message}`;
	} finally {
		aiBubble.classList.remove('streaming');
		isGenerating = false;
		sendBtn.disabled = false;
		chatInput.focus();
	}
});

/* --------------------------------------------------------------------------
	 Image controls, presets, queue, gallery
	 -------------------------------------------------------------------------- */
function syncImageControlLabels() {
	imageStepsVal.textContent = String(Number(imageSteps.value));
	imageCfgVal.textContent = Number(imageCfg.value).toFixed(1);
	imageDenoiseVal.textContent = Number(imageDenoise.value).toFixed(2);
}

imageSteps.addEventListener('input', syncImageControlLabels);
imageCfg.addEventListener('input', syncImageControlLabels);
imageDenoise.addEventListener('input', syncImageControlLabels);
syncImageControlLabels();

imageRandomSeed.addEventListener('click', () => {
	imageSeed.value = randomSeed();
});

function applyImagePreset(preset) {
	if (preset === 'fast') {
		imageSteps.value = '20';
		imageCfg.value = '6.5';
		imageDenoise.value = '0.70';
	} else if (preset === 'quality') {
		imageSteps.value = '40';
		imageCfg.value = '7.5';
		imageDenoise.value = '0.75';
	} else if (preset === 'creative') {
		imageSteps.value = '32';
		imageCfg.value = '9.0';
		imageDenoise.value = '0.85';
	}
	syncImageControlLabels();
}

imagePresetButtons.forEach((btn) => {
	btn.addEventListener('click', () => applyImagePreset(btn.dataset.imagePreset));
});

if (imageProfileSelect) {
	imageProfileSelect.addEventListener('change', () => {
		localStorage.setItem(IMAGE_PROFILE_SELECTED_KEY, imageProfileSelect.value || '');
	});
}

if (imageProfileSaveBtn) {
	imageProfileSaveBtn.addEventListener('click', saveCurrentImageProfile);
}

if (imageProfileApplyBtn) {
	imageProfileApplyBtn.addEventListener('click', applySelectedImageProfile);
}

if (imageProfileDeleteBtn) {
	imageProfileDeleteBtn.addEventListener('click', deleteSelectedImageProfile);
}

if (imageProfileName) {
	imageProfileName.addEventListener('keydown', (event) => {
		if (event.key !== 'Enter') return;
		event.preventDefault();
		saveCurrentImageProfile();
	});
}

renderImageProfileSelect('');

function renderQueueStatus(running, pending, donePromptIds = new Set()) {
	const focusedQueueAction = getFocusedQueueAction();
	const runningIds = new Set();
	const pendingIds = new Set();

	running.forEach((item) => {
		const pid = item[1] || '';
		if (pid) runningIds.add(pid);
	});
	pending.forEach((item) => {
		const pid = item[1] || '';
		if (pid) pendingIds.add(pid);
	});

	for (const promptId of trackedPromptIds) {
		const meta = queueJobMeta.get(promptId) || {};
		const prevStatus = meta.status || '';
		if (runningIds.has(promptId)) {
			meta.status = 'running';
			meta.missCount = 0;
		} else if (pendingIds.has(promptId)) {
			meta.status = 'queued';
			meta.missCount = 0;
		} else if (donePromptIds.has(promptId)) {
			meta.status = 'completed';
			meta.missCount = 0;
		} else {
			meta.missCount = (meta.missCount || 0) + 1;
			if (meta.missCount >= JOB_MISS_THRESHOLD) {
				meta.status = 'failed';
				if (prevStatus !== 'failed') {
					incrementQueueTelemetry('failed');
				}
				if (!meta.failReason) {
					meta.failReason = `No queue updates for ${JOB_MISS_THRESHOLD} polls.`;
				}
				trackedPromptIds.delete(promptId);
				pendingImageJobs.delete(promptId);
			} else {
				meta.status = 'processing';
			}
		}
		queueJobMeta.set(promptId, meta);
	}

	const failedCount = Array.from(queueJobMeta.values()).filter((m) => m.status === 'failed').length;
	const completedCount = Array.from(queueJobMeta.values()).filter((m) => m.status === 'completed').length;
	const runningCount = Array.from(queueJobMeta.entries()).filter(([promptId, meta]) => trackedPromptIds.has(promptId) && meta.status === 'running').length;
	const pendingCount = Array.from(queueJobMeta.entries()).filter(([promptId, meta]) => trackedPromptIds.has(promptId) && (meta.status === 'queued' || meta.status === 'processing')).length;
	if (clearFailedQueueBtn) {
		clearFailedQueueBtn.disabled = failedCount === 0;
		clearFailedQueueBtn.textContent = failedCount > 0 ? `Clear failed (${failedCount})` : 'Clear failed';
	}
	if (clearCompletedQueueBtn) {
		clearCompletedQueueBtn.disabled = completedCount === 0;
		clearCompletedQueueBtn.textContent = completedCount > 0 ? `Clear done (${completedCount})` : 'Clear done';
	}
	const visibleLabel = queueFilterFailedOnly ? 'Showing: Failed only' : 'Showing: All';
	queueSummary.textContent = `Running: ${runningCount}  Pending: ${pendingCount}  Tracked: ${trackedPromptIds.size}  Failed: ${failedCount}  Done: ${completedCount}  ${visibleLabel}`;

	const rows = Array.from(queueJobMeta.entries())
		.filter(([, meta]) => (queueFilterFailedOnly ? meta.status === 'failed' : true))
		.sort((a, b) => (b[1].updatedAt || 0) - (a[1].updatedAt || 0))
		.map(([promptId, meta]) => {
			const status = meta.status || 'queued';
			const promptLabel = escHtml(promptId);
			const snap = meta.snapshot || {};
			const badge =
				status === 'running' ? '<span class="history-badge positive">RUN</span>' :
				status === 'queued' ? '<span class="history-badge">WAIT</span>' :
				status === 'completed' ? '<span class="history-badge positive">DONE</span>' :
				status === 'canceled' ? '<span class="history-badge negative">CANCEL</span>' :
				status === 'failed' ? '<span class="history-badge negative">FAIL</span>' :
				'<span class="history-badge">WORK</span>';

			const canCancel = status === 'queued' || status === 'running' || status === 'processing';
			const canRetry = status === 'failed' || status === 'canceled';
			const canRerun = status === 'completed' && snap.mode !== 'img2img' && !!String(snap.prompt || '').trim();
			const cancelBusy = queueActionInFlight.has(`cancel:${promptId}`);
			const retryBusy = queueActionInFlight.has(`retry:${promptId}`);
			const rerunBusy = queueActionInFlight.has(`rerun:${promptId}`);
			const reason = meta.failReason ? `<span class="queue-reason">${escHtml(meta.failReason)}</span>` : '';
			const promptDisplay = escHtml((snap.prompt || promptId).slice(0, 72));
			const actions = [
				canCancel ? `<button class="btn btn-ghost btn-xs queue-action" data-action="cancel" data-prompt-id="${promptLabel}" aria-label="Cancel job ${promptLabel}" title="Cancel ${promptLabel}" ${cancelBusy ? 'disabled' : ''}>${cancelBusy ? 'Canceling...' : 'Cancel'}</button>` : '',
				canRetry ? `<button class="btn btn-ghost btn-xs queue-action" data-action="retry" data-prompt-id="${promptLabel}" aria-label="Retry job ${promptLabel}" title="Retry ${promptLabel}" ${retryBusy ? 'disabled' : ''}>${retryBusy ? 'Retrying...' : 'Retry'}</button>` : '',
				canRerun ? `<button class="btn btn-ghost btn-xs queue-action" data-action="rerun" data-prompt-id="${promptLabel}" aria-label="Re-run job ${promptLabel}" title="Re-run ${promptLabel}" ${rerunBusy ? 'disabled' : ''}>${rerunBusy ? 'Queuing...' : 'Re-run'}</button>` : '',
			].join('');

			const chips = [
				snap.model ? `<span class="chip">${escHtml(String(snap.model).split('/').pop().split('\\').pop())}</span>` : '',
				snap.seed != null ? `<span class="chip">seed ${escHtml(String(snap.seed))}</span>` : '',
				snap.steps ? `<span class="chip">${escHtml(String(snap.steps))} steps</span>` : '',
				snap.cfg ? `<span class="chip">cfg ${escHtml(String(snap.cfg))}</span>` : '',
				snap.width && snap.height ? `<span class="chip">${snap.width}×${snap.height}</span>` : '',
			].filter(Boolean).join('');

			return `
				<li class="history-item queue-item">
					<div class="queue-item-top">
						${badge}
						<span class="history-text" title="${escHtml(snap.prompt || promptId)}">${promptDisplay}</span>
						<span class="queue-actions">${actions}</span>
					</div>
					${chips ? `<div class="queue-item-chips">${chips}</div>` : ''}
					${reason}
				</li>
			`;
		});

	queueList.innerHTML = rows.length ? rows.join('') : '<li class="history-item"><span class="history-text">No queue items match this filter.</span></li>';
	restoreQueueActionFocus(focusedQueueAction);
}

function _clearQueueByStatus(status) {
	let cleared = 0;
	for (const [promptId, meta] of Array.from(queueJobMeta.entries())) {
		if (meta.status !== status) continue;
		queueJobMeta.delete(promptId);
		trackedPromptIds.delete(promptId);
		pendingImageJobs.delete(promptId);
		queueActionInFlight.delete(`cancel:${promptId}`);
		queueActionInFlight.delete(`retry:${promptId}`);
		queueActionInFlight.delete(`rerun:${promptId}`);
		cleared += 1;
	}
	return cleared;
}

async function clearFailedQueueItems() {
	const cleared = _clearQueueByStatus('failed');
	if (!cleared) {
		showToast('No failed items to clear.');
		renderQueueStatus([], [], new Set());
		return;
	}
	showToast(`Cleared ${cleared} failed item${cleared === 1 ? '' : 's'}.`, 'pos');
	if (trackedPromptIds.size) {
		await pollQueue();
		return;
	}
	renderQueueStatus([], [], new Set());
}

async function clearCompletedQueueItems() {
	const cleared = _clearQueueByStatus('completed');
	if (!cleared) {
		showToast('No completed items to clear.');
		renderQueueStatus([], [], new Set());
		return;
	}
	showToast(`Cleared ${cleared} completed item${cleared === 1 ? '' : 's'}.`, 'pos');
	if (trackedPromptIds.size) {
		await pollQueue();
		return;
	}
	renderQueueStatus([], [], new Set());
}

async function cancelImageJob(promptId) {
	queueActionInFlight.add(`cancel:${promptId}`);
	try {
		const res = await fetch('/api/image/cancel', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ prompt_id: promptId }),
		});
		const data = await res.json().catch(() => ({}));
		if (!res.ok) {
			showToast(`Cancel failed: ${data.error || 'Unknown error'}`, 'neg');
			return;
		}
		trackedPromptIds.delete(promptId);
		pendingImageJobs.delete(promptId);
		const meta = queueJobMeta.get(promptId) || {};
		meta.status = 'canceled';
		meta.failReason = 'Canceled by user.';
		meta.updatedAt = Date.now();
		queueJobMeta.set(promptId, meta);
		incrementQueueTelemetry('canceled');
		showToast('Job canceled.');
		await pollQueue();
	} catch (err) {
		showToast(`Cancel failed: ${err.message}`, 'neg');
	} finally {
		queueActionInFlight.delete(`cancel:${promptId}`);
	}
}

function getAutoRetryLimit() {
	const n = Number(autoRetryPolicy?.value || 0);
	if (Number.isNaN(n) || n < 0) return 0;
	return n;
}

async function retryImageJob(promptId, isAuto = false) {
	queueActionInFlight.add(`retry:${promptId}`);
	const snapshot = pendingImageJobs.get(promptId) || (queueJobMeta.get(promptId) || {}).snapshot;
	if (!snapshot) {
		showToast('Retry unavailable: no job snapshot found.', 'neg');
		queueActionInFlight.delete(`retry:${promptId}`);
		return;
	}

	try {
		const parentMeta = queueJobMeta.get(promptId) || {};
		const nextRetryCount = (parentMeta.retryCount || 0) + 1;
		const isImg2Img = snapshot.mode === 'img2img' && snapshot.image_name;
		let res;
		if (isImg2Img) {
			const failedMeta = queueJobMeta.get(promptId) || {};
			failedMeta.retryCount = nextRetryCount;
			failedMeta.failReason = 'Retry requires re-uploading img2img source image.';
			queueJobMeta.set(promptId, failedMeta);
			if (!isAuto) {
				showToast('Retry for img2img requires re-uploading source image.', 'neg');
			}
			queueActionInFlight.delete(`retry:${promptId}`);
			return;
		}

		res = await fetch('/api/image/generate', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(snapshot),
		});
		const data = await res.json();
		if (!res.ok) {
			showToast(`Retry failed: ${data.error || 'Unknown error'}`, 'neg');
			return;
		}

		const newPromptId = data.prompt_id;
		const retryCount = nextRetryCount;
		trackedPromptIds.add(newPromptId);
		pendingImageJobs.set(newPromptId, { ...snapshot, ...(data.meta || {}) });
		parentMeta.status = isAuto ? 'retrying' : 'failed';
		parentMeta.failReason = isAuto ? `Auto-retrying as ${newPromptId}` : 'Retried manually.';
		parentMeta.updatedAt = Date.now();
		queueJobMeta.set(promptId, parentMeta);
		queueJobMeta.set(newPromptId, {
			status: 'queued',
			missCount: 0,
			retryCount,
			updatedAt: Date.now(),
			snapshot: { ...snapshot, ...(data.meta || {}) },
		});
		incrementQueueTelemetry('retried');
		ensureQueuePolling();
		if (!isAuto) showToast('Retry submitted.', 'pos');
		await pollQueue();
	} catch (err) {
		showToast(`Retry failed: ${err.message}`, 'neg');
		const meta = queueJobMeta.get(promptId) || {};
		const prevStatus = meta.status || '';
		meta.status = 'failed';
		meta.retryCount = (meta.retryCount || 0) + 1;
		meta.failReason = `Retry failed: ${err.message}`;
		queueJobMeta.set(promptId, meta);
		if (prevStatus !== 'failed') {
			incrementQueueTelemetry('failed');
		}
	} finally {
		queueActionInFlight.delete(`retry:${promptId}`);
	}
}

async function rerunImageJob(promptId) {
	const snapshot = (queueJobMeta.get(promptId) || {}).snapshot;
	if (!snapshot || !String(snapshot.prompt || '').trim()) {
		showToast('Re-run unavailable: no job snapshot found.', 'neg');
		return;
	}
	if (snapshot.mode === 'img2img') {
		showToast('Re-run requires re-uploading the img2img source image.', 'neg');
		return;
	}
	queueActionInFlight.add(`rerun:${promptId}`);
	try {
		// Omit the seed so the backend generates a fresh one; reusing the same
		// seed causes ComfyUI to return a cached result with no output images.
		const { seed: _seed, ...rerunPayload } = snapshot;
		const res = await fetch('/api/image/generate', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(rerunPayload),
		});
		const data = await res.json();
		if (!res.ok) {
			showToast(`Re-run failed: ${data.error || 'Unknown error'}`, 'neg');
			return;
		}
		const newPromptId = data.prompt_id;
		trackedPromptIds.add(newPromptId);
		pendingImageJobs.set(newPromptId, { ...snapshot, ...(data.meta || {}) });
		queueJobMeta.set(newPromptId, {
			status: 'queued',
			missCount: 0,
			updatedAt: Date.now(),
			snapshot: { ...snapshot, ...(data.meta || {}) },
		});
		incrementQueueTelemetry('submitted');
		ensureQueuePolling();
		showToast('Re-run submitted.', 'pos');
		await pollQueue();
	} catch (err) {
		showToast(`Re-run failed: ${err.message}`, 'neg');
	} finally {
		queueActionInFlight.delete(`rerun:${promptId}`);
		if (trackedPromptIds.size) {
			await pollQueue();
		} else {
			renderQueueStatus([], [], new Set());
		}
	}
}

async function processAutoRetries() {
	const limit = getAutoRetryLimit();
	if (limit <= 0) return;

	for (const [promptId, meta] of queueJobMeta.entries()) {
		if (meta.status !== 'failed') continue;
		if ((meta.retryCount || 0) >= limit) continue;
		if (queueActionInFlight.has(`retry:${promptId}`)) continue;
		if (!meta.snapshot) continue;
		await retryImageJob(promptId, true);
	}
}

queueList.addEventListener('click', async (e) => {
	const target = e.target;
	if (!(target instanceof HTMLElement)) return;
	if (!target.classList.contains('queue-action')) return;

	const action = target.getAttribute('data-action');
	const promptId = target.getAttribute('data-prompt-id');
	if (!action || !promptId) return;

	if (action === 'cancel') {
		if (queueActionInFlight.has(`cancel:${promptId}`)) return;
		target.setAttribute('disabled', 'disabled');
		await cancelImageJob(promptId);
		return;
	}
	if (action === 'retry') {
		if (queueActionInFlight.has(`retry:${promptId}`)) return;
		target.setAttribute('disabled', 'disabled');
		await retryImageJob(promptId);
		return;
	}
	if (action === 'rerun') {
		if (queueActionInFlight.has(`rerun:${promptId}`)) return;
		target.setAttribute('disabled', 'disabled');
		await rerunImageJob(promptId);
	}
});

if (clearFailedQueueBtn) {
	clearFailedQueueBtn.addEventListener('click', async () => {
		clearFailedQueueBtn.disabled = true;
		await clearFailedQueueItems();
	});
}

if (clearCompletedQueueBtn) {
	clearCompletedQueueBtn.addEventListener('click', async () => {
		clearCompletedQueueBtn.disabled = true;
		await clearCompletedQueueItems();
	});
}

async function saveHistoryEntry(entry) {
	try {
		await fetch('/api/history', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(entry),
		});
	} catch {
		// non-fatal
	}
}

function imageProxyUrl(image) {
	const params = new URLSearchParams({
		filename: image.filename,
		subfolder: image.subfolder || '',
		type: image.type || 'output',
	});
	return `/api/image/view?${params.toString()}`;
}

function buildGalleryPreviewPayload(entry, imgUrl) {
	return {
		prompt: entry.prompt || 'Image generation',
		negative_prompt: entry.negative_prompt || '',
		model: entry.model || '',
		sampler: entry.params?.sampler || '',
		seed: entry.params?.seed ?? null,
		steps: entry.params?.steps ?? '',
		cfg: entry.params?.cfg ?? '',
		denoise: entry.params?.denoise ?? '',
		width: entry.params?.width ?? '',
		height: entry.params?.height ?? '',
		batch_size: entry.params?.batch_size ?? '',
		created_at: entry.created_at || null,
		imgUrl,
	};
}

function parseGalleryPreviewPayload(raw) {
	if (!raw) return null;
	try {
		const decoded = decodeURIComponent(raw);
		const parsed = JSON.parse(decoded);
		if (!parsed || typeof parsed !== 'object') return null;
		if (typeof parsed.imgUrl !== 'string' || !parsed.imgUrl) return null;
		return parsed;
	} catch {
		return null;
	}
}

function parseImageRefPayload(raw) {
	if (!raw) return null;
	try {
		const decoded = decodeURIComponent(raw);
		const parsed = JSON.parse(decoded);
		if (!parsed || typeof parsed !== 'object') return null;
		if (!parsed.filename) return null;
		return {
			filename: String(parsed.filename || ''),
			subfolder: String(parsed.subfolder || ''),
			type: String(parsed.type || 'output'),
		};
	} catch {
		return null;
	}
}

function buildGalleryExportBaseName(entry, imageRef) {
	const ts = Number(entry.created_at || 0);
	const stamp = ts ? new Date(ts * 1000).toISOString().replace(/[:.]/g, '-').replace('T', '_').replace('Z', '') : 'image';
	const rawPrompt = String(entry.prompt || 'generated-image').toLowerCase();
	const promptStem = rawPrompt
		.replace(/[^a-z0-9\s_-]/g, '')
		.trim()
		.replace(/\s+/g, '-')
		.slice(0, 48) || 'generated-image';
	const fileStem = String(imageRef.filename || '').replace(/\.[^.]+$/, '').replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 24);
	return [promptStem, fileStem, stamp].filter(Boolean).join('_');
}

function clampPreviewZoom(scale) {
	return Math.max(PREVIEW_ZOOM_MIN, Math.min(PREVIEW_ZOOM_MAX, scale));
}

function applyPreviewZoom(scale) {
	if (!previewImage || previewImage.hidden) return;
	previewZoomScale = clampPreviewZoom(scale);
	previewImage.style.transform = `scale(${previewZoomScale.toFixed(3)})`;
}

function resetPreviewZoom() {
	previewZoomScale = 1;
	if (!previewImage) return;
	previewImage.style.transform = 'scale(1)';
}

function closeGalleryContextMenu() {
	if (!galleryContextMenu) return;
	galleryContextMenu.hidden = true;
	galleryContextPayload = null;
}

function openGalleryContextMenu(payload, x, y) {
	if (!galleryContextMenu) return;
	galleryContextPayload = payload;
	galleryContextMenu.hidden = false;

	const viewportW = window.innerWidth;
	const viewportH = window.innerHeight;
	const menuRect = galleryContextMenu.getBoundingClientRect();
	const nextLeft = Math.max(6, Math.min(x, viewportW - menuRect.width - 6));
	const nextTop = Math.max(6, Math.min(y, viewportH - menuRect.height - 6));
	galleryContextMenu.style.left = `${nextLeft}px`;
	galleryContextMenu.style.top = `${nextTop}px`;
}

function buildImageRefFromElement(element) {
	if (!(element instanceof HTMLElement)) return null;
	const raw = element.dataset.imageRef;
	return parseImageRefPayload(raw || '');
}

async function callGalleryImageApi(path, imageRef) {
	const res = await fetch(path, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(imageRef),
	});
	const data = await res.json();
	if (!res.ok) {
		throw new Error(data.error || `Request failed (${res.status})`);
	}
	return data;
}

function saveBlobAs(blob, filename) {
	const objectUrl = URL.createObjectURL(blob);
	const link = document.createElement('a');
	link.href = objectUrl;
	link.download = filename;
	document.body.appendChild(link);
	link.click();
	link.remove();
	window.setTimeout(() => URL.revokeObjectURL(objectUrl), 1800);
}

function loadImageFromBlob(blob) {
	return new Promise((resolve, reject) => {
		const objectUrl = URL.createObjectURL(blob);
		const image = new Image();
		image.onload = () => {
			URL.revokeObjectURL(objectUrl);
			resolve(image);
		};
		image.onerror = () => {
			URL.revokeObjectURL(objectUrl);
			reject(new Error('Could not decode image for export'));
		};
		image.src = objectUrl;
	});
}

async function exportGalleryImage(payload, format, keepMetadata = false) {
	if (!payload || !payload.imageRef) return;
	const imgUrl = imageProxyUrl(payload.imageRef);
	const extension = format === 'jpeg' ? 'jpg' : format;
	const filename = `${payload.baseName || 'generated-image'}.${extension}`;
	const formatLabel = {
		png: 'PNG',
		jpeg: 'JPEG',
		webp: 'WebP',
	}[format] || String(format || '').toUpperCase();

	if (keepMetadata && format === 'png') {
		const link = document.createElement('a');
		link.href = imgUrl;
		link.download = filename;
		document.body.appendChild(link);
		link.click();
		link.remove();
		showToast(`Exported ${formatLabel} (metadata preserved): ${filename}`, 'pos');
		return;
	}

	const res = await fetch(imgUrl);
	if (!res.ok) {
		throw new Error('Could not fetch source image for export');
	}
	const sourceBlob = await res.blob();
	const image = await loadImageFromBlob(sourceBlob);
	const canvas = document.createElement('canvas');
	canvas.width = image.naturalWidth || image.width;
	canvas.height = image.naturalHeight || image.height;
	const ctx = canvas.getContext('2d');
	if (!ctx) {
		throw new Error('Canvas export is unavailable in this browser');
	}
	ctx.drawImage(image, 0, 0);

	const mime = {
		png: 'image/png',
		jpeg: 'image/jpeg',
		webp: 'image/webp',
	}[format] || 'image/png';

	const quality = format === 'jpeg' || format === 'webp' ? 0.92 : undefined;
	const exportedBlob = await new Promise((resolve) => canvas.toBlob(resolve, mime, quality));
	if (!exportedBlob) {
		throw new Error('Image export failed');
	}
	saveBlobAs(exportedBlob, filename);
	showToast(`Exported ${formatLabel}: ${filename}`, 'pos');
}

async function handleGalleryContextAction(action) {
	if (!galleryContextPayload) return;
	const payload = galleryContextPayload;
	closeGalleryContextMenu();

	try {
		if (action === 'open-location') {
			await callGalleryImageApi('/api/image/open-location', payload.imageRef);
			showToast('Opened image location.', 'pos');
			return;
		}

		if (action === 'delete-image') {
			const confirmed = window.confirm('Delete this image file and remove it from local history?');
			if (!confirmed) return;
			await callGalleryImageApi('/api/image/delete', payload.imageRef);
			showToast('Image deleted.', 'pos');
			await loadGallery();
			await loadLivePreview();
			return;
		}

		if (action === 'export-png-meta') {
			await exportGalleryImage(payload, 'png', true);
			return;
		}
		if (action === 'export-png') {
			await exportGalleryImage(payload, 'png');
			return;
		}
		if (action === 'export-jpeg') {
			await exportGalleryImage(payload, 'jpeg');
			return;
		}
		if (action === 'export-webp') {
			await exportGalleryImage(payload, 'webp');
		}
	} catch (err) {
		showToast(`Action failed: ${err.message}`, 'neg');
	}
}

function updateGalleryFilterHint(matching, total) {
	if (!galleryFilterHint) return;
	if (!gallerySearchQuery || !total) {
		galleryFilterHint.hidden = true;
		galleryFilterHint.textContent = '';
		return;
	}
	galleryFilterHint.hidden = false;
	galleryFilterHint.textContent = matching
		? `Showing ${matching} of ${total} images matching "${gallerySearchQuery}"`
		: `No images match "${gallerySearchQuery}"`;
}

function updateLightboxNav() {
	const total = currentGalleryImages.length;
	if (galleryLightboxPrev) galleryLightboxPrev.hidden = total <= 1;
	if (galleryLightboxNext) galleryLightboxNext.hidden = total <= 1;
	if (galleryLightboxCounter) {
		galleryLightboxCounter.textContent = total > 1 ? `${lightboxCurrentIndex + 1} / ${total}` : '';
	}
}

function navigateLightbox(delta) {
	const total = currentGalleryImages.length;
	if (total <= 1) return;
	lightboxCurrentIndex = ((lightboxCurrentIndex + delta) % total + total) % total;
	const entry = currentGalleryImages[lightboxCurrentIndex];
	if (!entry) return;
	const firstImage = entry.images?.[0];
	if (!firstImage || !galleryLightboxImage) return;
	galleryLightboxImage.src = imageProxyUrl(firstImage);
	galleryLightboxImage.alt = 'Generated image';
	if (galleryLightboxCaption) {
		galleryLightboxCaption.textContent = entry.prompt || 'Untitled generation';
	}
	updateLightboxNav();
}

function updateLivePreviewFromGalleryPayload(payload) {
	if (!payload || !payload.imgUrl) return;
	resetPreviewZoom();
	previewImage.src = payload.imgUrl;
	previewImage.hidden = false;
	previewEmpty.hidden = true;
	previewMeta.hidden = false;
	previewPrompt.textContent = payload.prompt || 'Image generation';

	const chips = [];
	if (payload.model) chips.push(`<span class="chip">${escHtml(payload.model)}</span>`);
	if (payload.sampler) chips.push(`<span class="chip">${escHtml(payload.sampler)}</span>`);
	if (payload.steps !== '' && payload.steps !== null) chips.push(`<span class="chip">steps ${escHtml(String(payload.steps))}</span>`);
	if (payload.cfg !== '' && payload.cfg !== null) chips.push(`<span class="chip">cfg ${escHtml(String(payload.cfg))}</span>`);
	previewChipRow.innerHTML = chips.join('');
	previewUpdated.textContent = `Loaded from gallery • ${formatPreviewTime(payload.created_at)}`;
}

function setSelectValueIfOptionExists(selectEl, value) {
	if (!selectEl || !value) return;
	const hasOption = [...selectEl.options].some((option) => option.value === value);
	if (!hasOption) {
		const option = document.createElement('option');
		option.value = value;
		option.textContent = value;
		selectEl.appendChild(option);
	}
	selectEl.value = value;
}

function setNumericInputIfFinite(inputEl, value) {
	if (!inputEl) return;
	const n = Number(value);
	if (Number.isFinite(n)) {
		inputEl.value = String(n);
	}
}

function applyGalleryPayloadToImageForm(payload) {
	if (!payload) return;

	if (typeof payload.prompt === 'string') imagePrompt.value = payload.prompt;
	if (typeof payload.negative_prompt === 'string') imageNegativePrompt.value = payload.negative_prompt;

	setSelectValueIfOptionExists(imageModelSelect, payload.model);
	setSelectValueIfOptionExists(imageSamplerSelect, payload.sampler);

	if (payload.seed !== null && payload.seed !== undefined && payload.seed !== '') {
		imageSeed.value = String(payload.seed);
	}
	setNumericInputIfFinite(imageSteps, payload.steps);
	setNumericInputIfFinite(imageCfg, payload.cfg);
	setNumericInputIfFinite(imageDenoise, payload.denoise);
	setNumericInputIfFinite(imageWidth, payload.width);
	setNumericInputIfFinite(imageHeight, payload.height);
	setNumericInputIfFinite(imageBatchSize, payload.batch_size);
	syncImageControlLabels();
}

function openGalleryLightbox(imgSrc, imgAlt, caption = '', index = 0) {
	if (!galleryLightbox || !galleryLightboxImage) return;
	lightboxCurrentIndex = index;
	galleryLightboxImage.src = imgSrc;
	galleryLightboxImage.alt = imgAlt || 'Generated image';
	if (galleryLightboxCaption) {
		galleryLightboxCaption.textContent = caption;
	}
	updateLightboxNav();
	galleryLightbox.hidden = false;
	galleryLightbox.setAttribute('aria-hidden', 'false');
	document.body.classList.add('gallery-lightbox-open');
	if (galleryLightboxCloseBtn) {
		galleryLightboxCloseBtn.focus();
	}
}

function closeGalleryLightbox() {
	if (!galleryLightbox || !galleryLightboxImage) return;
	galleryLightbox.hidden = true;
	galleryLightbox.setAttribute('aria-hidden', 'true');
	galleryLightboxImage.src = '';
	galleryLightboxImage.alt = '';
	if (galleryLightboxCaption) {
		galleryLightboxCaption.textContent = '';
	}
	document.body.classList.remove('gallery-lightbox-open');
}

function renderGallery(history) {
	currentFullHistory = history;
	const images = history.filter((item) => item.type === 'image');
	if (!images.length) {
		galleryGrid.innerHTML = '<div class="empty-gallery">No image generations yet.</div>';
		currentGalleryImages = [];
		closeGalleryContextMenu();
		updateGalleryFilterHint(0, 0);
		return;
	}

	const orderedImages = images
		.slice()
		.sort((a, b) => (Number(b.created_at) || 0) - (Number(a.created_at) || 0));

	const query = gallerySearchQuery.toLowerCase().trim();
	const filteredImages = query
		? orderedImages.filter((e) => (e.prompt || '').toLowerCase().includes(query))
		: orderedImages;

	updateGalleryFilterHint(filteredImages.length, orderedImages.length);

	if (!filteredImages.length) {
		galleryGrid.innerHTML = '<div class="empty-gallery">No images match that filter.</div>';
		currentGalleryImages = [];
		return;
	}

	currentGalleryImages = filteredImages;
	galleryGrid.classList.toggle('is-grid-mode', galleryViewMode === 'grid');

	galleryGrid.innerHTML = filteredImages
		.map((entry, index) => {
			const firstImage = entry.images?.[0];
			if (!firstImage) return '';
			const imgUrl = imageProxyUrl(firstImage);
			const dragPayload = encodeURIComponent(JSON.stringify(buildGalleryPreviewPayload(entry, imgUrl)));
			const imageRefPayload = encodeURIComponent(JSON.stringify({
				filename: firstImage.filename || '',
				subfolder: firstImage.subfolder || '',
				type: firstImage.type || 'output',
			}));
			const exportBaseName = buildGalleryExportBaseName(entry, firstImage);
			const prompt = escHtml(entry.prompt || 'Untitled generation');
			const model = escHtml(entry.model || 'unknown model');
			const sampler = escHtml(entry.params?.sampler || 'sampler');
			const steps = escHtml(String(entry.params?.steps || ''));
			const cfg = escHtml(String(entry.params?.cfg || ''));
			return `
				<article class="gallery-card" draggable="true" data-preview-payload="${dragPayload}" data-image-ref="${imageRefPayload}" data-export-base-name="${escHtml(exportBaseName)}" data-prompt="${prompt}" data-lightbox-index="${index}">
					<img src="${imgUrl}" alt="Generated image" loading="eager" decoding="async" data-lightbox-src="${imgUrl}" data-lightbox-caption="${prompt}" draggable="false" />
					<div class="gallery-meta">
						<p class="gallery-prompt" title="${prompt}">${prompt}</p>
						<p class="gallery-chip-row">
							<span class="chip">${model}</span>
							<span class="chip">${sampler}</span>
							<span class="chip">steps ${steps}</span>
							<span class="chip">cfg ${cfg}</span>
						</p>
					</div>
				</article>
			`;
		})
		.join('');
}

if (galleryGrid) {
	galleryGrid.addEventListener('dragstart', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLElement)) return;
		const card = target.closest('.gallery-card');
		if (!(card instanceof HTMLElement)) return;
		const payload = card.dataset.previewPayload;
		if (!payload || !event.dataTransfer) return;
		event.dataTransfer.effectAllowed = 'copy';
		event.dataTransfer.setData('text/plain', payload);
		card.classList.add('is-dragging');
	});

	galleryGrid.addEventListener('dragend', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLElement)) return;
		const card = target.closest('.gallery-card');
		if (!(card instanceof HTMLElement)) return;
		card.classList.remove('is-dragging');
		if (previewCard) previewCard.classList.remove('is-drop-target');
	});

	galleryGrid.addEventListener('click', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLImageElement)) return;
		const card = target.closest('.gallery-card');
		const index = card instanceof HTMLElement ? parseInt(card.dataset.lightboxIndex || '0', 10) : 0;
		const src = target.getAttribute('data-lightbox-src') || target.src;
		const caption = target.getAttribute('data-lightbox-caption') || '';
		openGalleryLightbox(src, target.alt, caption, index);
	});

	galleryGrid.addEventListener('contextmenu', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLElement)) return;
		const card = target.closest('.gallery-card');
		if (!(card instanceof HTMLElement)) return;
		const imageRef = buildImageRefFromElement(card);
		if (!imageRef) return;

		event.preventDefault();
		openGalleryContextMenu(
			{
				imageRef,
				baseName: card.dataset.exportBaseName || 'generated-image',
				prompt: card.dataset.prompt || 'Generated image',
			},
			event.clientX,
			event.clientY,
		);
	});
}

if (previewCard) {
	previewCard.addEventListener('dragover', (event) => {
		event.preventDefault();
		if (event.dataTransfer) {
			event.dataTransfer.dropEffect = 'copy';
		}
		previewCard.classList.add('is-drop-target');
	});

	previewCard.addEventListener('dragleave', (event) => {
		if (!(event.relatedTarget instanceof Node) || !previewCard.contains(event.relatedTarget)) {
			previewCard.classList.remove('is-drop-target');
		}
	});

	previewCard.addEventListener('drop', (event) => {
		event.preventDefault();
		previewCard.classList.remove('is-drop-target');
		const rawPayload = event.dataTransfer?.getData('text/plain') || '';
		const payload = parseGalleryPreviewPayload(rawPayload);
		if (!payload) return;
		updateLivePreviewFromGalleryPayload(payload);
		applyGalleryPayloadToImageForm(payload);
	});

	previewCard.addEventListener('wheel', (event) => {
		if (!previewImage || previewImage.hidden) return;
		event.preventDefault();
		const direction = event.deltaY < 0 ? 1 : -1;
		applyPreviewZoom(previewZoomScale + (direction * PREVIEW_ZOOM_STEP));
	}, { passive: false });
}

if (previewImage) {
	previewImage.addEventListener('dblclick', () => {
		if (previewImage.hidden) return;
		resetPreviewZoom();
	});
}

if (galleryLightbox) {
	galleryLightbox.addEventListener('click', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLElement)) return;
		if (target.dataset.lightboxClose === 'backdrop') {
			closeGalleryLightbox();
		}
	});
}

if (galleryLightboxCloseBtn) {
	galleryLightboxCloseBtn.addEventListener('click', closeGalleryLightbox);
}

document.addEventListener('keydown', (event) => {
	const key = event.key;
	if (key !== 'Escape' && key !== 'ArrowLeft' && key !== 'ArrowRight') return;

	if (key === 'Escape') {
		if (galleryContextMenu && !galleryContextMenu.hidden) {
			closeGalleryContextMenu();
			return;
		}
		if (!galleryLightbox || galleryLightbox.hidden) return;
		closeGalleryLightbox();
		return;
	}

	if (!galleryLightbox || galleryLightbox.hidden) return;
	event.preventDefault();
	if (key === 'ArrowLeft') navigateLightbox(-1);
	if (key === 'ArrowRight') navigateLightbox(1);
});

if (galleryContextMenu) {
	galleryContextMenu.addEventListener('click', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLElement)) return;
		const action = target.getAttribute('data-gallery-action');
		if (!action) return;
		handleGalleryContextAction(action);
	});

	document.addEventListener('click', (event) => {
		if (galleryContextMenu.hidden) return;
		if (!(event.target instanceof Node)) return;
		if (galleryContextMenu.contains(event.target)) return;
		closeGalleryContextMenu();
	});

	window.addEventListener('resize', closeGalleryContextMenu);
	window.addEventListener('scroll', closeGalleryContextMenu, true);
}

if (gallerySearch) {
	let searchDebounceTimer = null;
	gallerySearch.addEventListener('input', () => {
		clearTimeout(searchDebounceTimer);
		searchDebounceTimer = window.setTimeout(() => {
			gallerySearchQuery = gallerySearch.value || '';
			renderGallery(currentFullHistory);
		}, 220);
	});
	gallerySearch.addEventListener('keydown', (e) => {
		if (e.key !== 'Escape') return;
		e.stopPropagation();
		gallerySearch.value = '';
		gallerySearchQuery = '';
		renderGallery(currentFullHistory);
	});
}

if (galleryViewToggle) {
	galleryViewToggle.addEventListener('click', () => {
		galleryViewMode = galleryViewMode === 'grid' ? 'list' : 'grid';
		localStorage.setItem('galleryViewMode', galleryViewMode);
		galleryViewToggle.textContent = galleryViewMode === 'grid' ? 'List' : 'Grid';
		galleryViewToggle.setAttribute('aria-pressed', String(galleryViewMode === 'grid'));
		galleryGrid.classList.toggle('is-grid-mode', galleryViewMode === 'grid');
	});
	galleryViewToggle.textContent = galleryViewMode === 'grid' ? 'List' : 'Grid';
	galleryViewToggle.setAttribute('aria-pressed', String(galleryViewMode === 'grid'));
}

if (galleryLightboxPrev) {
	galleryLightboxPrev.addEventListener('click', () => navigateLightbox(-1));
}

if (galleryLightboxNext) {
	galleryLightboxNext.addEventListener('click', () => navigateLightbox(1));
}

function updateLivePreviewFromActiveJob(payload) {
	const imageRef = payload?.image;
	if (!imageRef || !imageRef.filename) return false;

	resetPreviewZoom();
	previewImage.src = imageProxyUrl(imageRef);
	previewImage.hidden = false;
	previewEmpty.hidden = true;
	previewMeta.hidden = false;
	previewPrompt.textContent = payload.prompt || 'Rendering image...';
	previewChipRow.innerHTML = payload.prompt_id ? `<span class="chip">job ${escHtml(payload.prompt_id)}</span>` : '';
	previewUpdated.textContent = payload.status === 'running'
		? 'Live preview from active generation'
		: 'Preview from queued generation';
	return true;
}

async function loadActiveLivePreview(promptIds) {
	if (!promptIds || !promptIds.length) return false;
	const query = encodeURIComponent(promptIds.join(','));
	try {
		const res = await fetch(`/api/image/live-preview?prompt_ids=${query}`);
		if (!res.ok) return false;
		const data = await res.json();
		if (!data.preview) return false;
		return updateLivePreviewFromActiveJob(data.preview);
	} catch {
		return false;
	}
}

function formatPreviewTime(unixTs) {
	if (!unixTs) return 'Waiting for output...';
	const date = new Date(unixTs * 1000);
	return `Updated ${date.toLocaleTimeString()}`;
}

function updateLivePreview(entry) {
	if (!entry || !entry.images || !entry.images.length) {
		previewEmpty.hidden = false;
		previewImage.hidden = true;
		previewMeta.hidden = true;
		previewUpdated.textContent = 'Waiting for output...';
		resetPreviewZoom();
		return;
	}

	const firstImage = entry.images[0];
	resetPreviewZoom();
	previewImage.src = imageProxyUrl(firstImage);
	previewImage.hidden = false;
	previewEmpty.hidden = true;
	previewMeta.hidden = false;
	previewPrompt.textContent = entry.prompt || 'Image generation';

	const chips = [];
	if (entry.model) chips.push(`<span class="chip">${escHtml(entry.model)}</span>`);
	if (entry.params?.sampler) chips.push(`<span class="chip">${escHtml(entry.params.sampler)}</span>`);
	if (entry.params?.steps) chips.push(`<span class="chip">steps ${escHtml(String(entry.params.steps))}</span>`);
	if (entry.params?.cfg) chips.push(`<span class="chip">cfg ${escHtml(String(entry.params.cfg))}</span>`);
	previewChipRow.innerHTML = chips.join('');
	previewUpdated.textContent = formatPreviewTime(entry.created_at);
}

async function loadLivePreview() {
	const activePromptIds = Array.from(trackedPromptIds);
	if (activePromptIds.length) {
		const foundActivePreview = await loadActiveLivePreview(activePromptIds);
		if (foundActivePreview) return;
	}

	try {
		const res = await fetch('/api/history?type=image&limit=1');
		const data = await res.json();
		const latest = (data.history || [])[0];
		updateLivePreview(latest);
	} catch {
		previewUpdated.textContent = 'Preview unavailable';
	}
}

/* --------------------------------------------------------------------------
	 ComfyUI WebSocket — real-time step preview
	 -------------------------------------------------------------------------- */
let comfyWs = null;
let comfyWsPreviewUrl = null;
let comfyWsReconnectTimer = null;
let comfyWsFailCount = 0;
const COMFY_WS_MAX_RETRIES = 4;
const comfyWsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const comfyWsHost = window.location.hostname || 'localhost';
const COMFY_WS_URL = `${comfyWsProtocol}://${comfyWsHost}:8188/ws?clientId=${tabInstanceId}`;

function _revokeComfyPreviewUrl() {
	if (comfyWsPreviewUrl) {
		URL.revokeObjectURL(comfyWsPreviewUrl);
		comfyWsPreviewUrl = null;
	}
}

function _showComfyStepPreview(blobUrl) {
	_revokeComfyPreviewUrl();
	comfyWsPreviewUrl = blobUrl;
	resetPreviewZoom();
	previewImage.src = blobUrl;
	previewImage.hidden = false;
	previewEmpty.hidden = true;
	previewMeta.hidden = false;
}

function connectComfyWebSocket() {
	if (comfyWs && (comfyWs.readyState === WebSocket.OPEN || comfyWs.readyState === WebSocket.CONNECTING)) return;
	if (comfyWsFailCount >= COMFY_WS_MAX_RETRIES) return; // gave up; reset on tab focus
	if (comfyWsReconnectTimer) {
		window.clearTimeout(comfyWsReconnectTimer);
		comfyWsReconnectTimer = null;
	}
	try {
		comfyWs = new WebSocket(COMFY_WS_URL);
		comfyWs.binaryType = 'arraybuffer';

		comfyWs.onmessage = (event) => {
			if (event.data instanceof ArrayBuffer) {
				if (!trackedPromptIds.size) return;
				// Binary frame: first 4 bytes = event type (big-endian uint32)
				// 1 = PREVIEW_IMAGE; remaining bytes are the JPEG image
				const view = new DataView(event.data);
				const eventType = view.getUint32(0);
				if (eventType === 1) {
					const imageBytes = event.data.slice(4);
					const blob = new Blob([imageBytes], { type: 'image/jpeg' });
					_showComfyStepPreview(URL.createObjectURL(blob));
					previewUpdated.textContent = 'Live preview — generating…';
					if (previewPrompt && !previewPrompt.textContent) {
						previewPrompt.textContent = 'Rendering…';
					}
				}
			} else {
				try {
					const msg = JSON.parse(event.data);
					if (msg.type === 'progress' && msg.data) {
						const { value, max } = msg.data;
						if (trackedPromptIds.size) {
							previewUpdated.textContent = `Generating… step ${value} / ${max}`;
						}
					} else if (msg.type === 'executed' && msg.data?.prompt_id) {
						if (trackedPromptIds.has(msg.data.prompt_id)) {
							// Final image is ready — refresh preview from history
							setTimeout(() => { loadLivePreview(); loadGallery(); }, 400);
						}
					}
				} catch { /* ignore malformed JSON */ }
			}
		};

		comfyWs.onopen = () => { comfyWsFailCount = 0; };
		comfyWs.onerror = () => { /* errors handled in onclose */ };
		comfyWs.onclose = () => {
			comfyWs = null;
			comfyWsFailCount++;
			if (comfyWsFailCount >= COMFY_WS_MAX_RETRIES) {
				// ComfyUI WS unavailable (likely cross-origin 403); HTTP polling covers live preview
				return;
			}
			// Reconnect with exponential backoff if page is still visible
			if (!document.hidden) {
				const delay = Math.min(5000 * Math.pow(2, comfyWsFailCount - 1), 60000);
				comfyWsReconnectTimer = window.setTimeout(connectComfyWebSocket, delay);
			}
		};
	} catch { /* WebSocket unavailable — polling will cover this */ }
}

document.addEventListener('visibilitychange', () => {
	if (!document.hidden && !comfyWs) {
		// Reset failure count on tab re-focus so it can retry after a long pause
		comfyWsFailCount = 0;
		connectComfyWebSocket();
	}
});

function startLivePreviewAutoRefresh() {
	if (!hasBackgroundPollingOwnership) return;
	if (livePreviewTimer) return;
	livePreviewTimer = window.setInterval(loadLivePreview, 4000);
}

async function loadGallery() {
	try {
		const res = await fetch('/api/history?type=image');
		const data = await res.json();
		const history = data.history || [];
		renderGallery(history);
		updateLivePreview(history[0]);
	} catch {
		galleryGrid.innerHTML = '<div class="empty-gallery">Could not load gallery.</div>';
		previewUpdated.textContent = 'Preview unavailable';
	}
}

refreshGalleryBtn.addEventListener('click', loadGallery);

async function pollQueue() {
	const ids = Array.from(trackedPromptIds);
	if (!ids.length) {
		renderQueueStatus([], [], new Set());
		stopQueuePolling();
		return;
	}

	try {
		const idList = ids.map((id) => encodeURIComponent(id)).join(',');
		const res = await fetch(`/api/image/queue?prompt_ids=${idList}`);
		const data = await res.json();
		const running = data.running || [];
		const pending = data.pending || [];
		const doneItems = data.done || [];
		const donePromptIds = new Set(doneItems.map((d) => d.prompt_id).filter(Boolean));
		renderQueueStatus(running, pending, donePromptIds);
		await loadActiveLivePreview(ids);
		if (doneItems.length) {
			for (const done of doneItems) {
				const promptId = done.prompt_id;
				const images = done.images || [];
				if (!images.length) continue;
				const snapshot = pendingImageJobs.get(promptId) || {};

				await saveHistoryEntry({
					type: 'image',
					prompt: snapshot.prompt || 'Image generation',
					negative_prompt: snapshot.negative_prompt || '',
					engine: 'comfyui',
					model: snapshot.model || '',
					params: {
						sampler: snapshot.sampler || '',
						seed: snapshot.seed || null,
						steps: snapshot.steps || 0,
						cfg: snapshot.cfg || 0,
						denoise: snapshot.denoise || 0,
						width: snapshot.width || 0,
						height: snapshot.height || 0,
						batch_size: snapshot.batch_size || 1,
						mode: snapshot.mode || 'txt2img',
						prompt_id: promptId,
					},
					images,
				});

				trackedPromptIds.delete(promptId);
				const meta = queueJobMeta.get(promptId) || {};
				meta.status = 'completed';
				meta.updatedAt = Date.now();
				meta.snapshot = snapshot;
				queueJobMeta.set(promptId, meta);
				pendingImageJobs.delete(promptId);
			}
			await loadGallery();
			await loadLivePreview();
		}

		if (!trackedPromptIds.size) {
			imageGenerateBtn.disabled = false;
			imageGenerateBtn.textContent = 'Generate Image';
		}

		await processAutoRetries();
	} catch {
		// non-fatal poll failures
	}
}

function ensureQueuePolling() {
	if (!hasBackgroundPollingOwnership) return;
	if (queuePollTimer) return;
	queuePollTimer = window.setInterval(pollQueue, 2500);
}

function stopQueuePolling() {
	if (!queuePollTimer) return;
	window.clearInterval(queuePollTimer);
	queuePollTimer = null;
}

function validateImageInputs(common) {
	if (!common.model) {
		return 'Select a checkpoint model before generating.';
	}
	if (/flux/i.test(common.model)) {
		return 'Selected model appears to be a FLUX checkpoint, which is not supported by the current workflow. Choose a non-FLUX checkpoint (SD/SDXL) for now.';
	}
	if (common.width < 256 || common.width > 2048 || common.height < 256 || common.height > 2048) {
		return 'Width and height must be between 256 and 2048.';
	}
	if (common.width % 64 !== 0 || common.height % 64 !== 0) {
		return 'Width and height should be multiples of 64.';
	}
	if (common.batch_size < 1 || common.batch_size > 8) {
		return 'Batch size must be between 1 and 8.';
	}
	if (common.steps < 1 || common.steps > 150) {
		return 'Steps must be between 1 and 150.';
	}
	if (common.cfg < 1 || common.cfg > 30) {
		return 'CFG must be between 1 and 30.';
	}
	if (common.denoise < 0.05 || common.denoise > 1) {
		return 'Denoise must be between 0.05 and 1.0.';
	}
	return '';
}

function setEnhancedPromptBreakdownVisible(isVisible) {
	if (!enhancedPromptFields || !enhancedPromptToggle || !normalPromptWrap) return;
	normalPromptWrap.hidden = isVisible;
	enhancedPromptFields.hidden = !isVisible;
	enhancedPromptToggle.checked = isVisible;
	enhancedPromptToggle.setAttribute('aria-checked', isVisible ? 'true' : 'false');
	if (promptModeHint) {
		promptModeHint.textContent = isVisible
			? 'Enhanced prompt mode is active. Generate and apply a suggestion before submitting.'
			: 'Standard prompt mode is active.';
	}
	if (isVisible) {
		// Reset all tag clouds inside the breakdown to hidden so they start collapsed
		enhancedPromptFields.querySelectorAll('.enhanced-tag-cloud').forEach((cloud) => {
			cloud.hidden = true;
		});
		enhancedPromptFields.querySelectorAll('[data-suggest-toggle]').forEach((btn) => {
			btn.textContent = 'Show';
			btn.setAttribute('aria-expanded', 'false');
		});
	}
	localStorage.setItem('enhancedPromptBreakdownEnabled', isVisible ? '1' : '0');
}

function collectEnhancedPromptBreakdown() {
	return {
		subject: enhancedSubject?.value.trim() || '',
		setting: enhancedSetting?.value.trim() || '',
		composition: enhancedComposition?.value.trim() || '',
		lighting: enhancedLighting?.value.trim() || '',
		style: enhancedStyle?.value.trim() || '',
	};
}

function cloneDefaultSuggestionTags() {
	return JSON.parse(JSON.stringify(DEFAULT_SUGGESTION_TAGS));
}

function normalizeSuggestionTagStore(raw) {
	const next = cloneDefaultSuggestionTags();
	if (!raw || typeof raw !== 'object') return next;

	Object.keys(next).forEach((key) => {
		const incoming = raw[key];
		if (!Array.isArray(incoming)) return;
		const cleaned = [];
		const seen = new Set();
		incoming.forEach((tag) => {
			const value = String(tag || '').trim();
			if (!value) return;
			const k = value.toLowerCase();
			if (seen.has(k)) return;
			seen.add(k);
			cleaned.push(value);
		});
		if (cleaned.length) {
			next[key] = cleaned;
		}
	});
	return next;
}

function saveSuggestionTagStore() {
	localStorage.setItem(SUGGESTION_TAG_STORAGE_KEY, JSON.stringify(suggestionTagStore));
}

function loadSuggestionTagStore() {
	try {
		const raw = JSON.parse(localStorage.getItem(SUGGESTION_TAG_STORAGE_KEY) || '{}');
		suggestionTagStore = normalizeSuggestionTagStore(raw);
	} catch {
		suggestionTagStore = cloneDefaultSuggestionTags();
	}
}

function appendEnhancedTagToField(textareaEl, tag) {
	if (!textareaEl || !tag) return;
	const current = (textareaEl.value || '').trim();
	const lowerCurrent = current.toLowerCase();
	if (lowerCurrent.includes(tag.toLowerCase())) {
		textareaEl.focus();
		return;
	}
	textareaEl.value = current ? `${current}, ${tag}` : tag;
	textareaEl.focus();
	textareaEl.dispatchEvent(new Event('input', { bubbles: true }));
}

function renderEnhancedTagSuggestions() {
	const clouds = document.querySelectorAll('.enhanced-tag-cloud[data-target]');
	if (!clouds.length) return;

	clouds.forEach((cloud) => {
		const targetId = cloud.getAttribute('data-target') || '';
		const targetField = document.getElementById(targetId);
		const tags = suggestionTagStore[targetId] || [];
		cloud.innerHTML = '';
		if (!targetField || !tags.length) return;

		tags.forEach((tag) => {
			const btn = document.createElement('button');
			btn.type = 'button';
			btn.className = 'tag-suggestion-btn';
			btn.textContent = `+ ${tag}`;
			btn.setAttribute('aria-label', `Add tag ${tag}`);
			btn.addEventListener('click', () => appendEnhancedTagToField(targetField, tag));
			cloud.appendChild(btn);
		});
	});
}

function getCurrentTagCategory() {
	const category = tagCategorySelect?.value || '';
	if (!category || !Object.prototype.hasOwnProperty.call(TAG_CATEGORY_LABELS, category)) {
		return 'enhanced-subject';
	}
	return category;
}

function updateTagManagerStatus(text, level = '') {
	if (!tagManagerStatus) return;
	tagManagerStatus.textContent = text;
	tagManagerStatus.style.color = level === 'error'
		? 'var(--clr-accent-neg)'
		: (level === 'ok' ? 'var(--clr-accent-pos)' : 'var(--clr-text-muted)');
}

function renderTagCategoryOptions() {
	if (!tagCategorySelect) return;
	tagCategorySelect.innerHTML = Object.entries(TAG_CATEGORY_LABELS)
		.map(([value, label]) => `<option value="${escHtml(value)}">${escHtml(label)}</option>`)
		.join('');
}

function setTagAtIndex(category, index, value) {
	const tags = suggestionTagStore[category] || [];
	if (index < 0 || index >= tags.length) return false;
	const cleaned = String(value || '').trim();
	if (!cleaned) return false;

	const already = tags.findIndex((t) => t.toLowerCase() === cleaned.toLowerCase());
	if (already >= 0 && already !== index) return false;
	const next = [...tags];
	next[index] = cleaned;
	suggestionTagStore[category] = next;
	return true;
}

function deleteTagAtIndex(category, index) {
	const tags = suggestionTagStore[category] || [];
	if (index < 0 || index >= tags.length) return;
	suggestionTagStore[category] = tags.filter((_, i) => i !== index);
}

function addTagToCategory(category, value) {
	const cleaned = String(value || '').trim();
	if (!cleaned) return false;
	const tags = suggestionTagStore[category] || [];
	if (tags.some((tag) => tag.toLowerCase() === cleaned.toLowerCase())) {
		return false;
	}
	suggestionTagStore[category] = [...tags, cleaned];
	return true;
}

function renderTagEditorList() {
	if (!tagEditorList) return;
	const category = getCurrentTagCategory();
	const tags = suggestionTagStore[category] || [];
	if (!tags.length) {
		tagEditorList.innerHTML = '<p class="hint">No tags yet for this category.</p>';
		return;
	}

	tagEditorList.innerHTML = tags
		.map((tag, index) => {
			return `
				<div class="tag-editor-row" data-tag-row="${index}">
					<input type="text" value="${escHtml(tag)}" data-tag-input="${index}" aria-label="Tag ${index + 1}" />
					<button class="btn btn-ghost btn-xs" type="button" data-tag-save="${index}">Save</button>
					<button class="btn btn-ghost btn-xs" type="button" data-tag-delete="${index}">Delete</button>
				</div>
			`;
		})
		.join('');
}

function renderTagManagerUi() {
	renderTagEditorList();
	const category = getCurrentTagCategory();
	updateTagManagerStatus(`${TAG_CATEGORY_LABELS[category]} tags: ${(suggestionTagStore[category] || []).length}`);
}

function bindSuggestionTagCollapsers() {
	const toggles = document.querySelectorAll('[data-suggest-toggle]');
	toggles.forEach((btn) => {
		const targetId = btn.getAttribute('data-suggest-toggle');
		if (!targetId) return;
		const target = document.getElementById(targetId);
		if (!target) return;
		btn.addEventListener('click', () => {
			target.hidden = !target.hidden;
			btn.textContent = target.hidden ? 'Show' : 'Hide';
			btn.setAttribute('aria-expanded', target.hidden ? 'false' : 'true');
		});
		btn.setAttribute('aria-controls', targetId);
		btn.setAttribute('aria-expanded', target.hidden ? 'false' : 'true');
	});
}

// ─── Model Browser ────────────────────────────────────────────────────────────

let mbCurrentPage = 1;
let mbTotalPages  = 1;
let mbPollTimer   = null;

function formatBytes(bytes) {
	if (!bytes || bytes === 0) return '—';
	const units = ['B', 'KB', 'MB', 'GB'];
	let v = bytes;
	let i = 0;
	while (v >= 1024 && i < units.length - 1) { v /= 1024; i++; }
	return v.toFixed(i === 0 ? 0 : 1) + ' ' + units[i];
}

function mbOnTabActivate() {
	loadModelLibrary();
}

async function loadModelLibrary() {
	if (!mbLibraryGrid) return;
	if (mbLibraryStatus) { mbLibraryStatus.textContent = 'Scanning local models…'; mbLibraryStatus.hidden = false; }
	mbLibraryGrid.innerHTML = '';
	try {
		const resp = await fetch('/api/models/library');
		const data = await resp.json();
		if (!resp.ok) throw new Error(data.error || resp.statusText);
		renderLocalLibrary(data.models || [], data.models_root || '');
	} catch (err) {
		if (mbLibraryStatus) { mbLibraryStatus.textContent = 'Could not load local models: ' + err.message; mbLibraryStatus.hidden = false; }
	}
}

function renderLocalLibrary(models, root) {
	if (!mbLibraryGrid) return;
	mbLibraryGrid.innerHTML = '';
	if (models.length === 0) {
		if (mbLibraryStatus) {
			mbLibraryStatus.textContent = root ? 'No models found in ' + root : 'ComfyUI path not configured — set it on the Configurations tab.';
			mbLibraryStatus.hidden = false;
		}
		return;
	}
	if (mbLibraryStatus) mbLibraryStatus.hidden = true;
	models.forEach(m => {
		const card = document.createElement('div');
		card.className = 'mb-local-card';
		card.innerHTML = `
			<div class="mb-local-card-name" title="${escHtml(m.name)}">${escHtml(m.name)}</div>
			<div class="mb-local-card-meta">${escHtml(m.folder)} &middot; ${formatBytes(m.size_bytes)}</div>
			<div class="mb-local-card-actions">
				<button class="btn btn-sm btn-danger mb-delete-btn" data-name="${escHtml(m.name)}" data-folder="${escHtml(m.folder)}">Delete</button>
			</div>`;
		mbLibraryGrid.appendChild(card);
	});
	mbLibraryGrid.querySelectorAll('.mb-delete-btn').forEach(btn => {
		btn.addEventListener('click', () => deleteLocalModel(btn.dataset.name, btn.dataset.folder, btn));
	});
}

async function deleteLocalModel(fileName, folder, btn) {
	if (!confirm(`Delete "${fileName}" from ${folder}? This cannot be undone.`)) return;
	if (btn) btn.disabled = true;
	try {
		const resp = await fetch('/api/models/delete', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({file_name: fileName, folder})
		});
		const data = await resp.json();
		if (!resp.ok) throw new Error(data.error || resp.statusText);
		loadModelLibrary();
	} catch (err) {
		alert('Delete failed: ' + err.message);
		if (btn) btn.disabled = false;
	}
}

async function runCivitaiSearch(page) {
	if (!mbResultsGrid) return;
	const query = mbSearchQuery ? mbSearchQuery.value.trim() : '';
	const type  = mbSearchType  ? mbSearchType.value : '';
	mbCurrentPage = page || 1;
	if (mbSearchStatus) { mbSearchStatus.textContent = 'Searching…'; mbSearchStatus.hidden = false; }
	if (mbResultsCount) mbResultsCount.textContent = '';
	mbResultsGrid.innerHTML = '';
	if (mbResultsSection) mbResultsSection.hidden = false;
	try {
		const params = new URLSearchParams({page: mbCurrentPage});
		if (query) params.set('query', query);
		if (type)  params.set('type', type);
		const resp = await fetch('/api/models/civitai/search?' + params.toString());
		const data = await resp.json();
		if (!resp.ok) throw new Error(data.error || resp.statusText);
		mbTotalPages = data.total_pages || 1;
		renderSearchResults(data.items || [], data.total_items);
	} catch (err) {
		if (mbSearchStatus) { mbSearchStatus.textContent = 'Search failed: ' + err.message; mbSearchStatus.hidden = false; }
	}
}

function renderSearchResults(items, totalItems) {
	if (!mbResultsGrid) return;
	mbResultsGrid.innerHTML = '';
	if (mbSearchStatus) mbSearchStatus.hidden = true;
	if (mbResultsCount) mbResultsCount.textContent = totalItems != null ? `(${totalItems.toLocaleString()} total)` : '';
	if (items.length === 0) {
		mbResultsGrid.innerHTML = '<p class="mb-library-status">No results found.</p>';
		updatePagination();
		return;
	}
	items.forEach(item => {
		const card = document.createElement('div');
		card.className = 'mb-result-card';
		const thumb = item.preview_url
			? `<img class="mb-result-thumb" src="${escHtml(item.preview_url)}" alt="" loading="lazy">`
			: `<div class="mb-result-thumb-placeholder"></div>`;
		card.innerHTML = `
			${thumb}
			<div class="mb-result-body">
				<div class="mb-result-name" title="${escHtml(item.name)}">${escHtml(item.name)}</div>
				<div class="mb-result-meta">
					<span class="mb-type-chip">${escHtml(item.type || '')}</span>
					${item.rating != null ? `<span>&#9733; ${item.rating.toFixed(1)}</span>` : ''}
					${item.download_count != null ? `<span>${item.download_count.toLocaleString()} downloads</span>` : ''}
				</div>
				${item.version_name ? `<div class="mb-result-meta" style="font-size:0.78em;opacity:0.7">v: ${escHtml(item.version_name)}</div>` : ''}
				<div class="mb-result-actions">
					<button class="btn btn-sm btn-primary mb-dl-btn"
						data-url="${escHtml(item.download_url || '')}"
						data-name="${escHtml(item.file_name || item.name)}"
						data-folder="${escHtml(item.model_type_folder || 'checkpoints')}"
						${item.download_url ? '' : 'disabled title="No download URL available"'}>
						Download
					</button>
				</div>
			</div>`;
		mbResultsGrid.appendChild(card);
	});
	mbResultsGrid.querySelectorAll('.mb-dl-btn').forEach(btn => {
		btn.addEventListener('click', () => startModelDownload(btn.dataset.url, btn.dataset.name, btn.dataset.folder, btn));
	});
	updatePagination();
}

function updatePagination() {
	if (!mbPrevPage || !mbNextPage || !mbPageInfo) return;
	mbPrevPage.disabled = mbCurrentPage <= 1;
	mbNextPage.disabled = mbCurrentPage >= mbTotalPages;
	mbPageInfo.textContent = `Page ${mbCurrentPage} of ${mbTotalPages}`;
}

async function startModelDownload(url, fileName, folder, btn) {
	if (!url) return;
	if (btn) btn.disabled = true;
	try {
		const resp = await fetch('/api/models/download', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({url, file_name: fileName, folder})
		});
		const data = await resp.json();
		if (!resp.ok) throw new Error(data.error || resp.statusText);
		if (mbDownloadsSection) mbDownloadsSection.hidden = false;
		ensureDownloadPoll();
	} catch (err) {
		alert('Download failed to start: ' + err.message);
		if (btn) btn.disabled = false;
	}
}

async function refreshDownloadsList() {
	if (!mbDownloadsList) return;
	try {
		// Collect known download IDs from existing rows, then poll each
		const rows = mbDownloadsList.querySelectorAll('[data-dl-id]');
		const ids = Array.from(rows).map(r => r.dataset.dlId);
		if (ids.length === 0) { stopDownloadPoll(); return; }
		await Promise.all(ids.map(async id => {
			const r = await fetch('/api/models/download/' + encodeURIComponent(id));
			if (!r.ok) return;
			const state = await r.json();
			updateDownloadRow(id, state);
		}));
	} catch (_) { /* ignore poll errors */ }
}

function ensureDownloadPoll() {
	if (mbPollTimer) return;
	// Immediately render any pending rows by fetching full state
	fetchAndRenderAllDownloads();
	mbPollTimer = setInterval(fetchAndRenderAllDownloads, 1500);
}

function stopDownloadPoll() {
	if (mbPollTimer) { clearInterval(mbPollTimer); mbPollTimer = null; }
}

async function fetchAndRenderAllDownloads() {
	if (!mbDownloadsList) return;
	// We don't have a list endpoint, so just refresh existing rows
	const rows = mbDownloadsList.querySelectorAll('[data-dl-id]');
	if (rows.length === 0) { stopDownloadPoll(); return; }
	let anyActive = false;
	await Promise.all(Array.from(rows).map(async row => {
		const id = row.dataset.dlId;
		try {
			const r = await fetch('/api/models/download/' + encodeURIComponent(id));
			if (!r.ok) return;
			const state = await r.json();
			updateDownloadRow(id, state);
			if (state.status === 'downloading') anyActive = true;
		} catch (_) {}
	}));
	if (!anyActive) stopDownloadPoll();
}

function addDownloadRow(downloadId, fileName) {
	if (!mbDownloadsList) return;
	const row = document.createElement('div');
	row.className = 'mb-download-row';
	row.dataset.dlId = downloadId;
	row.innerHTML = `
		<div class="mb-download-row-head">
			<span class="mb-download-name">${escHtml(fileName)}</span>
			<span class="mb-download-status">queued</span>
			<button class="btn btn-sm mb-cancel-dl-btn" data-id="${escHtml(downloadId)}">Cancel</button>
		</div>
		<div class="mb-progress"><div class="mb-progress-bar" style="width:0%"></div></div>`;
	mbDownloadsList.appendChild(row);
	row.querySelector('.mb-cancel-dl-btn').addEventListener('click', () => cancelDownload(downloadId, row));
	ensureDownloadPoll();
}

function updateDownloadRow(downloadId, state) {
	if (!mbDownloadsList) return;
	let row = mbDownloadsList.querySelector(`[data-dl-id="${CSS.escape(downloadId)}"]`);
	if (!row) {
		// Create row if missing (e.g. on page reload)
		const newRow = document.createElement('div');
		newRow.className = 'mb-download-row';
		newRow.dataset.dlId = downloadId;
		newRow.innerHTML = `
			<div class="mb-download-row-head">
				<span class="mb-download-name">${escHtml(state.file_name || downloadId)}</span>
				<span class="mb-download-status"></span>
				<button class="btn btn-sm mb-cancel-dl-btn" data-id="${escHtml(downloadId)}">Cancel</button>
			</div>
			<div class="mb-progress"><div class="mb-progress-bar" style="width:0%"></div></div>`;
		mbDownloadsList.appendChild(newRow);
		newRow.querySelector('.mb-cancel-dl-btn').addEventListener('click', () => cancelDownload(downloadId, newRow));
		row = newRow;
	}
	const statusEl = row.querySelector('.mb-download-status');
	const bar      = row.querySelector('.mb-progress-bar');
	const cancelBtn = row.querySelector('.mb-cancel-dl-btn');
	if (statusEl) statusEl.textContent = state.status === 'downloading'
		? `${state.downloaded_bytes != null ? formatBytes(state.downloaded_bytes) : ''}${state.total_bytes ? ' / ' + formatBytes(state.total_bytes) : ''}`
		: state.status;
	const pct = state.total_bytes && state.total_bytes > 0 ? (state.downloaded_bytes / state.total_bytes) * 100 : 0;
	if (bar) bar.style.width = pct.toFixed(1) + '%';
	row.classList.toggle('is-done',      state.status === 'done');
	row.classList.toggle('is-error',     state.status === 'error');
	row.classList.toggle('is-cancelled', state.status === 'cancelled');
	if (cancelBtn) cancelBtn.hidden = (state.status !== 'downloading');
	if (state.status === 'done') loadModelLibrary();
}

async function cancelDownload(downloadId, row) {
	try {
		await fetch('/api/models/download/' + encodeURIComponent(downloadId) + '/cancel', {method: 'POST'});
		if (row) row.classList.add('is-cancelled');
	} catch (_) {}
}

// Wire model browser events
if (mbSearchBtn) {
	mbSearchBtn.addEventListener('click', () => runCivitaiSearch(1));
}
if (mbSearchQuery) {
	mbSearchQuery.addEventListener('keydown', (e) => { if (e.key === 'Enter') runCivitaiSearch(1); });
}
if (mbLibraryRefreshBtn) {
	mbLibraryRefreshBtn.addEventListener('click', loadModelLibrary);
}
if (mbPrevPage) {
	mbPrevPage.addEventListener('click', () => { if (mbCurrentPage > 1) runCivitaiSearch(mbCurrentPage - 1); });
}
if (mbNextPage) {
	mbNextPage.addEventListener('click', () => { if (mbCurrentPage < mbTotalPages) runCivitaiSearch(mbCurrentPage + 1); });
}

function buildRandomPromptFromTags() {
	const pick = (key, fallback) => {
		const pool = suggestionTagStore[key] || [];
		if (!pool.length) return fallback;
		return pool[Math.floor(Math.random() * pool.length)];
	};

	const subject = pick('enhanced-subject', 'mysterious traveler');
	const setting = pick('enhanced-setting', 'misty forest');
	const composition = pick('enhanced-composition', 'cinematic framing');
	const lighting = pick('enhanced-lighting', 'soft diffused light');
	const style = pick('enhanced-style', 'concept art');
	const quality = ['high detail', 'ultra detailed', '8k texture', 'sharp focus', 'epic atmosphere'];
	const qualityTag = quality[Math.floor(Math.random() * quality.length)];

	return `${subject}, ${setting}, ${composition}, ${lighting}, ${style}, ${qualityTag}`;
}

function renderEnhancedPromptSuggestions(suggestions) {
	enhancedPromptSuggestions = Array.isArray(suggestions) ? suggestions.filter(Boolean) : [];
	if (!enhancedPromptSuggestionsOutput || !enhancedPromptUseBtn || !enhancedPromptSelect) return;
	if (!enhancedPromptSuggestions.length) {
		enhancedPromptSuggestionsOutput.value = '';
		enhancedPromptSelect.innerHTML = '<option value="">No suggestions yet</option>';
		enhancedPromptSelect.disabled = true;
		if (enhancedPromptUseSelectedBtn) enhancedPromptUseSelectedBtn.disabled = true;
		if (enhancedPromptRandomBtn) enhancedPromptRandomBtn.disabled = true;
		enhancedPromptUseBtn.disabled = true;
		return;
	}
	enhancedPromptSuggestionsOutput.value = enhancedPromptSuggestions
		.map((line, index) => `${index + 1}. ${line}`)
		.join('\n');
	enhancedPromptSelect.innerHTML = enhancedPromptSuggestions
		.map((line, index) => {
			const preview = String(line).replace(/\s+/g, ' ').trim();
			const clipped = preview.length > 72 ? `${preview.slice(0, 72)}...` : preview;
			return `<option value="${index}">${escHtml(`Suggestion ${index + 1}: ${clipped}`)}</option>`;
		})
		.join('');
	enhancedPromptSelect.disabled = false;
	if (enhancedPromptUseSelectedBtn) enhancedPromptUseSelectedBtn.disabled = false;
	if (enhancedPromptRandomBtn) enhancedPromptRandomBtn.disabled = false;
	enhancedPromptUseBtn.disabled = false;
}

function resolvePromptForSubmission() {
	let promptText = imagePrompt.value.trim();
	if (promptText) return promptText;

	if (!enhancedPromptToggle?.checked || !enhancedPromptSuggestions.length) {
		return '';
	}

	let fallback = enhancedPromptSuggestions[0];
	if (enhancedPromptSelect) {
		const idx = Number(enhancedPromptSelect.value);
		if (Number.isInteger(idx) && idx >= 0 && idx < enhancedPromptSuggestions.length) {
			fallback = enhancedPromptSuggestions[idx];
		}
	}

	if (!fallback) return '';
	applyEnhancedSuggestion(fallback);
	showToast('Applied enhanced suggestion for submission.', 'pos');
	return String(fallback).trim();
}

function applyEnhancedSuggestion(text) {
	if (!text) return;
	imagePrompt.value = text;
	imagePrompt.focus();
}

async function suggestEnhancedPrompts() {
	if (!enhancedPromptSuggestBtn || !enhancedPromptStatus) return;
	const payload = collectEnhancedPromptBreakdown();
	const missing = Object.entries(payload)
		.filter(([, value]) => !value)
		.map(([key]) => key);

	if (missing.length) {
		enhancedPromptStatus.textContent = `Please fill all breakdown fields: ${missing.join(', ')}.`;
		renderEnhancedPromptSuggestions([]);
		showToast('Fill all enhanced prompt fields first.', 'neg');
		return;
	}

	enhancedPromptSuggestBtn.disabled = true;
	if (enhancedPromptUseBtn) enhancedPromptUseBtn.disabled = true;
	if (enhancedPromptUseSelectedBtn) enhancedPromptUseSelectedBtn.disabled = true;
	if (enhancedPromptRandomBtn) enhancedPromptRandomBtn.disabled = true;
	enhancedPromptStatus.textContent = 'Generating suggestions from local Ollama...';

	try {
		const res = await fetch('/api/image/prompt-suggestions', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				...payload,
				model: modelSelect?.value || '',
			}),
		});
		const data = await res.json().catch(() => ({}));
		if (!res.ok) {
			enhancedPromptStatus.textContent = `Suggestion failed: ${data.error || 'Unknown error'}`;
			renderEnhancedPromptSuggestions([]);
			showToast('Enhanced prompt suggestion failed.', 'neg');
			return;
		}

		renderEnhancedPromptSuggestions(data.suggestions || []);
		enhancedPromptStatus.textContent = `Generated ${enhancedPromptSuggestions.length} suggestion${enhancedPromptSuggestions.length === 1 ? '' : 's'} using ${data.model || 'Ollama'}.`;
		showToast('Enhanced prompt suggestions ready.', 'pos');
	} catch (err) {
		enhancedPromptStatus.textContent = `Suggestion failed: ${err.message}`;
		renderEnhancedPromptSuggestions([]);
		showToast('Enhanced prompt suggestion failed.', 'neg');
	} finally {
		enhancedPromptSuggestBtn.disabled = false;
	}
}

if (enhancedPromptToggle) {
	enhancedPromptToggle.addEventListener('change', () => {
		setEnhancedPromptBreakdownVisible(enhancedPromptToggle.checked);
	});
	const saved = localStorage.getItem('enhancedPromptBreakdownEnabled') === '1';
	setEnhancedPromptBreakdownVisible(saved);
}

loadSuggestionTagStore();
renderEnhancedTagSuggestions();
if (tagCategorySelect) {
	renderTagManagerUi();
}
bindSuggestionTagCollapsers();

if (promptRandomizeBtn) {
	promptRandomizeBtn.addEventListener('click', () => {
		imagePrompt.value = buildRandomPromptFromTags();
		imagePrompt.focus();
		showToast('Random prompt added.', 'pos');
	});
}

if (enhancedPromptSuggestBtn) {
	enhancedPromptSuggestBtn.addEventListener('click', suggestEnhancedPrompts);
}

if (enhancedPromptBuildBtn) {
	enhancedPromptBuildBtn.addEventListener('click', () => {
		const parts = [
			enhancedSubject?.value.trim(),
			enhancedSetting?.value.trim(),
			enhancedComposition?.value.trim(),
			enhancedLighting?.value.trim(),
			enhancedStyle?.value.trim(),
		].filter(Boolean);
		if (!parts.length) {
			showToast('Fill in at least one breakdown field first.', 'neg');
			return;
		}
		applyEnhancedSuggestion(parts.join(', '));
		showToast('Prompt built from breakdown fields.', 'pos');
	});
}

if (enhancedPromptUseBtn) {
	enhancedPromptUseBtn.addEventListener('click', () => {
		if (!enhancedPromptSuggestions.length) {
			showToast('No suggestion available yet.', 'neg');
			return;
		}
		applyEnhancedSuggestion(enhancedPromptSuggestions[0]);
		showToast('Applied first suggestion to Image Inference Text.', 'pos');
	});
}

if (enhancedPromptRandomBtn) {
	enhancedPromptRandomBtn.addEventListener('click', () => {
		if (!enhancedPromptSuggestions.length) {
			showToast('No suggestion available yet.', 'neg');
			return;
		}
		const index = Math.floor(Math.random() * enhancedPromptSuggestions.length);
		applyEnhancedSuggestion(enhancedPromptSuggestions[index]);
		if (enhancedPromptSelect) enhancedPromptSelect.value = String(index);
		showToast(`Applied random suggestion ${index + 1}.`, 'pos');
	});
}

if (enhancedPromptUseSelectedBtn) {
	enhancedPromptUseSelectedBtn.addEventListener('click', () => {
		if (!enhancedPromptSuggestions.length || !enhancedPromptSelect) {
			showToast('No suggestion available yet.', 'neg');
			return;
		}
		const idx = Number(enhancedPromptSelect.value);
		if (!Number.isInteger(idx) || idx < 0 || idx >= enhancedPromptSuggestions.length) {
			showToast('Choose a suggestion first.', 'neg');
			return;
		}
		applyEnhancedSuggestion(enhancedPromptSuggestions[idx]);
		showToast(`Applied selected suggestion ${idx + 1}.`, 'pos');
	});
}

imageForm.addEventListener('submit', async (e) => {
	e.preventDefault();

	const prompt = resolvePromptForSubmission();
	if (!prompt) {
		queueSummary.textContent = 'Enter a prompt or apply an enhanced suggestion first.';
		if (enhancedPromptToggle?.checked) {
			enhancedPromptSuggestBtn?.focus();
		} else {
			imagePrompt.focus();
		}
		return;
	}

	imageGenerateBtn.disabled = true;
	imageGenerateBtn.textContent = 'Submitting...';

	try {
		const common = {
			prompt,
			negative_prompt: imageNegativePrompt.value.trim(),
			model: imageModelSelect.value,
			sampler: imageSamplerSelect.value,
			seed: imageSeed.value.trim() || null,
			steps: Number(imageSteps.value),
			cfg: Number(imageCfg.value),
			width: Number(imageWidth.value),
			height: Number(imageHeight.value),
			batch_size: Number(imageBatchSize.value),
			denoise: Number(imageDenoise.value),
		};

		const validationError = validateImageInputs(common);
		if (validationError) {
			queueSummary.textContent = `Error: ${validationError}`;
			imageGenerateBtn.disabled = false;
			imageGenerateBtn.textContent = 'Generate Image';
			return;
		}

		let res;
		if (imageUpload.files && imageUpload.files[0]) {
			const formData = new FormData();
			formData.append('image', imageUpload.files[0]);
			formData.append('prompt', common.prompt);
			formData.append('negative_prompt', common.negative_prompt);
			formData.append('model', common.model);
			formData.append('sampler', common.sampler);
			formData.append('seed', common.seed || '');
			formData.append('steps', String(common.steps));
			formData.append('cfg', String(common.cfg));
			formData.append('denoise', String(common.denoise));
			res = await fetch('/api/image/img2img', {
				method: 'POST',
				body: formData,
			});
		} else {
			res = await fetch('/api/image/generate', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(common),
			});
		}

		const data = await res.json();
		if (!res.ok) {
			queueSummary.textContent = `Error: ${data.error || 'Image request failed'}`;
			imageGenerateBtn.disabled = false;
			imageGenerateBtn.textContent = 'Generate Image';
			return;
		}

		const promptId = data.prompt_id;
		imageState.currentPromptId = promptId;
		trackedPromptIds.add(promptId);
		incrementQueueTelemetry('submitted');
		const snapshot = {
			prompt: common.prompt,
			negative_prompt: common.negative_prompt,
			model: common.model,
			sampler: common.sampler,
			seed: common.seed,
			steps: common.steps,
			cfg: common.cfg,
			denoise: common.denoise,
			width: common.width,
			height: common.height,
			batch_size: common.batch_size,
			mode: imageUpload.files && imageUpload.files[0] ? 'img2img' : 'txt2img',
			...(data.meta || {}),
		};
		pendingImageJobs.set(promptId, snapshot);
		queueJobMeta.set(promptId, {
			status: 'queued',
			missCount: 0,
			updatedAt: Date.now(),
			snapshot,
		});
		ensureQueuePolling();

		queueSummary.textContent = `Submitted: ${promptId}`;
		imageGenerateBtn.textContent = 'Queued';
		await pollQueue();
	} catch (err) {
		queueSummary.textContent = `Error: ${err.message}`;
		imageGenerateBtn.disabled = false;
		imageGenerateBtn.textContent = 'Generate Image';
	}
});

loadGallery();
loadLivePreview();
loadServiceConfig();
startPollingLeaseHeartbeat();
syncBackgroundPollingOwnership();

document.addEventListener('visibilitychange', () => {
	if (document.hidden) {
		releaseBackgroundPollingOwnership();
	}
	syncBackgroundPollingOwnership();
});

window.addEventListener('focus', () => {
	syncBackgroundPollingOwnership();
});

window.addEventListener('blur', () => {
	syncBackgroundPollingOwnership();
});

window.addEventListener('storage', (event) => {
	if (event.key !== BACKGROUND_POLL_OWNER_KEY) return;
	syncBackgroundPollingOwnership();
});

window.addEventListener('beforeunload', () => {
	releaseBackgroundPollingOwnership();
});
