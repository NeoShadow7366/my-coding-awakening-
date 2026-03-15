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


def test_diagnostics_drawer_keyboard_handler_wiring_present_in_js_bundle():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "function setDiagnosticsDrawerOpen(isOpen)" in content
    assert "diagDrawer.setAttribute('aria-hidden', isOpen ? 'false' : 'true');" in content
    assert "diagDrawer.addEventListener('keydown', (event) => {" in content
    assert "if (event.key !== 'Escape') return;" in content
    assert "} else if (event.key === 'Home' && event.ctrlKey) {" in content
    assert "} else if (event.key === 'End' && event.ctrlKey) {" in content


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


def test_model_search_disables_pagination_controls_while_request_is_active():
    js_path = Path(__file__).resolve().parents[1] / "static" / "js" / "main.js"
    content = js_path.read_text(encoding="utf-8")

    assert "mbPrevPage.disabled = mbSearchInFlight || mbCurrentPage <= 1;" in content
    assert "mbNextPage.disabled = mbSearchInFlight || (mbQueryMode ? !mbHasNextPage : (mbCurrentPage >= mbTotalPages));" in content
    assert "if (mbSearchInFlight) return;" in content


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
