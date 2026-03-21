"""UI accessibility regression tests for top-level tab semantics."""

from pathlib import Path

import app as app_module


def test_index_includes_tablist_and_tab_defaults():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert '<nav class="tab-nav" role="tablist" aria-label="Model type">' in html

    assert 'id="nav-generative"' in html
    assert 'role="tab" aria-controls="panel-generative" aria-selected="true" tabindex="0"' in html

    assert 'id="nav-image"' in html
    assert 'role="tab" aria-controls="panel-image" aria-selected="false" tabindex="-1"' in html

    assert 'id="nav-config"' in html
    assert 'role="tab" aria-controls="panel-config" aria-selected="false" tabindex="-1"' in html

    assert 'id="nav-models"' in html
    assert 'role="tab" aria-controls="panel-models" aria-selected="false" tabindex="-1"' in html
    assert '/static/css/style.css?v=' in html
    assert '/static/js/main.js?v=' in html


def test_index_panels_have_tabpanel_wiring():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert 'id="panel-generative" class="panel active" role="tabpanel" aria-labelledby="nav-generative"' in html
    assert 'id="panel-image" class="panel" role="tabpanel" aria-labelledby="nav-image" hidden' in html
    assert 'id="panel-config" class="panel" role="tabpanel" aria-labelledby="nav-config" hidden' in html
    assert 'id="panel-models" class="panel" role="tabpanel" aria-labelledby="nav-models" hidden' in html


def test_index_image_preset_buttons_expose_toggle_semantics():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert '<div class="preset-row" role="group" aria-label="Image presets">' in html
    assert 'data-image-preset="fast" aria-pressed="false"' in html
    assert 'data-image-preset="quality" aria-pressed="false"' in html
    assert 'data-image-preset="creative" aria-pressed="false"' in html
    assert 'id="image-preset-family-badge" class="hint preset-family-badge" aria-live="polite"' in html


def test_index_model_browser_quick_filters_group_semantics():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert '<div class="sidebar-section mb-filter-icons" role="group" aria-label="Model browser quick filters">' in html
    assert 'id="mb-page-size"' in html
    assert 'id="mb-hide-installed"' in html
    assert 'id="mb-show-installed-only"' in html
    assert 'id="mb-hide-early-access"' in html
    assert 'id="mb-show-nsfw"' in html


def test_queue_action_keyboard_handler_wiring_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "function onQueueActionKeydown(event)" in content
    assert "const runningPositions = new Map();" in content
    assert "const pendingPositions = new Map();" in content
    assert "<span class=\"chip\" title=\"Running position in ComfyUI\" aria-label=\"Running position ${runningPosition}\">run #${runningPosition}</span>" in content
    assert "<span class=\"chip\" title=\"Pending queue position in ComfyUI\" aria-label=\"Pending queue position ${pendingPosition}\">queue #${pendingPosition}</span>" in content
    assert "<span class=\"chip queue-chip-front\">front</span>" in content
    assert "async function prioritizeImageJob(promptId)" in content
    assert "data-action=\"prioritize\"" in content
    assert "aria-keyshortcuts=\"Alt+ArrowUp\"" in content
    assert "if (event.altKey && event.key === 'ArrowUp') {" in content
    assert "const prioritizeBtn = row ? row.querySelector('.queue-action[data-action=\"prioritize\"]') : null;" in content
    assert "prioritizeImageJob(promptId);" in content
    assert "body: JSON.stringify(resubmitBody)," in content
    assert "const resubmitUrl = isImg2Img ? '/api/image/img2img-requeue' : '/api/image/generate';" in content
    assert "const QUEUE_STATE_STORAGE_KEY = 'queueStateV1';" in content
    assert "const QUEUE_HELP_EXPANDED_KEY = 'queueHelpExpandedV1';" in content
    assert "const QUEUE_RESTORE_HINT_HIDDEN_KEY = 'queueRestoreHintHiddenV1';" in content
    assert "const QUEUE_LAST_ACTION_PINNED_KEY = 'queueLastActionPinnedV1';" in content
    assert "const QUEUE_LAST_ACTION_MAX_AGE_MS = 120000;" in content
    assert "function persistTrackedQueueState()" in content
    assert "function restoreTrackedQueueState()" in content
    assert "function renderQueueRestoreHint()" in content
    assert "function stopQueueRestoreHintTicker()" in content
    assert "function ensureQueueRestoreHintTicker()" in content
    assert "queueRestoreHintTimer = window.setInterval(() => {" in content
    assert "let queueLastActionInfo = null;" in content
    assert "let queueLastActionTimer = null;" in content
    assert "let queueLastActionPinned = localStorage.getItem(QUEUE_LAST_ACTION_PINNED_KEY) === '1';" in content
    assert "function stopQueueLastActionTicker()" in content
    assert "function ensureQueueLastActionTicker()" in content
    assert "function syncQueueLastActionPinButton()" in content
    assert "queueLastActionPinBtn.setAttribute('aria-label', queueLastActionPinned ? 'Unpin queue last action status' : 'Pin queue last action status');" in content
    assert "queueLastActionPinBtn.title = queueLastActionPinned ? 'Unpin to allow auto-clear after inactivity' : 'Pin this status so it does not auto-clear';" in content
    assert "function renderQueueLastAction()" in content
    assert "queueLastActionTimer = window.setInterval(() => {" in content
    assert "if (!queueLastActionPinned && ageMs > QUEUE_LAST_ACTION_MAX_AGE_MS) {" in content
    assert "queueLastActionInfo = null;" in content
    assert "queueLastAction.textContent = `Last action: ${queueLastActionInfo.message} (${ageText})`;" in content
    assert "const queueHelpDetails = document.getElementById('queue-help-details');" in content
    assert "const queueRestoreWrap = document.getElementById('queue-restore-wrap');" in content
    assert "const queueRestoreHint = document.getElementById('queue-restore-hint');" in content
    assert "const queueRestoreHideBtn = document.getElementById('queue-restore-hide');" in content
    assert "const queueRestoreShowBtn = document.getElementById('queue-restore-show');" in content
    assert "const queueLastAction = document.getElementById('queue-last-action');" in content
    assert "const queueLastActionPinBtn = document.getElementById('queue-last-action-pin');" in content
    assert "const queueUiResetBtn = document.getElementById('queue-ui-reset');" in content
    assert "function setQueueLastAction(message)" in content
    assert "if (queueRestoreHideBtn) {" in content
    assert "queueRestoreHintHidden = true;" in content
    assert "localStorage.setItem(QUEUE_RESTORE_HINT_HIDDEN_KEY, '1');" in content
    assert "setQueueLastAction('Restore hint hidden.');" in content
    assert "if (queueRestoreShowBtn) {" in content
    assert "queueRestoreHintHidden = false;" in content
    assert "localStorage.removeItem(QUEUE_RESTORE_HINT_HIDDEN_KEY);" in content
    assert "setQueueLastAction('Restore hint shown.');" in content
    assert "if (queueLastActionPinBtn) {" in content
    assert "queueLastActionPinned = !queueLastActionPinned;" in content
    assert "localStorage.setItem(QUEUE_LAST_ACTION_PINNED_KEY, '1');" in content
    assert "localStorage.removeItem(QUEUE_LAST_ACTION_PINNED_KEY);" in content
    assert "if (queueUiResetBtn) {" in content
    assert "queueFilterFailedOnly = false;" in content
    assert "localStorage.removeItem('queueFilterFailedOnly');" in content
    assert "setQueueLastAction('Queue UI preferences reset.');" in content
    assert "showToast('Queue UI preferences reset.', 'pos');" in content
    assert "if (queueHelpDetails) {" in content
    assert "queueHelpDetails.addEventListener('toggle', () => {" in content
    assert "localStorage.setItem(QUEUE_HELP_EXPANDED_KEY, queueHelpDetails.open ? '1' : '0');" in content
    assert "setQueueLastAction(queueHelpDetails.open ? 'Queue help opened.' : 'Queue help closed.');" in content
    assert "renderQueueRestoreHint();" in content
    assert "renderQueueLastAction();" in content
    assert "Restored ${count} active queue item" in content
    assert "restoreTrackedQueueState();" in content
    assert "localStorage.setItem(QUEUE_STATE_STORAGE_KEY" in content
    assert "setQueueLastAction(`Restored ${restoredCount} tracked queue item${restoredCount === 1 ? '' : 's'}.`);" in content
    assert "setQueueLastAction('Moved a job to the front of the queue.');" in content
    assert "if (action === 'prioritize') {" in content
    assert "queueList.addEventListener('keydown', onQueueActionKeydown);" in content

    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert 'id="queue-shortcuts-hint"' in html
    assert 'id="queue-help-details"' in html
    assert 'id="queue-help-toggle"' in html
    assert 'id="queue-help-copy"' in html
    assert 'id="queue-restore-wrap"' in html
    assert 'id="queue-restore-hint"' in html
    assert 'id="queue-restore-hide"' in html
    assert 'id="queue-restore-show"' in html
    assert 'id="queue-last-action"' in html
    assert 'id="queue-last-action-pin"' in html
    assert 'title="Pin this status so it does not auto-clear"' in html
    assert 'id="queue-ui-reset"' in html

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".queue-chip-front" in css
    assert ".queue-shortcuts-hint" in css
    assert ".queue-help" in css
    assert ".queue-help-copy" in css
    assert ".queue-restore-wrap" in css
    assert ".queue-restore-hint" in css
    assert ".queue-restore-show" in css
    assert ".queue-last-action-row" in css
    assert ".queue-last-action" in css
    assert ".queue-last-action-pin" in css


def test_index_gallery_controls_group_semantics():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert '<div class="gallery-controls" role="group" aria-label="Gallery controls">' in html
    assert '<option value="favorites-first">Favorites first</option>' in html
    assert 'id="gallery-view-toggle"' in html
    assert 'id="refresh-gallery"' in html


def test_gallery_toolbar_keyboard_handler_wiring_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "function onGalleryToolbarButtonKeydown(event)" in content
    assert "const VALID_GALLERY_SORT_ORDERS = new Set(['newest', 'oldest', 'favorites-first']);" in content
    assert "gallerySortOrder === 'favorites-first'" in content
    assert "if (!VALID_GALLERY_SORT_ORDERS.has(gallerySortOrder)) {" in content
    assert "galleryViewToggle.addEventListener('keydown', onGalleryToolbarButtonKeydown);" in content
    assert "refreshGalleryBtn.addEventListener('keydown', onGalleryToolbarButtonKeydown);" in content


def test_gallery_search_query_persistence_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const GALLERY_SEARCH_QUERY_KEY = 'gallerySearchQueryV1';" in content
    assert "let gallerySearchQuery = localStorage.getItem(GALLERY_SEARCH_QUERY_KEY) || '';" in content
    assert "if (gallerySearchQuery) gallerySearch.value = gallerySearchQuery;" in content
    assert "localStorage.setItem(GALLERY_SEARCH_QUERY_KEY, gallerySearchQuery);" in content
    assert "localStorage.removeItem(GALLERY_SEARCH_QUERY_KEY);" in content


def test_image_sidebar_section_collapse_persistence_present_in_assets():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const SIDEBAR_SECTION_COLLAPSE_KEY = 'imageSidebarSectionCollapseV1';" in content
    assert "let imageSidebarSectionCollapseState = getSidebarSectionCollapseState();" in content
    assert "function getSidebarSectionCollapseState()" in content
    assert "function persistSidebarSectionCollapseState()" in content
    assert "function setupImageSidebarSectionCollapse()" in content
    assert "toggleBtn.className = 'btn btn-ghost btn-xs sidebar-section-toggle';" in content
    assert "section.classList.toggle('is-collapsed', isCollapsed);" in content
    assert "localStorage.setItem(SIDEBAR_SECTION_COLLAPSE_KEY, JSON.stringify(imageSidebarSectionCollapseState));" in content
    assert "setupImageSidebarSectionCollapse();" in content

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".sidebar-section-head" in css
    assert ".sidebar-section-toggle" in css
    assert ".sidebar-section.is-collapsed > :not(.sidebar-section-head)" in css


def test_index_config_service_action_group_semantics():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert '<div class="config-actions-row" role="group" aria-label="Ollama service actions">' in html
    assert '<div class="config-actions-row" role="group" aria-label="ComfyUI service actions">' in html
    assert '<div class="config-actions-row" role="group" aria-label="ComfyUI custom node browser actions">' in html
    assert '<div class="config-actions-row" role="group" aria-label="Flask app actions">' in html


def test_config_service_keyboard_handler_wiring_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "function onConfigServiceControlsKeydown(event)" in content
    assert "configOllamaStartBtn.addEventListener('keydown', onConfigServiceControlsKeydown);" in content
    assert "configOllamaRestartBtn.addEventListener('keydown', onConfigServiceControlsKeydown);" in content
    assert "configOllamaStopBtn.addEventListener('keydown', onConfigServiceControlsKeydown);" in content
    assert "configComfyStartBtn.addEventListener('keydown', onConfigServiceControlsKeydown);" in content
    assert "configComfyRestartBtn.addEventListener('keydown', onConfigServiceControlsKeydown);" in content
    assert "configComfyStopBtn.addEventListener('keydown', onConfigServiceControlsKeydown);" in content


def test_config_comfy_custom_node_browser_markup_and_wiring_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'id="config-comfy-nodes-search"' in html
    assert 'id="config-comfy-nodes-include-builtins"' in html
    assert 'id="config-comfy-nodes-refresh"' in html
    assert 'id="config-comfy-nodes-status"' in html
    assert 'id="config-comfy-nodes-list" class="config-comfy-nodes-list" aria-live="polite"' in html
    assert 'id="config-comfy-packages-status"' in html
    assert 'id="config-comfy-packages-update-all"' in html
    assert 'id="config-comfy-packages-preview-disable-noncore"' in html
    assert 'id="config-comfy-packages-disable-noncore"' in html
    assert 'id="config-comfy-disable-preview" class="config-comfy-disable-preview" hidden' in html
    assert 'id="config-comfy-disable-preview-summary"' in html
    assert 'id="config-comfy-disable-preview-filter"' in html
    assert 'id="config-comfy-disable-preview-selected-only"' in html
    assert 'id="config-comfy-disable-preview-select-all"' in html
    assert 'id="config-comfy-disable-preview-select-visible"' in html
    assert 'id="config-comfy-disable-preview-invert"' in html
    assert 'id="config-comfy-disable-preview-clear-visible"' in html
    assert 'id="config-comfy-disable-preview-clear"' in html
    assert 'id="config-comfy-disable-preview-copy-selected"' in html
    assert 'id="config-comfy-disable-preview-copy-csv"' in html
    assert 'id="config-comfy-disable-preview-download-selected"' in html
    assert 'id="config-comfy-disable-preview-download-csv"' in html
    assert 'id="config-comfy-disable-preview-download-json"' in html
    assert 'id="config-comfy-disable-preview-reset-prefs"' in html
    assert 'id="config-comfy-disable-preview-export-status"' in html
    assert 'id="config-comfy-disable-preview-export-history-copy"' in html
    assert 'id="config-comfy-disable-preview-export-history-copy-json"' in html
    assert 'id="config-comfy-disable-preview-export-history-download"' in html
    assert 'id="config-comfy-disable-preview-export-history-download-csv"' in html
    assert 'id="config-comfy-disable-preview-export-history-download-json"' in html
    assert 'id="config-comfy-disable-preview-export-history-clear"' in html
    assert 'id="config-comfy-disable-preview-export-history-meta"' in html
    assert 'id="config-comfy-disable-preview-export-history"' in html
    assert 'id="config-comfy-disable-preview-list" class="config-comfy-disable-preview-list" aria-live="polite"' in html
    assert 'id="config-comfy-disable-preview-confirm"' in html
    assert 'id="config-comfy-packages-list" class="config-comfy-packages-list" aria-live="polite"' in html
    assert 'id="config-comfy-package-details"' in html
    assert 'id="config-comfy-disable-log-refresh"' in html
    assert 'id="config-comfy-disable-log-revert-last"' in html
    assert 'id="config-comfy-disable-log-pending-only"' in html
    assert 'id="config-comfy-disable-log-status"' in html
    assert 'id="config-comfy-disable-log-list" class="config-comfy-disable-log-list" aria-live="polite"' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "const configComfyNodesSearchInput = document.getElementById('config-comfy-nodes-search');" in js
    assert "const configComfyNodesIncludeBuiltinsToggle = document.getElementById('config-comfy-nodes-include-builtins');" in js
    assert "const configComfyNodesRefreshBtn = document.getElementById('config-comfy-nodes-refresh');" in js
    assert "const configComfyPackagesStatus = document.getElementById('config-comfy-packages-status');" in js
    assert "const configComfyPackagesUpdateAllBtn = document.getElementById('config-comfy-packages-update-all');" in js
    assert "const configComfyPackagesPreviewDisableNonCoreBtn = document.getElementById('config-comfy-packages-preview-disable-noncore');" in js
    assert "const configComfyPackagesDisableNonCoreBtn = document.getElementById('config-comfy-packages-disable-noncore');" in js
    assert "const configComfyDisablePreview = document.getElementById('config-comfy-disable-preview');" in js
    assert "const configComfyDisablePreviewSummary = document.getElementById('config-comfy-disable-preview-summary');" in js
    assert "const configComfyDisablePreviewFilter = document.getElementById('config-comfy-disable-preview-filter');" in js
    assert "const configComfyDisablePreviewSelectedOnly = document.getElementById('config-comfy-disable-preview-selected-only');" in js
    assert "const configComfyDisablePreviewSelectAllBtn = document.getElementById('config-comfy-disable-preview-select-all');" in js
    assert "const configComfyDisablePreviewSelectVisibleBtn = document.getElementById('config-comfy-disable-preview-select-visible');" in js
    assert "const configComfyDisablePreviewInvertBtn = document.getElementById('config-comfy-disable-preview-invert');" in js
    assert "const configComfyDisablePreviewClearVisibleBtn = document.getElementById('config-comfy-disable-preview-clear-visible');" in js
    assert "const configComfyDisablePreviewClearBtn = document.getElementById('config-comfy-disable-preview-clear');" in js
    assert "const configComfyDisablePreviewCopySelectedBtn = document.getElementById('config-comfy-disable-preview-copy-selected');" in js
    assert "const configComfyDisablePreviewCopyCsvBtn = document.getElementById('config-comfy-disable-preview-copy-csv');" in js
    assert "const configComfyDisablePreviewDownloadSelectedBtn = document.getElementById('config-comfy-disable-preview-download-selected');" in js
    assert "const configComfyDisablePreviewDownloadCsvBtn = document.getElementById('config-comfy-disable-preview-download-csv');" in js
    assert "const configComfyDisablePreviewDownloadJsonBtn = document.getElementById('config-comfy-disable-preview-download-json');" in js
    assert "const configComfyDisablePreviewResetPrefsBtn = document.getElementById('config-comfy-disable-preview-reset-prefs');" in js
    assert "const configComfyDisablePreviewExportStatus = document.getElementById('config-comfy-disable-preview-export-status');" in js
    assert "const configComfyDisablePreviewExportHistoryCopyBtn = document.getElementById('config-comfy-disable-preview-export-history-copy');" in js
    assert "const configComfyDisablePreviewExportHistoryCopyJsonBtn = document.getElementById('config-comfy-disable-preview-export-history-copy-json');" in js
    assert "const configComfyDisablePreviewExportHistoryDownloadBtn = document.getElementById('config-comfy-disable-preview-export-history-download');" in js
    assert "const configComfyDisablePreviewExportHistoryDownloadCsvBtn = document.getElementById('config-comfy-disable-preview-export-history-download-csv');" in js
    assert "const configComfyDisablePreviewExportHistoryDownloadJsonBtn = document.getElementById('config-comfy-disable-preview-export-history-download-json');" in js
    assert "const configComfyDisablePreviewExportHistoryClearBtn = document.getElementById('config-comfy-disable-preview-export-history-clear');" in js
    assert "const configComfyDisablePreviewExportHistoryMeta = document.getElementById('config-comfy-disable-preview-export-history-meta');" in js
    assert "const configComfyDisablePreviewExportHistory = document.getElementById('config-comfy-disable-preview-export-history');" in js
    assert "const configComfyDisablePreviewList = document.getElementById('config-comfy-disable-preview-list');" in js
    assert "const configComfyDisablePreviewConfirmBtn = document.getElementById('config-comfy-disable-preview-confirm');" in js
    assert "const configComfyPackagesList = document.getElementById('config-comfy-packages-list');" in js
    assert "const configComfyPackageDetails = document.getElementById('config-comfy-package-details');" in js
    assert "const configComfyDisableLogRefreshBtn = document.getElementById('config-comfy-disable-log-refresh');" in js
    assert "const configComfyDisableLogRevertLastBtn = document.getElementById('config-comfy-disable-log-revert-last');" in js
    assert "const configComfyDisableLogPendingOnlyToggle = document.getElementById('config-comfy-disable-log-pending-only');" in js
    assert "const configComfyDisableLogStatus = document.getElementById('config-comfy-disable-log-status');" in js
    assert "const configComfyDisableLogList = document.getElementById('config-comfy-disable-log-list');" in js
    assert "const CONFIG_COMFY_NODES_INCLUDE_BUILTINS_KEY = 'configComfyNodesIncludeBuiltinsV1';" in js
    assert "const CONFIG_COMFY_DISABLE_PREVIEW_FILTER_KEY = 'configComfyDisablePreviewFilterV1';" in js
    assert "const CONFIG_COMFY_DISABLE_PREVIEW_SELECTED_ONLY_KEY = 'configComfyDisablePreviewSelectedOnlyV1';" in js
    assert "const CONFIG_COMFY_DISABLE_PREVIEW_LAST_EXPORT_KEY = 'configComfyDisablePreviewLastExportV1';" in js
    assert "const CONFIG_COMFY_DISABLE_PREVIEW_EXPORT_HISTORY_KEY = 'configComfyDisablePreviewExportHistoryV1';" in js
    assert "const CONFIG_COMFY_DISABLE_PREVIEW_EXPORT_HISTORY_MAX = 5;" in js
    assert "const CONFIG_COMFY_DISABLE_LOG_PENDING_ONLY_KEY = 'configComfyDisableLogPendingOnlyV1';" in js
    assert "function renderComfyCustomNodeBrowser()" in js
    assert "function renderComfyCustomNodePackages()" in js
    assert "async function loadComfyCustomNodes()" in js
    assert "async function loadComfyCustomNodePackages()" in js
    assert "async function loadComfyCustomNodePackageDetails(packageName)" in js
    assert "async function openComfyCustomNodePackageFolder(packageName)" in js
    assert "async function toggleComfyCustomNodePackageEnabled(packageName, enable)" in js
    assert "async function updateComfyCustomNodePackage(packageName)" in js
    assert "function resetComfyDisablePreview()" in js
    assert "function getSortedComfyDisablePreviewSelectedNames()" in js
    assert "function setComfyDisablePreviewExportStatus(message, persist = true)" in js
    assert "function syncComfyDisablePreviewExportHistoryClearButtonState()" in js
    assert "function renderComfyDisablePreviewExportHistory()" in js
    assert "function recordComfyDisablePreviewExportHistory(entry)" in js
    assert "function clearComfyDisablePreviewExportHistory()" in js
    assert "configComfyDisablePreviewExportHistoryMeta.textContent = `History ${comfyDisablePreviewExportHistory.length}/${CONFIG_COMFY_DISABLE_PREVIEW_EXPORT_HISTORY_MAX}`;" in js
    assert "function applyComfyDisablePreviewFilter()" in js
    assert "function syncComfyDisablePreviewConfirmLabel()" in js
    assert "function renderComfyDisableNonCorePreview(data)" in js
    assert "function renderComfyDisableOperationLog(data)" in js
    assert "async function loadComfyDisableOperationLog()" in js
    assert "async function revertLastComfyDisableBatch()" in js
    assert "async function revertComfyDisableBatch(batchId = '', useLast = false, pendingCount = 0)" in js
    assert "let comfyDisableLogPendingOnly = localStorage.getItem(CONFIG_COMFY_DISABLE_LOG_PENDING_ONLY_KEY) === '1';" in js
    assert "let comfyDisableLogRevertLastInFlight = false;" in js
    assert "Would disable" in js
    assert "Selection" in js
    assert "let comfyDisablePreviewSelectedNames = new Set();" in js
    assert "let comfyDisablePreviewFilterQuery = localStorage.getItem(CONFIG_COMFY_DISABLE_PREVIEW_FILTER_KEY) || '';" in js
    assert "let comfyDisablePreviewSelectedOnlyPref = localStorage.getItem(CONFIG_COMFY_DISABLE_PREVIEW_SELECTED_ONLY_KEY) === '1';" in js
    assert "let comfyDisablePreviewStats = { wouldDisable: 0, skipped: 0, failed: 0 };" in js
    assert "async function runComfyCustomNodePackageBulkAction(action, dryRun = false, selectedNames = null)" in js
    assert "fetch(`/api/comfy/custom-nodes?include_builtin=${includeBuiltins ? '1' : '0'}`)" in js
    assert "fetch('/api/comfy/custom-node-packages')" in js
    assert "fetch(`/api/comfy/custom-node-packages/details?name=${encodeURIComponent(packageName)}`)" in js
    assert "fetch('/api/comfy/custom-node-packages/open', {" in js
    assert "fetch('/api/comfy/custom-node-packages/toggle', {" in js
    assert "fetch('/api/comfy/custom-node-packages/update', {" in js
    assert "fetch('/api/comfy/custom-node-packages/bulk', {" in js
    assert "fetch('/api/comfy/custom-node-packages/disable-log')" in js
    assert "const url = useLast ? '/api/comfy/custom-node-packages/revert-last-disable' : '/api/comfy/custom-node-packages/revert-disable-batch';" in js
    assert "const payload = useLast ? {} : { batch_id: batchId };" in js
    assert "payload.names = selectedNames;" in js
    assert "data-package-action=\"details\"" in js
    assert "data-package-action=\"open\"" in js
    assert "data-package-action=\"toggle\"" in js
    assert "data-package-action=\"update\"" in js
    assert "runComfyCustomNodePackageBulkAction('update_all');" in js
    assert "runComfyCustomNodePackageBulkAction('disable_non_core', true);" in js
    assert "runComfyCustomNodePackageBulkAction('disable_non_core');" in js
    assert "if (!comfyDisablePreviewReady) return;" in js
    assert "data-disable-preview-select=\"1\"" in js
    assert "data-disable-preview-row=\"1\"" in js
    assert "data-disable-preview-selectable=" in js
    assert "data-disable-preview-selected=" in js
    assert "data-preview-name=" in js
    assert "config-comfy-disable-preview-item is-action" in js
    assert "config-comfy-disable-preview-item is-skip" in js
    assert "config-comfy-disable-preview-item is-error" in js
    assert "config-comfy-disable-preview-chip is-action" in js
    assert "config-comfy-disable-preview-chip is-skip" in js
    assert "config-comfy-disable-preview-chip is-error" in js
    assert "configComfyDisablePreviewList.addEventListener('change', (event) => {" in js
    assert "configComfyDisablePreviewFilter.addEventListener('input', () => {" in js
    assert "configComfyDisablePreviewSelectedOnly.addEventListener('change', () => {" in js
    assert "localStorage.setItem(CONFIG_COMFY_DISABLE_PREVIEW_FILTER_KEY, comfyDisablePreviewFilterQuery);" in js
    assert "localStorage.removeItem(CONFIG_COMFY_DISABLE_PREVIEW_FILTER_KEY);" in js
    assert "localStorage.setItem(CONFIG_COMFY_DISABLE_PREVIEW_SELECTED_ONLY_KEY, '1');" in js
    assert "localStorage.removeItem(CONFIG_COMFY_DISABLE_PREVIEW_SELECTED_ONLY_KEY);" in js
    assert "configComfyDisablePreviewResetPrefsBtn.addEventListener('click', () => {" in js
    assert "comfyDisablePreviewSelectedNames.add(packageName);" in js
    assert "comfyDisablePreviewSelectedNames.delete(packageName);" in js
    assert "configComfyDisablePreviewSelectAllBtn.addEventListener('click', () => {" in js
    assert "configComfyDisablePreviewSelectVisibleBtn.addEventListener('click', () => {" in js
    assert "configComfyDisablePreviewInvertBtn.addEventListener('click', () => {" in js
    assert "configComfyDisablePreviewClearVisibleBtn.addEventListener('click', () => {" in js
    assert "configComfyDisablePreviewClearBtn.addEventListener('click', () => {" in js
    assert "configComfyDisablePreviewCopySelectedBtn.addEventListener('click', async () => {" in js
    assert "await copyTextToClipboard(selected.join('\\n'));" in js
    assert "configComfyDisablePreviewCopyCsvBtn.addEventListener('click', async () => {" in js
    assert "await copyTextToClipboard(csvLines.join('\\n'));" in js
    assert "configComfyDisablePreviewDownloadSelectedBtn.addEventListener('click', () => {" in js
    assert "anchor.download = `la-disable-selected-${dateStr}.txt`;" in js
    assert "configComfyDisablePreviewDownloadCsvBtn.addEventListener('click', () => {" in js
    assert "anchor.download = `la-disable-selected-${dateStr}.csv`;" in js
    assert "configComfyDisablePreviewDownloadJsonBtn.addEventListener('click', () => {" in js
    assert "anchor.download = `la-disable-selected-${dateStr}.json`;" in js
    assert "if (configComfyDisablePreviewExportStatus) {" in js
    assert "if (configComfyDisablePreviewExportHistoryClearBtn) {" in js
    assert "configComfyDisablePreviewExportHistoryClearBtn.addEventListener('click', () => {" in js
    assert "if (configComfyDisablePreviewExportHistoryCopyBtn) {" in js
    assert "configComfyDisablePreviewExportHistoryCopyBtn.addEventListener('click', async () => {" in js
    assert "if (configComfyDisablePreviewExportHistoryCopyJsonBtn) {" in js
    assert "configComfyDisablePreviewExportHistoryCopyJsonBtn.addEventListener('click', async () => {" in js
    assert "if (configComfyDisablePreviewExportHistoryDownloadBtn) {" in js
    assert "configComfyDisablePreviewExportHistoryDownloadBtn.addEventListener('click', () => {" in js
    assert "if (configComfyDisablePreviewExportHistoryDownloadCsvBtn) {" in js
    assert "configComfyDisablePreviewExportHistoryDownloadCsvBtn.addEventListener('click', () => {" in js
    assert "if (configComfyDisablePreviewExportHistoryDownloadJsonBtn) {" in js
    assert "configComfyDisablePreviewExportHistoryDownloadJsonBtn.addEventListener('click', () => {" in js
    assert "await copyTextToClipboard(comfyDisablePreviewExportHistory.join('\\n'));" in js
    assert "await copyTextToClipboard(JSON.stringify(payload, null, 2));" in js
    assert "anchor.download = `la-disable-export-history-${dateStr}.txt`;" in js
    assert "anchor.download = `la-disable-export-history-${dateStr}.csv`;" in js
    assert "anchor.download = `la-disable-export-history-${dateStr}.json`;" in js
    assert "clearComfyDisablePreviewExportHistory();" in js
    assert "configComfyDisablePreviewExportHistoryCopyBtn.disabled = !hasItems;" in js
    assert "configComfyDisablePreviewExportHistoryCopyJsonBtn.disabled = !hasItems;" in js
    assert "configComfyDisablePreviewExportHistoryDownloadBtn.disabled = !hasItems;" in js
    assert "configComfyDisablePreviewExportHistoryDownloadCsvBtn.disabled = !hasItems;" in js
    assert "configComfyDisablePreviewExportHistoryDownloadJsonBtn.disabled = !hasItems;" in js
    assert "const hasItems = comfyDisablePreviewExportHistory.length > 0;" in js
    assert "configComfyDisablePreviewExportHistoryClearBtn.disabled = !hasItems;" in js
    assert "setComfyDisablePreviewExportStatus(comfyDisablePreviewLastExport || 'No export yet.', false);" in js
    assert "setComfyDisablePreviewExportStatus('', true);" in js
    assert "recordComfyDisablePreviewExportHistory(statusWithTime);" in js
    assert "renderComfyDisablePreviewExportHistory();" in js
    assert "const statusWithTime = `${status} (${new Date().toLocaleTimeString()})`;" in js
    assert "setComfyDisablePreviewExportStatus(statusWithTime);" in js
    assert "runComfyCustomNodePackageBulkAction('disable_non_core', false, selected);" in js
    assert "configComfyDisablePreviewConfirmBtn.addEventListener('click', () => {" in js
    assert "configComfyDisableLogRefreshBtn.addEventListener('click', () => {" in js
    assert "configComfyDisableLogRevertLastBtn.addEventListener('click', () => {" in js
    assert "configComfyDisableLogPendingOnlyToggle.addEventListener('change', () => {" in js
    assert "localStorage.setItem(CONFIG_COMFY_DISABLE_LOG_PENDING_ONLY_KEY, '1');" in js
    assert "localStorage.removeItem(CONFIG_COMFY_DISABLE_LOG_PENDING_ONLY_KEY);" in js
    assert "configComfyDisableLogList.addEventListener('click', (event) => {" in js
    assert "data-disable-log-revert-batch" in js
    assert "data-disable-log-pending-count" in js
    assert "if (!window.confirm(`Revert ${targetLabel}? This will attempt to re-enable ${moveLabel}.`)) {" in js
    assert "if (comfyDisableLogRevertLastInFlight) {" in js
    assert "comfyDisableLogRevertLastInFlight = true;" in js
    assert "comfyDisableLogRevertLastInFlight = false;" in js
    assert "revertComfyDisableBatch(batchId, false, pendingCount);" in js
    assert "loadComfyDisableOperationLog();" in js
    assert "revertLastComfyDisableBatch();" in js
    assert "resetComfyDisablePreview();" in js
    assert "await loadComfyCustomNodePackages();" in js
    assert "loadComfyCustomNodes();" in js

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".config-inline-checkbox" in css
    assert ".config-comfy-nodes-list" in css
    assert ".config-comfy-node-row" in css
    assert ".config-comfy-node-chip.is-custom" in css
    assert ".config-comfy-packages-list" in css
    assert ".config-comfy-package-row" in css
    assert ".config-comfy-package-chip.is-enabled" in css
    assert ".config-comfy-package-actions" in css
    assert ".config-comfy-package-row.is-selected" in css
    assert ".config-comfy-disable-preview" in css
    assert ".config-comfy-disable-preview-list" in css
    assert ".config-comfy-disable-preview-item" in css
    assert ".config-comfy-disable-preview-item input[type=\"checkbox\"]" in css
    assert ".config-comfy-disable-preview-item.is-action" in css
    assert ".config-comfy-disable-preview-item.is-skip" in css
    assert ".config-comfy-disable-preview-item.is-error" in css
    assert ".config-comfy-disable-preview-chip" in css
    assert ".config-comfy-disable-preview-chip.is-action" in css
    assert ".config-comfy-disable-preview-chip.is-skip" in css
    assert ".config-comfy-disable-preview-chip.is-error" in css
    assert ".config-comfy-disable-preview-export-history" in css
    assert ".config-comfy-disable-preview-export-history li" in css
    assert ".config-comfy-disable-log-list" in css


def test_index_tag_manager_action_group_semantics():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert '<div class="config-actions-row" role="group" aria-label="Add tag actions">' in html
    assert '<div class="config-actions-row" role="group" aria-label="Reset tag actions">' in html


def test_tag_editor_keyboard_handler_wiring_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "tagEditorList.addEventListener('keydown', (event) => {" in content
    assert "const hasTagAction = target.hasAttribute('data-tag-save') || target.hasAttribute('data-tag-delete');" in content
    assert "<span class=\"tag-editor-actions\" role=\"group\" aria-label=\"Tag ${index + 1} actions\">" in content


def test_index_diagnostics_drawer_semantics():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert 'id="diag-drawer-toggle"' in html
    assert 'aria-expanded="false"' in html
    assert 'id="diag-drawer" class="diag-drawer" hidden aria-hidden="true" aria-label="Diagnostics console"' in html
    assert 'id="diag-copy-btn"' in html
    assert 'id="diag-ws-retry-btn"' in html
    assert 'id="diag-disable-log-repair-btn"' in html
    assert 'id="diag-clear-repair-status-btn"' in html
    assert 'id="diag-backend-health"' in html
    assert 'id="diag-disable-log-health"' in html
    assert 'id="diag-frontend-build"' in html
    assert 'id="diag-repair-status"' in html
    assert 'Backend health' in html
    assert 'Disable log store' in html
    assert 'Frontend build' in html
    assert 'id="ws-transport-status"' in html


def test_diagnostics_drawer_keyboard_handler_wiring_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "function setDiagnosticsDrawerOpen(isOpen)" in content
    assert "const diagCopyBtn = document.getElementById('diag-copy-btn');" in content
    assert "const diagWsRetryBtn = document.getElementById('diag-ws-retry-btn');" in content
    assert "const diagDisableLogRepairBtn = document.getElementById('diag-disable-log-repair-btn');" in content
    assert "const diagClearRepairStatusBtn = document.getElementById('diag-clear-repair-status-btn');" in content
    assert "const diagBackendHealth = document.getElementById('diag-backend-health');" in content
    assert "const diagDisableLogHealth = document.getElementById('diag-disable-log-health');" in content
    assert "const diagFrontendBuild = document.getElementById('diag-frontend-build');" in content
    assert "const diagRepairStatus = document.getElementById('diag-repair-status');" in content
    assert "const backend = diagBackendHealth?.textContent || 'unknown';" in content
    assert "const disableLog = diagDisableLogHealth?.textContent || 'unknown';" in content
    assert "backend=${backend}" in content
    assert "disable-log=${disableLog}" in content
    assert "fetch('/api/healthz')" in content
    assert "async function copyTextToClipboard(text)" in content
    assert "await navigator.clipboard.writeText(value);" in content
    assert "const copied = document.execCommand('copy');" in content
    assert "const commandAliases = {" in content
    assert "const DIAGNOSTICS_COMMAND_SUGGESTIONS = [" in content
    assert "ws: 'ws-status'," in content
    assert "retry: 'ws-retry'," in content
    assert "cls: 'clear'," in content
    assert "const normalizedCommand = commandAliases[command] || command;" in content
    assert "appendDiagnosticsConsoleLine('Aliases: h/?=help, q=queue, p=poll, ws=ws-status, retry=ws-retry, cls=clear');" in content
    assert "const frontend = diagFrontendBuild?.textContent || 'unknown';" in content
    assert "frontend=${frontend}" in content
    assert "Unknown command: ${command}. Try: ${suggestions.join(', ')}" in content
    assert "Unknown command: ${command}. Type help for commands." in content
    assert "if (normalizedCommand === 'ws-status') {" in content
    assert "if (normalizedCommand === 'ws-retry') {" in content
    assert "function forceRetryComfyWebSocket(sourceLabel = 'manual') {" in content
    assert "Hint: start ComfyUI with --enable-cors-header * (or use Configurations > Start ComfyUI) so WS origin checks accept the app host. Current WS target: ${COMFY_WS_URL}" in content
    assert "ComfyUI HTTP API base: ${COMFY_HTTP_BASE}" in content
    assert "function renderWsRetryButtonState() {" in content
    assert "function onDiagnosticsActionsKeydown(event) {" in content
    assert "const controls = [diagCopyBtn, diagWsRetryBtn, diagDisableLogRepairBtn, diagClearRepairStatusBtn, diagnosticsRunBtn].filter(Boolean);" in content
    assert "diagCopyBtn.addEventListener('keydown', onDiagnosticsActionsKeydown);" in content
    assert "diagCopyBtn.addEventListener('click', async () => {" in content
    assert "appendDiagnosticsConsoleLine('Copied diagnostics snapshot.', 'info');" in content
    assert "showToast('Diagnostics snapshot copied.', 'pos');" in content
    assert "diagWsRetryBtn.addEventListener('keydown', onDiagnosticsActionsKeydown);" in content
    assert "diagDisableLogRepairBtn.addEventListener('keydown', onDiagnosticsActionsKeydown);" in content
    assert "diagDisableLogRepairBtn.addEventListener('click', async () => {" in content
    assert "await repairDisableLogStore();" in content
    assert "diagClearRepairStatusBtn.addEventListener('keydown', onDiagnosticsActionsKeydown);" in content
    assert "diagClearRepairStatusBtn.addEventListener('click', () => {" in content
    assert "clearDiagRepairStatusLine();" in content
    assert "function clearDiagRepairStatusLine() {" in content
    assert "function withDiagStatusTimestamp(text) {" in content
    assert "return `${text} (${new Date().toLocaleTimeString()})`;" in content
    assert "setDiagRepairStatusLine(withDiagStatusTimestamp('Last repair: never.'), false);" in content
    assert "async function repairDisableLogStore() {" in content
    assert "setDiagRepairStatusLine(withDiagStatusTimestamp(`Last repair: ${status} (${count}) via ${source}.`));" in content
    assert "setDiagRepairStatusLine(withDiagStatusTimestamp(`Last repair: failed (${err.message}).`));" in content
    assert "fetch('/api/diagnostics/repair-disable-log', {" in content
    assert "diagnosticsRunBtn.addEventListener('keydown', onDiagnosticsActionsKeydown);" in content
    assert "diagWsRetryBtn.addEventListener('click', () => {" in content
    assert "diagDrawer.setAttribute('aria-hidden', isOpen ? 'false' : 'true');" in content
    assert "diagDrawer.addEventListener('keydown', (event) => {" in content
    assert "if (event.key !== 'Escape') return;" in content
    assert "} else if (event.key === 'Escape') {" in content
    assert "} else if (event.key === 'Tab') {" in content
    assert "const matches = DIAGNOSTICS_COMMAND_SUGGESTIONS.filter((candidate) => candidate.startsWith(raw));" in content
    assert "appendDiagnosticsConsoleLine(`Matches: ${matches.join(', ')}`);" in content
    assert "diagHistoryIndex = -1;" in content
    assert "diagHistoryDraft = '';" in content
    assert "diagDrawerCommandInput.value = '';" in content
    assert "appendDiagnosticsConsoleLine('Command input cleared.');" in content
    assert "} else if ((event.key === 'l' || event.key === 'L') && event.ctrlKey) {" in content
    assert "appendDiagnosticsConsoleLine('Console cleared.');" in content
    assert "} else if ((event.key === 'r' || event.key === 'R') && event.ctrlKey) {" in content
    assert "const attempted = forceRetryComfyWebSocket('diagnostics shortcut');" in content
    assert "appendDiagnosticsConsoleLine(attempted ? 'Triggered ComfyUI websocket retry attempt.' : 'ComfyUI websocket already connected.');" in content
    assert "} else if (event.key === 'Home' && event.ctrlKey) {" in content
    assert "} else if (event.key === 'End' && event.ctrlKey) {" in content
    assert "const now = new Date();" in content
    assert "const ts = now.toTimeString().slice(0, 8);" in content
    assert "row.textContent = `[${ts}] ${text}`;" in content


def test_diagnostics_drawer_state_persistence_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const DIAG_DRAWER_COLLAPSED_KEY = 'diagDrawerCollapsedV1';" in content
    assert "const diagDrawerCollapsedStored = localStorage.getItem(DIAG_DRAWER_COLLAPSED_KEY);" in content
    assert "let diagDrawerCollapsed = diagDrawerCollapsedStored === null ? null : diagDrawerCollapsedStored === '1';" in content
    assert "diagDrawerCollapsed = !isOpen;" in content
    assert "if (diagDrawerCollapsed) {" in content
    assert "localStorage.setItem(DIAG_DRAWER_COLLAPSED_KEY, '1');" in content
    assert "} else {" in content
    assert "localStorage.setItem(DIAG_DRAWER_COLLAPSED_KEY, '0');" in content
    assert "// Restore diagnostics drawer open/collapsed state from localStorage" in content
    assert "if (diagDrawer && diagDrawerCollapsed !== null) {" in content
    assert "setDiagnosticsDrawerOpen(!diagDrawerCollapsed);" in content


def test_diagnostics_command_history_session_persistence_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const DIAG_COMMAND_HISTORY_KEY = 'diagCommandHistoryV1';" in content
    assert "const DIAG_REPAIR_STATUS_KEY = 'diagRepairStatusV1';" in content
    assert "const diagRepairStatusStored = localStorage.getItem(DIAG_REPAIR_STATUS_KEY) || '';" in content
    assert "function setDiagRepairStatusLine(text, persist = true) {" in content
    assert "localStorage.setItem(DIAG_REPAIR_STATUS_KEY, value);" in content
    assert "localStorage.removeItem(DIAG_REPAIR_STATUS_KEY);" in content
    assert "if (diagRepairStatus && diagRepairStatusStored) {" in content
    assert "setDiagRepairStatusLine(diagRepairStatusStored, false);" in content
    assert "function getDiagnosticsCommandHistoryState() {" in content
    assert "const parsed = JSON.parse(sessionStorage.getItem(DIAG_COMMAND_HISTORY_KEY) || '[]');" in content
    assert "if (!Array.isArray(parsed)) return [];" in content
    assert "const diagHistory = getDiagnosticsCommandHistoryState();" in content
    assert "function persistDiagnosticsCommandHistoryState() {" in content
    assert "sessionStorage.setItem(DIAG_COMMAND_HISTORY_KEY, JSON.stringify(diagHistory.slice(-50)));" in content
    assert "persistDiagnosticsCommandHistoryState();" in content


def test_index_model_download_actions_and_modal_semantics():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert '<div class="mb-downloads-actions" role="group" aria-label="Download queue actions">' in html
    assert 'id="mb-clear-finished-downloads"' in html
    assert 'id="mb-downloads-section" hidden aria-hidden="true"' in html
    assert 'id="mb-downloads-counter" class="mb-downloads-counter" hidden aria-hidden="true"' in html
    assert 'id="mb-reset-status" class="hint mb-reset-status" aria-live="polite" hidden aria-hidden="true"' in html
    assert 'id="mb-downloads-toggle" type="button" aria-controls="mb-downloads-body" aria-expanded="true"' in html
    assert 'id="mb-type-info-panel" class="mb-type-info-panel" hidden aria-hidden="true" tabindex="-1"' in html
    assert 'id="mb-model-modal" class="mb-model-modal" hidden aria-hidden="true" role="dialog" aria-modal="true" aria-label="Model details"' in html
    assert 'id="mb-model-modal-download-status" class="hint mb-model-modal-download-status" aria-live="polite" hidden' in html


def test_index_model_pagination_group_semantics():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert 'id="mb-search-status" class="hint" hidden aria-hidden="true"' in html
    assert 'id="mb-results-section" hidden aria-hidden="true"' in html
    assert '<div class="mb-pagination" id="mb-pagination" role="group" aria-label="Model search pagination" hidden aria-hidden="true">' in html
    assert 'id="mb-local-controls" hidden aria-hidden="true"' in html
    assert 'id="mb-local-view" hidden aria-hidden="true"' in html
    assert 'id="mb-prev-page"' in html
    assert 'id="mb-next-page"' in html


def test_index_model_search_controls_include_cancel_button():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert 'id="mb-search-btn"' in html
    assert 'id="mb-cancel-search-btn"' in html
    assert 'id="mb-cancel-search-btn" type="button" disabled' in html


def test_model_download_actions_keyboard_handler_wiring_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "function setElementHiddenState(element, isHidden)" in content
    assert "element.setAttribute('aria-hidden', isHidden ? 'true' : 'false');" in content
    assert "setElementHiddenState(mbLocalControls, nextView !== 'library');" in content
    assert "setElementHiddenState(mbLocalView, nextView !== 'library');" in content
    assert "setElementHiddenState(mbResultsSection, false);" in content
    assert "setElementHiddenState(mbPagination, true);" in content
    assert "setElementHiddenState(mbPagination, false);" in content
    assert "setElementHiddenState(mbDownloadsSection, false);" in content
    assert "setElementHiddenState(mbDownloadsSection, rows.length === 0);" in content
    assert "setElementHiddenState(mbResetStatus, true);" in content
    assert "setElementHiddenState(mbResetStatus, false);" in content
    assert "setElementHiddenState(mbDownloadsCounter, !mbDownloadsMinimized);" in content
    assert "setElementHiddenState(mbLibraryActionReport, true);" in content
    assert "setElementHiddenState(mbLibraryActionReport, false);" in content
    assert "function onModelDownloadsActionsKeydown(event)" in content
    assert "mbClearFinishedDownloadsBtn.addEventListener('keydown', onModelDownloadsActionsKeydown);" in content
    assert "mbDownloadsToggleBtn.addEventListener('keydown', onModelDownloadsActionsKeydown);" in content
    assert "mbDownloadsBody.setAttribute('aria-hidden', mbDownloadsMinimized ? 'true' : 'false');" in content
    assert "mbTypeInfoPanel.setAttribute('aria-hidden', isOpen ? 'false' : 'true');" in content
    assert "mbTypeInfoPanel.setAttribute('aria-hidden', mbTypeInfoPanel.hidden ? 'true' : 'false');" in content
    assert "let mbTypeInfoLastFocus = null;" in content
    assert "function setMbTypeInfoPanelOpen(isOpen)" in content
    assert "mbTypeInfoPanel.focus();" in content
    assert "mbTypeInfoBtn.addEventListener('keydown', (event) => {" in content
    assert "if (event.key === 'ArrowDown') {" in content
    assert "setMbTypeInfoPanelOpen(true);" in content
    assert "mbTypeInfoPanel.addEventListener('keydown', (event) => {" in content
    assert "setMbTypeInfoPanelOpen(false);" in content
    assert "let mbModelModalLastFocus = null;" in content
    assert "function getModelModalTabStops()" in content
    assert "mbModelModal.addEventListener('keydown', (event) => {" in content
    assert "if (event.key !== 'Tab' || mbModelModal.hidden) return;" in content
    assert "const tabStops = getModelModalTabStops();" in content
    assert "mbModelModalLastFocus = null;" in content


def test_model_pagination_keyboard_handler_wiring_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "function onModelPaginationKeydown(event)" in content
    assert "mbPrevPage.addEventListener('keydown', onModelPaginationKeydown);" in content
    assert "mbNextPage.addEventListener('keydown', onModelPaginationKeydown);" in content


def test_model_download_actions_are_modal_version_based_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "class=\"btn btn-sm btn-primary mb-model-modal-download-btn\"" in content
    assert "mb-model-modal-refresh-btn" in content
    assert "card.setAttribute('role', 'button');" in content
    assert "card.setAttribute('tabindex', '0');" in content
    assert "mbModelModalFiles.querySelectorAll('.mb-model-modal-download-btn').forEach((btn) => {" in content
    assert "mbModelModalFiles.querySelectorAll('.mb-model-modal-refresh-btn').forEach((btn) => {" in content
    assert "function getVersionFileDownloadTarget(item, version, file)" in content
    assert "async function refreshInstalledVersionMetadata(version, installedFiles, btn)" in content
    assert "function setModelModalDownloadStatus(message, level = '')" in content
    assert "fetch('/api/models/library/update-version-metadata'" in content
    assert "setModelModalDownloadStatus(`Queueing ${fileLabel} from ${versionName}...`);" in content
    assert "setModelModalDownloadStatus(`Queued ${label} from ${versionLabel}.`, 'ok');" in content
    assert "card.addEventListener('keydown', (event) => {" in content
    assert "mbResultsGrid.querySelectorAll('.mb-dl-btn').forEach" not in content


def test_model_download_target_prefers_model_type_before_base_model_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    model_type_line = "\tconst folderFromModelType = inferModelFolderFromTypeLabel(item?.type || '');"
    version_type_line = "\tconst folderFromVersionType = inferModelFolderFromTypeLabel(version?.base_model || '');"

    assert model_type_line in content
    assert version_type_line in content
    assert content.index(model_type_line) < content.index(version_type_line)


def test_model_search_status_lifecycle_is_cleared_after_successful_render():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "function setModelSearchStatus(message = '', isVisible = false)" in content
    assert "setElementHiddenState(mbSearchStatus, !isVisible);" in content
    assert "setElementHiddenState(mbSearchStatus, false);" in content
    assert "setModelSearchStatus(provider === 'huggingface' ? 'Searching Hugging Face…' : 'Searching CivitAI…', true);" in content
    assert "setModelSearchStatus('Search failed: ' + err.message, true);" in content
    assert "setModelSearchStatus('', false);" in content


def test_model_search_results_count_handles_unavailable_provider_totals():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const hasProviderTotal = Object.prototype.hasOwnProperty.call(data || {}, 'total_items');" in content
    assert "function renderSearchResults(items, totalItems, hasProviderTotal = false)" in content
    assert "mbResultsCount.textContent = `(${shown} shown - total unavailable)`;" in content


def test_model_search_aborts_previous_requests_and_ignores_stale_results():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "let mbSearchAbortController = null;" in content
    assert "let mbSearchRequestSeq = 0;" in content
    assert "let mbSearchInFlight = false;" in content
    assert "let mbSearchCancelRequested = false;" in content
    assert "const MB_SEARCH_TIMEOUT_MS = 25000;" in content
    assert "const requestId = ++mbSearchRequestSeq;" in content
    assert "mbSearchAbortController.abort();" in content
    assert "const controller = new AbortController();" in content
    assert "const { signal } = controller;" in content
    assert "timeoutHandle = setTimeout(() => {" in content
    assert "mbSearchInFlight = true;" in content
    assert "mbSearchInFlight = false;" in content
    assert "await fetch(endpoint + params.toString(), { signal });" in content
    assert "if (requestId !== mbSearchRequestSeq) return;" in content
    assert "if (err && err.name === 'AbortError') {" in content
    assert "if (mbSearchCancelRequested) {" in content
    assert "setModelSearchStatus('Search cancelled.', true);" in content
    assert "if (searchTimedOut) {" in content
    assert "clearTimeout(timeoutHandle);" in content


def test_model_search_timeout_message_is_exposed_for_stalled_requests():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "Search timed out after ${Math.round(MB_SEARCH_TIMEOUT_MS / 1000)}s. Please try again." in content


def test_model_search_cancel_button_is_wired_to_abort_active_request():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const mbCancelSearchBtn = document.getElementById('mb-cancel-search-btn');" in content
    assert "function cancelModelSearch() {" in content
    assert "mbSearchCancelRequested = true;" in content
    assert "mbSearchAbortController.abort();" in content
    assert "if (mbCancelSearchBtn) {" in content
    assert "mbCancelSearchBtn.addEventListener('click', cancelModelSearch);" in content
    assert "if (mbCancelSearchBtn) mbCancelSearchBtn.disabled = !mbSearchInFlight;" in content
    assert "if (event.key !== 'Escape') return;" in content
    assert "if (!mbSearchInFlight) return;" in content
    assert "cancelModelSearch();" in content
    assert "function onModelSearchControlKeydown(event) {" in content
    assert "if (event.key !== 'Escape') return;" in content
    assert "mbSearchType.addEventListener('keydown', onModelSearchControlKeydown);" in content
    assert "mbProvider.addEventListener('keydown', onModelSearchControlKeydown);" in content
    assert "mbSort.addEventListener('keydown', onModelSearchControlKeydown);" in content


def test_model_search_disables_pagination_controls_while_request_is_active():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "mbPrevPage.disabled = mbSearchInFlight || mbCurrentPage <= 1;" in content
    assert "mbNextPage.disabled = mbSearchInFlight || (mbQueryMode ? !mbHasNextPage : (mbCurrentPage >= mbTotalPages));" in content
    assert "if (mbSearchInFlight) return;" in content


def test_model_search_cancel_status_is_auto_cleared_after_delay():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "let mbSearchStatusTimer = null;" in content
    assert "const MB_CANCEL_STATUS_CLEAR_MS = 2500;" in content
    assert "if (message === 'Search cancelled.' && isVisible) {" in content
    assert "mbSearchStatusTimer = setTimeout(() => {" in content
    assert "if (mbSearchStatus.textContent !== 'Search cancelled.') return;" in content
    assert "setModelSearchStatus('', false);" in content


def test_preview_websocket_retry_backoff_is_respected_between_attempts():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "let comfyWsNextRetryAt = 0;" in content
    assert "let comfyWsBlockedUntil = 0;" in content
    assert "let comfyWsQuickCloseCount = 0;" in content
    assert "const COMFY_WS_BLOCKED_COOLDOWN_MS = 5 * 60 * 1000;" in content
    assert "const COMFY_WS_QUICK_CLOSE_THRESHOLD = 3;" in content
    assert "function _isComfyWsBlockedActive() {" in content
    assert "if (comfyWsNextRetryAt > Date.now()) {" in content
    assert "ComfyUI WebSocket retry scheduled in ${secsLeft}s. HTTP polling fallback is active." in content
    assert "ComfyUI WebSocket appears blocked (${secsLeft}s left). HTTP polling fallback is active." in content
    assert "const likelyBlocked = Boolean(event?.code === 1006 && comfyWsQuickCloseCount >= COMFY_WS_QUICK_CLOSE_THRESHOLD);" in content
    assert "ComfyUI WebSocket appears blocked (likely 403/forbidden). HTTP polling fallback is active." in content
    assert "comfyWsNextRetryAt = Date.now() + delay;" in content
    assert "comfyWsNextRetryAt = 0;" in content


def test_preview_transport_diagnostics_line_shows_retry_and_cooldown_state():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const wsTransportStatus = document.getElementById('ws-transport-status');" in content
    assert "function renderWsTransportStatus() {" in content
    assert "Preview transport: cooldown (${minsLeft}m left), retries ${comfyWsFailCount}/${COMFY_WS_MAX_RETRIES}" in content
    assert "Preview transport: websocket blocked (${secsLeft}s left), polling active" in content
    assert "Preview transport: retry in ${secsLeft}s (${comfyWsFailCount}/${COMFY_WS_MAX_RETRIES})" in content
    assert "Preview transport: websocket connected" in content
    assert "diagWsRetryBtn.textContent = 'WS Connected';" in content
    assert "diagWsRetryBtn.textContent = 'Connecting...';" in content
    assert "diagWsRetryBtn.textContent = `Retry WS (${secsLeft}s)`;" in content
    assert "diagWsRetryBtn.textContent = `Retry WS (${minsLeft}m)`;" in content
    assert "diagWsRetryBtn.textContent = 'Retry WS';" in content
    assert "renderWsTransportStatus();" in content
    assert "let wsTransportStatusTimer = null;" in content
    assert "function startWsTransportStatusTicker() {" in content
    assert "wsTransportStatusTimer = window.setInterval(() => {" in content
    assert "function stopWsTransportStatusTicker() {" in content
    assert "stopWsTransportStatusTicker();" in content


def test_model_modal_preserves_search_result_type_when_details_are_less_specific():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const fallbackType = String(item?.type || '');" in content
    assert "const resolvedType = data.type && data.type !== 'Checkpoint'" in content
    assert "type: resolvedType," in content


def test_generic_model_file_type_does_not_force_stablediffusion_folder_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "if (value.includes('checkpoint')) return 'StableDiffusion';" in content
    assert "value.includes('checkpoint') || value.includes('model')" not in content


def test_model_card_missing_preview_has_explicit_fallback_label_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "mb-result-thumb-placeholder" in content
    assert "aria-label=\"No preview available\"" in content
    assert "mb-result-thumb-placeholder-badge" in content
    assert "No preview" in content


def test_local_library_cards_use_model_card_layout_features_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "card.className = 'mb-result-card mb-local-card';" in content
    assert "mb-result-thumb-placeholder" in content
    assert "Local model" in content
    assert "<span class=\"mb-result-type-chip\">Local</span>" in content
    assert "const versionLabel = String(m.version_name || '').trim();" in content
    assert "const previewUrls = Array.isArray(m.preview_urls)" in content
    assert "class=\"mb-local-card-version\"" in content
    assert "class=\"mb-local-card-preview-strip\"" in content
    assert "class=\"mb-local-card-preview-thumb" in content
    assert "Matched version:" in content
    assert "class=\"mb-local-card-actions\"" in content
    assert "class=\"btn btn-sm btn-danger mb-delete-btn\"" in content


def test_index_local_library_quick_filters_include_matched_only_toggle():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert 'id="mb-local-matched-only"' in html
    assert 'Show only models with matched metadata' in html
    assert 'Matched Only' in html


def test_model_browser_hidden_sidebar_controls_are_not_forced_visible_by_css():
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    content = css_path.read_text(encoding="utf-8")

    assert "#mb-remote-controls[hidden]," in content
    assert "#mb-local-controls[hidden]" in content
    assert "display: none !important;" in content


def test_model_card_missing_preview_badge_style_present_in_css():
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    content = css_path.read_text(encoding="utf-8")

    assert ".mb-result-thumb-placeholder-badge" in content
    assert "text-transform: uppercase;" in content


def test_index_search_controls_include_bulk_installed_update_button():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert 'id="mb-search-bulk-refresh-installed-btn"' in html
    assert "Bulk Update Installed Preview + Metadata" in html


def test_index_local_library_includes_search_parity_filters():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert 'id="mb-local-query"' in html
    assert 'id="mb-local-type"' in html
    assert 'id="mb-local-base-model"' in html
    assert '<option value="Checkpoint">Checkpoint</option>' in html
    assert '<option value="LORA">LoRA</option>' in html
    assert '<option value="SDXL 1.0">SDXL 1.0</option>' in html


def test_local_library_search_parity_filters_are_wired_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const mbLocalType = document.getElementById('mb-local-type');" in content
    assert "const mbLocalBaseModel = document.getElementById('mb-local-base-model');" in content
    assert "const mbLocalMatchedOnly = document.getElementById('mb-local-matched-only');" in content
    assert "localStorage.setItem('mbLocalType', mbLocalType.value || '');" in content
    assert "localStorage.setItem('mbLocalBaseModel', mbLocalBaseModel.value || '');" in content
    assert "const type = mbLocalType ? String(mbLocalType.value || '').trim().toLowerCase() : '';" in content
    assert "const baseModel = mbLocalBaseModel ? String(mbLocalBaseModel.value || '').trim().toLowerCase() : '';" in content
    assert "const matchedOnly = mbToggleIsOn(mbLocalMatchedOnly);" in content
    assert "const itemProvider = String(item.provider || '').toLowerCase();" in content
    assert "const itemModelName = String(item.model_name || '').toLowerCase();" in content
    assert "const itemVersionName = String(item.version_name || '').toLowerCase();" in content
    assert "mbLocalMatchedOnly.addEventListener('click', () => {" in content
    assert "localStorage.setItem('mbLocalMatchedOnly', mbToggleIsOn(mbLocalMatchedOnly) ? '1' : '0');" in content
    assert "mbLocalMatchedOnly.addEventListener('keydown', onLocalLibraryQuickFiltersKeydown);" in content


def test_local_library_cards_open_local_details_modal_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "function openLocalModelDetailsModal(item)" in content
    assert "card.setAttribute('role', 'button');" in content
    assert "card.setAttribute('tabindex', '0');" in content
    assert "if (target.closest('.mb-delete-btn')) return;" in content
    assert "openLocalModelDetailsModal(m);" in content
    assert "preview_url: previewUrl," in content


def test_index_local_library_has_find_missing_previews_button():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert 'id="mb-library-enrich-previews-btn"' in html
    assert "Find Missing Previews" in html
    assert 'id="mb-library-recover-metadata-btn"' in html
    assert "Find Missing Metadata and Previews" in html


def test_local_library_find_missing_previews_button_wired_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const mbLibraryEnrichPreviewsBtn = document.getElementById('mb-library-enrich-previews-btn');" in content
    assert "const mbLibraryRecoverMetadataBtn = document.getElementById('mb-library-recover-metadata-btn');" in content
    assert "async function enrichLocalLibraryPreviews()" in content
    assert "async function recoverLocalLibraryMetadataAndPreviews()" in content
    assert "fetch('/api/models/library/enrich-previews'" in content
    assert "fetch('/api/models/library/recover-metadata'" in content
    assert "if (!selectedProviders.length) throw new Error('Select at least one provider for recovery.');" in content
    assert "renderLocalLibraryActionReport('Metadata + Preview Recovery'" in content
    assert "mbLibraryEnrichPreviewsBtn.addEventListener('click', enrichLocalLibraryPreviews);" in content
    assert "mbLibraryRecoverMetadataBtn.addEventListener('click', recoverLocalLibraryMetadataAndPreviews);" in content


def test_search_bulk_installed_update_button_wired_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const mbSearchBulkRefreshInstalledBtn = document.getElementById('mb-search-bulk-refresh-installed-btn');" in content
    assert "function isInstalledFileName(fileName)" in content
    assert "async function bulkUpdateInstalledSearchMetadata()" in content
    assert "const installedItems = searchItems.filter((item) => modelIsInstalled(item));" in content
    assert "fetch('/api/models/library/update-version-metadata'" in content
    assert "renderLocalLibraryActionReport('Search Bulk Installed Update'" in content
    assert "mbSearchBulkRefreshInstalledBtn.addEventListener('click', bulkUpdateInstalledSearchMetadata);" in content


def test_index_local_library_has_compare_missing_metadata_button():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert 'id="mb-library-compare-metadata-btn"' in html
    assert "Compare Missing Metadata" in html
    assert 'id="mb-compare-provider-civitai" type="checkbox" checked' in html
    assert 'id="mb-compare-provider-huggingface" type="checkbox" checked' in html
    assert 'id="mb-library-status" class="hint" aria-hidden="false"' in html
    assert 'id="mb-library-action-report" class="mb-library-action-report" hidden aria-hidden="true" aria-live="polite"' in html
    assert 'id="mb-library-action-report-clear"' in html
    assert 'Clear Report' in html


def test_local_library_compare_missing_metadata_button_wired_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const mbLibraryCompareMetadataBtn = document.getElementById('mb-library-compare-metadata-btn');" in content
    assert "const mbCompareProviderCivitai = document.getElementById('mb-compare-provider-civitai');" in content
    assert "const mbCompareProviderHuggingface = document.getElementById('mb-compare-provider-huggingface');" in content
    assert "const mbLibraryActionReport = document.getElementById('mb-library-action-report');" in content
    assert "const mbLibraryActionReportClear = document.getElementById('mb-library-action-report-clear');" in content
    assert "function getSelectedCompareProviders()" in content
    assert "function createReportItem(label, file = '')" in content
    assert "function focusLocalLibraryReportItem(fileName)" in content
    assert "function renderLocalLibraryActionReport(title, summary, groups = [])" in content
    assert "function buildReportItemsFromSamples(samples, mapper)" in content
    assert "button class=\"mb-library-action-report-link\"" in content
    assert "button.addEventListener('click', () => focusLocalLibraryReportItem(button.dataset.reportFile || ''));" in content
    assert "card.dataset.modelName = String(m.name || '');" in content
    assert "targetCard.classList.add('is-report-target');" in content
    assert "<button class=\"btn btn-ghost btn-xs\" id=\"mb-library-action-report-clear\" type=\"button\">Clear Report</button>" in content
    assert "clearBtn.addEventListener('click', () => renderLocalLibraryActionReport('', '', []));" in content
    assert "if (!selectedProviders.length) throw new Error('Select at least one provider for compare.');" in content
    assert "let providerSummary = '';" in content
    assert "providerSummary = selectedProviders" in content
    assert "Metadata compare complete (${providerSummary})" in content
    assert "const versionName = String(sample.version_name || '').trim();" in content
    assert "const details = [provider, versionName].filter(Boolean).join(' · ');" in content
    assert "const errorPrefix = providerSummary ? `Metadata compare failed (${providerSummary}): ` : 'Metadata compare failed: ';" in content
    assert "Could not compare metadata (${providerSummary}): " in content
    assert "renderLocalLibraryActionReport('Preview Lookup'" in content
    assert "renderLocalLibraryActionReport('Metadata Compare'" in content
    assert "setElementHiddenState(mbLibraryStatus, false);" in content
    assert "async function compareLocalLibraryMetadata()" in content
    assert "fetch('/api/models/library/compare-metadata'" in content
    assert "providers: selectedProviders" in content
    assert "mbLibraryCompareMetadataBtn.addEventListener('click', compareLocalLibraryMetadata);" in content
    assert "const versionLabel = String(item.version_name || '');" in content
    assert "['Matched version', versionLabel || 'Not provided']" in content


def test_local_library_action_report_target_styles_present():
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    content = css_path.read_text(encoding="utf-8")

    assert ".mb-library-action-report-link" in content
    assert ".mb-local-card.is-report-target" in content
    assert ".mb-local-card-version" in content
    assert ".mb-local-card-preview-strip" in content
    assert ".mb-model-modal-file-actions" in content


def test_local_library_filename_query_candidates_present_in_backend():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    content = app_path.read_text(encoding="utf-8")

    assert "def _build_local_model_query_candidates(file_name: str) -> list[str]:" in content
    assert "stripped_stem = re.sub" in content
    assert "for query_index, query in enumerate(query_candidates):" in content
    assert "type_candidates = [model_type] if model_type in _CIVITAI_MODEL_TYPES else []" in content


def test_index_image_aspect_ratio_and_seed_helper_controls_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert '<div class="aspect-ratio-row" role="group" aria-label="Aspect ratio presets">' in html
    assert 'data-ar="1024:1024"' in html
    assert 'data-ar="1344:768"' in html
    assert 'data-ar="768:1344"' in html
    assert 'id="image-use-last-seed"' in html
    assert 'id="image-lock-seed"' in html


def test_image_seed_helper_and_aspect_ratio_wiring_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "document.querySelectorAll('[data-ar]').forEach((btn) => {" in content
    assert "const imageUseLastSeedBtn = document.getElementById('image-use-last-seed');" in content
    assert "const imageLockSeedBtn = document.getElementById('image-lock-seed');" in content
    assert "let _lastGeneratedSeed = null;" in content
    assert "let _seedLocked = false;" in content
    assert "function setLastGeneratedSeed(seed) {" in content
    assert "imageLockSeedBtn.setAttribute('aria-pressed', String(_seedLocked));" in content


def test_image_seed_helper_and_aspect_ratio_styles_present_in_css():
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    content = css_path.read_text(encoding="utf-8")

    assert ".seed-action-row" in content
    assert ".aspect-ratio-row" in content
    assert ".btn-ghost.active" in content


def test_index_image_model_stack_controls_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert 'class="sidebar-section model-stack-panel"' in html
    assert 'id="image-model-mode-all"' in html
    assert 'id="image-model-mode-recent"' in html
    assert 'id="image-model-mode-favorites"' in html
    assert 'id="image-model-filter"' in html
    assert 'id="image-model-favorite-toggle"' in html
    assert 'id="image-model-recent-list"' in html
    assert 'id="image-model-favorite-list"' in html
    assert 'id="model-stack-badges"' in html
    assert 'id="model-stack-compat-hint"' in html
    assert 'title="Tip: keep Base, Refiner, and VAE in the same family (SD1.5 vs SDXL) when possible."' in html
    assert 'title="Second-pass quality boost (SDXL refiner style)."' in html
    assert 'Loaded from ComfyUI CheckpointLoaderSimple' not in html
    assert '<p class="hint model-recent-label">Recent</p>' not in html
    assert '<p class="hint model-recent-label">Favorites</p>' not in html


def test_image_model_stack_filter_and_recent_wiring_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const imageModelModeAll = document.getElementById('image-model-mode-all');" in content
    assert "const imageModelModeRecent = document.getElementById('image-model-mode-recent');" in content
    assert "const imageModelModeFavorites = document.getElementById('image-model-mode-favorites');" in content
    assert "const imageModelFavoriteToggle = document.getElementById('image-model-favorite-toggle');" in content
    assert "const imageModelFilter = document.getElementById('image-model-filter');" in content
    assert "const imageModelRecentList = document.getElementById('image-model-recent-list');" in content
    assert "const imageModelFavoriteList = document.getElementById('image-model-favorite-list');" in content
    assert "const modelStackBadges = document.getElementById('model-stack-badges');" in content
    assert "const modelStackCompatHint = document.getElementById('model-stack-compat-hint');" in content
    assert "function renderFilteredImageModels(rawFilter = '', preferredValue = '')" in content
    assert "function canSelectCheckpointInCurrentFamilyMode(modelName)" in content
    assert "if (requestedMode === 'auto' || requestedMode === 'flux') return true;" in content
    assert "if (requestedMode === 'sd' && family === 'flux') return false;" in content
    assert "set family mode to Auto/Flux to enable" in content
    assert "const isUnsupportedFluxModel = (name) => /flux/i.test(name || '');" not in content
    assert "function rememberRecentImageModel(modelName)" in content
    assert "function getFavoriteImageModels()" in content
    assert "function toggleFavoriteImageModel(modelName)" in content
    assert "function setImageModelFilterMode(mode)" in content
    assert "function renderRecentImageModels()" in content
    assert "function renderFavoriteImageModels()" in content
    assert "function updateModelStackBadges()" in content
    assert "function updateModelStackCompatibilityHint()" in content


def test_image_model_stack_styles_present_in_css():
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    content = css_path.read_text(encoding="utf-8")

    assert ".model-stack-panel" in content
    assert ".model-stack-badges" in content
    assert ".model-stack-chip" in content
    assert ".model-mode-row" in content
    assert ".model-favorite-toggle-row" in content
    assert ".model-recent-list" in content
    assert ".model-stack-compat-hint" in content
    assert ".lora-row-header" in content
    assert ".lora-row-enable" in content
    assert ".lora-row-collapse" in content
    assert ".lora-disabled" in content
    assert ".gallery-grid.is-grid-mode .gallery-card" in content


def test_sidebar_profiles_at_top_and_sampler_in_model_stack_panel():
    """Profiles section must appear before model-stack-panel; Sampler must be inside it."""
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)

    # profiles section exists and appears before the model-stack-panel
    assert 'class="sidebar-section preset-profile-section"' in html
    profiles_pos = html.index('class="sidebar-section preset-profile-section"')
    stack_pos = html.index('class="sidebar-section model-stack-panel"')
    assert profiles_pos < stack_pos, "Profiles section must precede model-stack-panel"

    # sampler select is inside the model-stack-panel block
    model_stack_block = html[stack_pos:]
    assert 'id="image-sampler-select"' in model_stack_block

    # vae appears before refiner within the model-stack-panel
    vae_pos = model_stack_block.index('id="vae-model-select"')
    refiner_pos = model_stack_block.index('id="refiner-model-select"')
    assert vae_pos < refiner_pos, "VAE selector must appear before Refiner selector"


def test_lora_row_ux_js_wiring():
    """LoRA rows must have enable-toggle and collapse controls wired in JS."""
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "lora-row-enable" in content
    assert "lora-row-collapse" in content
    assert "lora-row-body" in content
    assert "lora-disabled" in content
    assert "lora-row-header" in content
    # ARIA: collapse button must declare its controlled region
    assert 'aria-controls="lora-row-body-${id}"' in content
    # ARIA: body must carry a matching id
    assert 'id="lora-row-body-${id}"' in content
    # ARIA: hidden state kept in sync with aria-hidden on toggle
    assert "rowBody.setAttribute('aria-hidden', expanded ? 'false' : 'true');" in content


def test_compat_grouping_helpers_present_in_js():
    """buildCompatGroupedOptions, getBaseCheckpointFamily, and refreshCompatibilityGroupings must exist."""
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "function buildCompatGroupedOptions(" in content
    assert "function getBaseCheckpointFamily()" in content
    assert "function refreshCompatibilityGroupings()" in content
    assert "Compatible (" in content  # optgroup label template
    assert "Possibly incompatible" in content  # optgroup label


def test_lora_tag_chip_duplicate_safe_insertion_in_js():
    """Tag chip click must use comma-split deduplication instead of naive append."""
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "split(',').map(" in content
    assert "parts.includes(tag)" in content
    assert "parts.join(', ')" in content


def test_gallery_loading_optimizations_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "const QUEUE_POLL_INTERVAL_MS = 1200;" in content
    assert "const GALLERY_HISTORY_LIMIT = 240;" in content
    assert "const GALLERY_EAGER_IMAGE_COUNT = 6;" in content
    assert "const GALLERY_RENDER_CHUNK_SIZE = 24;" in content
    assert "const GALLERY_VIRTUALIZE_THRESHOLD = 120;" in content
    assert "const GALLERY_VIRTUAL_OVERSCAN_ROWS = 3;" in content
    assert "let galleryRenderSeq = 0;" in content
    assert "let galleryVirtualState = null;" in content
    assert "function buildGalleryCardHtml(entry, index)" in content
    assert "function _renderVirtualGalleryWindow()" in content
    assert "function _scheduleVirtualGalleryWindowRender()" in content
    assert "loading=\"${eagerLoad}\"" in content
    assert "fetchpriority=\"${fetchPriority}\"" in content
    assert "fetch(`/api/history?type=image&limit=${GALLERY_HISTORY_LIMIT}`" in content
    assert "window.requestAnimationFrame(() => renderChunk(endIndex));" in content
    assert "galleryGrid.addEventListener('scroll'" in content
    assert "if (err?.name === 'AbortError') return;" in content


def test_gallery_virtualization_styles_present_in_css():
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    content = css_path.read_text(encoding="utf-8")

    assert ".gallery-virtual-spacer" in content
    assert ".gallery-grid.is-grid-mode .gallery-virtual-spacer" in content


def test_controlnet_preview_markup_present_in_index():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert 'id="controlnet-image-preview-wrap"' in html
    assert 'id="controlnet-image-preview"' in html
    assert 'id="controlnet-image-name"' in html
    assert 'id="controlnet-image-clear"' in html
    assert 'id="controlnet-preprocessor-select"' in html


def test_controlnet_preview_wiring_present_in_js_and_css():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")

    assert "const controlnetImagePreviewWrap = document.getElementById('controlnet-image-preview-wrap');" in js
    assert "const controlnetImagePreview = document.getElementById('controlnet-image-preview');" in js
    assert "const controlnetImageName = document.getElementById('controlnet-image-name');" in js
    assert "const controlnetImageClearBtn = document.getElementById('controlnet-image-clear');" in js
    assert "const controlnetPreprocessorSelect = document.getElementById('controlnet-preprocessor-select');" in js
    assert "function updateControlnetImagePreview()" in js
    assert "controlnetImageUpload.addEventListener('change', updateControlnetImagePreview);" in js
    assert "controlnetImageClearBtn.addEventListener('click'" in js
    assert "function loadControlnetPreprocessors()" in js
    assert "chip-controlnet" in js

    assert ".controlnet-image-preview-wrap" in css
    assert ".controlnet-image-preview" in css
    assert ".controlnet-image-preview-row" in css


def test_gallery_lightbox_compare_markup_and_wiring_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'id="gallery-lightbox-compare-toggle"' in html
    assert 'aria-keyshortcuts="C"' in html
    assert 'id="gallery-lightbox-source-upload"' in html
    assert 'id="gallery-lightbox-compare"' in html
    assert 'id="gallery-lightbox-before-image"' in html
    assert 'id="gallery-lightbox-after-image"' in html
    assert 'id="gallery-lightbox-compare-slider"' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "function getImg2ImgSourceImageUrl(entry)" in js
    assert "function resolveLegacyImg2ImgSourceImage(entry)" in js
    assert "async function attachSourceImageToLightboxEntry(file)" in js
    assert "const galleryLightboxSourceUploadInput = document.getElementById('gallery-lightbox-source-upload');" in js
    assert "const mode = String(galleryLightboxCompareToggle.dataset.mode || '').trim();" in js
    assert "if (mode === 'attach')" in js
    assert "fetch('/api/image/upload-image', {" in js
    assert "fetch(`/api/image/source-image?prompt_id=${encodeURIComponent(promptId)}`)" in js
    assert "fetch('/api/history/img2img-source', {" in js
    assert "function applyLightboxCompareSplit(splitValue)" in js
    assert "function toggleGalleryLightboxCompare()" in js
    assert "function updateLightboxMedia(entry, fallbackSrc = '', fallbackAlt = 'Generated image', fallbackCaption = '')" in js
    assert "function isGalleryLightboxInteractiveTarget(target)" in js
    assert "function getGalleryLightboxFocusableControls()" in js
    assert "function getGalleryLightboxTabStops()" in js
    assert "function onGalleryLightboxControlsKeydown(event)" in js
    assert "const isImg2Img = snapshot.mode === 'img2img' && (snapshot.image || snapshot.image_name);" in js
    assert "image: snapshot.image || snapshot.image_name || ''," in js
    assert "if (isGalleryLightboxInteractiveTarget(event.target)) return;" in js
    assert "if (key !== 'Escape' && key !== 'ArrowLeft' && key !== 'ArrowRight' && key !== 'c' && key !== 'C') return;" in js
    assert "if (key === 'c' || key === 'C') {" in js
    assert "toggleGalleryLightboxCompare();" in js
    assert "galleryLightboxPrev.addEventListener('keydown', onGalleryLightboxControlsKeydown);" in js
    assert "galleryLightboxNext.addEventListener('keydown', onGalleryLightboxControlsKeydown);" in js
    assert "galleryLightboxCompareToggle.addEventListener('click'" in js
    assert "galleryLightboxCompareToggle.addEventListener('keydown', onGalleryLightboxControlsKeydown);" in js
    assert "galleryLightboxSourceUploadInput.addEventListener('change', async () => {" in js
    assert "galleryLightboxCompareSlider.addEventListener('input'" in js
    assert "galleryLightboxCompareToggle.hidden = false;" in js
    assert "galleryLightboxCompareToggle.setAttribute('aria-hidden', 'false');" in js
    assert "galleryLightboxCompareToggle.hidden = true;" in js
    assert "galleryLightboxCompareToggle.setAttribute('aria-hidden', 'true');" in js
    assert "galleryLightboxStarBtn.setAttribute('aria-hidden', entryId ? 'false' : 'true');" in js
    assert "galleryLightboxPrev.setAttribute('aria-hidden', total <= 1 ? 'true' : 'false');" in js
    assert "galleryLightboxNext.setAttribute('aria-hidden', total <= 1 ? 'true' : 'false');" in js

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".gallery-lightbox-compare" in css
    assert ".gallery-lightbox-compare-after-wrap" in css
    assert ".gallery-lightbox-compare-slider" in css


def test_gallery_lightbox_meta_panel_markup_and_wiring_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'id="gallery-lightbox-meta-toggle"' in html
    assert 'id="gallery-lightbox-meta"' in html
    assert 'id="gallery-lightbox-meta-chips"' in html
    assert 'id="gallery-lightbox-reuse"' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "const galleryLightboxMetaToggle = document.getElementById('gallery-lightbox-meta-toggle');" in js
    assert "const galleryLightboxMeta = document.getElementById('gallery-lightbox-meta');" in js
    assert "const galleryLightboxMetaChips = document.getElementById('gallery-lightbox-meta-chips');" in js
    assert "const galleryLightboxReuseBtn = document.getElementById('gallery-lightbox-reuse');" in js
    assert "let galleryLightboxLastFocus = null;" in js
    assert "let lightboxMetaOpen = false;" in js
    assert "function updateLightboxMeta(entry)" in js
    assert "galleryLightboxMetaToggle.addEventListener('click'" in js
    assert "galleryLightboxMetaToggle.addEventListener('keydown', onGalleryLightboxControlsKeydown);" in js
    assert "galleryLightboxReuseBtn.addEventListener('click'" in js
    assert "galleryLightboxReuseBtn.addEventListener('keydown', onGalleryLightboxControlsKeydown);" in js
    assert "galleryLightboxCloseBtn.addEventListener('keydown', onGalleryLightboxControlsKeydown);" in js
    assert "applyImageSettings(settings);" in js
    assert "showPanel('image');" in js
    assert "galleryLightboxLastFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;" in js
    assert "if (galleryLightboxLastFocus && document.contains(galleryLightboxLastFocus)) {" in js
    assert "galleryLightboxMetaToggle.hidden = !hasParams;" in js
    assert "galleryLightboxMetaToggle.setAttribute('aria-hidden', hasParams ? 'false' : 'true');" in js
    assert "if (p.scheduler) chips.push(`<span class=\"chip\">scheduler: ${escHtml(p.scheduler)}</span>`);" in js
    assert "galleryLightboxMetaToggle.hidden = true;" in js
    assert "galleryLightboxMetaToggle.setAttribute('aria-hidden', 'true');" in js

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".gallery-lightbox-meta {" in css
    assert ".gallery-lightbox-meta-chips {" in css
    assert ".gallery-lightbox-meta-actions {" in css


def test_fast_preset_applies_speed_focused_settings():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")

    assert "const family = resolveActiveImageFamily(imageModelSelect?.value || '');" in js
    assert "const familyPresetMap = {" in js
    assert "const IMAGE_PRESET_BASE_LABELS = {" in js
    assert "function getImagePresetFamilyLabel()" in js
    assert "function getImagePresetModeLabel()" in js
    assert "function syncImagePresetButtonLabels()" in js
    assert "const imagePresetFamilyBadge = document.getElementById('image-preset-family-badge');" in js
    assert "btn.textContent = `${baseLabel} (${familyLabel})`;" in js
    assert "btn.title = `${baseLabel} preset tuned for ${familyLabel} (${modeLabel})`;" in js
    assert "imagePresetFamilyBadge.textContent = `Preset profile: ${familyLabel} (${modeLabel})`;" in js
    assert "imagePresetFamilyBadge.setAttribute('aria-label', `Preset profile ${familyLabel} in ${modeLabel}`);" in js
    assert "imagePresetFamilyBadge.classList.toggle('is-auto', modeLabel === 'Auto mode');" in js
    assert "imagePresetFamilyBadge.classList.toggle('is-manual', modeLabel === 'Manual mode');" in js
    assert "imagePresetFamilyBadge.classList.toggle('is-flux', familyLabel.startsWith('FLUX'));" in js
    assert "imagePresetFamilyBadge.classList.toggle('is-sd', familyLabel === 'SD');" in js

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".preset-family-badge" in css
    assert ".preset-family-badge.is-auto" in css
    assert ".preset-family-badge.is-manual" in css
    assert ".preset-family-badge.is-flux" in css
    assert ".preset-family-badge.is-sd" in css
    assert "sd:" in js
    assert "flux:" in js
    assert "const fluxRecommendation = family === 'flux' ? getFluxWorkflowRecommendation(imageModelSelect?.value || '') : null;" in js
    assert "fast: { steps: 12, cfg: 5.5, denoise: 0.65, width: 768, height: 768, batch: 1, scheduler: 'normal' }" in js
    assert "fast: { steps: 16, cfg: 3.0, denoise: 0.65, width: 1024, height: 1024, batch: 1, scheduler: fluxRecommendation?.scheduler || 'normal' }" in js
    assert "setSelectValueIfOptionExists(imageSamplerSelect, fluxRecommendation.sampler);" in js
    assert "if (activeImagePreset && activeFamily !== lastResolvedPresetFamily) {" in js
    assert "applyImagePreset(activeImagePreset);" in js
    assert "if (refinerModelSelect) refinerModelSelect.value = '';" in js
    assert "const IMAGE_ACTIVE_PRESET_KEY = 'imageActivePresetV1';" in js
    assert "function updateImagePresetSummary(presetData)" in js
    assert "localStorage.setItem(IMAGE_ACTIVE_PRESET_KEY, preset);" in js
    assert "localStorage.removeItem(IMAGE_ACTIVE_PRESET_KEY);" in js
    assert "const _persistedImagePreset = localStorage.getItem(IMAGE_ACTIVE_PRESET_KEY);" in js

    html_path = Path(__file__).resolve().parents[1] / "templates" / "index.html"
    tpl = html_path.read_text(encoding="utf-8")
    assert 'id="image-preset-summary" class="hint preset-summary" hidden' in tpl
    assert ".preset-summary" in css
    assert "if (hiresfixEnable) hiresfixEnable.checked = false;" in js


def test_flux_lora_hint_and_strength_clamp_wiring():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "const loraFluxHint = document.getElementById('lora-flux-hint');" in js
    assert "function updateLoraFluxHint()" in js
    assert "function clampAllLoraStrengthsForFamily(isFlux)" in js
    assert "function getActiveLoraCompatibilityFamily()" in js
    assert "function resolveLoraCompatibilityFamilyForModel(modelName = '')" in js
    assert "function sanitizeLoraStackForCompatibilityFamily(entries, compatibilityFamily)" in js
    assert "function getIncompatibleEnabledLoraCount()" in js
    assert "function getIncompatibleEnabledLoraRows()" in js
    assert "function refreshLoraOptionsForCurrentFamily()" in js
    assert "const loraCompatModeHint = document.getElementById('lora-compat-mode-hint');" in js
    assert "const loraHideIncompatibleToggle = document.getElementById('lora-hide-incompatible-toggle');" in js
    assert "const loraShowRowHintsToggle = document.getElementById('lora-show-row-hints-toggle');" in js
    assert "const loraCompactPreservedToggle = document.getElementById('lora-compact-preserved-toggle');" in js
    assert "const loraCompactRowClearToggle = document.getElementById('lora-compact-row-clear-toggle');" in js
    assert "const loraCompactMismatchToggle = document.getElementById('lora-compact-mismatch-toggle');" in js
    assert "const loraHideIncompatibleStatus = document.getElementById('lora-hide-incompatible-status');" in js
    assert "const loraClearPreservedBtn = document.getElementById('lora-clear-preserved-btn');" in js
    assert "const loraCompatUiResetBtn = document.getElementById('lora-compat-ui-reset');" in js
    assert "const loraDisplayOptions = document.getElementById('lora-display-options');" in js
    assert "const loraDisplayOptionsToggle = document.getElementById('lora-display-options-toggle');" in js
    assert "const loraDisplayOptionsCompactBtn = document.getElementById('lora-display-options-compact');" in js
    assert "const loraDisplayOptionsResetBtn = document.getElementById('lora-display-options-reset');" in js
    assert "const loraDisplayOptionsModeChip = document.getElementById('lora-display-options-mode-chip');" in js
    assert "const loraDisplayOptionsActiveHint = document.getElementById('lora-display-options-active-hint');" in js
    assert "const loraFamilyLegend = document.getElementById('lora-family-legend');" in js
    assert "function resolveLoraCompatibilityHintState(selectedModel, requestedMode)" in js
    assert "function updateLoraCompatibilityModeHint()" in js
    assert "LoRA grouping source: manual Flux mode." in js
    assert "LoRA grouping source: manual SD mode." in js
    assert "LoRA grouping source: manual SD mode (SDXL checkpoint selected)." in js
    assert "LoRA grouping source: manual SD mode (SD 1.5 checkpoint selected)." in js
    assert "LoRA grouping source: generic list (family unknown)." in js
    assert "loraCompatModeHint.classList.remove('is-manual', 'is-detected', 'is-generic', 'is-flux', 'is-sd', 'detail-flux', 'detail-sd', 'detail-sdxl', 'detail-sd15', 'detail-unknown');" in js
    assert "loraCompatModeHint.classList.add(`detail-${familyDetail}`);" in js
    assert "loraCompatModeHint.setAttribute('aria-label', text);" in js
    assert "loraCompatModeHint.title = text;" in js
    assert "loraCompatModeHint.dataset.source = source;" in js
    assert "loraCompatModeHint.dataset.family = family;" in js
    assert "loraCompatModeHint.dataset.familyDetail = familyDetail;" in js
    assert "familyDetail: 'flux'," in js
    assert "familyDetail: 'sdxl'," in js
    assert "familyDetail: 'sd15'," in js
    assert "familyDetail: 'unknown'," in js
    assert "const state = resolveLoraCompatibilityHintState(selectedModel, requestedMode);" in js
    assert "setHint(state.text, state.classNames, state.source, state.family, state.familyDetail);" in js
    assert "buildCompatGroupedOptions(models, baseFamily, inferCheckpointFamily);" in js
    assert "loraFluxHint.hidden = false;" in js
    assert "loraFluxHint.hidden = true;" in js
    assert "updateLoraFluxHint();" in js
    assert "updateLoraCompatibilityModeHint();" in js
    assert "refreshLoraOptionsForCurrentFamily();" in js
    assert "clampAllLoraStrengthsForFamily(isFluxActive);" in js
    assert "const _isFlux = resolveActiveImageFamily(imageModelSelect?.value || '') === 'flux';" in js
    assert "if (_strInput && _isFlux) _strInput.max = '1';" in js
    assert "const isFluxFamily = resolveActiveImageFamily(imageModelSelect?.value || '') === 'flux';" in js
    assert "const compatibilityFamily = resolveLoraCompatibilityFamilyForModel(common.model || '');" in js
    assert "const safeStrength = Math.max(0, Math.min(maxStrength, Number(entry.strength)));" in js
    assert "const maxLoraStrength = isFluxFamily ? 1 : 2;" in js
    assert "normalized.loras = normalized.loras" in js
    assert "normalized.loras = sanitizeLoraStackForCompatibilityFamily(normalized.loras, compatibilityFamily);" in js
    assert "const filteredLoraCount = Math.max(0, (common.loras?.length || 0) - (normalizedCommon.loras?.length || 0));" in js
    assert "incompatible LoRA" in js
    assert "Skipped ${filteredLoraCount} incompatible LoRA" in js
    assert "const LORA_FAMILY_LEGEND_EXPANDED_KEY = 'loraFamilyLegendExpandedV1';" in js
    assert "const LORA_DISPLAY_OPTIONS_EXPANDED_KEY = 'loraDisplayOptionsExpandedV1';" in js
    assert "const LORA_HIDE_INCOMPATIBLE_OPTIONS_KEY = 'loraHideIncompatibleOptionsV1';" in js
    assert "const LORA_SHOW_ROW_HINTS_KEY = 'loraShowRowHintsV1';" in js
    assert "const LORA_COMPACT_PRESERVED_KEY = 'loraCompactPreservedV1';" in js
    assert "const LORA_COMPACT_ROW_CLEAR_KEY = 'loraCompactRowClearV1';" in js
    assert "const LORA_COMPACT_MISMATCH_KEY = 'loraCompactMismatchV1';" in js
    assert "let loraHideIncompatibleOptions = localStorage.getItem(LORA_HIDE_INCOMPATIBLE_OPTIONS_KEY) === '1';" in js
    assert "let loraShowRowHints = localStorage.getItem(LORA_SHOW_ROW_HINTS_KEY) !== '0';" in js
    assert "let loraCompactPreservedIndicators = localStorage.getItem(LORA_COMPACT_PRESERVED_KEY) === '1';" in js
    assert "let loraCompactRowClearButtons = localStorage.getItem(LORA_COMPACT_ROW_CLEAR_KEY) === '1';" in js
    assert "let loraCompactMismatchBadges = localStorage.getItem(LORA_COMPACT_MISMATCH_KEY) === '1';" in js
    assert "loraFamilyLegend.open = localStorage.getItem(LORA_FAMILY_LEGEND_EXPANDED_KEY) === '1';" in js
    assert "loraFamilyLegend.addEventListener('toggle', () => {" in js
    assert "localStorage.setItem(LORA_FAMILY_LEGEND_EXPANDED_KEY, loraFamilyLegend.open ? '1' : '0');" in js
    assert "const persistedDisplayOpenState = localStorage.getItem(LORA_DISPLAY_OPTIONS_EXPANDED_KEY);" in js
    assert "const hasActiveDisplayPrefs = !loraShowRowHints || loraCompactPreservedIndicators || loraCompactRowClearButtons || loraCompactMismatchBadges;" in js
    assert "loraDisplayOptions.open = persistedDisplayOpenState === '1' || (persistedDisplayOpenState !== '0' && hasActiveDisplayPrefs);" in js
    assert "loraDisplayOptions.addEventListener('toggle', () => {" in js
    assert "localStorage.setItem(LORA_DISPLAY_OPTIONS_EXPANDED_KEY, loraDisplayOptions.open ? '1' : '0');" in js
    assert "function getFilteredLoraModels(baseFamily)" in js
    assert "function getPreservedHiddenIncompatibleSelectionCount()" in js
    assert "function getPreservedHiddenIncompatibleRows()" in js
    assert ".filter((row) => !row.classList.contains('lora-disabled'))" in js
    assert "if (row.classList.contains('lora-disabled')) return false;" in js
    assert "function updateLoraHideIncompatibleStatus()" in js
    assert "function updateLoraClearPreservedButton()" in js
    assert "function updateLoraDisplayOptionsSummary()" in js
    assert "function resetLoraDisplayOptionsPrefs()" in js
    assert "function applyLoraDisplayOptionsCompactPreset()" in js
    assert "function updateLoraCompatUiResetButtonState()" in js
    assert "function resetLoraCompatibilityUiPrefs()" in js
    assert "const models = getFilteredLoraModels(baseFamily);" in js
    assert "const curFamilyLabel = curFamily === 'flux' ? 'FLUX'" in js
    assert "(hidden incompatible: ${curFamilyLabel})" in js
    assert "const baseFamilyLabel = baseFamily === 'flux'" in js
    assert "const preservedCount = getPreservedHiddenIncompatibleSelectionCount();" in js
    assert "Preserving ${preservedCount} selected mismatch${preservedCount === 1 ? '' : 'es'}." in js
    assert "Hiding ${hiddenCount} incompatible option${hiddenCount === 1 ? '' : 's'} for ${baseFamilyLabel}." in js
    assert "No incompatible options to hide for ${baseFamilyLabel}." in js
    assert "loraClearPreservedBtn.hidden = true;" in js
    assert "loraClearPreservedBtn.hidden = false;" in js
    assert "loraClearPreservedBtn.textContent = 'Clear preserved';" in js
    assert "loraClearPreservedBtn.textContent = `Clear preserved (${count})`;" in js
    assert "loraClearPreservedBtn.setAttribute('aria-label', loraClearPreservedBtn.title);" in js
    assert "loraDisplayOptionsToggle.textContent = activeCount > 0 ? `Display options (${activeCount} active)` : 'Display options';" in js
    assert "loraDisplayOptionsToggle.dataset.active = activeCount > 0 ? '1' : '0';" in js
    assert "const activeOptionLabels = [];" in js
    assert "if (!loraShowRowHints) activeOptionLabels.push('row hints hidden');" in js
    assert "if (loraCompactPreservedIndicators) activeOptionLabels.push('compact preserved');" in js
    assert "if (loraCompactRowClearButtons) activeOptionLabels.push('compact row clear');" in js
    assert "if (loraCompactMismatchBadges) activeOptionLabels.push('compact mismatch');" in js
    assert "const displayMode = activeCount === 0 ? 'default' : (isCompactPreset ? 'compact' : 'custom');" in js
    assert "loraDisplayOptionsToggle.setAttribute('aria-label', activeCount > 0 ? `Display options, ${activeCount} active: ${activeOptionLabels.join(', ')}` : 'Display options, defaults active');" in js
    assert "enabled: ${activeOptionLabels.join(', ')}." in js
    assert "loraDisplayOptions.dataset.mode = displayMode;" in js
    assert "const modeLabel = displayMode === 'compact' ? 'Compact' : (displayMode === 'custom' ? 'Custom' : 'Default');" in js
    assert "loraDisplayOptionsModeChip.dataset.mode = displayMode;" in js
    assert "loraDisplayOptionsModeChip.textContent = `Mode: ${modeLabel} (${activeCount})`;" in js
    assert "loraDisplayOptionsModeChip.setAttribute('aria-pressed', displayMode === 'compact' ? 'true' : 'false');" in js
    assert "Compact mode active with ${activeCount} non-default display options. Click to switch to default display options." in js
    assert "Custom mode active with ${activeCount} non-default display options. Click to switch to compact display options." in js
    assert "Default mode active with 0 non-default display options. Click to switch to compact display options." in js
    assert "Display mode compact with ${activeCount} active options. Activate to switch to default display options." in js
    assert "Display mode custom with ${activeCount} active options. Activate to switch to compact display options." in js
    assert "Display mode default with 0 active options. Activate to switch to compact display options." in js
    assert "loraDisplayOptionsActiveHint.hidden = false;" in js
    assert "loraDisplayOptionsActiveHint.textContent = activeCount > 0" in js
    assert "Display mode: ${displayMode}. Active display options: ${activeOptionLabels.join(', ')}." in js
    assert "Display mode: default. Active display options: none." in js
    assert "loraDisplayOptionsResetBtn.disabled = activeCount === 0;" in js
    assert "Reset only LoRA display options to defaults." in js
    assert "LoRA display options are already using defaults." in js
    assert "loraDisplayOptionsCompactBtn.disabled = isCompactPreset;" in js
    assert "LoRA display options are already set to compact mode." in js
    assert "Enable all compact LoRA display options and hide row hints." in js
    assert "non-default LoRA display option" in js
    assert "All LoRA display options are using defaults." in js
    assert "loraHideIncompatibleToggle.checked = loraHideIncompatibleOptions;" in js
    assert "loraShowRowHintsToggle.checked = loraShowRowHints;" in js
    assert "loraCompactPreservedToggle.checked = loraCompactPreservedIndicators;" in js
    assert "loraCompactRowClearToggle.checked = loraCompactRowClearButtons;" in js
    assert "loraCompactMismatchToggle.checked = loraCompactMismatchBadges;" in js
    assert "localStorage.setItem(LORA_HIDE_INCOMPATIBLE_OPTIONS_KEY, loraHideIncompatibleOptions ? '1' : '0');" in js
    assert "localStorage.removeItem(LORA_HIDE_INCOMPATIBLE_OPTIONS_KEY);" in js
    assert "localStorage.removeItem(LORA_SHOW_ROW_HINTS_KEY);" in js
    assert "localStorage.setItem(LORA_SHOW_ROW_HINTS_KEY, '0');" in js
    assert "localStorage.setItem(LORA_COMPACT_PRESERVED_KEY, '1');" in js
    assert "localStorage.removeItem(LORA_COMPACT_PRESERVED_KEY);" in js
    assert "localStorage.setItem(LORA_COMPACT_ROW_CLEAR_KEY, '1');" in js
    assert "localStorage.removeItem(LORA_COMPACT_ROW_CLEAR_KEY);" in js
    assert "localStorage.setItem(LORA_COMPACT_MISMATCH_KEY, '1');" in js
    assert "localStorage.removeItem(LORA_COMPACT_MISMATCH_KEY);" in js
    assert "showToast('LoRA display options set to compact mode.', 'pos');" in js
    assert "showToast('LoRA display options reset.', 'pos');" in js
    assert "const mode = loraDisplayOptionsModeChip.dataset.mode || 'default';" in js
    assert "if (mode === 'compact') {" in js
    assert "resetLoraDisplayOptionsPrefs();" in js
    assert "applyLoraDisplayOptionsCompactPreset();" in js
    assert "localStorage.removeItem(LORA_FAMILY_LEGEND_EXPANDED_KEY);" in js
    assert "localStorage.removeItem(LORA_DISPLAY_OPTIONS_EXPANDED_KEY);" in js
    assert "updateLoraDisplayOptionsSummary();" in js
    assert "loraCompatUiResetBtn.disabled = !hasCustomPrefs;" in js
    assert "updateLoraCompatUiResetButtonState();" in js
    assert "showToast('LoRA compatibility UI preferences reset.', 'pos');" in js
    assert "strength: safeStrength," in js

    html_path = Path(__file__).resolve().parents[1] / "templates" / "index.html"
    tpl = html_path.read_text(encoding="utf-8")
    assert 'id="lora-flux-hint" class="hint lora-flux-hint" hidden' in tpl
    assert 'id="lora-compat-mode-hint" class="hint lora-compat-mode-hint" aria-live="polite"' in tpl
    assert 'id="lora-hide-incompatible-toggle"' in tpl
    assert 'id="lora-show-row-hints-toggle"' in tpl
    assert 'id="lora-compact-preserved-toggle"' in tpl
    assert 'id="lora-compact-row-clear-toggle"' in tpl
    assert 'id="lora-compact-mismatch-toggle"' in tpl
    assert 'id="lora-display-options" class="lora-display-options"' in tpl
    assert 'id="lora-display-options-toggle"' in tpl
    assert 'id="lora-display-options-compact"' in tpl
    assert 'id="lora-display-options-reset"' in tpl
    assert 'id="lora-display-options-mode-chip" type="button" aria-live="polite"' in tpl
    assert 'Mode: default (0)' in tpl
    assert 'id="lora-display-options-active-hint" class="hint lora-display-options-active-hint" hidden aria-live="polite"' in tpl
    assert 'Compact all' in tpl
    assert 'Reset display options' in tpl
    assert 'Display options' in tpl
    assert 'class="lora-display-options-grid"' in tpl
    assert 'id="lora-hide-incompatible-status"' in tpl
    assert 'Hide incompatible options' in tpl
    assert 'Show row hints' in tpl
    assert 'Compact preserved indicators' in tpl
    assert 'Compact row clear buttons' in tpl
    assert 'Compact mismatch badges' in tpl
    assert 'id="lora-clear-preserved-btn"' in tpl
    assert 'Clear preserved' in tpl
    assert 'id="lora-compat-ui-reset"' in tpl
    assert 'Reset LoRA UI' in tpl
    assert 'id="lora-family-legend"' in tpl
    assert 'id="lora-family-legend-toggle"' in tpl
    assert 'Family legend' in tpl
    assert 'Chip labels indicate inferred LoRA family' in tpl

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".lora-flux-hint" in css
    assert ".lora-compat-mode-hint" in css
    assert ".lora-compat-mode-hint.is-manual" in css
    assert ".lora-compat-mode-hint.is-detected" in css
    assert ".lora-compat-mode-hint.is-generic" in css
    assert ".lora-compat-mode-hint.is-flux" in css
    assert ".lora-compat-mode-hint.is-sd" in css
    assert ".lora-compat-mode-hint.detail-sdxl" in css
    assert ".lora-compat-mode-hint.detail-sd15" in css
    assert ".lora-compat-mode-hint.detail-unknown" in css
    assert "--clr-caution" in css
    # per-row compat badge
    assert "function updateLoraRowCompatBadge(row)" in js
    assert "function updateAllLoraRowCompatBadges()" in js
    assert "function updateDisableIncompatibleLoraButton()" in js
    assert "function clearLoraRowSelection(row)" in js
    assert "function clearPreservedHiddenIncompatibleRows()" in js
    assert "function disableIncompatibleLoraRows()" in js
    assert "function updateLoraSubmitSkipHint()" in js
    assert "const familyChip = row.querySelector('.lora-row-family-chip');" in js
    assert "const preservedChip = row.querySelector('.lora-row-preserved-chip');" in js
    assert "const preservedHint = row.querySelector('.lora-row-preserved-hint');" in js
    assert "const clearPreservedBtn = row.querySelector('.lora-row-clear-preserved');" in js
    assert "const applyFamilyChip = (family) => {" in js
    assert "const applyPreservedChip = (show, family) => {" in js
    assert "const applyPreservedHint = (show, family) => {" in js
    assert "const applyClearPreservedButton = (show, family) => {" in js
    assert "const rowEnabled = !row.classList.contains('lora-disabled');" in js
    assert "const preservedMismatch = Boolean(rowEnabled && loraHideIncompatibleOptions" in js
    assert "'lora-row-compat-badge'" in js
    assert 'class="lora-row-family-chip"' in js
    assert 'class="lora-row-preserved-chip"' in js
    assert 'class="lora-row-clear-preserved btn btn-ghost btn-xs"' in js
    assert "preservedChip.textContent = 'Preserved';" in js
    assert "mismatch is preserved while incompatible options are hidden." in js
    assert "Preserved ${label} mismatch: hidden options are enabled." in js
    assert "preservedChip.hidden = loraCompactPreservedIndicators;" in js
    assert "clearPreservedBtn.textContent = 'Clear';" in js
    assert "clearPreservedBtn.textContent = loraCompactRowClearButtons ? 'Clear' : `Clear ${label}`;" in js
    assert "Clear preserved ${label} mismatch from this row." in js
    assert "badge.textContent = loraCompactMismatchBadges ? '⚠' : badgeText;" in js
    assert "badge.className = 'lora-row-compat-badge is-mismatch';" in js
    assert "'\u26a0 Not Flux'" in js
    assert "'\u26a0 Flux LoRA'" in js
    assert "'\u26a0 SDXL\u2192SD1.5'" in js
    assert "'\u26a0 SD1.5\u2192SDXL'" in js
    assert "updateAllLoraRowCompatBadges();" in js
    assert "updateDisableIncompatibleLoraButton();" in js
    assert "updateLoraClearPreservedButton();" in js
    assert "updateLoraSubmitSkipHint();" in js
    assert "updateLoraHideIncompatibleStatus();" in js
    assert "enableBtn.addEventListener('click', () => {" in js
    assert "sel.addEventListener('change', async () => {" in js
    assert "removeBtn.addEventListener('click', () => {" in js
    assert "clearLoraRowSelection(row);" in js
    assert "Cleared preserved mismatch from LoRA ${id}." in js
    assert "collectLoraStack();" in js
    assert ".lora-row-family-chip" in css
    assert ".lora-row-preserved-chip" in css
    assert ".lora-row-preserved-hint" in css
    assert ".lora-row-clear-preserved" in css
    assert ".lora-row-family-chip.is-flux" in css
    assert ".lora-row-family-chip.is-sdxl" in css
    assert ".lora-row-family-chip.is-sd15" in css
    assert ".lora-row-family-chip.is-unknown" in css
    assert ".lora-family-legend" in css
    assert ".lora-options-row" in css
    assert ".lora-hide-incompatible-toggle" in css
    assert ".lora-show-row-hints-toggle" in css
    assert ".lora-compact-preserved-toggle" in css
    assert ".lora-compact-row-clear-toggle" in css
    assert ".lora-compact-mismatch-toggle" in css
    assert ".lora-display-options" in css
    assert ".lora-display-options > summary" in css
    assert ".lora-display-options > summary[data-active='1']" in css
    assert ".lora-display-options-grid" in css
    assert ".lora-display-options-actions" in css
    assert ".lora-display-options-mode-chip" in css
    assert ".lora-display-options-mode-chip[data-mode='compact']" in css
    assert ".lora-display-options-mode-chip[data-mode='custom']" in css
    assert ".lora-display-options-active-hint" in css
    assert ".lora-display-options[data-mode='compact'] .lora-display-options-active-hint" in css
    assert ".lora-display-options[data-mode='default'] .lora-display-options-active-hint" in css
    assert ".lora-hide-incompatible-status" in css
    assert ".lora-family-legend > summary" in css
    assert ".lora-row-compat-badge" in css
    assert ".lora-row-compat-badge.is-mismatch" in css
    # mismatch summary at stack header
    assert "const loraMismatchSummary = document.getElementById('lora-mismatch-summary');" in js
    assert "function updateLoraStackMismatchSummary()" in js
    assert "updateLoraStackMismatchSummary();" in js
    assert "loraMismatchSummary.hidden = true;" in js
    assert "loraMismatchSummary.hidden = false;" in js
    assert ".lora-row:not(.lora-disabled) .lora-row-compat-badge.is-mismatch:not([hidden])" in js
    assert "mismatch${count === 1 ? '' : 'es'}" in js
    assert "updateAllLoraRowCompatBadges();" in js
    assert 'id="lora-mismatch-summary"' in tpl
    assert 'id="lora-disable-incompatible-btn"' in tpl
    assert "Cleared ${clearedCount} preserved hidden mismatch" in js
    assert ".lora-mismatch-summary" in css
    assert "Disabled ${disabledCount} incompatible LoRA" in js
    assert "#lora-disable-incompatible-btn[hidden]" in css
    assert "#lora-clear-preserved-btn[hidden]" in css
    assert 'id="lora-submit-skip-hint"' in tpl
    assert "will be skipped on submit." in js
    assert ".lora-submit-skip-hint" in css
    assert ".lora-submit-skip-hint.is-warning" in css


def test_profile_export_import_markup_and_wiring_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'id="image-profile-export"' in html
    assert 'id="image-profile-import-btn"' in html
    assert 'id="image-profile-import-input"' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "const imageProfileExportBtn = document.getElementById('image-profile-export');" in js
    assert "const imageProfileImportBtn = document.getElementById('image-profile-import-btn');" in js
    assert "const imageProfileImportInput = document.getElementById('image-profile-import-input');" in js
    assert "function exportPresetsAsJson()" in js
    assert "function importPresetsFromJson(file)" in js
    assert "imageProfileExportBtn.addEventListener('click', exportPresetsAsJson);" in js
    assert "imageProfileImportInput.addEventListener('change'" in js
    assert "getImageProfileState()" in js
    assert "renderPromptSavedSelect();" in js


def test_model_notes_markup_and_wiring_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'id="mb-model-modal-notes"' in html
    assert 'class="mb-model-modal-notes-wrap"' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "const mbModelModalNotes = document.getElementById('mb-model-modal-notes');" in js
    assert "const MB_MODEL_NOTES_KEY = 'mbModelNotesV1';" in js
    assert "let mbCurrentModelNoteKey = '';" in js
    assert "function loadAllModelNotes()" in js
    assert "function getModelNote(key)" in js
    assert "function saveModelNote(key, text)" in js
    assert "function populateModelNote(key)" in js
    assert "function flushModelNote()" in js
    assert "flushModelNote();" in js
    assert "populateModelNote(`local:${item.name || ''}`)" in js
    assert "populateModelNote(`${provider}:${item.id}`)" in js

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".mb-model-modal-notes-wrap {" in css
    assert ".mb-model-modal-notes {" in css


def test_gallery_sort_and_mode_filter_markup_and_wiring_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'id="gallery-sort"' in html
    assert 'id="gallery-mode-filter"' in html
    assert 'id="gallery-tag-filter"' in html
    assert '<option value="newest">' in html
    assert '<option value="oldest">' in html
    assert '<option value="img2img">' in html
    assert '<option value="all">All tags</option>' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "const gallerySortSelect = document.getElementById('gallery-sort');" in js
    assert "const galleryModeFilterSelect = document.getElementById('gallery-mode-filter');" in js
    assert "const galleryTagFilterSelect = document.getElementById('gallery-tag-filter');" in js
    assert "let gallerySortOrder = " in js
    assert "let galleryModeFilter = " in js
    assert "let galleryTagFilter = " in js
    assert "gallerySortOrder === 'oldest'" in js
    assert "galleryModeFilter === 'img2img'" in js
    assert "galleryTagFilter === 'all'" in js
    assert "GALLERY_TAGS_KEY" in js
    assert "GALLERY_TAG_FILTER_KEY" in js
    assert "syncGalleryTagFilterOptions(images);" in js
    assert "renderLightboxTags(entry);" in js
    assert "galleryLightboxAddTagBtn.addEventListener('click'" in js
    assert "data-gallery-tag-remove" in js
    assert "localStorage.setItem('gallerySortOrder'" in js
    assert "localStorage.setItem('galleryModeFilter'" in js

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".gallery-sort-wrap," in css
    assert ".gallery-mode-filter-wrap," in css
    assert ".gallery-tag-filter-wrap {" in css
    assert ".gallery-lightbox-tag-input" in css
    assert ".gallery-lightbox-tags" in css


def test_gallery_lightbox_tag_editor_markup_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'id="gallery-lightbox-tag-input"' in html
    assert 'id="gallery-lightbox-add-tag-btn"' in html
    assert 'id="gallery-lightbox-tags" class="gallery-lightbox-tags" aria-live="polite"' in html


def test_gallery_favorites_markup_and_wiring_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'id="gallery-mode-filter"' in html
    assert 'value="favorites"' in html
    assert 'id="gallery-lightbox-star"' in html
    assert 'gallery-lightbox-star-btn' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "GALLERY_FAVORITES_KEY" in js
    assert "loadGalleryFavorites" in js
    assert "toggleGalleryFavorite" in js
    assert "isGalleryFavorite" in js
    assert "updateLightboxStarBtn" in js
    assert "galleryLightboxStarBtn" in js
    assert "galleryLightboxStarBtn.addEventListener('keydown', onGalleryLightboxControlsKeydown);" in js
    assert "gallery-star-btn" in js
    assert "galleryModeFilter === 'favorites'" in js

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".gallery-star-btn {" in css
    assert ".gallery-star-btn.is-favorited {" in css
    assert "gallery-lightbox-star-btn" in css


def test_prompt_recent_chips_markup_and_wiring_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'id="prompt-recent-chips"' in html
    assert 'id="prompt-recent-clear-btn"' in html
    assert 'aria-label="Recent prompt chips"' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "const promptRecentChips = document.getElementById('prompt-recent-chips');" in js
    assert "const promptRecentClearBtn = document.getElementById('prompt-recent-clear-btn');" in js
    assert "const PROMPT_RECENT_CHIPS_MAX = 8;" in js
    assert "function applyRecentPromptByIndex(index)" in js
    assert "function renderPromptRecentChips()" in js
    assert "function onPromptRecentControlsKeydown(event)" in js
    assert "if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;" in js
    assert "btn.addEventListener('keydown', onPromptRecentControlsKeydown);" in js
    assert "promptRecentClearBtn.addEventListener('keydown', onPromptRecentControlsKeydown);" in js
    assert "promptRecentChips.innerHTML = '<span class=\"hint\">No recent prompts yet.</span>';" in js
    assert "promptRecentChips.querySelectorAll('.prompt-recent-chip').forEach((btn) => {" in js
    assert "localStorage.removeItem(PROMPT_RECENT_KEY);" in js
    assert "renderPromptRecentChips();" in js
    assert "setSelectValueIfOptionExists(loraModelSelect, payload.lora);" not in js
    assert "setNumericInputIfFinite(loraStrength, payload.lora_strength);" not in js
    assert "const incomingLoras = Array.isArray(payload.loras) ? payload.loras : [];" in js
    assert "const legacyLora = String(payload.lora || '').trim();" in js

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".prompt-history-row {" in css
    assert ".prompt-recent-chips {" in css
    assert ".prompt-recent-chip {" in css


def test_prompt_syntax_popup_markup_and_wiring_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'id="prompt-syntax-info-btn"' in html
    assert 'aria-haspopup="dialog"' in html
    assert 'aria-controls="prompt-syntax-popup"' in html
    assert 'aria-expanded="false"' in html
    assert 'id="prompt-syntax-popup"' in html
    assert 'id="prompt-syntax-close-btn"' in html
    assert 'id="prompt-syntax-popup" class="prompt-syntax-popup" hidden aria-hidden="true" role="dialog" aria-modal="true" aria-label="Prompt syntax guide"' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "let promptSyntaxLastFocus = null;" in js
    assert "function getPromptSyntaxTabStops()" in js
    assert "function setPromptSyntaxPopupOpen(isOpen)" in js
    assert "setPromptSyntaxPopupOpen(promptSyntaxPopup.hidden);" in js
    assert "setPromptSyntaxPopupOpen(false);" in js
    assert "promptSyntaxPopup.addEventListener('keydown', (event) => {" in js
    assert "if (event.key === 'Escape') {" in js
    assert "if (event.key !== 'Tab') return;" in js
    assert "const tabStops = getPromptSyntaxTabStops();" in js
    assert "promptSyntaxPopup.setAttribute('aria-hidden', isOpen ? 'false' : 'true');" in js
    assert "promptSyntaxInfoBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');" in js


def test_prompt_weight_helpers_markup_and_wiring_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'class="prompt-weight-toolbar" role="group" aria-label="Prompt weight helpers"' in html
    assert 'id="prompt-weight-up-btn"' in html
    assert 'id="prompt-weight-down-btn"' in html
    assert 'id="prompt-break-wrap-btn"' in html
    assert '(text:1.2)' in html
    assert '[text:0.8]' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "const promptWeightUpBtn = document.getElementById('prompt-weight-up-btn');" in js
    assert "const promptWeightDownBtn = document.getElementById('prompt-weight-down-btn');" in js
    assert "const promptBreakWrapBtn = document.getElementById('prompt-break-wrap-btn');" in js
    assert "function applyPromptWeightHelper(action)" in js
    assert "insert = `(${selected}:1.2)`;" in js
    assert "insert = `[${selected}:0.8]`;" in js
    assert "insert = selected ? `BREAK ${selected} BREAK` : ' BREAK ';" in js
    assert "promptWeightUpBtn.addEventListener('click', () => applyPromptWeightHelper('up'));" in js
    assert "promptWeightDownBtn.addEventListener('click', () => applyPromptWeightHelper('down'));" in js
    assert "promptBreakWrapBtn.addEventListener('click', () => applyPromptWeightHelper('break'));" in js

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".prompt-weight-toolbar" in css


def test_prompt_recent_dropdown_semantics_and_keyboard_wiring_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'id="prompt-recent-btn"' in html
    assert 'aria-haspopup="listbox"' in html
    assert 'aria-controls="prompt-recent-dropdown"' in html
    assert 'id="prompt-recent-dropdown" class="prompt-recent-dropdown" role="listbox" aria-label="Recent prompts" hidden aria-hidden="true"' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "function setPromptRecentDropdownOpen(isOpen, focusFirst = false)" in js
    assert "promptRecentDropdown.setAttribute('aria-hidden', isOpen ? 'false' : 'true');" in js
    assert "promptRecentBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');" in js
    assert "promptRecentBtn.addEventListener('keydown', (event) => {" in js
    assert "if (!['ArrowDown', 'Enter', ' '].includes(event.key)) return;" in js
    assert "setPromptRecentDropdownOpen(true, true);" in js
    assert "promptRecentDropdown.addEventListener('keydown', (event) => {" in js
    assert "if (!['ArrowDown', 'ArrowUp'].includes(event.key)) return;" in js
    assert "setPromptRecentDropdownOpen(false);" in js


def test_suggestion_tag_collapser_semantics_and_aria_hidden_sync_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'data-suggest-toggle="enhanced-subject-tags" aria-controls="enhanced-subject-tags" aria-expanded="false"' in html
    assert 'id="enhanced-subject-tags" class="enhanced-tag-cloud" data-target="enhanced-subject" aria-label="Subject suggestion tags" hidden aria-hidden="true"' in html
    assert 'data-suggest-toggle="negative-prompt-tags" aria-controls="negative-prompt-tags" aria-expanded="false"' in html
    assert 'id="negative-prompt-tags" class="enhanced-tag-cloud" data-target="image-negative-prompt" aria-label="Negative prompt suggestion tags" hidden aria-hidden="true"' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "function bindSuggestionTagCollapsers()" in js
    assert "target.setAttribute('aria-hidden', target.hidden ? 'true' : 'false');" in js
    assert "btn.setAttribute('aria-controls', targetId);" in js
    assert "btn.setAttribute('aria-expanded', target.hidden ? 'false' : 'true');" in js


def test_image_scheduler_select_present_in_html():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)

    assert 'id="image-model-family-select"' in html
    assert 'Auto detect from checkpoint' in html
    assert 'FLUX workflow' in html
    assert 'id="image-model-family-hint" class="hint" aria-live="polite"' in html
    assert 'id="image-vae-field"' in html
    assert 'id="image-refiner-field"' in html
    assert 'id="image-cfg-row"' in html
    assert 'id="image-scheduler-select"' in html
    assert '<label for="image-scheduler-select"' in html
    assert 'Scheduler' in html
    assert 'id="image-sampler-filter"' in html
    assert 'id="image-scheduler-filter"' in html
    assert 'aria-label="Filter sampler list"' in html
    assert 'aria-label="Filter scheduler list"' in html
    assert 'id="image-sampler-filter-status" class="hint" aria-live="polite"' in html
    assert 'id="image-scheduler-filter-status" class="hint" aria-live="polite"' in html
    assert 'Keyboard: ArrowDown opens sampler list, ArrowUp on first option returns to filter.' in html
    assert 'Keyboard: ArrowDown opens scheduler list, ArrowUp on first option returns to filter.' in html
    assert 'id="flux-sampler-hint"' in html
    assert 'id="flux-no-neg-hint"' in html
    assert 'id="image-negative-prompt-section"' in html
    assert 'id="flux-variant-chip"' in html
    assert 'id="image-apply-recommendation-btn"' in html
    assert 'id="image-recommendation-info-btn"' in html
    assert 'id="image-auto-apply-recommendation-toggle"' in html

    assert 'id="image-auto-apply-recommendation-toggle"' in html
    assert 'id="image-auto-apply-recommendation-label"' in html
    assert 'id="image-lock-recommendation-toggle"' in html
    assert 'id="image-lock-recommendation-label"' in html
    assert 'id="image-unlock-recommendation-once-btn"' in html
    assert 'id="image-unlock-expiry-hint"' in html
    assert 'id="image-recommendation-status"' in html
    assert 'id="image-recommendation-drift-hint"' in html
    assert 'id="image-recommendation-source-tag"' in html


def test_image_scheduler_js_wiring_present_in_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")

    assert "imageSchedulerSelect" in js
    assert "imageSamplerFilter" in js
    assert "imageSchedulerFilter" in js
    assert "const imageApplyRecommendationBtn = document.getElementById('image-apply-recommendation-btn');" in js
    assert "const imageRecommendationInfoBtn = document.getElementById('image-recommendation-info-btn');" in js
    assert "const imageAutoApplyRecommendationLabel = document.getElementById('image-auto-apply-recommendation-label');" in js
    assert "const imageAutoApplyRecommendationToggle = document.getElementById('image-auto-apply-recommendation-toggle');" in js
    assert "const imageLockRecommendationLabel = document.getElementById('image-lock-recommendation-label');" in js
    assert "const imageLockRecommendationToggle = document.getElementById('image-lock-recommendation-toggle');" in js
    assert "const imageUnlockRecommendationOnceBtn = document.getElementById('image-unlock-recommendation-once-btn');" in js
    assert "const imageUnlockExpiryHint = document.getElementById('image-unlock-expiry-hint');" in js
    assert "const imageRecommendationStatus = document.getElementById('image-recommendation-status');" in js
    assert "const imageRecommendationDriftHint = document.getElementById('image-recommendation-drift-hint');" in js
    assert "const imageRecommendationSourceTag = document.getElementById('image-recommendation-source-tag');" in js
    assert "imageModelFamilySelect" in js
    assert "imageModelFamilyHint" in js
    assert "const fluxVariantChip = document.getElementById('flux-variant-chip');" in js
    assert "const IMAGE_MODEL_FAMILY_MODE_KEY = 'imageModelFamilyModeV1';" in js
    assert "const IMAGE_FAMILY_CAPABILITIES = {" in js
    assert "function resolveActiveImageFamily(modelName = '')" in js
    assert "function inferFluxVariant(modelName = '')" in js
    assert "function getFluxWorkflowRecommendation(modelName = '')" in js
    assert "source: 'metadata'" in js
    assert "source: 'heuristic'" in js
    assert "function updateFluxRecommendationInfoButton()" in js
    assert "function updateFluxRecommendationSourceTag()" in js
    assert "function applyCurrentFluxRecommendation(options = {})" in js
    assert "function updateFluxRecommendationDriftHint()" in js
    assert "const IMAGE_FLUX_AUTO_APPLY_RECOMMENDATION_KEY = 'imageFluxAutoApplyRecommendationV1';" in js
    assert "const IMAGE_FLUX_LOCK_RECOMMENDATION_KEY = 'imageFluxLockRecommendationV1';" in js
    assert "let imageFluxAutoApplyRecommendation = localStorage.getItem(IMAGE_FLUX_AUTO_APPLY_RECOMMENDATION_KEY) === '1';" in js
    assert "let imageFluxLockRecommendation = localStorage.getItem(IMAGE_FLUX_LOCK_RECOMMENDATION_KEY) === '1';" in js
    assert "let imageFluxLockBypassOnce = false;" in js
    assert "const sampler = String(details?.recommended_sampler || '').toLowerCase();" in js
    assert "const scheduler = String(details?.recommended_scheduler || '').toLowerCase();" in js
    assert "if (sampler && scheduler) {" in js
    assert "const detailsVariant = String(details?.flux_variant || '').toLowerCase();" in js
    assert "if (detailsVariant === 'schnell' || detailsVariant === 'dev') return detailsVariant;" in js
    assert "function applyImageFamilyModeUi()" in js
    assert "function normalizeImageRequestByFamily(common)" in js
    assert "async function loadImageSchedulers()" in js
    assert "/api/image/schedulers" in js
    assert "function applySelectFilterQuery(selectEl, query)" in js
    assert "function updateSelectFilterStatus(statusEl, query, counts, noun)" in js
    assert "function bindSelectFilterInput(inputEl, selectEl, storageKey, statusEl, noun)" in js
    assert "IMAGE_SAMPLER_FILTER_QUERY_KEY" in js
    assert "IMAGE_SCHEDULER_FILTER_QUERY_KEY" in js
    assert "No ${noun} match" in js
    assert "scheduler: imageSchedulerSelect" in js
    assert "flux: {" in js
    assert "schnell:" in js
    assert "setSelectValueIfOptionExists(imageSamplerSelect, fluxRecommendation.sampler);" in js
    assert "FLUX Schnell tip: use ${sampler} + ${scheduler} scheduler with lower step counts for fast output." in js
    assert "FLUX Dev tip: use ${sampler} + ${scheduler} scheduler for stable quality and detail." in js
    assert "fluxVariantChip.textContent = `Flux Variant: ${variantLabel}`;" in js
    assert "fluxVariantChip.classList.add('is-schnell');" in js
    assert "fluxVariantChip.classList.add('is-dev');" in js
    assert "fluxVariantChip.classList.add('is-auto');" in js
    assert "imageApplyRecommendationBtn.hidden = !isFluxActive;" in js
    assert "if (imageAutoApplyRecommendationLabel) {" in js
    assert "imageAutoApplyRecommendationLabel.hidden = !isFluxActive;" in js
    assert "if (imageLockRecommendationLabel) {" in js
    assert "imageLockRecommendationLabel.hidden = !isFluxActive;" in js
    assert "if (isFluxActive && imageFluxAutoApplyRecommendation) {" in js
    assert "if (isFluxActive && imageFluxLockRecommendation && !imageFluxLockBypassOnce) {" in js
    assert "applyCurrentFluxRecommendation({ announce: false, suppressNoopStatus: true });" in js
    assert "applyCurrentFluxRecommendation({ announce: true });" in js
    assert "if (imageRecommendationInfoBtn) {" in js
    assert "updateFluxRecommendationDriftHint();" in js
    assert "updateFluxRecommendationSourceTag();" in js
    assert "if (imageAutoApplyRecommendationToggle) {" in js
    assert "localStorage.setItem(IMAGE_FLUX_AUTO_APPLY_RECOMMENDATION_KEY, imageFluxAutoApplyRecommendation ? '1' : '0');" in js
    assert "if (imageLockRecommendationToggle) {" in js
    assert "localStorage.setItem(IMAGE_FLUX_LOCK_RECOMMENDATION_KEY, imageFluxLockRecommendation ? '1' : '0');" in js
    assert "if (imageUnlockRecommendationOnceBtn) {" in js
    assert "if (imageUnlockExpiryHint) {" in js
    assert "imageUnlockExpiryHint.classList.toggle('is-active', imageFluxLockBypassOnce && canUseTemporaryUnlock);" in js
    assert "imageFluxLockBypassOnce = true;" in js
    assert "Temporary unlock active for next run." in js
    assert "Recommendation lock restored after submit." in js

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".recommendation-source-tag {" in css
    assert ".recommendation-expiry-tag {" in css
    assert ".recommendation-expiry-tag.is-active {" in css


def test_filter_input_arrow_down_js_wiring():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")

    assert "ArrowDown" in js
    assert "selectEl.focus()" in js
    bind_idx = js.index("function bindSelectFilterInput(")
    arrow_idx = js.index("ArrowDown")
    assert arrow_idx > bind_idx


def test_filter_select_arrow_up_returns_focus_to_filter_js_wiring():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")

    bind_idx = js.index("function bindSelectFilterInput(")
    arrow_up_idx = js.index("event.key !== 'ArrowUp'")
    assert arrow_up_idx > bind_idx
    assert "const firstVisible = [...selectEl.options].find((opt) => !opt.hidden && !opt.disabled);" in js
    assert "if (selectEl.value !== firstVisible.value) return;" in js
    assert "inputEl.focus();" in js


def test_filter_arrow_up_focus_flash_class_wiring():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")

    bind_idx = js.index("function bindSelectFilterInput(")
    flash_idx = js.index("filter-input-focus-flash")
    assert flash_idx > bind_idx
    assert "inputEl.classList.add('filter-input-focus-flash');" in js
    assert "setTimeout(() => inputEl.classList.remove('filter-input-focus-flash')" in js
    assert "filter-input-focus-flash" in css
    assert "filter-focus-flash" in css


def test_image_prompt_ctrl_enter_shortcut():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()
    html = client.get("/").get_data(as_text=True)

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")

    assert 'title="Generate Image (Ctrl+Enter)"' in html
    assert 'id="image-generate-btn"' in html
    assert "event.ctrlKey || event.metaKey" in js
    assert "imageForm.requestSubmit()" in js
    assert js.count("imageForm.addEventListener('submit', async (e) => {") == 1


def test_queue_poll_done_items_clear_tracking_without_images():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    poll_queue_block = js[js.index("async function pollQueue() {"):js.index("function ensureQueuePolling() {")]

    assert "const doneItems = data.done || [];" in poll_queue_block
    assert "const images = done.images || [];" in poll_queue_block
    assert "if (images.length) {" in poll_queue_block
    assert "trackedPromptIds.delete(promptId);" in poll_queue_block
    assert poll_queue_block.index("if (images.length) {") < poll_queue_block.index("trackedPromptIds.delete(promptId);")


def test_queue_poll_retries_done_history_persistence_until_post_ok():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    poll_queue_block = js[js.index("async function pollQueue() {"):js.index("function ensureQueuePolling() {")]

    assert "const saved = await saveHistoryEntry({" in poll_queue_block
    assert "if (!saved) {" in poll_queue_block
    assert "meta.status = 'processing';" in poll_queue_block
    assert "meta.failReason = HISTORY_PERSIST_PENDING_REASON;" in poll_queue_block
    assert "continue;" in poll_queue_block
    assert poll_queue_block.index("if (!saved) {") < poll_queue_block.index("trackedPromptIds.delete(promptId);")


def test_queue_summary_and_badge_include_history_persisting_state():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    queue_render_block = js[js.index("function renderQueueStatus("):js.index("function _clearQueueByStatus(")]

    assert "const HISTORY_PERSIST_PENDING_REASON = 'Waiting to persist history entry.';" in js
    assert "const persistingCount =" in queue_render_block
    assert "Persisting: ${persistingCount}" in queue_render_block
    assert "status === 'processing' && meta.failReason === HISTORY_PERSIST_PENDING_REASON" in queue_render_block
    assert "SAVE" in queue_render_block


def test_queue_help_explains_persisting_state_in_html():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)

    assert 'id="queue-help-copy"' in html
    assert "Persisting counts jobs that are done in ComfyUI but still saving local history." in html
    assert "SAVE badge" in html
    assert 'id="queue-summary"' in html
    assert 'title="Persisting counts done jobs waiting for local history save before leaving tracked queue."' in html


def test_save_history_entry_returns_response_ok_boolean():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    save_block = js[js.index("async function saveHistoryEntry(entry) {"):js.index("function imageProxyUrl(image) {")]

    assert "const res = await fetch('/api/history', {" in save_block
    assert "return res.ok;" in save_block
    assert "return false;" in save_block


def test_flux_negative_prompt_section_present_in_html():
    """Negative prompt section must have an id so JS can hide it in Flux mode."""
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)

    assert 'id="image-negative-prompt-section"' in html
    assert 'id="flux-no-neg-hint"' in html
    assert 'Flux models do not use negative prompts' in html
    assert 'id="flux-sampler-hint"' in html
    assert 'FLUX tip:' in html


def test_flux_negative_prompt_js_wiring_present_in_bundle():
    """JS bundle must declare Flux UI variables and toggle them inside applyImageFamilyModeUi."""
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")

    assert "const imageNegativePromptSection = document.getElementById('image-negative-prompt-section');" in js
    assert "const fluxNoNegHint = document.getElementById('flux-no-neg-hint');" in js
    assert "const fluxSamplerHint = document.getElementById('flux-sampler-hint');" in js

    # Verify toggle logic is inside applyImageFamilyModeUi
    fn_start = js.index("function applyImageFamilyModeUi()")
    fn_end = js.index("\nfunction ", fn_start + 1)
    fn_body = js[fn_start:fn_end]
    assert "isFluxActive" in fn_body
    assert "imageNegativePromptSection.hidden = isFluxActive" in fn_body
    assert "fluxNoNegHint.hidden = !isFluxActive" in fn_body
    assert "const variant = inferFluxVariant(selectedModel);" in fn_body
    assert "if (variant === 'schnell')" in fn_body
    assert "fluxSamplerHint.hidden = false;" in fn_body
    assert "if (imageApplyRecommendationBtn)" in fn_body
    assert "imageApplyRecommendationBtn.hidden = !isFluxActive;" in fn_body
    assert "if (imageAutoApplyRecommendationLabel)" in fn_body
    assert "imageAutoApplyRecommendationLabel.hidden = !isFluxActive;" in fn_body
    assert "if (imageRecommendationStatus && !isFluxActive)" in fn_body
    assert "if (imageRecommendationDriftHint && !isFluxActive)" in fn_body
    assert "imageRecommendationDriftHint.classList.remove('is-warning');" in fn_body
    assert "if (isFluxActive && imageFluxAutoApplyRecommendation)" in fn_body
    assert "lastAutoRecommendationModelKey = autoKey;" in fn_body
    assert "updateFluxRecommendationDriftHint();" in fn_body
    assert "if (fluxVariantChip)" in fn_body
    assert "fluxVariantChip.hidden = false;" in fn_body
    assert "fluxVariantChip.classList.remove('is-dev', 'is-schnell', 'is-auto');" in fn_body


def test_flux_variant_chip_color_classes_present_in_css():
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")

    assert ".flux-variant-chip.is-dev" in css
    assert ".flux-variant-chip.is-schnell" in css
    assert ".flux-variant-chip.is-auto" in css
    assert "#image-auto-apply-recommendation-label" in css
    assert ".recommendation-drift-hint.is-warning" in css


def test_flux_cfg_guidance_label_rename_in_html_and_js():
    """CFG label wraps text in a span for dynamic renaming; Flux guidance hint present."""
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()
    html = client.get("/").get_data(as_text=True)

    assert 'id="image-cfg-label-text"' in html
    assert 'id="image-cfg-flux-hint"' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "imageCfgLabelText" in content
    assert "imageCfgFluxHint" in content
    assert "isFluxActive ? 'Guidance' : 'CFG'" in content


def test_flux_prompt_tips_block_in_html_and_js():
    """Flux prompt tips div is present in the template and toggled in applyImageFamilyModeUi."""
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()
    html = client.get("/").get_data(as_text=True)

    assert 'id="flux-prompt-tips"' in html
    assert "flux-prompt-tips-block" in html
    assert "Flux Prompt Tips:" in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")
    assert "fluxPromptTips" in content
    assert "fluxPromptTips.hidden = !isFluxActive" in content

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".flux-prompt-tips-block" in css
    assert ".flux-tips-list" in css


def test_queue_elapsed_timer_present_in_js():
    """Running jobs stamp startedAt and the live elapsed interval is wired."""
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "meta.startedAt = Date.now();" in content
    assert "queue-elapsed" in content
    assert "data-started-at=" in content
    assert ".queue-elapsed[data-started-at]" in content

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".queue-elapsed" in css


def test_gallery_select_mode_elements_in_html_and_js():
    """Gallery select mode toolbar is present in the template and wired in JS."""
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()
    html = client.get("/").get_data(as_text=True)

    assert 'id="gallery-select-mode-btn"' in html
    assert 'id="gallery-select-toolbar"' in html
    assert 'id="gallery-select-count"' in html
    assert 'id="gallery-select-all-btn"' in html
    assert 'id="gallery-bulk-delete-btn"' in html
    assert 'id="gallery-bulk-export-btn"' in html
    assert 'id="gallery-deselect-all-btn"' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "gallerySelectMode" in content
    assert "gallerySelectedIds" in content
    assert "enterGallerySelectMode" in content
    assert "exitGallerySelectMode" in content
    assert "bulkDeleteSelectedGalleryItems" in content
    assert "bulkExportSelectedGalleryItems" in content
    assert "/api/gallery/bulk-delete" in content
    assert "/api/gallery/bulk-export" in content

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".gallery-select-toolbar" in css
    assert ".gallery-select-count" in css
    assert ".gallery-card.is-selected" in css
    assert ".gallery-select-check" in css


def test_gentime_helper_and_storage_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "function _formatGenTime(ms)" in content
    assert "gallery-gentime-chip" in content
    assert "generation_time_ms" in content
    assert "meta.generationTimeMs = Date.now() - meta.startedAt" in content


def test_gentime_chip_css_present():
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".gallery-gentime-chip" in css


def test_prompt_preset_v2_html_elements_present():
    """Tags input, fav toggle, tag filter, and tag chip container are present in HTML."""
    from pathlib import Path
    html_path = Path(__file__).resolve().parents[1] / "templates" / "index.html"
    html = html_path.read_text(encoding="utf-8")
    assert 'id="prompt-saved-tags"' in html
    assert 'id="prompt-fav-toggle"' in html
    assert 'id="prompt-favorites-only-toggle"' in html
    assert 'id="prompt-tag-filter"' in html
    assert 'id="prompt-preset-filter-status"' in html
    assert 'id="prompt-preset-filter-shortcut-hint"' in html
    assert 'id="prompt-preset-recent-pinned-only-toggle"' in html
    assert 'id="prompt-preset-clear-filters"' in html
    assert 'aria-keyshortcuts="Control+Shift+K"' in html
    assert 'id="prompt-preset-recent-filters"' in html
    assert 'id="prompt-preset-tag-chips"' in html
    assert 'id="prompt-saved-select"' in html
    assert 'id="prompt-save-btn"' in html
    assert 'id="prompt-load-btn"' in html
    assert 'id="prompt-delete-saved-btn"' in html


def test_prompt_preset_v2_js_functions_present():
    """v2 storage functions, migration helper, tag rendering, and fav toggle are in JS."""
    from pathlib import Path
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "function _migratePresetV1ToV2(value)" in js
    assert "function loadPromptSavedPresets()" in js
    assert "function renderPromptSavedSelect()" in js
    assert "function renderPresetTagChips(name)" in js
    assert "function _getFavoritesOnlyFilter()" in js
    assert "function _setFavoritesOnlyFilter(enabled)" in js
    assert "function _updateFavoritesOnlyToggleUi()" in js
    assert "function _getStoredTagFilter()" in js
    assert "function _setStoredTagFilter(value)" in js
    assert "function _restoreStoredTagFilterSelection()" in js
    assert "function _renderPresetFilterStatus(filteredCount, totalCount)" in js
    assert "function clearPromptPresetFilters(showToastOnClear = true)" in js
    assert "function _loadRecentPresetFilters()" in js
    assert "function _saveRecentPresetFilters(list)" in js
    assert "function removeRecentPresetFilterCombo(index)" in js
    assert "function rememberCurrentPresetFilterCombo()" in js
    assert "function applyPresetFilterCombo(combo)" in js
    assert "function renderRecentPresetFilterChips()" in js
    assert "function refreshPromptTagFilterOptions()" in js
    assert "function saveNamedPromptPreset(name, text, tagsRaw)" in js
    assert "function togglePresetFavorite(name)" in js
    assert "function _updateFavToggleBtn(name, isFav)" in js
    assert "function deleteNamedPromptPreset(name)" in js
    # v2 structure written on save
    assert "text: t, tags, favorite, created_at" in js
    # migration writes object from string
    assert "if (typeof value === 'string')" in js
    # favorites shown with star prefix in select
    assert "starPrefix = presets[k].favorite ? '\\u2605 ' : ''" in js
    # tag filter dropdown wired
    assert "promptTagFilter.addEventListener('change'" in js
    # favorites-only quick filter wired
    assert "promptFavoritesOnlyToggle.addEventListener('click'" in js
    assert "promptPresetClearFilters.addEventListener('click'" in js
    assert "Preset filters cleared." in js
    # keyboard shortcut for quick clear
    assert "e.ctrlKey && e.shiftKey && String(e.key || '').toLowerCase() === 'k'" in js
    assert "clearPromptPresetFilters(true);" in js
    # persisted tag filter key
    assert "PROMPT_SAVED_TAG_FILTER_KEY = 'promptSavedTagFilterV1'" in js
    assert "PROMPT_SAVED_RECENT_FILTERS_KEY = 'promptSavedRecentFiltersV1'" in js
    assert "PROMPT_SAVED_RECENT_FILTERS_PINNED_ONLY_KEY = 'promptSavedRecentFiltersPinnedOnlyV1'" in js
    assert "function _getRecentPinnedOnlyFilter()" in js
    assert "function _setRecentPinnedOnlyFilter(enabled)" in js
    assert "function _updateRecentPinnedOnlyToggleUi()" in js
    # tag chips are clickable filter buttons
    assert "promptPresetTagChips.addEventListener('click'" in js
    assert "preset-tag-chip-btn" in js
    # recent filter chips are clickable
    assert "promptPresetRecentFilters.addEventListener('click'" in js
    assert "data-recent-filter-index" in js
    assert "data-recent-filter-pin" in js
    assert "data-recent-filter-remove" in js
    assert "Pinned recent filter." in js
    assert "Unpinned recent filter." in js
    assert "Pinned-only recent filters on." in js
    assert "Pinned-only recent filters off." in js
    assert "function togglePinRecentPresetFilterCombo(index)" in js
    assert "Removed recent filter." in js
    # fav toggle wired
    assert "promptFavToggle.addEventListener('click'" in js


def test_prompt_preset_v2_dom_refs_present():
    """New DOM const declarations for v2 preset controls are in JS."""
    from pathlib import Path
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "const promptSavedTags = document.getElementById('prompt-saved-tags');" in js
    assert "const promptFavToggle = document.getElementById('prompt-fav-toggle');" in js
    assert "const promptFavoritesOnlyToggle = document.getElementById('prompt-favorites-only-toggle');" in js
    assert "const promptTagFilter = document.getElementById('prompt-tag-filter');" in js
    assert "const promptPresetFilterStatus = document.getElementById('prompt-preset-filter-status');" in js
    assert "const promptPresetRecentPinnedOnlyToggle = document.getElementById('prompt-preset-recent-pinned-only-toggle');" in js
    assert "const promptPresetClearFilters = document.getElementById('prompt-preset-clear-filters');" in js
    assert "const promptPresetRecentFilters = document.getElementById('prompt-preset-recent-filters');" in js
    assert "const promptPresetTagChips = document.getElementById('prompt-preset-tag-chips');" in js


def test_prompt_preset_v2_css_present():
    """New preset CSS classes are present in style.css."""
    from pathlib import Path
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".prompt-presets-block" in css
    assert ".prompt-saved-controls-row" in css
    assert ".preset-fav-btn" in css
    assert ".prompt-favorites-only-toggle.is-active" in css
    assert ".prompt-preset-filter-row" in css
    assert ".prompt-preset-filter-status" in css
    assert ".prompt-preset-filter-actions" in css
    assert ".prompt-preset-filter-shortcut-hint" in css
    assert ".prompt-preset-recent-pinned-only-toggle.is-active" in css
    assert ".prompt-preset-recent-filters" in css
    assert ".prompt-preset-recent-filter-chip-wrap" in css
    assert ".prompt-preset-recent-filter-chip-wrap.is-pinned" in css
    assert ".prompt-preset-recent-filter-chip" in css
    assert ".prompt-preset-recent-filter-pin" in css
    assert ".prompt-preset-recent-filter-remove" in css
    assert ".preset-tag-chips" in css
    assert ".preset-tag-chip" in css
    assert ".preset-tag-chip-btn" in css
    assert ".prompt-tags-input" in css
    assert ".prompt-tag-filter-wrap" in css


def test_preset_edit_modal_html_elements_present():
    """Edit button, modal container, and all modal form fields are in HTML."""
    from pathlib import Path
    html_path = Path(__file__).resolve().parents[1] / "templates" / "index.html"
    html = html_path.read_text(encoding="utf-8")
    assert 'id="prompt-edit-preset-btn"' in html
    assert 'id="preset-edit-modal"' in html
    assert 'id="preset-edit-modal-close"' in html
    assert 'id="preset-edit-name"' in html
    assert 'id="preset-edit-text"' in html
    assert 'id="preset-edit-tags"' in html
    assert 'id="preset-edit-notes"' in html
    assert 'id="preset-edit-created"' in html
    assert 'id="preset-edit-save"' in html
    assert 'id="preset-edit-cancel"' in html
    assert 'id="preset-edit-delete"' in html
    assert 'id="prompt-preset-notes-preview"' in html
    assert 'role="dialog"' in html
    assert 'aria-modal="true"' in html


def test_preset_edit_modal_js_functions_and_wiring_present():
    """openPresetEditModal, savePresetEditModal, closePresetEditModal and event wiring in JS."""
    from pathlib import Path
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "let _presetEditOriginalName = '';" in js
    assert "function openPresetEditModal(name)" in js
    assert "function closePresetEditModal()" in js
    assert "function savePresetEditModal()" in js
    assert "function renderPresetNotesPreview(name)" in js
    # rename: delete old key and write new
    assert "delete presets[original];" in js
    # rename conflict path requests explicit overwrite confirmation
    assert "if (newName !== original && presets[newName])" in js
    assert "already exists. Overwrite it?" in js
    assert "showToast('Rename canceled.', 'neg');" in js
    # notes preserved on save
    assert "notes: existing.notes" in js or "notes," in js
    # edit button wired
    assert "promptEditPresetBtn.addEventListener('click'" in js
    # save/cancel/close wired
    assert "presetEditSave.addEventListener('click', savePresetEditModal);" in js
    assert "presetEditCancel.addEventListener('click', closePresetEditModal);" in js
    assert "presetEditModalClose.addEventListener('click', closePresetEditModal);" in js
    # escape key
    assert "e.key === 'Escape' && presetEditModal && !presetEditModal.hidden" in js
    # backdrop click
    assert "classList.contains('preset-edit-modal-backdrop')" in js
    # DOM refs
    assert "const presetEditModal = document.getElementById('preset-edit-modal');" in js
    assert "const presetEditName = document.getElementById('preset-edit-name');" in js
    assert "const presetEditNotes = document.getElementById('preset-edit-notes');" in js
    assert "const promptPresetNotesPreview = document.getElementById('prompt-preset-notes-preview');" in js


def test_preset_edit_modal_css_present():
    """Modal CSS classes are present in style.css."""
    from pathlib import Path
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".preset-edit-modal {" in css
    assert ".preset-edit-modal[hidden]" in css
    assert ".preset-edit-modal-backdrop {" in css
    assert ".preset-edit-modal-panel {" in css
    assert ".preset-edit-modal-head {" in css
    assert ".preset-edit-modal-actions {" in css
    assert ".preset-edit-delete-btn {" in css


def test_preset_notes_field_in_v2_migration():
    """notes: '' field is included in _migratePresetV1ToV2 for both v1 string and v2 object."""
    from pathlib import Path
    js = (Path(__file__).resolve().parents[1] / "static" / "js" / "main.js").read_text(encoding="utf-8")
    assert "notes: ''" in js
    assert "notes: String(value.notes || '')" in js
