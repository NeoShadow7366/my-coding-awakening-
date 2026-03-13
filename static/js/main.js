'use strict';

/* --------------------------------------------------------------------------
	 DOM references
	 -------------------------------------------------------------------------- */
const themeToggle = document.getElementById('theme-toggle');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const navGenerative = document.getElementById('nav-generative');
const navImage = document.getElementById('nav-image');
const panelGen = document.getElementById('panel-generative');
const panelImage = document.getElementById('panel-image');

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
const imageSteps = document.getElementById('image-steps');
const imageStepsVal = document.getElementById('image-steps-val');
const imageCfg = document.getElementById('image-cfg');
const imageCfgVal = document.getElementById('image-cfg-val');
const imageDenoise = document.getElementById('image-denoise');
const imageDenoiseVal = document.getElementById('image-denoise-val');
const imageEngineStatus = document.getElementById('image-engine-status');
const imageForm = document.getElementById('image-form');
const imagePrompt = document.getElementById('image-prompt');
const imageNegativePrompt = document.getElementById('image-negative-prompt');
const imageWidth = document.getElementById('image-width');
const imageHeight = document.getElementById('image-height');
const imageBatchSize = document.getElementById('image-batch-size');
const imageUpload = document.getElementById('image-upload');
const imageGenerateBtn = document.getElementById('image-generate-btn');
const queueSummary = document.getElementById('queue-summary');
const queueList = document.getElementById('queue-list');
const autoRetryPolicy = document.getElementById('auto-retry-policy');
const failedOnlyToggle = document.getElementById('failed-only-toggle');
const refreshGalleryBtn = document.getElementById('refresh-gallery');
const galleryGrid = document.getElementById('gallery-grid');
const imagePresetButtons = document.querySelectorAll('[data-image-preset]');
const previewUpdated = document.getElementById('preview-updated');
const previewEmpty = document.getElementById('preview-empty');
const previewImage = document.getElementById('preview-image');
const previewMeta = document.getElementById('preview-meta');
const previewPrompt = document.getElementById('preview-prompt');
const previewChipRow = document.getElementById('preview-chip-row');

/* --------------------------------------------------------------------------
	 State
	 -------------------------------------------------------------------------- */
let isGenerating = false;
let queuePollTimer = null;
let livePreviewTimer = null;
const trackedPromptIds = new Set();
const pendingImageJobs = new Map();
const queueJobMeta = new Map();
const JOB_MISS_THRESHOLD = 4;
const queueActionInFlight = new Set();
let queueFilterFailedOnly = localStorage.getItem('queueFilterFailedOnly') === '1';

if (failedOnlyToggle) {
	failedOnlyToggle.checked = queueFilterFailedOnly;
	failedOnlyToggle.addEventListener('change', () => {
		queueFilterFailedOnly = failedOnlyToggle.checked;
		localStorage.setItem('queueFilterFailedOnly', queueFilterFailedOnly ? '1' : '0');
		renderQueueStatus([], [], new Set());
	});
}

const imageState = {
	currentPromptId: '',
};

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
	if (panel === 'generative') {
		panelGen.classList.add('active');
		panelImage.classList.remove('active');
		panelGen.hidden = false;
		panelImage.hidden = true;
		navGenerative.classList.add('active');
		navImage.classList.remove('active');
		navGenerative.setAttribute('aria-selected', 'true');
		navImage.setAttribute('aria-selected', 'false');
	} else {
		panelImage.classList.add('active');
		panelGen.classList.remove('active');
		panelImage.hidden = false;
		panelGen.hidden = true;
		navImage.classList.add('active');
		navGenerative.classList.remove('active');
		navImage.setAttribute('aria-selected', 'true');
		navGenerative.setAttribute('aria-selected', 'false');
	}
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

(function initPanel() {
	const saved = localStorage.getItem('activePanel');
	showPanel(saved === 'image' ? 'image' : 'generative');
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

function randomSeed() {
	return Math.floor(Math.random() * 2_147_483_647) + 1;
}

function setModelSelectMessage(msg) {
	modelSelect.innerHTML = `<option value="">${escHtml(msg)}</option>`;
}

function setImageModelMessage(msg) {
	imageModelSelect.innerHTML = `<option value="">${escHtml(msg)}</option>`;
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
		const current = imageModelSelect.value;
		imageModelSelect.innerHTML = models
			.map((name) => `<option value="${escHtml(name)}">${escHtml(name)}</option>`)
			.join('');
		if (current && [...imageModelSelect.options].some((o) => o.value === current)) {
			imageModelSelect.value = current;
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
		} else {
			imageEngineStatus.textContent = 'ComfyUI offline - start server at localhost:8188';
			imageEngineStatus.style.color = 'var(--clr-accent-neg)';
			setImageModelMessage('ComfyUI unavailable');
		}
	} catch {
		statusDot.className = 'status-dot offline';
		statusText.textContent = 'Offline';
		imageEngineStatus.textContent = 'Could not reach backend status endpoint';
	}
}

checkStatus();
setInterval(checkStatus, 6000);

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

function renderQueueStatus(running, pending, donePromptIds = new Set()) {
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
	const visibleLabel = queueFilterFailedOnly ? 'Showing: Failed only' : 'Showing: All';
	queueSummary.textContent = `Running: ${runningIds.size}  Pending: ${pendingIds.size}  Tracked: ${trackedPromptIds.size}  Failed: ${failedCount}  ${visibleLabel}`;

	const rows = Array.from(queueJobMeta.entries())
		.filter(([, meta]) => (queueFilterFailedOnly ? meta.status === 'failed' : true))
		.sort((a, b) => (b[1].updatedAt || 0) - (a[1].updatedAt || 0))
		.map(([promptId, meta]) => {
			const status = meta.status || 'queued';
			const badge =
				status === 'running' ? '<span class="history-badge positive">RUN</span>' :
				status === 'queued' ? '<span class="history-badge">WAIT</span>' :
				status === 'completed' ? '<span class="history-badge positive">DONE</span>' :
				status === 'canceled' ? '<span class="history-badge negative">CANCEL</span>' :
				status === 'failed' ? '<span class="history-badge negative">FAIL</span>' :
				'<span class="history-badge">WORK</span>';

			const canCancel = status === 'queued' || status === 'running' || status === 'processing';
			const canRetry = status === 'failed' || status === 'canceled';
			const cancelBusy = queueActionInFlight.has(`cancel:${promptId}`);
			const retryBusy = queueActionInFlight.has(`retry:${promptId}`);
			const reason = meta.failReason ? `<span class="queue-reason">${escHtml(meta.failReason)}</span>` : '';
			const actions = [
				canCancel ? `<button class="btn btn-ghost btn-xs queue-action" data-action="cancel" data-prompt-id="${escHtml(promptId)}" ${cancelBusy ? 'disabled' : ''}>${cancelBusy ? 'Canceling...' : 'Cancel'}</button>` : '',
				canRetry ? `<button class="btn btn-ghost btn-xs queue-action" data-action="retry" data-prompt-id="${escHtml(promptId)}" ${retryBusy ? 'disabled' : ''}>${retryBusy ? 'Retrying...' : 'Retry'}</button>` : '',
			].join('');

			return `
				<li class="history-item">
					${badge}
					<span class="history-text" title="${escHtml(promptId)}">${escHtml(promptId)}${reason}</span>
					<span class="queue-actions">${actions}</span>
				</li>
			`;
		});

	queueList.innerHTML = rows.length ? rows.join('') : '<li class="history-item"><span class="history-text">No queue items match this filter.</span></li>';
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
			queueSummary.textContent = `Cancel failed: ${data.error || 'Unknown error'}`;
			return;
		}
		trackedPromptIds.delete(promptId);
		pendingImageJobs.delete(promptId);
		const meta = queueJobMeta.get(promptId) || {};
		meta.status = 'canceled';
		meta.failReason = 'Canceled by user.';
		meta.updatedAt = Date.now();
		queueJobMeta.set(promptId, meta);
		await pollQueue();
	} catch (err) {
		queueSummary.textContent = `Cancel failed: ${err.message}`;
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
		queueSummary.textContent = 'Retry unavailable: no job snapshot found.';
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
				queueSummary.textContent = 'Retry for img2img currently requires re-uploading source image.';
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
			queueSummary.textContent = `Retry failed: ${data.error || 'Unknown error'}`;
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
		ensureQueuePolling();
		queueSummary.textContent = `Retry submitted: ${newPromptId}`;
		await pollQueue();
	} catch (err) {
		queueSummary.textContent = `Retry failed: ${err.message}`;
		const meta = queueJobMeta.get(promptId) || {};
		meta.status = 'failed';
		meta.retryCount = (meta.retryCount || 0) + 1;
		meta.failReason = `Retry failed: ${err.message}`;
		queueJobMeta.set(promptId, meta);
	} finally {
		queueActionInFlight.delete(`retry:${promptId}`);
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
	}
});

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

function renderGallery(history) {
	const images = history.filter((item) => item.type === 'image');
	if (!images.length) {
		galleryGrid.innerHTML = '<div class="empty-gallery">No image generations yet.</div>';
		return;
	}

	galleryGrid.innerHTML = images
		.map((entry) => {
			const firstImage = entry.images?.[0];
			if (!firstImage) return '';
			const imgUrl = imageProxyUrl(firstImage);
			const prompt = escHtml(entry.prompt || 'Untitled generation');
			const model = escHtml(entry.model || 'unknown model');
			const sampler = escHtml(entry.params?.sampler || 'sampler');
			const steps = escHtml(String(entry.params?.steps || '')); 
			const cfg = escHtml(String(entry.params?.cfg || ''));
			return `
				<article class="gallery-card">
					<img src="${imgUrl}" alt="Generated image" loading="lazy" />
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
		return;
	}

	const firstImage = entry.images[0];
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
	try {
		const res = await fetch('/api/history?type=image&limit=1');
		const data = await res.json();
		const latest = (data.history || [])[0];
		updateLivePreview(latest);
	} catch {
		previewUpdated.textContent = 'Preview unavailable';
	}
}

function startLivePreviewAutoRefresh() {
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

imageForm.addEventListener('submit', async (e) => {
	e.preventDefault();

	const prompt = imagePrompt.value.trim();
	if (!prompt) return;

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
startLivePreviewAutoRefresh();
