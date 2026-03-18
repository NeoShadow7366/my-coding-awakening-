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
    assert "queueList.addEventListener('keydown', onQueueActionKeydown);" in content


def test_index_gallery_controls_group_semantics():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert '<div class="gallery-controls" role="group" aria-label="Gallery controls">' in html
    assert 'id="gallery-view-toggle"' in html
    assert 'id="refresh-gallery"' in html


def test_gallery_toolbar_keyboard_handler_wiring_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "function onGalleryToolbarButtonKeydown(event)" in content
    assert "galleryViewToggle.addEventListener('keydown', onGalleryToolbarButtonKeydown);" in content
    assert "refreshGalleryBtn.addEventListener('keydown', onGalleryToolbarButtonKeydown);" in content


def test_index_config_service_action_group_semantics():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert '<div class="config-actions-row" role="group" aria-label="Ollama service actions">' in html
    assert '<div class="config-actions-row" role="group" aria-label="ComfyUI service actions">' in html
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
    assert 'id="diag-ws-retry-btn"' in html
    assert 'id="ws-transport-status"' in html


def test_diagnostics_drawer_keyboard_handler_wiring_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "function setDiagnosticsDrawerOpen(isOpen)" in content
    assert "const diagWsRetryBtn = document.getElementById('diag-ws-retry-btn');" in content
    assert "const commandAliases = {" in content
    assert "const DIAGNOSTICS_COMMAND_SUGGESTIONS = [" in content
    assert "ws: 'ws-status'," in content
    assert "retry: 'ws-retry'," in content
    assert "cls: 'clear'," in content
    assert "const normalizedCommand = commandAliases[command] || command;" in content
    assert "appendDiagnosticsConsoleLine('Aliases: h/?=help, q=queue, p=poll, ws=ws-status, retry=ws-retry, cls=clear');" in content
    assert "Unknown command: ${command}. Try: ${suggestions.join(', ')}" in content
    assert "Unknown command: ${command}. Type help for commands." in content
    assert "if (normalizedCommand === 'ws-status') {" in content
    assert "if (normalizedCommand === 'ws-retry') {" in content
    assert "function forceRetryComfyWebSocket(sourceLabel = 'manual') {" in content
    assert "Hint: start ComfyUI with --enable-cors-header * (or use Configurations > Start ComfyUI) so WS origin checks accept the app host. Current WS target: ${COMFY_WS_URL}" in content
    assert "ComfyUI HTTP API base: ${COMFY_HTTP_BASE}" in content
    assert "function renderWsRetryButtonState() {" in content
    assert "function onDiagnosticsActionsKeydown(event) {" in content
    assert "diagWsRetryBtn.addEventListener('keydown', onDiagnosticsActionsKeydown);" in content
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


def test_index_model_download_actions_and_modal_semantics():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert '<div class="mb-downloads-actions" role="group" aria-label="Download queue actions">' in html
    assert 'id="mb-clear-finished-downloads"' in html
    assert 'id="mb-downloads-toggle"' in html
    assert 'id="mb-model-modal" class="mb-model-modal" hidden aria-hidden="true" role="dialog" aria-modal="true" aria-label="Model details"' in html
    assert 'id="mb-model-modal-download-status" class="hint mb-model-modal-download-status" aria-live="polite" hidden' in html


def test_index_model_pagination_group_semantics():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    resp = client.get("/")

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)

    assert '<div class="mb-pagination" id="mb-pagination" role="group" aria-label="Model search pagination" hidden>' in html
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

    assert "function onModelDownloadsActionsKeydown(event)" in content
    assert "mbClearFinishedDownloadsBtn.addEventListener('keydown', onModelDownloadsActionsKeydown);" in content
    assert "mbDownloadsToggleBtn.addEventListener('keydown', onModelDownloadsActionsKeydown);" in content
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
    assert 'id="mb-library-action-report" class="mb-library-action-report" hidden aria-live="polite"' in html
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


def test_controlnet_preview_wiring_present_in_js_and_css():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")

    assert "const controlnetImagePreviewWrap = document.getElementById('controlnet-image-preview-wrap');" in js
    assert "const controlnetImagePreview = document.getElementById('controlnet-image-preview');" in js
    assert "const controlnetImageName = document.getElementById('controlnet-image-name');" in js
    assert "const controlnetImageClearBtn = document.getElementById('controlnet-image-clear');" in js
    assert "function updateControlnetImagePreview()" in js
    assert "controlnetImageUpload.addEventListener('change', updateControlnetImagePreview);" in js
    assert "controlnetImageClearBtn.addEventListener('click'" in js

    assert ".controlnet-image-preview-wrap" in css
    assert ".controlnet-image-preview" in css
    assert ".controlnet-image-preview-row" in css


def test_gallery_lightbox_compare_markup_and_wiring_present():
    app_module.app.config["TESTING"] = True
    client = app_module.app.test_client()

    html = client.get("/").get_data(as_text=True)
    assert 'id="gallery-lightbox-compare-toggle"' in html
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
    assert "function updateLightboxMedia(entry, fallbackSrc = '', fallbackAlt = 'Generated image', fallbackCaption = '')" in js
    assert "function isGalleryLightboxInteractiveTarget(target)" in js
    assert "function getGalleryLightboxFocusableControls()" in js
    assert "function getGalleryLightboxTabStops()" in js
    assert "function onGalleryLightboxControlsKeydown(event)" in js
    assert "const isImg2Img = snapshot.mode === 'img2img' && (snapshot.image || snapshot.image_name);" in js
    assert "image: snapshot.image || snapshot.image_name || ''," in js
    assert "if (isGalleryLightboxInteractiveTarget(event.target)) return;" in js
    assert "galleryLightboxPrev.addEventListener('keydown', onGalleryLightboxControlsKeydown);" in js
    assert "galleryLightboxNext.addEventListener('keydown', onGalleryLightboxControlsKeydown);" in js
    assert "galleryLightboxCompareToggle.addEventListener('click'" in js
    assert "galleryLightboxCompareToggle.addEventListener('keydown', onGalleryLightboxControlsKeydown);" in js
    assert "galleryLightboxSourceUploadInput.addEventListener('change', async () => {" in js
    assert "galleryLightboxCompareSlider.addEventListener('input'" in js
    assert "galleryLightbox.addEventListener('keydown', (event) => {" in js
    assert "if (event.key !== 'Tab' || galleryLightbox.hidden) return;" in js

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
    assert "galleryLightboxLastFocus = null;" in js

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".gallery-lightbox-meta {" in css
    assert ".gallery-lightbox-meta-chips {" in css
    assert ".gallery-lightbox-meta-actions {" in css


def test_fast_preset_applies_speed_focused_settings():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")

    assert "if (preset === 'fast')" in js
    assert "imageSteps.value = '12';" in js
    assert "imageCfg.value = '5.5';" in js
    assert "imageDenoise.value = '0.65';" in js
    assert "if (imageWidth) imageWidth.value = '768';" in js
    assert "if (imageHeight) imageHeight.value = '768';" in js
    assert "if (refinerModelSelect) refinerModelSelect.value = '';" in js
    assert "if (hiresfixEnable) hiresfixEnable.checked = false;" in js


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
    assert '<option value="newest">' in html
    assert '<option value="oldest">' in html
    assert '<option value="img2img">' in html

    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")
    assert "const gallerySortSelect = document.getElementById('gallery-sort');" in js
    assert "const galleryModeFilterSelect = document.getElementById('gallery-mode-filter');" in js
    assert "let gallerySortOrder = " in js
    assert "let galleryModeFilter = " in js
    assert "gallerySortOrder === 'oldest'" in js
    assert "galleryModeFilter === 'img2img'" in js
    assert "localStorage.setItem('gallerySortOrder'" in js
    assert "localStorage.setItem('galleryModeFilter'" in js

    css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "style.css"
    css = css_path.read_text(encoding="utf-8")
    assert ".gallery-sort-wrap," in css
    assert ".gallery-mode-filter-wrap {" in css


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
