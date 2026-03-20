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
const mbCancelSearchBtn = document.getElementById('mb-cancel-search-btn');
const mbProvider = document.getElementById('mb-provider');
const mbSearchQuery = document.getElementById('mb-search-query');
const mbSearchType = document.getElementById('mb-search-type');
const mbBaseModel = document.getElementById('mb-base-model');
const mbSort = document.getElementById('mb-sort');
const mbPageSize = document.getElementById('mb-page-size');
const mbHideInstalledToggle = document.getElementById('mb-hide-installed');
const mbShowInstalledOnlyToggle = document.getElementById('mb-show-installed-only');
const mbHideEarlyAccessToggle = document.getElementById('mb-hide-early-access');
const mbShowNsfwToggle = document.getElementById('mb-show-nsfw');
const mbTypeInfoBtn = document.getElementById('mb-type-info-btn');
const mbTypeInfoPanel = document.getElementById('mb-type-info-panel');
const mbViewSearchBtn = document.getElementById('mb-view-search-btn');
const mbViewLibraryBtn = document.getElementById('mb-view-library-btn');
const mbRemoteControls = document.getElementById('mb-remote-controls');
const mbLocalControls = document.getElementById('mb-local-controls');
const mbRemoteView = document.getElementById('mb-remote-view');
const mbLocalView = document.getElementById('mb-local-view');
const mbLibraryRefreshBtn = document.getElementById('mb-library-refresh-btn');
const mbLibraryEnrichPreviewsBtn = document.getElementById('mb-library-enrich-previews-btn');
const mbLibraryRecoverMetadataBtn = document.getElementById('mb-library-recover-metadata-btn');
const mbCompareProviderCivitai = document.getElementById('mb-compare-provider-civitai');
const mbCompareProviderHuggingface = document.getElementById('mb-compare-provider-huggingface');
const mbLibraryCompareMetadataBtn = document.getElementById('mb-library-compare-metadata-btn');
const mbLibraryGrid = document.getElementById('mb-library-grid');
const mbLibraryStatus = document.getElementById('mb-library-status');
const mbLocalQuery = document.getElementById('mb-local-query');
const mbLocalType = document.getElementById('mb-local-type');
const mbLocalBaseModel = document.getElementById('mb-local-base-model');
const mbLocalSort = document.getElementById('mb-local-sort');
const mbLocalHideEmbeddings = document.getElementById('mb-local-hide-embeddings');
const mbLocalMatchedOnly = document.getElementById('mb-local-matched-only');
const mbResetFiltersBtn = document.getElementById('mb-reset-filters-btn');
const mbResetStatus = document.getElementById('mb-reset-status');
const mbLibraryActionReport = document.getElementById('mb-library-action-report');
const mbLibraryActionReportClear = document.getElementById('mb-library-action-report-clear');
const mbResultsSection = document.getElementById('mb-results-section');
const mbResultsGrid = document.getElementById('mb-results-grid');
const mbResultsCount = document.getElementById('mb-results-count');
const mbSearchStatus = document.getElementById('mb-search-status');
const mbPagination = document.getElementById('mb-pagination');
const mbModelModal = document.getElementById('mb-model-modal');
const mbModelModalClose = document.getElementById('mb-model-modal-close');
const mbModelModalTitle = document.getElementById('mb-model-modal-title');
const mbModelModalMeta = document.getElementById('mb-model-modal-meta');
const mbModelModalDescription = document.getElementById('mb-model-modal-description');
const mbModelModalPreview = document.getElementById('mb-model-modal-preview');
const mbModelModalPreviewVideo = document.getElementById('mb-model-modal-preview-video');
const mbModelModalThumbs = document.getElementById('mb-model-modal-thumbs');
const mbModelModalVersion = document.getElementById('mb-model-modal-version');
const mbModelModalVersionStatus = document.getElementById('mb-model-modal-version-status');
const mbModelModalDownloadStatus = document.getElementById('mb-model-modal-download-status');
const mbModelModalFiles = document.getElementById('mb-model-modal-files');
const mbModelModalDefaults = document.getElementById('mb-model-modal-defaults');
const mbModelModalNotes = document.getElementById('mb-model-modal-notes');
const mbSearchBulkRefreshInstalledBtn = document.getElementById('mb-search-bulk-refresh-installed-btn');
const mbDownloadsSection = document.getElementById('mb-downloads-section');
const mbDownloadsBody = document.getElementById('mb-downloads-body');
const mbDownloadsList = document.getElementById('mb-downloads-list');
const mbDownloadsCounter = document.getElementById('mb-downloads-counter');
const mbDownloadsToggleBtn = document.getElementById('mb-downloads-toggle');
const mbClearFinishedDownloadsBtn = document.getElementById('mb-clear-finished-downloads');
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
const imageModelFamilySelect = document.getElementById('image-model-family-select');
const imageModelFamilyHint = document.getElementById('image-model-family-hint');
const imageModelFilter = document.getElementById('image-model-filter');
const imageModelModeAll = document.getElementById('image-model-mode-all');
const imageModelModeRecent = document.getElementById('image-model-mode-recent');
const imageModelModeFavorites = document.getElementById('image-model-mode-favorites');
const imageModelFavoriteToggle = document.getElementById('image-model-favorite-toggle');
const imageModelRecentList = document.getElementById('image-model-recent-list');
const imageModelFavoriteList = document.getElementById('image-model-favorite-list');
const fluxVariantChip = document.getElementById('flux-variant-chip');
const imageVaeField = document.getElementById('image-vae-field');
const imageRefinerField = document.getElementById('image-refiner-field');
const imageCfgRow = document.getElementById('image-cfg-row');
const controlnetPanel = document.getElementById('controlnet-panel');
const modelStackBadges = document.getElementById('model-stack-badges');
const modelStackCompatHint = document.getElementById('model-stack-compat-hint');
const refinerModelSelect = document.getElementById('refiner-model-select');
const vaeModelSelect = document.getElementById('vae-model-select');
const imageSamplerSelect = document.getElementById('image-sampler-select');
const imageSamplerFilter = document.getElementById('image-sampler-filter');
const imageSamplerFilterStatus = document.getElementById('image-sampler-filter-status');
const imageSchedulerSelect = document.getElementById('image-scheduler-select');
const imageSchedulerFilter = document.getElementById('image-scheduler-filter');
const imageSchedulerFilterStatus = document.getElementById('image-scheduler-filter-status');
const imageApplyRecommendationBtn = document.getElementById('image-apply-recommendation-btn');
const imageRecommendationInfoBtn = document.getElementById('image-recommendation-info-btn');
const imageAutoApplyRecommendationLabel = document.getElementById('image-auto-apply-recommendation-label');
const imageAutoApplyRecommendationToggle = document.getElementById('image-auto-apply-recommendation-toggle');
const imageLockRecommendationLabel = document.getElementById('image-lock-recommendation-label');
const imageLockRecommendationToggle = document.getElementById('image-lock-recommendation-toggle');
const imageUnlockRecommendationOnceBtn = document.getElementById('image-unlock-recommendation-once-btn');
const imageUnlockExpiryHint = document.getElementById('image-unlock-expiry-hint');
const imageRecommendationStatus = document.getElementById('image-recommendation-status');
const imageRecommendationDriftHint = document.getElementById('image-recommendation-drift-hint');
const imageRecommendationSourceTag = document.getElementById('image-recommendation-source-tag');
const loraAddBtn = document.getElementById('lora-add-btn');
const loraStackContainer = document.getElementById('lora-stack-container');
// NOTE: loraModelSelect / loraStrength / loraStrengthVal replaced by multi-LoRA stack
const controlnetModelSelect = document.getElementById('controlnet-model-select');
const controlnetPreprocessorSelect = document.getElementById('controlnet-preprocessor-select');
const controlnetImageUpload = document.getElementById('controlnet-image-upload');
const controlnetImagePreviewWrap = document.getElementById('controlnet-image-preview-wrap');
const controlnetImagePreview = document.getElementById('controlnet-image-preview');
const controlnetImageName = document.getElementById('controlnet-image-name');
const controlnetImageClearBtn = document.getElementById('controlnet-image-clear');
const controlnetWeight = document.getElementById('controlnet-weight');
const controlnetWeightVal = document.getElementById('controlnet-weight-val');
const controlnetStart = document.getElementById('controlnet-start');
const controlnetStartVal = document.getElementById('controlnet-start-val');
const controlnetEnd = document.getElementById('controlnet-end');
const controlnetEndVal = document.getElementById('controlnet-end-val');
const imageSeed = document.getElementById('image-seed');
const imageRandomSeed = document.getElementById('image-random-seed');
const imageProfileSelect = document.getElementById('image-profile-select');
const imageProfileName = document.getElementById('image-profile-name');
const imageProfileSaveBtn = document.getElementById('image-profile-save');
const imageProfileApplyBtn = document.getElementById('image-profile-apply');
const imageProfileDeleteBtn = document.getElementById('image-profile-delete');
const imageProfileExportBtn = document.getElementById('image-profile-export');
const imageProfileImportBtn = document.getElementById('image-profile-import-btn');
const imageProfileImportInput = document.getElementById('image-profile-import-input');
const imageSteps = document.getElementById('image-steps');
const imageStepsVal = document.getElementById('image-steps-val');
const imageCfg = document.getElementById('image-cfg');
const imageCfgVal = document.getElementById('image-cfg-val');
const imageCfgLabelText = document.getElementById('image-cfg-label-text');
const imageCfgFluxHint = document.getElementById('image-cfg-flux-hint');
const fluxPromptTips = document.getElementById('flux-prompt-tips');
const imageDenoise = document.getElementById('image-denoise');
const imageDenoiseVal = document.getElementById('image-denoise-val');
const imageEngineStatus = document.getElementById('image-engine-status');
const imageForm = document.getElementById('image-form');
const promptSyntaxInfoBtn = document.getElementById('prompt-syntax-info-btn');
const promptSyntaxPopup = document.getElementById('prompt-syntax-popup');
const promptSyntaxCloseBtn = document.getElementById('prompt-syntax-close-btn');
const imagePrompt = document.getElementById('image-prompt');
const promptRandomizeBtn = document.getElementById('prompt-randomize-btn');
const promptRecentBtn = document.getElementById('prompt-recent-btn');
const promptRecentDropdown = document.getElementById('prompt-recent-dropdown');
const promptRecentChips = document.getElementById('prompt-recent-chips');
const promptRecentClearBtn = document.getElementById('prompt-recent-clear-btn');
const promptWeightUpBtn = document.getElementById('prompt-weight-up-btn');
const promptWeightDownBtn = document.getElementById('prompt-weight-down-btn');
const promptBreakWrapBtn = document.getElementById('prompt-break-wrap-btn');
const textPromptRecentBtn = document.getElementById('text-prompt-recent-btn');
const textPromptRecentDropdown = document.getElementById('text-prompt-recent-dropdown');
const textPromptRecentChips = document.getElementById('text-prompt-recent-chips');
const promptSavedName = document.getElementById('prompt-saved-name');
const promptSavedTags = document.getElementById('prompt-saved-tags');
const promptSaveBtn = document.getElementById('prompt-save-btn');
const promptSavedSelect = document.getElementById('prompt-saved-select');
const promptLoadBtn = document.getElementById('prompt-load-btn');
const promptDeleteSavedBtn = document.getElementById('prompt-delete-saved-btn');
const promptFavToggle = document.getElementById('prompt-fav-toggle');
const promptFavoritesOnlyToggle = document.getElementById('prompt-favorites-only-toggle');
const promptTagFilter = document.getElementById('prompt-tag-filter');
const promptPresetFilterStatus = document.getElementById('prompt-preset-filter-status');
const promptPresetClearFilters = document.getElementById('prompt-preset-clear-filters');
const promptPresetTagChips = document.getElementById('prompt-preset-tag-chips');
const promptPresetNotesPreview = document.getElementById('prompt-preset-notes-preview');
const promptEditPresetBtn = document.getElementById('prompt-edit-preset-btn');
const presetEditModal = document.getElementById('preset-edit-modal');
const presetEditModalClose = document.getElementById('preset-edit-modal-close');
const presetEditName = document.getElementById('preset-edit-name');
const presetEditText = document.getElementById('preset-edit-text');
const presetEditTags = document.getElementById('preset-edit-tags');
const presetEditNotes = document.getElementById('preset-edit-notes');
const presetEditCreated = document.getElementById('preset-edit-created');
const presetEditSave = document.getElementById('preset-edit-save');
const presetEditCancel = document.getElementById('preset-edit-cancel');
const presetEditDelete = document.getElementById('preset-edit-delete');
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
const negativePromptDefaultBtn = document.getElementById('negative-prompt-default-btn');
const imageNegativePrompt = document.getElementById('image-negative-prompt');
const imageNegativePromptSection = document.getElementById('image-negative-prompt-section');
const fluxNoNegHint = document.getElementById('flux-no-neg-hint');
const fluxSamplerHint = document.getElementById('flux-sampler-hint');
const hiresfixEnable = document.getElementById('hiresfix-enable');
const hiresfixPanel = document.getElementById('hiresfix-panel');
const hiresfixUpscalerSelect = document.getElementById('hiresfix-upscaler-select');
const hiresfixScale = document.getElementById('hiresfix-scale');
const hiresfixSteps = document.getElementById('hiresfix-steps');
const hiresfixDenoise = document.getElementById('hiresfix-denoise');
const hiresfixDenoiseVal = document.getElementById('hiresfix-denoise-val');
const img2imgDropZone = document.getElementById('img2img-drop-zone');
const img2imgDropHint = document.getElementById('img2img-drop-hint');
const imageWidth = document.getElementById('image-width');
const imageHeight = document.getElementById('image-height');
const imageBatchSize = document.getElementById('image-batch-size');
const imageUpload = document.getElementById('image-upload');
const imageGenerateBtn = document.getElementById('image-generate-btn');
const queueTelemetry = document.getElementById('queue-telemetry');
const queueTelemetryResetBtn = document.getElementById('queue-telemetry-reset');
const queueHelpDetails = document.getElementById('queue-help-details');
const queueRestoreWrap = document.getElementById('queue-restore-wrap');
const queueRestoreHint = document.getElementById('queue-restore-hint');
const queueRestoreHideBtn = document.getElementById('queue-restore-hide');
const queueRestoreShowBtn = document.getElementById('queue-restore-show');
const queueLastAction = document.getElementById('queue-last-action');
const queueLastActionPinBtn = document.getElementById('queue-last-action-pin');
const queueSummary = document.getElementById('queue-summary');
const queueList = document.getElementById('queue-list');
const configOllamaPath = document.getElementById('config-ollama-path');
const configComfyuiPath = document.getElementById('config-comfyui-path');
const configModelsPath = document.getElementById('config-models-path');
const configCivitaiKey = document.getElementById('config-civitai-key');
const configHuggingfaceKey = document.getElementById('config-huggingface-key');
const configDefaultNegPrompt = document.getElementById('config-default-negative-prompt');
const configOllamaBrowseBtn = document.getElementById('config-ollama-browse');
const configComfyuiBrowseBtn = document.getElementById('config-comfyui-browse');
const configModelsBrowseBtn = document.getElementById('config-models-browse');
const configSaveBtn = document.getElementById('config-save-btn');
const configModelsMigrateBtn = document.getElementById('config-models-migrate-btn');
const configSaveStatus = document.getElementById('config-save-status');
const configLastSaved = document.getElementById('config-last-saved');
const configOllamaStartBtn = document.getElementById('config-ollama-start');
const configOllamaRestartBtn = document.getElementById('config-ollama-restart');
const configOllamaStopBtn = document.getElementById('config-ollama-stop');
const configComfyStartBtn = document.getElementById('config-comfy-start');
const configComfyRestartBtn = document.getElementById('config-comfy-restart');
const configComfyStopBtn = document.getElementById('config-comfy-stop');
const configComfyCheckUpdatesBtn = document.getElementById('config-comfy-check-updates');
const configComfyUpdateBtn = document.getElementById('config-comfy-update');
const configComfyVersionInfo = document.getElementById('config-comfy-version-info');
const configComfyNodesSearchInput = document.getElementById('config-comfy-nodes-search');
const configComfyNodesIncludeBuiltinsToggle = document.getElementById('config-comfy-nodes-include-builtins');
const configComfyNodesRefreshBtn = document.getElementById('config-comfy-nodes-refresh');
const configComfyNodesStatus = document.getElementById('config-comfy-nodes-status');
const configComfyNodesList = document.getElementById('config-comfy-nodes-list');
const configComfyPackagesStatus = document.getElementById('config-comfy-packages-status');
const configComfyPackagesUpdateAllBtn = document.getElementById('config-comfy-packages-update-all');
const configComfyPackagesPreviewDisableNonCoreBtn = document.getElementById('config-comfy-packages-preview-disable-noncore');
const configComfyPackagesDisableNonCoreBtn = document.getElementById('config-comfy-packages-disable-noncore');
const configComfyDisablePreview = document.getElementById('config-comfy-disable-preview');
const configComfyDisablePreviewSummary = document.getElementById('config-comfy-disable-preview-summary');
const configComfyDisablePreviewFilter = document.getElementById('config-comfy-disable-preview-filter');
const configComfyDisablePreviewSelectedOnly = document.getElementById('config-comfy-disable-preview-selected-only');
const configComfyDisablePreviewSelectAllBtn = document.getElementById('config-comfy-disable-preview-select-all');
const configComfyDisablePreviewSelectVisibleBtn = document.getElementById('config-comfy-disable-preview-select-visible');
const configComfyDisablePreviewInvertBtn = document.getElementById('config-comfy-disable-preview-invert');
const configComfyDisablePreviewClearVisibleBtn = document.getElementById('config-comfy-disable-preview-clear-visible');
const configComfyDisablePreviewClearBtn = document.getElementById('config-comfy-disable-preview-clear');
const configComfyDisablePreviewCopySelectedBtn = document.getElementById('config-comfy-disable-preview-copy-selected');
const configComfyDisablePreviewCopyCsvBtn = document.getElementById('config-comfy-disable-preview-copy-csv');
const configComfyDisablePreviewDownloadSelectedBtn = document.getElementById('config-comfy-disable-preview-download-selected');
const configComfyDisablePreviewDownloadCsvBtn = document.getElementById('config-comfy-disable-preview-download-csv');
const configComfyDisablePreviewDownloadJsonBtn = document.getElementById('config-comfy-disable-preview-download-json');
const configComfyDisablePreviewResetPrefsBtn = document.getElementById('config-comfy-disable-preview-reset-prefs');
const configComfyDisablePreviewExportStatus = document.getElementById('config-comfy-disable-preview-export-status');
const configComfyDisablePreviewExportHistoryCopyBtn = document.getElementById('config-comfy-disable-preview-export-history-copy');
const configComfyDisablePreviewExportHistoryCopyJsonBtn = document.getElementById('config-comfy-disable-preview-export-history-copy-json');
const configComfyDisablePreviewExportHistoryDownloadBtn = document.getElementById('config-comfy-disable-preview-export-history-download');
const configComfyDisablePreviewExportHistoryDownloadCsvBtn = document.getElementById('config-comfy-disable-preview-export-history-download-csv');
const configComfyDisablePreviewExportHistoryDownloadJsonBtn = document.getElementById('config-comfy-disable-preview-export-history-download-json');
const configComfyDisablePreviewExportHistoryClearBtn = document.getElementById('config-comfy-disable-preview-export-history-clear');
const configComfyDisablePreviewExportHistoryMeta = document.getElementById('config-comfy-disable-preview-export-history-meta');
const configComfyDisablePreviewExportHistory = document.getElementById('config-comfy-disable-preview-export-history');
const configComfyDisablePreviewList = document.getElementById('config-comfy-disable-preview-list');
const configComfyDisablePreviewConfirmBtn = document.getElementById('config-comfy-disable-preview-confirm');
const configComfyPackagesList = document.getElementById('config-comfy-packages-list');
const configComfyPackageDetails = document.getElementById('config-comfy-package-details');
const configComfyDisableLogRefreshBtn = document.getElementById('config-comfy-disable-log-refresh');
const configComfyDisableLogRevertLastBtn = document.getElementById('config-comfy-disable-log-revert-last');
const configComfyDisableLogPendingOnlyToggle = document.getElementById('config-comfy-disable-log-pending-only');
const configComfyDisableLogStatus = document.getElementById('config-comfy-disable-log-status');
const configComfyDisableLogList = document.getElementById('config-comfy-disable-log-list');
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
const diagCopyBtn = document.getElementById('diag-copy-btn');
const diagnosticsRunBtn = document.getElementById('diagnostics-run-btn');
const diagWsRetryBtn = document.getElementById('diag-ws-retry-btn');
const diagDisableLogRepairBtn = document.getElementById('diag-disable-log-repair-btn');
const diagClearRepairStatusBtn = document.getElementById('diag-clear-repair-status-btn');
const diagnosticsSummary = document.getElementById('diagnostics-summary');
const diagnosticsHint = document.getElementById('diagnostics-hint');
const diagTextStatus = document.getElementById('diag-text-status');
const diagImageStatus = document.getElementById('diag-image-status');
const diagCheckpoints = document.getElementById('diag-checkpoints');
const diagSamplers = document.getElementById('diag-samplers');
const diagBackendHealth = document.getElementById('diag-backend-health');
const diagDisableLogHealth = document.getElementById('diag-disable-log-health');
const diagFrontendBuild = document.getElementById('diag-frontend-build');
const diagLastRun = document.getElementById('diag-last-run');
const diagRepairStatus = document.getElementById('diag-repair-status');
const pollOwnerStatus = document.getElementById('poll-owner-status');
const wsTransportStatus = document.getElementById('ws-transport-status');
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
const queueUiResetBtn = document.getElementById('queue-ui-reset');
const toastContainer = document.getElementById('toast-container');

if (queueSummary) {
	queueSummary.setAttribute('aria-live', 'polite');
}
if (queueLastAction) {
	queueLastAction.setAttribute('aria-atomic', 'true');
}
const refreshGalleryBtn = document.getElementById('refresh-gallery');
const galleryGrid = document.getElementById('gallery-grid');
const galleryLightbox = document.getElementById('gallery-lightbox');
const galleryLightboxImage = document.getElementById('gallery-lightbox-image');
const galleryLightboxCaption = document.getElementById('gallery-lightbox-caption');
const galleryLightboxCloseBtn = document.getElementById('gallery-lightbox-close');
const galleryLightboxMetaToggle = document.getElementById('gallery-lightbox-meta-toggle');
const galleryLightboxMeta = document.getElementById('gallery-lightbox-meta');
const galleryLightboxMetaChips = document.getElementById('gallery-lightbox-meta-chips');
const galleryLightboxStats = document.getElementById('gallery-lightbox-stats');
const galleryLightboxReuseBtn = document.getElementById('gallery-lightbox-reuse');
const galleryLightboxCompareToggle = document.getElementById('gallery-lightbox-compare-toggle');
const galleryLightboxSourceUploadInput = document.getElementById('gallery-lightbox-source-upload');
const galleryLightboxCompare = document.getElementById('gallery-lightbox-compare');
const galleryLightboxBeforeImage = document.getElementById('gallery-lightbox-before-image');
const galleryLightboxAfterWrap = document.getElementById('gallery-lightbox-after-wrap');
const galleryLightboxAfterImage = document.getElementById('gallery-lightbox-after-image');
const galleryLightboxCompareSlider = document.getElementById('gallery-lightbox-compare-slider');
const galleryContextMenu = document.getElementById('gallery-context-menu');
const gallerySearch = document.getElementById('gallery-search');
const gallerySortSelect = document.getElementById('gallery-sort');
const galleryModeFilterSelect = document.getElementById('gallery-mode-filter');
const galleryTagFilterSelect = document.getElementById('gallery-tag-filter');
const galleryLightboxStarBtn = document.getElementById('gallery-lightbox-star');
const galleryViewToggle = document.getElementById('gallery-view-toggle');
const gallerySelectModeBtn = document.getElementById('gallery-select-mode-btn');
const gallerySelectToolbar = document.getElementById('gallery-select-toolbar');
const gallerySelectCountEl = document.getElementById('gallery-select-count');
const gallerySelectAllBtn = document.getElementById('gallery-select-all-btn');
const galleryBulkDeleteBtn = document.getElementById('gallery-bulk-delete-btn');
const galleryBulkExportBtn = document.getElementById('gallery-bulk-export-btn');
const galleryDeselectAllBtn = document.getElementById('gallery-deselect-all-btn');
const galleryFilterHint = document.getElementById('gallery-filter-hint');
const galleryLightboxPrev = document.getElementById('gallery-lightbox-prev');
const galleryLightboxNext = document.getElementById('gallery-lightbox-next');
const galleryLightboxCounter = document.getElementById('gallery-lightbox-counter');
const galleryLightboxTagInput = document.getElementById('gallery-lightbox-tag-input');
const galleryLightboxAddTagBtn = document.getElementById('gallery-lightbox-add-tag-btn');
const galleryLightboxTags = document.getElementById('gallery-lightbox-tags');
const imagePresetButtons = document.querySelectorAll('[data-image-preset]');
const previewUpdated = document.getElementById('preview-updated');
const previewTransportBadge = document.getElementById('preview-transport-badge');
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
const QUEUE_POLL_INTERVAL_MS = 1200;
let livePreviewTimer = null;
let statusPollTimer = null;
let pollLeaseTimer = null;
const trackedPromptIds = new Set();
const pendingImageJobs = new Map();
const queueJobMeta = new Map();
let enhancedPromptSuggestions = [];
const JOB_MISS_THRESHOLD = 4;
const HISTORY_PERSIST_PENDING_REASON = 'Waiting to persist history entry.';
const queueActionInFlight = new Set();
const QUEUE_STATE_STORAGE_KEY = 'queueStateV1';
const QUEUE_RESTORE_HINT_HIDDEN_KEY = 'queueRestoreHintHiddenV1';
const QUEUE_HELP_EXPANDED_KEY = 'queueHelpExpandedV1';
const QUEUE_TELEMETRY_KEY = 'queueTelemetryV1';
const QUEUE_LAST_ACTION_PINNED_KEY = 'queueLastActionPinnedV1';
const QUEUE_LAST_ACTION_MAX_AGE_MS = 120000;
const DIAG_DRAWER_COLLAPSED_KEY = 'diagDrawerCollapsedV1';
const DIAG_COMMAND_HISTORY_KEY = 'diagCommandHistoryV1';
const DIAG_REPAIR_STATUS_KEY = 'diagRepairStatusV1';
const SIDEBAR_SECTION_COLLAPSE_KEY = 'imageSidebarSectionCollapseV1';
const diagDrawerCollapsedStored = localStorage.getItem(DIAG_DRAWER_COLLAPSED_KEY);
const diagRepairStatusStored = localStorage.getItem(DIAG_REPAIR_STATUS_KEY) || '';
let queueFilterFailedOnly = localStorage.getItem('queueFilterFailedOnly') === '1';
let restoredQueueStateInfo = null;
let queueRestoreHintTimer = null;
let queueLastActionInfo = null;
let queueLastActionTimer = null;
let queueLastActionPinned = localStorage.getItem(QUEUE_LAST_ACTION_PINNED_KEY) === '1';
let queueRestoreHintHidden = localStorage.getItem(QUEUE_RESTORE_HINT_HIDDEN_KEY) === '1';
let diagDrawerCollapsed = diagDrawerCollapsedStored === null ? null : diagDrawerCollapsedStored === '1';
const IMAGE_PROFILE_STORAGE_KEY = 'imagePresetProfilesV1';
const IMAGE_PROFILE_SELECTED_KEY = 'imagePresetProfilesSelectedV1';
const MB_MODEL_NOTES_KEY = 'mbModelNotesV1';
const GALLERY_FAVORITES_KEY = 'galleryFavoritesV1';
const GALLERY_TAGS_KEY = 'galleryTagsV1';
const GALLERY_TAG_FILTER_KEY = 'galleryTagFilterV1';
let mbCurrentModelNoteKey = '';
const IMAGE_RECENT_MODELS_KEY = 'imageRecentModelsV1';
const IMAGE_FAVORITE_MODELS_KEY = 'imageFavoriteModelsV1';
const IMAGE_MODEL_FILTER_MODE_KEY = 'imageModelFilterModeV1';
const IMAGE_MODEL_FAMILY_MODE_KEY = 'imageModelFamilyModeV1';
const IMAGE_SAMPLER_FILTER_QUERY_KEY = 'imageSamplerFilterQueryV1';
const IMAGE_SCHEDULER_FILTER_QUERY_KEY = 'imageSchedulerFilterQueryV1';
const IMAGE_FLUX_AUTO_APPLY_RECOMMENDATION_KEY = 'imageFluxAutoApplyRecommendationV1';
const IMAGE_FLUX_LOCK_RECOMMENDATION_KEY = 'imageFluxLockRecommendationV1';
const CONFIG_COMFY_NODES_INCLUDE_BUILTINS_KEY = 'configComfyNodesIncludeBuiltinsV1';
const CONFIG_COMFY_DISABLE_PREVIEW_FILTER_KEY = 'configComfyDisablePreviewFilterV1';
const CONFIG_COMFY_DISABLE_PREVIEW_SELECTED_ONLY_KEY = 'configComfyDisablePreviewSelectedOnlyV1';
const CONFIG_COMFY_DISABLE_PREVIEW_LAST_EXPORT_KEY = 'configComfyDisablePreviewLastExportV1';
const CONFIG_COMFY_DISABLE_PREVIEW_EXPORT_HISTORY_KEY = 'configComfyDisablePreviewExportHistoryV1';
const CONFIG_COMFY_DISABLE_PREVIEW_EXPORT_HISTORY_MAX = 5;
const CONFIG_COMFY_DISABLE_LOG_PENDING_ONLY_KEY = 'configComfyDisableLogPendingOnlyV1';
const QUEUE_STATE_MAX_ITEMS = 40;
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
let imageModelAllOptions = [];
let imageModelDetailsByName = new Map();
let imageModelFilterMode = localStorage.getItem(IMAGE_MODEL_FILTER_MODE_KEY) || 'all';
if (!['all', 'recent', 'favorites'].includes(imageModelFilterMode)) {
	imageModelFilterMode = 'all';
}
let imageModelFamilyMode = localStorage.getItem(IMAGE_MODEL_FAMILY_MODE_KEY) || 'auto';
if (!['auto', 'sd', 'flux'].includes(imageModelFamilyMode)) {
	imageModelFamilyMode = 'auto';
}
let imageFluxAutoApplyRecommendation = localStorage.getItem(IMAGE_FLUX_AUTO_APPLY_RECOMMENDATION_KEY) === '1';
let imageFluxLockRecommendation = localStorage.getItem(IMAGE_FLUX_LOCK_RECOMMENDATION_KEY) === '1';
let imageFluxLockBypassOnce = false;
let lastAutoRecommendationModelKey = '';
let activeImagePreset = '';
let lastResolvedPresetFamily = '';
let comfyCustomNodeRows = [];
let comfyCustomNodePackages = [];
let comfyCustomNodeIncludeBuiltins = localStorage.getItem(CONFIG_COMFY_NODES_INCLUDE_BUILTINS_KEY) === '1';
let comfySelectedPackageName = '';
let comfyDisablePreviewReady = false;
let comfyDisablePreviewSelectedNames = new Set();
let comfyDisablePreviewFilterQuery = localStorage.getItem(CONFIG_COMFY_DISABLE_PREVIEW_FILTER_KEY) || '';
let comfyDisablePreviewSelectedOnlyPref = localStorage.getItem(CONFIG_COMFY_DISABLE_PREVIEW_SELECTED_ONLY_KEY) === '1';
let comfyDisablePreviewStats = { wouldDisable: 0, skipped: 0, failed: 0 };
let comfyDisablePreviewLastExport = localStorage.getItem(CONFIG_COMFY_DISABLE_PREVIEW_LAST_EXPORT_KEY) || '';
let comfyDisableLogPendingOnly = localStorage.getItem(CONFIG_COMFY_DISABLE_LOG_PENDING_ONLY_KEY) === '1';
const comfyDisableLogRevertInFlight = new Set();
let comfyDisableLogRevertLastInFlight = false;
let comfyDisablePreviewExportHistory = (() => {
	try {
		const parsed = JSON.parse(localStorage.getItem(CONFIG_COMFY_DISABLE_PREVIEW_EXPORT_HISTORY_KEY) || '[]');
		return Array.isArray(parsed) ? parsed.filter((item) => typeof item === 'string' && item.trim()).slice(0, CONFIG_COMFY_DISABLE_PREVIEW_EXPORT_HISTORY_MAX) : [];
	} catch {
		return [];
	}
})();
const IMAGE_FAMILY_CAPABILITIES = {
	sd: {
		supports_refiner: true,
		supports_vae: true,
		supports_controlnet: true,
		supports_hiresfix: true,
		cfg_min: 1,
		cfg_max: 30,
		cfg_default: 7,
	},
	flux: {
		supports_refiner: false,
		supports_vae: false,
		supports_controlnet: false,
		supports_hiresfix: false,
		cfg_min: 1,
		cfg_max: 10,
		cfg_default: 3.5,
	},
};
let currentGalleryImages = [];
let currentFullHistory = [];
let galleryViewMode = localStorage.getItem('galleryViewMode') || 'list';
const GALLERY_HISTORY_LIMIT = 240;
const GALLERY_EAGER_IMAGE_COUNT = 6;
const GALLERY_RENDER_CHUNK_SIZE = 24;
const GALLERY_VIRTUALIZE_THRESHOLD = 120;
const GALLERY_VIRTUAL_OVERSCAN_ROWS = 3;
const GALLERY_LIST_EST_CARD_HEIGHT = 280;
const GALLERY_GRID_EST_CARD_HEIGHT = 230;
const GALLERY_GRID_MIN_COL_WIDTH = 148;
let galleryLoadController = null;
let galleryLoadSeq = 0;
let galleryRenderSeq = 0;
let galleryVirtualState = null;
let galleryVirtualRaf = null;
const img2imgSourceResolveCache = new Map();
let controlnetPreviewObjectUrl = '';
const GALLERY_SEARCH_QUERY_KEY = 'gallerySearchQueryV1';
let gallerySearchQuery = localStorage.getItem(GALLERY_SEARCH_QUERY_KEY) || '';
let gallerySortOrder = localStorage.getItem('gallerySortOrder') || 'newest';
let galleryModeFilter = localStorage.getItem('galleryModeFilter') || 'all';
let galleryTagFilter = localStorage.getItem(GALLERY_TAG_FILTER_KEY) || 'all';
const VALID_GALLERY_SORT_ORDERS = new Set(['newest', 'oldest', 'favorites-first']);
if (!VALID_GALLERY_SORT_ORDERS.has(gallerySortOrder)) {
	gallerySortOrder = 'newest';
}

function normalizeGalleryTag(rawTag) {
	return String(rawTag || '').trim().toLowerCase().slice(0, 40);
}

function loadGalleryTagsByEntry() {
	try {
		const parsed = JSON.parse(localStorage.getItem(GALLERY_TAGS_KEY) || '{}');
		if (!parsed || typeof parsed !== 'object') return {};
		return parsed;
	} catch {
		return {};
	}
}

function saveGalleryTagsByEntry(tagMap) {
	localStorage.setItem(GALLERY_TAGS_KEY, JSON.stringify(tagMap || {}));
}

function getGalleryEntryTagKey(entry) {
	return String(entry?.id || entry?.params?.prompt_id || '').trim();
}

function getGalleryTags(entry) {
	const key = getGalleryEntryTagKey(entry);
	if (!key) return [];
	const tagMap = loadGalleryTagsByEntry();
	const tags = Array.isArray(tagMap[key]) ? tagMap[key] : [];
	return tags.map((t) => normalizeGalleryTag(t)).filter(Boolean);
}

function setGalleryTags(entry, tags) {
	const key = getGalleryEntryTagKey(entry);
	if (!key) return [];
	const normalized = [...new Set((tags || []).map((t) => normalizeGalleryTag(t)).filter(Boolean))].slice(0, 12);
	const tagMap = loadGalleryTagsByEntry();
	if (!normalized.length) {
		delete tagMap[key];
	} else {
		tagMap[key] = normalized;
	}
	saveGalleryTagsByEntry(tagMap);
	return normalized;
}

function getAllGalleryTagsFromImages(images) {
	const tagSet = new Set();
	(images || []).forEach((entry) => {
		getGalleryTags(entry).forEach((tag) => tagSet.add(tag));
	});
	return [...tagSet].sort((a, b) => a.localeCompare(b));
}

function syncGalleryTagFilterOptions(images) {
	if (!galleryTagFilterSelect) return;
	const tags = getAllGalleryTagsFromImages(images);
	let html = '<option value="all">All tags</option>';
	tags.forEach((tag) => {
		html += `<option value="${escHtml(tag)}">#${escHtml(tag)}</option>`;
	});
	galleryTagFilterSelect.innerHTML = html;
	if (galleryTagFilter !== 'all' && !tags.includes(galleryTagFilter)) {
		galleryTagFilter = 'all';
		localStorage.removeItem(GALLERY_TAG_FILTER_KEY);
	}
	galleryTagFilterSelect.value = galleryTagFilter;
}
let gallerySelectMode = false;
const gallerySelectedIds = new Set();
let galleryLastSelectedIndex = -1;
let lightboxCurrentIndex = 0;
let lightboxCompareEnabled = false;
let lightboxCompareSplit = 50;
let lightboxMetaOpen = false;
let galleryLightboxLastFocus = null;
let promptSyntaxLastFocus = null;
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
let imageSidebarSectionCollapseState = getSidebarSectionCollapseState();

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

function getDiagnosticsCommandHistoryState() {
	try {
		const parsed = JSON.parse(sessionStorage.getItem(DIAG_COMMAND_HISTORY_KEY) || '[]');
		if (!Array.isArray(parsed)) return [];
		return parsed
			.map((entry) => String(entry || '').trim())
			.filter(Boolean)
			.slice(-50);
	} catch {
		return [];
	}
}

function getSidebarSectionCollapseState() {
	try {
		const parsed = JSON.parse(localStorage.getItem(SIDEBAR_SECTION_COLLAPSE_KEY) || '{}');
		if (!parsed || Array.isArray(parsed) || typeof parsed !== 'object') return {};
		return parsed;
	} catch {
		return {};
	}
}

function persistSidebarSectionCollapseState() {
	try {
		localStorage.setItem(SIDEBAR_SECTION_COLLAPSE_KEY, JSON.stringify(imageSidebarSectionCollapseState));
	} catch {
		// best-effort persistence only
	}
}

function toSidebarSectionKey(label, index) {
	const slug = String(label || '')
		.toLowerCase()
		.replace(/[^a-z0-9]+/g, '-')
		.replace(/^-+|-+$/g, '');
	return slug ? `image:${slug}` : `image:section-${index}`;
}

function getSidebarSectionLabel(section, index) {
	const direct = section.querySelector(':scope > .field-label, :scope > label.field-label');
	if (direct?.textContent) return direct.textContent.trim();
	const nested = section.querySelector(':scope > .model-stack-head .field-label, :scope > .diagnostics-head .field-label, :scope > .cn-panel > summary.field-label');
	if (nested?.textContent) return nested.textContent.trim();
	return `Section ${index + 1}`;
}

function syncSidebarSectionCollapsedState(section, toggleBtn, isCollapsed) {
	const label = section.dataset.sidebarSectionLabel || 'section';
	section.classList.toggle('is-collapsed', isCollapsed);
	section.setAttribute('data-collapsed', isCollapsed ? '1' : '0');
	toggleBtn.textContent = isCollapsed ? 'Show' : 'Hide';
	toggleBtn.setAttribute('aria-expanded', isCollapsed ? 'false' : 'true');
	toggleBtn.setAttribute('aria-label', `${isCollapsed ? 'Expand' : 'Collapse'} ${label}`);
	toggleBtn.title = `${isCollapsed ? 'Expand' : 'Collapse'} ${label}`;
}

function setupImageSidebarSectionCollapse() {
	const imageSidebar = document.querySelector('#panel-image .sidebar');
	if (!imageSidebar) return;
	const sections = [...imageSidebar.querySelectorAll(':scope > .sidebar-section')];
	sections.forEach((section, index) => {
		if (section.classList.contains('sidebar-section-collapse-ready')) return;
		let header = section.querySelector(':scope > .model-stack-head, :scope > .diagnostics-head');
		const directTitle = section.querySelector(':scope > .field-label, :scope > label.field-label');
		if (!header) {
			header = document.createElement('div');
			header.className = 'sidebar-section-head';
			if (directTitle) {
				header.appendChild(directTitle);
			}
			section.insertBefore(header, section.firstElementChild);
		} else {
			header.classList.add('sidebar-section-head');
		}

		const label = getSidebarSectionLabel(section, index);
		section.dataset.sidebarSectionLabel = label;
		const key = section.dataset.sidebarSectionKey || toSidebarSectionKey(label, index);
		section.dataset.sidebarSectionKey = key;

		const toggleBtn = document.createElement('button');
		toggleBtn.type = 'button';
		toggleBtn.className = 'btn btn-ghost btn-xs sidebar-section-toggle';
		header.appendChild(toggleBtn);

		const collapsedStored = imageSidebarSectionCollapseState[key] === 1 || imageSidebarSectionCollapseState[key] === true;
		syncSidebarSectionCollapsedState(section, toggleBtn, collapsedStored);

		toggleBtn.addEventListener('click', () => {
			const nextCollapsed = !section.classList.contains('is-collapsed');
			syncSidebarSectionCollapsedState(section, toggleBtn, nextCollapsed);
			imageSidebarSectionCollapseState[key] = nextCollapsed ? 1 : 0;
			persistSidebarSectionCollapseState();
		});

		section.classList.add('sidebar-section-collapse-ready');
	});
}

let queueTelemetryState = getQueueTelemetryState();
let lastDiagnosticsLogKey = '';
const diagHistory = getDiagnosticsCommandHistoryState();
let diagHistoryIndex = -1;
let diagHistoryDraft = '';
let diagDrawerLastFocus = null;
const DIAGNOSTICS_COMMAND_SUGGESTIONS = [
	'help', 'status', 'ws-status', 'ws-retry', 'checks', 'logs', 'queue', 'poll', 'clear',
	'h', '?', 'q', 'p', 'ws', 'retry', 'cls',
];

function appendDiagnosticsConsoleLine(text, level = 'info') {
	if (!diagDrawerOutput) return;
	const now = new Date();
	const ts = now.toTimeString().slice(0, 8);
	const row = document.createElement('p');
	row.className = `diag-line ${level}`.trim();
	row.textContent = `[${ts}] ${text}`;
	diagDrawerOutput.appendChild(row);
	while (diagDrawerOutput.childElementCount > 250) {
		diagDrawerOutput.removeChild(diagDrawerOutput.firstChild);
	}
	diagDrawerOutput.scrollTop = diagDrawerOutput.scrollHeight;
}

function setDiagnosticsDrawerOpen(isOpen) {
	if (!diagDrawer) return;
	if (isOpen) {
		diagDrawerLastFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
	}
	diagDrawer.hidden = !isOpen;
	diagDrawer.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
	diagDrawerCollapsed = !isOpen;
	if (diagDrawerCollapsed) {
		localStorage.setItem(DIAG_DRAWER_COLLAPSED_KEY, '1');
	} else {
		localStorage.setItem(DIAG_DRAWER_COLLAPSED_KEY, '0');
	}
	if (diagDrawerToggle) {
		diagDrawerToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
	}
	if (isOpen && diagDrawerCommandInput) {
		diagDrawerCommandInput.focus();
		return;
	}
	if (!isOpen) {
		const active = document.activeElement;
		if (active instanceof HTMLElement && diagDrawer.contains(active) && diagDrawerToggle) {
			diagDrawerToggle.focus();
			return;
		}
		if (diagDrawerLastFocus && document.contains(diagDrawerLastFocus)) {
			diagDrawerLastFocus.focus();
		}
	}
}

function getDiagnosticsStatusSnapshotText() {
	const text = diagTextStatus?.textContent || 'unknown';
	const image = diagImageStatus?.textContent || 'unknown';
	const checkpoints = diagCheckpoints?.textContent || '-';
	const samplers = diagSamplers?.textContent || '-';
	const backend = diagBackendHealth?.textContent || 'unknown';
	const disableLog = diagDisableLogHealth?.textContent || 'unknown';
	const frontend = diagFrontendBuild?.textContent || 'unknown';
	const summary = diagnosticsSummary?.textContent || 'Diagnostics unavailable';
	return `${summary} | text=${text} image=${image} checkpoints=${checkpoints} samplers=${samplers} backend=${backend} disable-log=${disableLog} frontend=${frontend}`;
}

async function copyTextToClipboard(text) {
	const value = String(text || '');
	if (navigator.clipboard?.writeText) {
		await navigator.clipboard.writeText(value);
		return;
	}
	const textarea = document.createElement('textarea');
	textarea.value = value;
	textarea.setAttribute('readonly', 'readonly');
	textarea.style.position = 'fixed';
	textarea.style.opacity = '0';
	textarea.style.pointerEvents = 'none';
	document.body.appendChild(textarea);
	textarea.select();
	textarea.setSelectionRange(0, textarea.value.length);
	const copied = document.execCommand('copy');
	document.body.removeChild(textarea);
	if (!copied) {
		throw new Error('Copy command failed.');
	}
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

async function repairDisableLogStore() {
	if (diagDisableLogRepairBtn) diagDisableLogRepairBtn.disabled = true;
	try {
		const res = await fetch('/api/diagnostics/repair-disable-log', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
		});
		const data = await res.json().catch(() => ({}));
		if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
		const status = String(data.status || 'ok');
		const source = String(data.source || 'unknown');
		const count = Number(data.count || 0);
		setDiagRepairStatusLine(withDiagStatusTimestamp(`Last repair: ${status} (${count}) via ${source}.`));
		appendDiagnosticsConsoleLine(`Disable log repair: ${status} (${count}) via ${source}.`, status === 'ok' ? 'info' : 'warn');
		showToast(`Disable log repair: ${status} (${count}).`, 'pos');
		await runDiagnosticsChecks(false);
	} catch (err) {
		setDiagRepairStatusLine(withDiagStatusTimestamp(`Last repair: failed (${err.message}).`));
		appendDiagnosticsConsoleLine(`Disable log repair failed: ${err.message}`, 'error');
		showToast('Disable log repair failed.', 'neg');
	} finally {
		if (diagDisableLogRepairBtn) diagDisableLogRepairBtn.disabled = false;
	}
}

async function runDiagnosticsConsoleCommand(rawInput) {
	const command = rawInput.trim().toLowerCase();
	if (!command) return;
	const commandAliases = {
		h: 'help',
		'?': 'help',
		q: 'queue',
		p: 'poll',
		ws: 'ws-status',
		retry: 'ws-retry',
		cls: 'clear',
	};
	const normalizedCommand = commandAliases[command] || command;
	appendDiagnosticsConsoleLine(`$ ${rawInput}`, 'command');

	if (normalizedCommand === 'help') {
		appendDiagnosticsConsoleLine('Commands: help, status, ws-status, ws-retry, checks, logs, queue, poll, clear');
		appendDiagnosticsConsoleLine('Aliases: h/?=help, q=queue, p=poll, ws=ws-status, retry=ws-retry, cls=clear');
		return;
	}
	if (normalizedCommand === 'status') {
		appendDiagnosticsConsoleLine(getDiagnosticsStatusSnapshotText());
		return;
	}
	if (normalizedCommand === 'ws-status') {
		appendDiagnosticsConsoleLine(wsTransportStatus?.textContent || 'Preview transport status unavailable');
		return;
	}
	if (normalizedCommand === 'ws-retry') {
		const attempted = forceRetryComfyWebSocket('diagnostics console');
		appendDiagnosticsConsoleLine(attempted ? 'Triggered ComfyUI websocket retry attempt.' : 'ComfyUI websocket already connected.');
		return;
	}
	if (normalizedCommand === 'queue') {
		appendDiagnosticsConsoleLine(queueSummary?.textContent || 'Queue summary unavailable');
		return;
	}
	if (normalizedCommand === 'poll') {
		appendDiagnosticsConsoleLine(pollOwnerStatus?.textContent || 'Poll owner status unavailable');
		return;
	}
	if (normalizedCommand === 'clear') {
		if (diagDrawerOutput) diagDrawerOutput.innerHTML = '';
		appendDiagnosticsConsoleLine('Console cleared.');
		return;
	}
	if (normalizedCommand === 'checks') {
		appendDiagnosticsConsoleLine('Running diagnostics checks...');
		await runDiagnosticsChecks(true);
		appendDiagnosticsConsoleLine(getDiagnosticsStatusSnapshotText());
		return;
	}
	if (normalizedCommand === 'logs') {
		appendDiagnosticsConsoleLine('Fetching ComfyUI logs...');
		await appendServiceDiagnosticLogs('comfyui');
		return;
	}

	const suggestions = DIAGNOSTICS_COMMAND_SUGGESTIONS
		.filter((candidate) => candidate.startsWith(command) || candidate.includes(command))
		.slice(0, 4);
	if (suggestions.length) {
		appendDiagnosticsConsoleLine(`Unknown command: ${command}. Try: ${suggestions.join(', ')}`, 'warn');
		return;
	}
	appendDiagnosticsConsoleLine(`Unknown command: ${command}. Type help for commands.`, 'warn');
}

function persistQueueTelemetryState() {
	sessionStorage.setItem(QUEUE_TELEMETRY_KEY, JSON.stringify(queueTelemetryState));
}

function persistDiagnosticsCommandHistoryState() {
	sessionStorage.setItem(DIAG_COMMAND_HISTORY_KEY, JSON.stringify(diagHistory.slice(-50)));
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

function stopQueueRestoreHintTicker() {
	if (!queueRestoreHintTimer) return;
	window.clearInterval(queueRestoreHintTimer);
	queueRestoreHintTimer = null;
}

function ensureQueueRestoreHintTicker() {
	if (queueRestoreHintTimer) return;
	queueRestoreHintTimer = window.setInterval(() => {
		renderQueueRestoreHint();
	}, 1000);
}

function stopQueueLastActionTicker() {
	if (!queueLastActionTimer) return;
	window.clearInterval(queueLastActionTimer);
	queueLastActionTimer = null;
}

function ensureQueueLastActionTicker() {
	if (queueLastActionTimer) return;
	queueLastActionTimer = window.setInterval(() => {
		renderQueueLastAction();
	}, 1000);
}

function syncQueueLastActionPinButton() {
	if (!queueLastActionPinBtn) return;
	queueLastActionPinBtn.textContent = queueLastActionPinned ? 'Unpin' : 'Pin';
	queueLastActionPinBtn.setAttribute('aria-pressed', queueLastActionPinned ? 'true' : 'false');
	queueLastActionPinBtn.setAttribute('aria-label', queueLastActionPinned ? 'Unpin queue last action status' : 'Pin queue last action status');
	queueLastActionPinBtn.title = queueLastActionPinned ? 'Unpin to allow auto-clear after inactivity' : 'Pin this status so it does not auto-clear';
}

function renderQueueLastAction() {
	if (!queueLastAction) return;
	if (!queueLastActionInfo || !queueLastActionInfo.message) {
		queueLastAction.textContent = 'Last action: none yet.';
		stopQueueLastActionTicker();
		syncQueueLastActionPinButton();
		return;
	}

	const ageMs = Math.max(0, Date.now() - Number(queueLastActionInfo.at || Date.now()));
	if (!queueLastActionPinned && ageMs > QUEUE_LAST_ACTION_MAX_AGE_MS) {
		queueLastActionInfo = null;
		queueLastAction.textContent = 'Last action: none yet.';
		stopQueueLastActionTicker();
		syncQueueLastActionPinButton();
		return;
	}
	const ageSeconds = Math.max(1, Math.round(ageMs / 1000));
	const ageText = ageSeconds <= 1 ? 'just now' : `${ageSeconds}s ago`;
	queueLastAction.textContent = `Last action: ${queueLastActionInfo.message} (${ageText})`;
	ensureQueueLastActionTicker();
	syncQueueLastActionPinButton();
}

function setQueueLastAction(message) {
	queueLastActionInfo = {
		message: String(message || '').trim(),
		at: Date.now(),
	};
	renderQueueLastAction();
}

function renderQueueRestoreHint() {
	if (!queueRestoreHint || !queueRestoreWrap || !queueRestoreShowBtn) return;
	if (!restoredQueueStateInfo || !trackedPromptIds.size) {
		queueRestoreWrap.hidden = true;
		queueRestoreShowBtn.hidden = true;
		queueRestoreHint.textContent = '';
		stopQueueRestoreHintTicker();
		return;
	}
	if (queueRestoreHintHidden) {
		queueRestoreWrap.hidden = true;
		queueRestoreShowBtn.hidden = false;
		queueRestoreHint.textContent = '';
		stopQueueRestoreHintTicker();
		return;
	}

	const count = Number(restoredQueueStateInfo.count) || trackedPromptIds.size;
	const ageMs = Math.max(0, Date.now() - Number(restoredQueueStateInfo.savedAt || Date.now()));
	const ageSeconds = Math.max(1, Math.round(ageMs / 1000));
	queueRestoreHint.textContent = `Restored ${count} active queue item${count === 1 ? '' : 's'} from a previous tab (${ageSeconds}s ago).`;
	queueRestoreWrap.hidden = false;
	queueRestoreShowBtn.hidden = true;
	ensureQueueRestoreHintTicker();
}

if (queueRestoreHideBtn) {
	queueRestoreHideBtn.addEventListener('click', () => {
		queueRestoreHintHidden = true;
		localStorage.setItem(QUEUE_RESTORE_HINT_HIDDEN_KEY, '1');
		setQueueLastAction('Restore hint hidden.');
		renderQueueRestoreHint();
	});
}

if (queueRestoreShowBtn) {
	queueRestoreShowBtn.addEventListener('click', () => {
		queueRestoreHintHidden = false;
		localStorage.removeItem(QUEUE_RESTORE_HINT_HIDDEN_KEY);
		setQueueLastAction('Restore hint shown.');
		renderQueueRestoreHint();
	});
}

if (queueLastActionPinBtn) {
	queueLastActionPinBtn.addEventListener('click', () => {
		queueLastActionPinned = !queueLastActionPinned;
		if (queueLastActionPinned) {
			localStorage.setItem(QUEUE_LAST_ACTION_PINNED_KEY, '1');
		} else {
			localStorage.removeItem(QUEUE_LAST_ACTION_PINNED_KEY);
		}
		renderQueueLastAction();
	});
}

function persistTrackedQueueState() {
	const entries = Array.from(trackedPromptIds)
		.map((promptId) => {
			const meta = queueJobMeta.get(promptId) || {};
			const snapshot = pendingImageJobs.get(promptId) || meta.snapshot || {};
			if (!snapshot || typeof snapshot !== 'object') return null;
			return {
				prompt_id: promptId,
				status: String(meta.status || 'queued'),
				miss_count: Number.isFinite(Number(meta.missCount)) ? Number(meta.missCount) : 0,
				updated_at: Number.isFinite(Number(meta.updatedAt)) ? Number(meta.updatedAt) : Date.now(),
				started_at: Number.isFinite(Number(meta.startedAt)) ? Number(meta.startedAt) : undefined,
				snapshot,
			};
		})
		.filter(Boolean)
		.sort((a, b) => b.updated_at - a.updated_at)
		.slice(0, QUEUE_STATE_MAX_ITEMS);

	try {
		if (!entries.length) {
			restoredQueueStateInfo = null;
			localStorage.removeItem(QUEUE_STATE_STORAGE_KEY);
			renderQueueRestoreHint();
			return;
		}
		localStorage.setItem(QUEUE_STATE_STORAGE_KEY, JSON.stringify({ entries, saved_at: Date.now() }));
	} catch {
		// Ignore storage write failures; queue processing still works in-memory.
	}
}

function restoreTrackedQueueState() {
	let parsed;
	try {
		parsed = JSON.parse(localStorage.getItem(QUEUE_STATE_STORAGE_KEY) || '{}');
	} catch {
		return;
	}

	const entries = Array.isArray(parsed?.entries) ? parsed.entries : [];
	if (!entries.length) return;

	let restoredCount = 0;
	for (const entry of entries) {
		const promptId = String(entry?.prompt_id || '').trim();
		if (!promptId) continue;
		const snapshot = entry?.snapshot && typeof entry.snapshot === 'object' ? entry.snapshot : {};
		const rawStatus = String(entry?.status || 'queued');
		const status = ['queued', 'running', 'processing'].includes(rawStatus) ? rawStatus : 'queued';
		const missCount = Number.isFinite(Number(entry?.miss_count)) ? Math.max(0, Number(entry.miss_count)) : 0;
		const updatedAt = Number.isFinite(Number(entry?.updated_at)) ? Number(entry.updated_at) : Date.now();
		const startedAt = Number.isFinite(Number(entry?.started_at)) ? Number(entry.started_at) : undefined;

		trackedPromptIds.add(promptId);
		if (snapshot && Object.keys(snapshot).length) {
			pendingImageJobs.set(promptId, snapshot);
		}
		queueJobMeta.set(promptId, {
			status,
			missCount,
			updatedAt,
			startedAt,
			snapshot,
		});
		restoredCount += 1;
	}

	if (!restoredCount) {
		restoredQueueStateInfo = null;
		try { localStorage.removeItem(QUEUE_STATE_STORAGE_KEY); } catch { /* no-op */ }
		renderQueueRestoreHint();
		return;
	}

	restoredQueueStateInfo = {
		count: restoredCount,
		savedAt: Number(parsed?.saved_at) || Date.now(),
	};
	setQueueLastAction(`Restored ${restoredCount} tracked queue item${restoredCount === 1 ? '' : 's'}.`);

	renderQueueStatus([], [], new Set());
	ensureQueuePolling();
	pollQueue();
}

if (failedOnlyToggle) {
	failedOnlyToggle.checked = queueFilterFailedOnly;
	failedOnlyToggle.addEventListener('change', () => {
		queueFilterFailedOnly = failedOnlyToggle.checked;
		localStorage.setItem('queueFilterFailedOnly', queueFilterFailedOnly ? '1' : '0');
		setQueueLastAction(queueFilterFailedOnly ? 'Showing only failed queue items.' : 'Showing all queue items.');
		renderQueueStatus([], [], new Set());
	});
}

if (queueHelpDetails) {
	queueHelpDetails.open = localStorage.getItem(QUEUE_HELP_EXPANDED_KEY) === '1';
	queueHelpDetails.addEventListener('toggle', () => {
		localStorage.setItem(QUEUE_HELP_EXPANDED_KEY, queueHelpDetails.open ? '1' : '0');
		setQueueLastAction(queueHelpDetails.open ? 'Queue help opened.' : 'Queue help closed.');
	});
}

renderQueueTelemetry();
renderQueueLastAction();

if (queueTelemetryResetBtn) {
	queueTelemetryResetBtn.addEventListener('click', () => {
		resetQueueTelemetry();
		setQueueLastAction('Queue counters reset.');
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
	applyTheme(saved || 'dark');
})();

themeToggle.addEventListener('click', () => {
	const current = document.body.getAttribute('data-theme');
	applyTheme(current === 'dark' ? 'light' : 'dark');
});

/* --------------------------------------------------------------------------
	 Tab navigation
	 -------------------------------------------------------------------------- */
function getTopNavTabs() {
	return [navGenerative, navImage, navConfig, navModels].filter(Boolean);
}

function panelForTopNavTab(tab) {
	if (tab === navImage) return 'image';
	if (tab === navConfig) return 'config';
	if (tab === navModels) return 'models';
	return 'generative';
}

function onTopNavTabKeydown(event) {
	const tabs = getTopNavTabs();
	if (!tabs.length) return;
	const currentIndex = tabs.indexOf(event.currentTarget);
	if (currentIndex < 0) return;
	const key = event.key;
	if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
	event.preventDefault();
	let nextIndex = currentIndex;
	if (key === 'Home') {
		nextIndex = 0;
	} else if (key === 'End') {
		nextIndex = tabs.length - 1;
	} else if (key === 'ArrowRight') {
		nextIndex = (currentIndex + 1) % tabs.length;
	} else if (key === 'ArrowLeft') {
		nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
	}
	const nextTab = tabs[nextIndex];
	if (!nextTab) return;
	nextTab.focus();
	showPanel(panelForTopNavTab(nextTab));
}

function onDiagnosticsActionsKeydown(event) {
	const controls = [diagCopyBtn, diagWsRetryBtn, diagDisableLogRepairBtn, diagClearRepairStatusBtn, diagnosticsRunBtn].filter(Boolean);
	if (!controls.length) return;
	const currentIndex = controls.indexOf(event.currentTarget);
	if (currentIndex < 0) return;
	const key = event.key;
	if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
	event.preventDefault();
	let nextIndex = currentIndex;
	if (key === 'Home') {
		nextIndex = 0;
	} else if (key === 'End') {
		nextIndex = controls.length - 1;
	} else if (key === 'ArrowRight') {
		nextIndex = (currentIndex + 1) % controls.length;
	} else if (key === 'ArrowLeft') {
		nextIndex = (currentIndex - 1 + controls.length) % controls.length;
	}
	const nextControl = controls[nextIndex];
	if (nextControl) nextControl.focus();
}

function showPanel(panel) {
	const allPanels = [panelGen, panelImage, panelConfig, panelModels].filter(Boolean);
	const allNavs = getTopNavTabs();
	allPanels.forEach(p => { p.hidden = true; p.classList.remove('active'); });
	allNavs.forEach(n => {
		n.classList.remove('active');
		n.setAttribute('aria-selected', 'false');
		n.setAttribute('tabindex', '-1');
	});

	let targetPanel = panelGen;
	let targetNav = navGenerative;
	if (panel === 'image') { targetPanel = panelImage; targetNav = navImage; }
	else if (panel === 'config') { targetPanel = panelConfig; targetNav = navConfig; }
	else if (panel === 'models') { targetPanel = panelModels; targetNav = navModels; }

	if (targetPanel) { targetPanel.hidden = false; targetPanel.classList.add('active'); }
	if (targetNav) {
		targetNav.classList.add('active');
		targetNav.setAttribute('aria-selected', 'true');
		targetNav.setAttribute('tabindex', '0');
	}

	if (panel === 'models') mbOnTabActivate();
	localStorage.setItem('activePanel', panel);
}

navGenerative.addEventListener('click', (e) => {
	e.preventDefault();
	showPanel('generative');
});
navGenerative.addEventListener('keydown', onTopNavTabKeydown);
navImage.addEventListener('click', (e) => {
	e.preventDefault();
	showPanel('image');
});
navImage.addEventListener('keydown', onTopNavTabKeydown);
if (navConfig) {
	navConfig.addEventListener('click', (e) => {
		e.preventDefault();
		showPanel('config');
	});
	navConfig.addEventListener('keydown', onTopNavTabKeydown);
}
if (navModels) {
	navModels.addEventListener('click', (e) => {
		e.preventDefault();
		showPanel('models');
	});
	navModels.addEventListener('keydown', onTopNavTabKeydown);
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

function isComfyWsOpen() {
	return Boolean(comfyWs && comfyWs.readyState === WebSocket.OPEN);
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

function renderWsTransportStatus() {
	if (!wsTransportStatus) {
		renderWsRetryButtonState();
		return;
	}
	if (document.hidden) {
		wsTransportStatus.textContent = 'Preview transport: hidden tab';
		renderWsRetryButtonState();
		return;
	}
	if (_isComfyWsCooldownActive()) {
		const minsLeft = _getComfyWsCooldownMinutesLeft();
		wsTransportStatus.textContent = `Preview transport: cooldown (${minsLeft}m left), retries ${comfyWsFailCount}/${COMFY_WS_MAX_RETRIES}`;
		renderWsRetryButtonState();
		return;
	}
	if (_isComfyWsBlockedActive()) {
		const secsLeft = _getComfyWsBlockedSecondsLeft();
		wsTransportStatus.textContent = `Preview transport: websocket blocked (${secsLeft}s left), polling active`;
		renderWsRetryButtonState();
		return;
	}
	if (comfyWsNextRetryAt > Date.now()) {
		const secsLeft = Math.max(1, Math.ceil((comfyWsNextRetryAt - Date.now()) / 1000));
		wsTransportStatus.textContent = `Preview transport: retry in ${secsLeft}s (${comfyWsFailCount}/${COMFY_WS_MAX_RETRIES})`;
		renderWsRetryButtonState();
		return;
	}
	if (comfyWs && comfyWs.readyState === WebSocket.OPEN) {
		wsTransportStatus.textContent = 'Preview transport: websocket connected';
		renderWsRetryButtonState();
		return;
	}
	if (comfyWs && comfyWs.readyState === WebSocket.CONNECTING) {
		const attempt = Math.max(1, Math.min(comfyWsFailCount + 1, COMFY_WS_MAX_RETRIES));
		wsTransportStatus.textContent = `Preview transport: websocket connecting (attempt ${attempt}/${COMFY_WS_MAX_RETRIES})`;
		renderWsRetryButtonState();
		return;
	}
	if (comfyWsFailCount > 0) {
		wsTransportStatus.textContent = `Preview transport: polling fallback (ws retries ${comfyWsFailCount}/${COMFY_WS_MAX_RETRIES})`;
		renderWsRetryButtonState();
		return;
	}
	wsTransportStatus.textContent = 'Preview transport: polling fallback ready';
	renderWsRetryButtonState();
}

function renderWsRetryButtonState() {
	if (!diagWsRetryBtn) return;
	const isConnecting = Boolean(comfyWs && comfyWs.readyState === WebSocket.CONNECTING);
	if (isComfyWsOpen()) {
		diagWsRetryBtn.disabled = true;
		diagWsRetryBtn.textContent = 'WS Connected';
		diagWsRetryBtn.title = 'ComfyUI WebSocket is connected.';
		return;
	}
	if (isConnecting) {
		diagWsRetryBtn.disabled = true;
		diagWsRetryBtn.textContent = 'Connecting...';
		diagWsRetryBtn.title = 'ComfyUI WebSocket connection attempt is in progress.';
		return;
	}
	if (_isComfyWsBlockedActive()) {
		const secsLeft = _getComfyWsBlockedSecondsLeft();
		diagWsRetryBtn.disabled = false;
		diagWsRetryBtn.textContent = `Retry WS (${secsLeft}s)`;
		diagWsRetryBtn.title = 'WebSocket appears blocked; click to force a retry now.';
		return;
	}
	if (_isComfyWsCooldownActive()) {
		const minsLeft = _getComfyWsCooldownMinutesLeft();
		diagWsRetryBtn.disabled = false;
		diagWsRetryBtn.textContent = `Retry WS (${minsLeft}m)`;
		diagWsRetryBtn.title = 'WebSocket cooldown is active; click to force a retry now.';
		return;
	}
	if (comfyWsNextRetryAt > Date.now()) {
		const secsLeft = Math.max(1, Math.ceil((comfyWsNextRetryAt - Date.now()) / 1000));
		diagWsRetryBtn.disabled = false;
		diagWsRetryBtn.textContent = `Retry WS (${secsLeft}s)`;
		diagWsRetryBtn.title = 'WebSocket retry is scheduled; click to force a retry now.';
		return;
	}
	diagWsRetryBtn.disabled = false;
	diagWsRetryBtn.textContent = 'Retry WS';
	diagWsRetryBtn.title = 'Retry ComfyUI WebSocket connection now.';
}

function startWsTransportStatusTicker() {
	if (wsTransportStatusTimer) return;
	wsTransportStatusTimer = window.setInterval(() => {
		if (document.hidden) return;
		renderWsTransportStatus();
	}, 1000);
}

function stopWsTransportStatusTicker() {
	if (!wsTransportStatusTimer) return;
	window.clearInterval(wsTransportStatusTimer);
	wsTransportStatusTimer = null;
}

function syncBackgroundPollingOwnership() {
	const hadOwnership = hasBackgroundPollingOwnership;
	hasBackgroundPollingOwnership = refreshBackgroundPollingOwnership() || claimBackgroundPollingOwnership();

	if (!hasBackgroundPollingOwnership) {
		stopStatusPolling();
		stopLivePreviewAutoRefresh();
		stopQueuePolling();
		if (!isComfyWsOpen()) {
			setPreviewTransportMode('polling', 'Polling fallback is active in another tab that owns the lease.');
		}
		renderPollOwnerStatus();
		renderWsTransportStatus();
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
	renderWsTransportStatus();
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
		model_family: resolveActiveImageFamily(imageModelSelect?.value || ''),
		sampler: imageSamplerSelect.value,
		scheduler: imageSchedulerSelect?.value || 'normal',
		negative_prompt: imageNegativePrompt?.value || '',
		loras: collectLoraStack(),
		vae: vaeModelSelect?.value || '',
		refiner_model: refinerModelSelect?.value || '',
		hiresfix_enable: hiresfixEnable?.checked || false,
		hiresfix_upscaler: hiresfixUpscalerSelect?.value || '',
		hiresfix_scale: Number(hiresfixScale?.value || 2),
		hiresfix_steps: Number(hiresfixSteps?.value || 20),
		hiresfix_denoise: Number(hiresfixDenoise?.value || 0.4),
		controlnet_model: controlnetModelSelect?.value || '',
		controlnet_preprocessor: controlnetPreprocessorSelect?.value || 'none',
		controlnet_weight: Number(controlnetWeight?.value || 1),
		controlnet_start: Number(controlnetStart?.value || 0),
		controlnet_end: Number(controlnetEnd?.value || 1),
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
	if (imageModelFamilySelect && typeof settings.model_family === 'string') {
		const requested = settings.model_family.toLowerCase();
		if (['auto', 'sd', 'flux'].includes(requested)) {
			imageModelFamilySelect.value = requested;
			imageModelFamilyMode = requested;
			localStorage.setItem(IMAGE_MODEL_FAMILY_MODE_KEY, requested);
		}
	}
	applyImageFamilyModeUi();
	if (settings.sampler && [...imageSamplerSelect.options].some((o) => o.value === settings.sampler)) {
		imageSamplerSelect.value = settings.sampler;
	}
	if (settings.scheduler && imageSchedulerSelect && [...imageSchedulerSelect.options].some((o) => o.value === settings.scheduler)) {
		imageSchedulerSelect.value = settings.scheduler;
	}
	if (typeof settings.negative_prompt === 'string' && imageNegativePrompt) {
		imageNegativePrompt.value = settings.negative_prompt;
	}
	// Restore LoRA stack
	if (loraStackContainer && Array.isArray(settings.loras)) {
		loraStackContainer.innerHTML = '';
		for (const entry of settings.loras) {
			addLoraRow();
			const lastRow = loraStackContainer.lastElementChild;
			if (!lastRow) continue;
			const sel = lastRow.querySelector('.lora-row-select');
			const str = lastRow.querySelector('.lora-row-strength');
			const strVal = lastRow.querySelector('.lora-strength-val');
			if (sel && entry.name && [...sel.options].some((o) => o.value === entry.name)) sel.value = entry.name;
			if (str && Number.isFinite(entry.strength)) {
				str.value = String(entry.strength);
				if (strVal) strVal.textContent = Number(entry.strength).toFixed(2);
			}
		}
	}
	if (vaeModelSelect && settings.vae !== undefined) {
		if (!settings.vae || [...vaeModelSelect.options].some((o) => o.value === settings.vae)) {
			vaeModelSelect.value = settings.vae || '';
		}
	}
	if (refinerModelSelect && settings.refiner_model !== undefined) {
		if (!settings.refiner_model || [...refinerModelSelect.options].some((o) => o.value === settings.refiner_model)) {
			refinerModelSelect.value = settings.refiner_model || '';
		}
	}
	if (hiresfixEnable && typeof settings.hiresfix_enable === 'boolean') {
		hiresfixEnable.checked = settings.hiresfix_enable;
	}
	if (hiresfixUpscalerSelect && settings.hiresfix_upscaler !== undefined) {
		if (!settings.hiresfix_upscaler || [...hiresfixUpscalerSelect.options].some((o) => o.value === settings.hiresfix_upscaler)) {
			hiresfixUpscalerSelect.value = settings.hiresfix_upscaler || '';
		}
	}
	if (hiresfixScale && Number.isFinite(settings.hiresfix_scale)) hiresfixScale.value = String(settings.hiresfix_scale);
	if (hiresfixSteps && Number.isFinite(settings.hiresfix_steps)) hiresfixSteps.value = String(settings.hiresfix_steps);
	if (hiresfixDenoise && Number.isFinite(settings.hiresfix_denoise)) {
		hiresfixDenoise.value = String(settings.hiresfix_denoise);
		if (hiresfixDenoiseVal) hiresfixDenoiseVal.textContent = Number(settings.hiresfix_denoise).toFixed(2);
	}
	if (settings.controlnet_model && controlnetModelSelect && [...controlnetModelSelect.options].some((o) => o.value === settings.controlnet_model)) {
		controlnetModelSelect.value = settings.controlnet_model;
	}
	if (settings.controlnet_preprocessor && controlnetPreprocessorSelect
			&& [...controlnetPreprocessorSelect.options].some((o) => o.value === settings.controlnet_preprocessor)) {
		controlnetPreprocessorSelect.value = settings.controlnet_preprocessor;
	}
	if (Number.isFinite(settings.controlnet_weight) && controlnetWeight) controlnetWeight.value = String(settings.controlnet_weight);
	if (Number.isFinite(settings.controlnet_start) && controlnetStart) controlnetStart.value = String(settings.controlnet_start);
	if (Number.isFinite(settings.controlnet_end) && controlnetEnd) controlnetEnd.value = String(settings.controlnet_end);
	if (settings.seed !== undefined && settings.seed !== null) imageSeed.value = String(settings.seed);
	if (Number.isFinite(settings.steps)) imageSteps.value = String(settings.steps);
	if (Number.isFinite(settings.cfg)) imageCfg.value = String(settings.cfg);
	if (Number.isFinite(settings.denoise)) imageDenoise.value = String(settings.denoise);
	if (Number.isFinite(settings.width)) imageWidth.value = String(settings.width);
	if (Number.isFinite(settings.height)) imageHeight.value = String(settings.height);
	if (Number.isFinite(settings.batch_size)) imageBatchSize.value = String(settings.batch_size);
	syncImageControlLabels();
	updateModelStackBadges();
	updateModelStackCompatibilityHint();
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

function exportPresetsAsJson() {
	const payload = {
		version: 1,
		exported: new Date().toISOString(),
		imageProfiles: getImageProfileState(),
		promptPresets: (() => {
			try { return JSON.parse(localStorage.getItem(PROMPT_SAVED_KEY) || '{}'); }
			catch { return {}; }
		})(),
	};
	const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
	const url = URL.createObjectURL(blob);
	const a = document.createElement('a');
	const dateStr = new Date().toISOString().slice(0, 10);
	a.href = url;
	a.download = `la-presets-${dateStr}.json`;
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
	URL.revokeObjectURL(url);
	const profileCount = Object.keys(payload.imageProfiles).length;
	const promptCount = Object.keys(payload.promptPresets).length;
	showToast(`Exported ${profileCount} profile(s) and ${promptCount} prompt preset(s).`, 'pos');
}

function importPresetsFromJson(file) {
	if (!file) return;
	const reader = new FileReader();
	reader.onload = (e) => {
		let payload;
		try { payload = JSON.parse(e.target.result); }
		catch { showToast('Invalid JSON file — import failed.', 'neg'); return; }

		if (!payload || typeof payload !== 'object') {
			showToast('Unrecognized format — import failed.', 'neg');
			return;
		}

		let profilesImported = 0;
		if (payload.imageProfiles && typeof payload.imageProfiles === 'object') {
			const existing = getImageProfileState();
			Object.assign(existing, payload.imageProfiles);
			setImageProfileState(existing);
			renderImageProfileSelect('');
			profilesImported = Object.keys(payload.imageProfiles).length;
		}

		let promptsImported = 0;
		if (payload.promptPresets && typeof payload.promptPresets === 'object') {
			const existing = loadPromptSavedPresets();
			for (const [k, v] of Object.entries(payload.promptPresets)) {
				existing[k] = _migratePresetV1ToV2(v);
			}
			localStorage.setItem(PROMPT_SAVED_KEY, JSON.stringify(existing));
			refreshPromptTagFilterOptions();
			renderPromptSavedSelect();
			promptsImported = Object.keys(payload.promptPresets).length;
		}

		showToast(`Imported ${profilesImported} profile(s) and ${promptsImported} prompt preset(s).`, 'pos');
	};
	reader.onerror = () => { showToast('Failed to read file.', 'neg'); };
	reader.readAsText(file);
}

function setDiagnosticValue(el, text, level = '') {
	if (!el) return;
	el.textContent = text;
	el.classList.remove('ok', 'warn');
	if (level) el.classList.add(level);
}

function setDiagRepairStatusLine(text, persist = true) {
	if (diagRepairStatus) diagRepairStatus.textContent = text;
	if (!persist) return;
	const value = String(text || '').trim();
	if (value) {
		localStorage.setItem(DIAG_REPAIR_STATUS_KEY, value);
	} else {
		localStorage.removeItem(DIAG_REPAIR_STATUS_KEY);
	}
}

function withDiagStatusTimestamp(text) {
	return `${text} (${new Date().toLocaleTimeString()})`;
}

function clearDiagRepairStatusLine() {
	setDiagRepairStatusLine(withDiagStatusTimestamp('Last repair: never.'), false);
	localStorage.removeItem(DIAG_REPAIR_STATUS_KEY);
}

if (diagRepairStatus && diagRepairStatusStored) {
	setDiagRepairStatusLine(diagRepairStatusStored, false);
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
	setDiagnosticValue(diagBackendHealth, snapshot.backendHealthLabel || 'unknown', snapshot.backendHealthOk ? 'ok' : 'warn');
	setDiagnosticValue(diagDisableLogHealth, snapshot.disableLogHealthLabel || 'unknown', snapshot.disableLogHealthOk ? 'ok' : 'warn');
	setDiagnosticValue(diagLastRun, snapshot.lastRunLabel);
	diagnosticsSummary.textContent = snapshot.summary;
	if (diagnosticsHint) diagnosticsHint.textContent = snapshot.hint;
	if (diagStatusBadge) {
		const status = snapshot.failed ? 'error' : (snapshot.textOk && snapshot.imageOk ? 'ok' : 'warn');
		diagStatusBadge.dataset.status = status;
		diagStatusBadge.title = snapshot.summary;
	}

	const key = [snapshot.lastRunLabel, snapshot.summary, snapshot.textStatusLabel, snapshot.imageStatusLabel, snapshot.checkpoints, snapshot.samplers, snapshot.backendHealthLabel || 'unknown', snapshot.disableLogHealthLabel || 'unknown'].join('|');
	if (key !== lastDiagnosticsLogKey) {
		lastDiagnosticsLogKey = key;
		const level = snapshot.textOk && snapshot.imageOk ? 'info' : 'warn';
		appendDiagnosticsConsoleLine(`[${snapshot.lastRunLabel}] ${snapshot.summary} | text=${snapshot.textStatusLabel} image=${snapshot.imageStatusLabel} ckpt=${snapshot.checkpoints} samplers=${snapshot.samplers} backend=${snapshot.backendHealthLabel || 'unknown'} disable-log=${snapshot.disableLogHealthLabel || 'unknown'}`, level);
	}
}

async function runDiagnosticsChecks(manual = false) {
	if (!diagnosticsSummary) return;
	if (diagnosticsRunBtn) diagnosticsRunBtn.disabled = true;
	const lastRunLabel = new Date().toLocaleTimeString();
	try {
		const [statusRes, textModelRes, imageModelRes, samplerRes, healthRes] = await Promise.all([
			fetch('/api/status'),
			fetch('/api/models'),
			fetch('/api/image/models'),
			fetch('/api/image/samplers'),
			fetch('/api/healthz'),
		]);

		const statusData = await statusRes.json().catch(() => ({}));
		const textData = await textModelRes.json().catch(() => ({}));
		const imageData = await imageModelRes.json().catch(() => ({}));
		const samplerData = await samplerRes.json().catch(() => ({}));
		const healthData = await healthRes.json().catch(() => ({}));

		const textOk = !!statusData.text?.available;
		const imageOk = !!statusData.image?.available;
		const checkpoints = (imageData.models || []).length;
		const samplers = (samplerData.samplers || []).length;
		const textModels = (textData.models || []).length;
		const backendHealthOk = !!healthData.ok;
		const disableLogStore = healthData?.app?.disable_log_store || {};
		const disableLogStatus = String(disableLogStore.status || 'unknown');
		const disableLogCount = Number(disableLogStore.count || 0);
		const disableLogHealthOk = disableLogStore.ok === true;
		const disableLogHealthLabel = `${disableLogStatus} (${disableLogCount})`;
		const backendHealthLabel = backendHealthOk
			? `ok (build ${healthData.app?.template_version || 'unknown'})`
			: 'unhealthy';

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
			backendHealthOk,
			backendHealthLabel,
			disableLogHealthOk,
			disableLogHealthLabel,
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
			backendHealthOk: false,
			backendHealthLabel: 'unknown',
			disableLogHealthOk: false,
			disableLogHealthLabel: 'unknown',
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
	if (!configOllamaPath || !configComfyuiPath || !configModelsPath) return;
	try {
		const res = await fetch('/api/config/services');
		const data = await res.json();
		if (!res.ok) {
			setConfigStatusLine(configSaveStatus, data.error || 'Could not load saved paths.', 'error');
			return;
		}
		configOllamaPath.value = data.ollama_path || '';
		configComfyuiPath.value = data.comfyui_path || '';
		configModelsPath.value = data.shared_models_path || '';
		if (configCivitaiKey) configCivitaiKey.value = data.civitai_api_key || '';
		if (configHuggingfaceKey) configHuggingfaceKey.value = data.huggingface_api_key || '';
		if (configDefaultNegPrompt) {
			configDefaultNegPrompt.value = data.default_negative_prompt || '';
			localStorage.setItem('defaultNegativePrompt', data.default_negative_prompt || '');
		}
		setConfigSavedTimestamp(data.updated_at || '');
		setConfigStatusLine(configSaveStatus, 'Saved configuration loaded.');
	} catch {
		setConfigStatusLine(configSaveStatus, 'Could not load saved configuration.', 'error');
		setConfigSavedTimestamp('');
	}
}

async function saveServiceConfig(options = {}) {
	const { silentSuccess = false } = options;
	if (!configOllamaPath || !configComfyuiPath || !configModelsPath) return;
	const payload = {
		ollama_path: configOllamaPath.value.trim(),
		comfyui_path: configComfyuiPath.value.trim(),
		shared_models_path: configModelsPath.value.trim(),
		civitai_api_key: configCivitaiKey ? configCivitaiKey.value.trim() : '',
		huggingface_api_key: configHuggingfaceKey ? configHuggingfaceKey.value.trim() : '',
		default_negative_prompt: configDefaultNegPrompt ? configDefaultNegPrompt.value : '',
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
			setConfigStatusLine(configSaveStatus, data.error || 'Could not save configuration.', 'error');
			showToast('Could not save configuration.', 'neg');
			return;
		}
		setConfigSavedTimestamp(data.config?.updated_at || '');
		setConfigStatusLine(configSaveStatus, 'Configuration saved.', 'ok');
		// Update localStorage cache for the Default neg-prompt button
		if (configDefaultNegPrompt) {
			localStorage.setItem('defaultNegativePrompt', configDefaultNegPrompt.value);
		}
		if (!silentSuccess) {
			showToast('Configuration saved.', 'pos');
		}
	} catch {
		setConfigStatusLine(configSaveStatus, 'Could not save configuration.', 'error');
		showToast('Could not save configuration.', 'neg');
	} finally {
		if (configSaveBtn) configSaveBtn.disabled = false;
	}
}

async function browseServicePath(service) {
	const serviceMap = {
		ollama: { input: configOllamaPath, button: configOllamaBrowseBtn },
		comfyui: { input: configComfyuiPath, button: configComfyuiBrowseBtn },
		models: { input: configModelsPath, button: configModelsBrowseBtn },
	};
	const mapped = serviceMap[service];
	const input = mapped?.input;
	const button = mapped?.button;
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

async function migrateSharedModelFolders() {
	if (!configModelsMigrateBtn) return;

	configModelsMigrateBtn.disabled = true;
	setConfigStatusLine(configSaveStatus, 'Analyzing folders for migration preview...');

	try {
		const previewRes = await fetch('/api/config/migrate-model-folders', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ dry_run: true }),
		});
		const preview = await previewRes.json().catch(() => ({}));
		if (!previewRes.ok) {
			setConfigStatusLine(configSaveStatus, preview.error || 'Migration preview failed.', 'error');
			showToast('Model folder migration preview failed.', 'neg');
			return;
		}

		const total = Number(preview.total_files || 0);
		const wouldMove = Number(preview.moved_count || 0);
		const wouldSkip = Number(preview.skipped_count || 0);
		const previewMsg = `Preview: ${total} files scanned, ${wouldMove} to move, ${wouldSkip} to skip.`;

		if (total === 0) {
			setConfigStatusLine(configSaveStatus, 'No legacy files found to migrate.', 'ok');
			showToast('No legacy model folders needed migration.', 'pos');
			return;
		}

		const confirmed = window.confirm(`${previewMsg}\n\nRun migration now?`);
		if (!confirmed) {
			setConfigStatusLine(configSaveStatus, 'Migration canceled after preview.');
			return;
		}

		setConfigStatusLine(configSaveStatus, 'Starting migration job...');
		const startRes = await fetch('/api/config/migrate-model-folders', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ async: true }),
		});
		const startData = await startRes.json().catch(() => ({}));
		if (!startRes.ok) {
			setConfigStatusLine(configSaveStatus, startData.error || 'Migration failed to start.', 'error');
			showToast('Model folder migration failed.', 'neg');
			return;
		}

		const jobId = startData.job?.id;
		if (!jobId) {
			setConfigStatusLine(configSaveStatus, 'Migration failed: missing job id.', 'error');
			showToast('Model folder migration failed.', 'neg');
			return;
		}

		let finalJob = null;
		for (let i = 0; i < 600; i++) {
			await new Promise((resolve) => window.setTimeout(resolve, 500));
			const statusRes = await fetch(`/api/config/migrate-model-folders/status/${encodeURIComponent(jobId)}`);
			const statusData = await statusRes.json().catch(() => ({}));
			if (!statusRes.ok) {
				setConfigStatusLine(configSaveStatus, statusData.error || 'Migration status check failed.', 'error');
				showToast('Migration status check failed.', 'neg');
				return;
			}

			const job = statusData.job || {};
			const progress = job.progress || {};
			const processed = Number(progress.processed_files || 0);
			const totalFiles = Number(progress.total_files || 0);
			setConfigStatusLine(configSaveStatus, `Migrating... ${processed}/${totalFiles} files`);

			if (job.status === 'done' || job.status === 'error') {
				finalJob = job;
				break;
			}
		}

		if (!finalJob) {
			setConfigStatusLine(configSaveStatus, 'Migration is still running. Check again shortly.');
			showToast('Migration still running in background.', '');
			return;
		}

		if (finalJob.status === 'error') {
			setConfigStatusLine(configSaveStatus, finalJob.error || 'Migration failed.', 'error');
			showToast('Model folder migration failed.', 'neg');
			return;
		}

		const result = finalJob.result || {};
		const movedCount = Number(result.moved_count || 0);
		const skippedCount = Number(result.skipped_count || 0);
		const errorCount = Number(result.error_count || 0);
		const summary = `Migration complete: moved ${movedCount}, skipped ${skippedCount}, errors ${errorCount}.`;
		setConfigStatusLine(configSaveStatus, summary, errorCount > 0 ? 'error' : 'ok');
		showToast(summary, errorCount > 0 ? 'neg' : 'pos');
		if (typeof loadModelLibrary === 'function') {
			loadModelLibrary();
		}
	} catch {
		setConfigStatusLine(configSaveStatus, 'Migration failed.', 'error');
		showToast('Model folder migration failed.', 'neg');
	} finally {
		configModelsMigrateBtn.disabled = false;
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
			await loadImageSchedulers();
			await loadImageLoraModels();
			await loadControlnetModels();
			await loadControlnetPreprocessors();
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
			imageModelDetailsByName = new Map();
			applyImageFamilyModeUi();
			return;
		}
		const models = data.models || [];
		const details = Array.isArray(data.model_details) ? data.model_details : [];
		imageModelDetailsByName = new Map(
			details
				.filter((entry) => entry && typeof entry.name === 'string' && entry.name.trim())
				.map((entry) => [entry.name, entry])
		);
		if (!models.length) {
			setImageModelMessage('No checkpoints found in ComfyUI');
			applyImageFamilyModeUi();
			return;
		}
		imageModelAllOptions = models.slice();
		renderFilteredImageModels(imageModelFilter ? imageModelFilter.value : '', imageModelSelect.value);
		if (!imageModelSelect.value) {
			const firstSupported = [...imageModelSelect.options].find((o) => !o.disabled && o.value);
			if (firstSupported) imageModelSelect.value = firstSupported.value;
		}
		renderRecentImageModels();
		renderFavoriteImageModels();
		updateModelFavoriteToggleState();
		updateModelStackBadges();
		updateModelStackCompatibilityHint();
		updateControlnetCompatibilityHint();
		applyImageFamilyModeUi();
	} catch {
		setImageModelMessage('Could not fetch checkpoints');
		imageModelDetailsByName = new Map();
		applyImageFamilyModeUi();
	}
}

function getRecentImageModels() {
	try {
		const parsed = JSON.parse(localStorage.getItem(IMAGE_RECENT_MODELS_KEY) || '[]');
		if (!Array.isArray(parsed)) return [];
		return parsed.filter((m) => typeof m === 'string' && m.trim());
	} catch {
		return [];
	}
}

function setRecentImageModels(models) {
	localStorage.setItem(IMAGE_RECENT_MODELS_KEY, JSON.stringify(models.slice(0, 6)));
}

function getFavoriteImageModels() {
	try {
		const parsed = JSON.parse(localStorage.getItem(IMAGE_FAVORITE_MODELS_KEY) || '[]');
		if (!Array.isArray(parsed)) return [];
		return parsed.filter((m) => typeof m === 'string' && m.trim());
	} catch {
		return [];
	}
}

function setFavoriteImageModels(models) {
	localStorage.setItem(IMAGE_FAVORITE_MODELS_KEY, JSON.stringify(models.slice(0, 12)));
}

function isFavoriteImageModel(modelName) {
	if (!modelName) return false;
	return getFavoriteImageModels().includes(modelName);
}

function toggleFavoriteImageModel(modelName) {
	if (!modelName) return;
	const favorites = getFavoriteImageModels();
	const hasModel = favorites.includes(modelName);
	const next = hasModel
		? favorites.filter((name) => name !== modelName)
		: [modelName, ...favorites.filter((name) => name !== modelName)].slice(0, 12);
	setFavoriteImageModels(next);
	renderFavoriteImageModels();
	updateModelFavoriteToggleState();
	if (imageModelFilterMode === 'favorites') {
		renderFilteredImageModels(imageModelFilter ? imageModelFilter.value : '', imageModelSelect ? imageModelSelect.value : '');
	}
	updateModelStackBadges();
}

function setImageModelFilterMode(mode) {
	const nextMode = ['all', 'recent', 'favorites'].includes(mode) ? mode : 'all';
	imageModelFilterMode = nextMode;
	localStorage.setItem(IMAGE_MODEL_FILTER_MODE_KEY, nextMode);
	if (imageModelModeAll) {
		imageModelModeAll.classList.toggle('active', nextMode === 'all');
		imageModelModeAll.setAttribute('aria-pressed', String(nextMode === 'all'));
	}
	if (imageModelModeRecent) {
		imageModelModeRecent.classList.toggle('active', nextMode === 'recent');
		imageModelModeRecent.setAttribute('aria-pressed', String(nextMode === 'recent'));
	}
	if (imageModelModeFavorites) {
		imageModelModeFavorites.classList.toggle('active', nextMode === 'favorites');
		imageModelModeFavorites.setAttribute('aria-pressed', String(nextMode === 'favorites'));
	}
	renderFilteredImageModels(imageModelFilter ? imageModelFilter.value : '', imageModelSelect ? imageModelSelect.value : '');
}

function getImageModelPoolForMode() {
	const available = new Set(imageModelAllOptions);
	if (imageModelFilterMode === 'recent') {
		return getRecentImageModels().filter((name) => available.has(name));
	}
	if (imageModelFilterMode === 'favorites') {
		return getFavoriteImageModels().filter((name) => available.has(name));
	}
	return imageModelAllOptions.slice();
}

function rememberRecentImageModel(modelName) {
	if (!modelName) return;
	const next = [modelName, ...getRecentImageModels().filter((m) => m !== modelName)].slice(0, 6);
	setRecentImageModels(next);
	renderRecentImageModels();
	if (imageModelFilterMode === 'recent') {
		renderFilteredImageModels(imageModelFilter ? imageModelFilter.value : '', modelName);
	}
}

function renderRecentImageModels() {
	if (!imageModelRecentList) return;
	const available = new Set(imageModelAllOptions);
	const recents = getRecentImageModels().filter((m) => available.has(m));
	if (!recents.length) {
		imageModelRecentList.innerHTML = '<span class="hint">No recent models yet.</span>';
		return;
	}
	imageModelRecentList.innerHTML = recents
		.map((name) => `<button class="btn btn-ghost btn-xs model-recent-chip" type="button" data-model="${escHtml(name)}" title="Use ${escHtml(name)}">${escHtml(name)}</button>`)
		.join('');
	imageModelRecentList.querySelectorAll('.model-recent-chip').forEach((btn) => {
		btn.addEventListener('click', () => {
			const modelName = btn.dataset.model || '';
			if (!modelName) return;
			applyImageModelSelection(modelName);
		});
	});
}

function renderFavoriteImageModels() {
	if (!imageModelFavoriteList) return;
	const available = new Set(imageModelAllOptions);
	const favorites = getFavoriteImageModels().filter((m) => available.has(m));
	if (!favorites.length) {
		imageModelFavoriteList.innerHTML = '<span class="hint">No favorites yet.</span>';
		return;
	}
	imageModelFavoriteList.innerHTML = favorites
		.map((name) => `<button class="btn btn-ghost btn-xs model-recent-chip" type="button" data-model="${escHtml(name)}" title="Use ${escHtml(name)}">${escHtml(name)}</button>`)
		.join('');
	imageModelFavoriteList.querySelectorAll('.model-recent-chip').forEach((btn) => {
		btn.addEventListener('click', () => {
			const modelName = btn.dataset.model || '';
			if (!modelName) return;
			applyImageModelSelection(modelName);
		});
	});
}

function updateModelFavoriteToggleState() {
	if (!imageModelFavoriteToggle) return;
	const modelName = imageModelSelect ? imageModelSelect.value : '';
	const isFavorite = isFavoriteImageModel(modelName);
	imageModelFavoriteToggle.classList.toggle('active', isFavorite);
	imageModelFavoriteToggle.setAttribute('aria-pressed', String(isFavorite));
	imageModelFavoriteToggle.textContent = isFavorite ? 'Favorited Selected' : 'Favorite Selected';
	imageModelFavoriteToggle.disabled = !modelName;
}

function applyImageModelSelection(modelName) {
	if (!imageModelSelect || !modelName) return;
	const target = [...imageModelSelect.options].find((o) => o.value === modelName && !o.disabled);
	if (!target) {
		if (imageModelFilter) {
			imageModelFilter.value = '';
			renderFilteredImageModels('', modelName);
		}
	}
	if ([...imageModelSelect.options].some((o) => o.value === modelName && !o.disabled)) {
		imageModelSelect.value = modelName;
		rememberRecentImageModel(modelName);
		updateModelFavoriteToggleState();
		updateModelStackBadges();
		updateModelStackCompatibilityHint();
		updateControlnetCompatibilityHint();
	}
}

function canSelectCheckpointInCurrentFamilyMode(modelName) {
	const requestedMode = imageModelFamilySelect?.value || imageModelFamilyMode || 'auto';
	if (requestedMode === 'auto' || requestedMode === 'flux') return true;
	const family = inferImageModelFamily(modelName);
	if (requestedMode === 'sd' && family === 'flux') return false;
	return true;
}

function renderFilteredImageModels(rawFilter = '', preferredValue = '') {
	if (!imageModelSelect) return;
	const filter = String(rawFilter || '').trim().toLowerCase();
	const modePool = getImageModelPoolForMode();
	const filtered = filter
		? modePool.filter((name) => String(name).toLowerCase().includes(filter))
		: modePool.slice();
	if (!modePool.length) {
		const modeLabel = imageModelFilterMode === 'favorites'
			? 'No favorite checkpoints yet.'
			: imageModelFilterMode === 'recent'
				? 'No recent checkpoints yet.'
				: 'No checkpoints available';
		imageModelSelect.innerHTML = `<option value="">${escHtml(modeLabel)}</option>`;
		updateModelFavoriteToggleState();
		return;
	}
	if (!filtered.length) {
		imageModelSelect.innerHTML = '<option value="">No matching checkpoints</option>';
		updateModelFavoriteToggleState();
		return;
	}
	imageModelSelect.innerHTML = filtered
		.map((name) => {
			const unsupported = !canSelectCheckpointInCurrentFamilyMode(name);
			const optionLabel = unsupported ? `${name} (set family mode to Auto/Flux to enable)` : name;
			return `<option value="${escHtml(name)}" ${unsupported ? 'disabled data-unsupported="true"' : ''}>${escHtml(optionLabel)}</option>`;
		})
		.join('');
	if (preferredValue && [...imageModelSelect.options].some((o) => o.value === preferredValue && !o.disabled)) {
		imageModelSelect.value = preferredValue;
		updateModelFavoriteToggleState();
		return;
	}
	const firstSupported = [...imageModelSelect.options].find((o) => !o.disabled && o.value);
	if (firstSupported) imageModelSelect.value = firstSupported.value;
	updateModelFavoriteToggleState();
}

function updateModelStackBadges() {
	if (!modelStackBadges) return;
	const badges = [];
	if (imageModelSelect?.value) badges.push(`Base: ${imageModelSelect.value}`);
	if (refinerModelSelect?.value) badges.push(`Refiner: ${refinerModelSelect.value}`);
	if (vaeModelSelect?.value) badges.push(`VAE: ${vaeModelSelect.value}`);
	const loraCount = collectLoraStack().length;
	if (loraCount) badges.push(`LoRA x${loraCount}`);
	if (isFavoriteImageModel(imageModelSelect?.value || '')) badges.push('Favorite');
	if (!badges.length) {
		modelStackBadges.innerHTML = '<span class="hint">Defaults</span>';
		return;
	}
	modelStackBadges.innerHTML = badges
		.map((label) => `<span class="model-stack-chip" title="${escHtml(label)}">${escHtml(label)}</span>`)
		.join('');
}

async function loadImageSamplers() {
	if (!imageSamplerSelect) return;
	try {
		const res = await fetch('/api/image/samplers');
		const data = await res.json();
		if (!res.ok) {
			imageSamplerSelect.innerHTML = '<option value="euler">euler</option>';
			const counts = applySelectFilterQuery(imageSamplerSelect, imageSamplerFilter ? imageSamplerFilter.value : '');
			updateSelectFilterStatus(imageSamplerFilterStatus, imageSamplerFilter ? imageSamplerFilter.value : '', counts, 'samplers');
			return;
		}
		const samplers = data.samplers || [];
		if (!samplers.length) {
			imageSamplerSelect.innerHTML = '<option value="euler">euler</option>';
			const counts = applySelectFilterQuery(imageSamplerSelect, imageSamplerFilter ? imageSamplerFilter.value : '');
			updateSelectFilterStatus(imageSamplerFilterStatus, imageSamplerFilter ? imageSamplerFilter.value : '', counts, 'samplers');
			return;
		}
		imageSamplerSelect.innerHTML = samplers
			.map((name) => `<option value="${escHtml(name)}">${escHtml(name)}</option>`)
			.join('');
		const counts = applySelectFilterQuery(imageSamplerSelect, imageSamplerFilter ? imageSamplerFilter.value : '');
		updateSelectFilterStatus(imageSamplerFilterStatus, imageSamplerFilter ? imageSamplerFilter.value : '', counts, 'samplers');
	} catch {
		imageSamplerSelect.innerHTML = '<option value="euler">euler</option>';
		const counts = applySelectFilterQuery(imageSamplerSelect, imageSamplerFilter ? imageSamplerFilter.value : '');
		updateSelectFilterStatus(imageSamplerFilterStatus, imageSamplerFilter ? imageSamplerFilter.value : '', counts, 'samplers');
	}
}

async function loadImageSchedulers() {
	if (!imageSchedulerSelect) return;
	const DEFAULT_SCHEDULERS = ['normal', 'karras', 'exponential', 'sgm_uniform', 'simple', 'ddim_uniform'];
	try {
		const res = await fetch('/api/image/schedulers');
		const data = await res.json();
		if (!res.ok) {
			imageSchedulerSelect.innerHTML = DEFAULT_SCHEDULERS
				.map((n) => `<option value="${escHtml(n)}">${escHtml(n)}</option>`).join('');
			const counts = applySelectFilterQuery(imageSchedulerSelect, imageSchedulerFilter ? imageSchedulerFilter.value : '');
			updateSelectFilterStatus(imageSchedulerFilterStatus, imageSchedulerFilter ? imageSchedulerFilter.value : '', counts, 'schedulers');
			return;
		}
		const schedulers = data.schedulers || [];
		if (!schedulers.length) {
			imageSchedulerSelect.innerHTML = DEFAULT_SCHEDULERS
				.map((n) => `<option value="${escHtml(n)}">${escHtml(n)}</option>`).join('');
			const counts = applySelectFilterQuery(imageSchedulerSelect, imageSchedulerFilter ? imageSchedulerFilter.value : '');
			updateSelectFilterStatus(imageSchedulerFilterStatus, imageSchedulerFilter ? imageSchedulerFilter.value : '', counts, 'schedulers');
			return;
		}
		imageSchedulerSelect.innerHTML = schedulers
			.map((name) => `<option value="${escHtml(name)}">${escHtml(name)}</option>`)
			.join('');
		const counts = applySelectFilterQuery(imageSchedulerSelect, imageSchedulerFilter ? imageSchedulerFilter.value : '');
		updateSelectFilterStatus(imageSchedulerFilterStatus, imageSchedulerFilter ? imageSchedulerFilter.value : '', counts, 'schedulers');
	} catch {
		imageSchedulerSelect.innerHTML = DEFAULT_SCHEDULERS
			.map((n) => `<option value="${escHtml(n)}">${escHtml(n)}</option>`).join('');
		const counts = applySelectFilterQuery(imageSchedulerSelect, imageSchedulerFilter ? imageSchedulerFilter.value : '');
		updateSelectFilterStatus(imageSchedulerFilterStatus, imageSchedulerFilter ? imageSchedulerFilter.value : '', counts, 'schedulers');
	}
}

function applySelectFilterQuery(selectEl, query) {
	if (!selectEl) return { visible: 0, total: 0 };
	const normalized = String(query || '').trim().toLowerCase();
	const selected = selectEl.value;
	let visible = 0;
	const total = selectEl.options.length;
	for (const option of selectEl.options) {
		if (!normalized) {
			option.hidden = false;
			visible += 1;
			continue;
		}
		const label = String(option.textContent || option.value || '').toLowerCase();
		const matches = option.value === selected || label.includes(normalized);
		option.hidden = !matches;
		if (matches) visible += 1;
	}
	return { visible, total };
}

function updateSelectFilterStatus(statusEl, query, counts, noun) {
	if (!statusEl) return;
	const q = String(query || '').trim();
	const visible = Number.isFinite(counts?.visible) ? counts.visible : 0;
	const total = Number.isFinite(counts?.total) ? counts.total : 0;
	if (!q) {
		statusEl.textContent = `Showing all ${noun}`;
		return;
	}
	if (visible === 0) {
		statusEl.textContent = `No ${noun} match "${q}"`;
		return;
	}
	statusEl.textContent = `Showing ${visible} of ${total} ${noun}`;
}

function bindSelectFilterInput(inputEl, selectEl, storageKey, statusEl, noun) {
	if (!inputEl || !selectEl) return;
	const saved = localStorage.getItem(storageKey) || '';
	if (saved) {
		inputEl.value = saved;
	}
	const initCounts = applySelectFilterQuery(selectEl, inputEl.value);
	updateSelectFilterStatus(statusEl, inputEl.value, initCounts, noun);

	inputEl.addEventListener('input', () => {
		const query = inputEl.value || '';
		if (query) {
			localStorage.setItem(storageKey, query);
		} else {
			localStorage.removeItem(storageKey);
		}
		const counts = applySelectFilterQuery(selectEl, query);
		updateSelectFilterStatus(statusEl, query, counts, noun);
	});

	inputEl.addEventListener('keydown', (event) => {
		if (event.key === 'Escape' && inputEl.value) {
			event.preventDefault();
			inputEl.value = '';
			localStorage.removeItem(storageKey);
			const counts = applySelectFilterQuery(selectEl, '');
			updateSelectFilterStatus(statusEl, '', counts, noun);
		} else if (event.key === 'ArrowDown') {
			event.preventDefault();
			selectEl.focus();
		}
	});

	selectEl.addEventListener('keydown', (event) => {
		if (event.key !== 'ArrowUp') return;
		const firstVisible = [...selectEl.options].find((opt) => !opt.hidden && !opt.disabled);
		if (!firstVisible) return;
		if (selectEl.value !== firstVisible.value) return;
		event.preventDefault();
		inputEl.focus();
		inputEl.classList.add('filter-input-focus-flash');
		setTimeout(() => inputEl.classList.remove('filter-input-focus-flash'), 420);
	});
}

/* --------------------------------------------------------------------------
	 Multi-LoRA stack
	 -------------------------------------------------------------------------- */
let loraStack = [];       // [{ id, name, strength }]
let _loraModelsCache = []; // fetched once and reused for new rows
let _loraRowCounter = 0;

async function loadImageLoraModels() {
	// Fetch the LoRA list once and cache it; refresh all existing rows' selects.
	try {
		const res = await fetch('/api/image/lora-models');
		const data = await res.json().catch(() => ({}));
		_loraModelsCache = Array.isArray(data.loras) ? data.loras : [];
		// Repopulate any existing row selects (e.g. after refresh)
		loraStackContainer?.querySelectorAll('.lora-row-select').forEach((sel) => {
			const cur = sel.value;
			sel.innerHTML = _buildLoraOptions();
			if (cur && [...sel.options].some((o) => o.value === cur)) sel.value = cur;
		});
	} catch {
		_loraModelsCache = [];
	}
}

function _buildLoraOptions() {
	return '<option value="">None</option>' +
		buildCompatGroupedOptions(_loraModelsCache, getBaseCheckpointFamily(), inferCheckpointFamily);
}

function addLoraRow() {
	if (!loraStackContainer) return;
	const id = ++_loraRowCounter;
	const row = document.createElement('div');
	row.className = 'lora-row';
	row.dataset.loraId = id;
	row.innerHTML = `
		<div class="lora-row-header">
			<span class="lora-row-label hint">LoRA ${id}</span>
			<button class="lora-row-enable btn btn-ghost btn-xs" type="button" aria-pressed="true" title="Toggle this LoRA on/off">On</button>
			<button class="lora-row-collapse btn btn-ghost btn-xs" type="button" aria-expanded="true" aria-controls="lora-row-body-${id}" aria-label="Collapse LoRA row">&#9660;</button>
			<button class="lora-row-remove btn btn-ghost btn-xs" type="button" aria-label="Remove LoRA row">&#x2212;</button>
		</div>
		<div class="lora-row-body" id="lora-row-body-${id}">
			<div class="lora-row-head">
				<div class="select-wrapper">
					<select class="lora-row-select" aria-label="LoRA model">
						${_buildLoraOptions()}
					</select>
				</div>
				<label class="inline-label">Str <span class="lora-strength-val">0.80</span>
					<input class="lora-row-strength" type="range" min="0" max="2" step="0.01" value="0.8" />
				</label>
			</div>
			<div class="lora-tag-cloud" hidden></div>
			<p class="lora-tag-hint" hidden>Click a tag to add it to your prompt.</p>
		</div>
	`;

	const sel = row.querySelector('.lora-row-select');
	const strengthRange = row.querySelector('.lora-row-strength');
	const strengthVal = row.querySelector('.lora-strength-val');
	const tagCloud = row.querySelector('.lora-tag-cloud');
	const tagHint = row.querySelector('.lora-tag-hint');
	const removeBtn = row.querySelector('.lora-row-remove');
	const enableBtn = row.querySelector('.lora-row-enable');
	const collapseBtn = row.querySelector('.lora-row-collapse');
	const rowBody = row.querySelector('.lora-row-body');

	enableBtn.addEventListener('click', () => {
		const enabled = row.classList.toggle('lora-disabled') === false;
		enableBtn.setAttribute('aria-pressed', String(enabled));
		enableBtn.textContent = enabled ? 'On' : 'Off';
		updateModelStackBadges();
	});

	collapseBtn.addEventListener('click', () => {
		const expanded = rowBody.hidden;
		rowBody.hidden = !expanded;
		rowBody.setAttribute('aria-hidden', expanded ? 'false' : 'true');
		collapseBtn.setAttribute('aria-expanded', String(expanded));
		collapseBtn.innerHTML = expanded ? '&#9660;' : '&#9654;';
	});

	sel.addEventListener('change', async () => {
		updateModelStackBadges();
		tagCloud.hidden = true;
		tagHint.hidden = true;
		tagCloud.innerHTML = '';
		const loraName = sel.value;
		if (!loraName) return;
		try {
			const res = await fetch(`/api/image/lora-tags?name=${encodeURIComponent(loraName)}`);
			const data = await res.json().catch(() => ({}));
			const tags = Array.isArray(data.tags) ? data.tags : [];
			if (tags.length) {
				tagCloud.innerHTML = tags
					.map((t) => `<span class="chip lora-tag-chip" title="Insert tag into prompt">${escHtml(t)}</span>`)
					.join('');
				tagCloud.hidden = false;
				tagHint.hidden = false;
				tagCloud.querySelectorAll('.lora-tag-chip').forEach((chip) => {
					chip.addEventListener('click', () => {
						if (!imagePrompt) return;
						const tag = chip.textContent.trim();
						const parts = (imagePrompt.value || '').split(',').map((p) => p.trim()).filter(Boolean);
						if (!parts.includes(tag)) parts.push(tag);
						imagePrompt.value = parts.join(', ');
						imagePrompt.focus();
					});
				});
			}
		} catch { /* ignore tag fetch errors */ }
	});

	strengthRange.addEventListener('input', () => {
		strengthVal.textContent = Number(strengthRange.value).toFixed(2);
	});

	removeBtn.addEventListener('click', () => {
		row.remove();
		updateModelStackBadges();
	});

	loraStackContainer.appendChild(row);
	updateModelStackBadges();
}

if (loraAddBtn) {
	loraAddBtn.addEventListener('click', () => addLoraRow());
}

function collectLoraStack() {
	if (!loraStackContainer) return [];
	return [...loraStackContainer.querySelectorAll('.lora-row')]
		.filter((row) => !row.classList.contains('lora-disabled'))
		.map((row) => ({
			name: row.querySelector('.lora-row-select')?.value || '',
			strength: Number(row.querySelector('.lora-row-strength')?.value || 0.8),
		})).filter((e) => e.name);
}

async function loadControlnetModels() {
	if (!controlnetModelSelect) return;
	try {
		const res = await fetch('/api/image/controlnet-models');
		const data = await res.json().catch(() => ({}));
		const models = Array.isArray(data.models) ? data.models : [];
		const current = controlnetModelSelect.value;
		controlnetModelSelect.innerHTML = '<option value="">None</option>' +
			buildCompatGroupedOptions(models, getBaseCheckpointFamily(), inferControlnetFamily);
		if (current && [...controlnetModelSelect.options].some((o) => o.value === current)) {
			controlnetModelSelect.value = current;
		}
		updateControlnetCompatibilityHint();
	} catch {
		controlnetModelSelect.innerHTML = '<option value="">None</option>';
		updateControlnetCompatibilityHint();
	}
}

async function loadControlnetPreprocessors() {
	if (!controlnetPreprocessorSelect) return;
	try {
		const res = await fetch('/api/image/controlnet-preprocessors');
		const data = await res.json().catch(() => ({}));
		const preprocessors = Array.isArray(data.preprocessors) ? data.preprocessors : ['none'];
		const current = controlnetPreprocessorSelect.value || 'none';
		controlnetPreprocessorSelect.innerHTML = preprocessors
			.map((p) => `<option value="${escHtml(p)}">${escHtml(p === 'none' ? 'none (raw image)' : p)}</option>`)
			.join('');
		if ([...controlnetPreprocessorSelect.options].some((o) => o.value === current)) {
			controlnetPreprocessorSelect.value = current;
		}
	} catch {
		controlnetPreprocessorSelect.innerHTML = '<option value="none">none (raw image)</option>';
	}
}

async function loadRefinerModels() {
	if (!refinerModelSelect) return;
	try {
		const res = await fetch('/api/image/refiner-models');
		const data = await res.json().catch(() => ({}));
		const models = Array.isArray(data.models) ? data.models : [];
		const current = refinerModelSelect.value;
		refinerModelSelect.innerHTML = '<option value="">None</option>' +
			buildCompatGroupedOptions(models, getBaseCheckpointFamily(), inferCheckpointFamily);
		if (current && [...refinerModelSelect.options].some((o) => o.value === current)) {
			refinerModelSelect.value = current;
		}
	} catch {
		if (refinerModelSelect) refinerModelSelect.innerHTML = '<option value="">None</option>';
	}
}

async function loadVaeModels() {
	if (!vaeModelSelect) return;
	try {
		const res = await fetch('/api/image/vae-models');
		const data = await res.json().catch(() => ({}));
		const vaes = Array.isArray(data.vaes) ? data.vaes : [];
		const current = vaeModelSelect.value;
		vaeModelSelect.innerHTML = '<option value="">Default</option>' +
			buildCompatGroupedOptions(vaes, getBaseCheckpointFamily(), inferCheckpointFamily);
		if (current && [...vaeModelSelect.options].some((o) => o.value === current)) {
			vaeModelSelect.value = current;
		}
	} catch {
		if (vaeModelSelect) vaeModelSelect.innerHTML = '<option value="">Default</option>';
	}
}

async function loadHiresfixUpscalers() {
	if (!hiresfixUpscalerSelect) return;
	try {
		const res = await fetch('/api/image/upscaler-models');
		const data = await res.json().catch(() => ({}));
		const models = Array.isArray(data.models) ? data.models : [];
		hiresfixUpscalerSelect.innerHTML = '<option value="">None</option>' + models
			.map((name) => `<option value="${escHtml(name)}">${escHtml(name)}</option>`)
			.join('');
	} catch {
		if (hiresfixUpscalerSelect) hiresfixUpscalerSelect.innerHTML = '<option value="">None</option>';
	}
}

async function checkStatus() {
	try {
		const [statusRes, healthRes] = await Promise.all([
			fetch('/api/status'),
			fetch('/api/healthz'),
		]);
		const data = await statusRes.json();
		const healthData = await healthRes.json().catch(() => ({}));

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
			if (!isComfyWsOpen()) {
				setPreviewTransportMode('polling', 'Attempting ComfyUI WebSocket connection. HTTP polling fallback is active until connected.');
			}
			await loadImageModels();
			await loadImageSamplers();
			await loadImageSchedulers();
			await loadImageLoraModels();
			await loadRefinerModels();
			await loadVaeModels();
			await loadControlnetModels();
			await loadControlnetPreprocessors();
			await loadHiresfixUpscalers();
			connectComfyWebSocket();
		} else {
			imageEngineStatus.textContent = 'ComfyUI offline - start server at localhost:8188';
			imageEngineStatus.style.color = 'var(--clr-accent-neg)';
			setPreviewTransportMode('offline');
			setImageModelMessage('ComfyUI unavailable');
			if (controlnetModelSelect) controlnetModelSelect.innerHTML = '<option value="">None</option>';
			if (refinerModelSelect) refinerModelSelect.innerHTML = '<option value="">None</option>';
			if (vaeModelSelect) vaeModelSelect.innerHTML = '<option value="">Default</option>';
			if (hiresfixUpscalerSelect) hiresfixUpscalerSelect.innerHTML = '<option value="">None</option>';
		}

		renderDiagnosticsSnapshot({
			textOk,
			imageOk,
			textStatusLabel: textOk ? `online (${getActiveSelectOptionCount(modelSelect)})` : 'offline',
			imageStatusLabel: imageOk ? 'online' : 'offline',
			checkpoints: getActiveSelectOptionCount(imageModelSelect),
			samplers: getActiveSelectOptionCount(imageSamplerSelect),
			backendHealthOk: !!healthData.ok,
			backendHealthLabel: healthData.ok
				? `ok (build ${healthData.app?.template_version || 'unknown'})`
				: 'unhealthy',
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
		setPreviewTransportMode('offline', 'Backend status endpoint is unavailable, so preview transport status is unknown.');
		renderDiagnosticsSnapshot({
			textOk: false,
			imageOk: false,
			textStatusLabel: 'unknown',
			imageStatusLabel: 'unknown',
			checkpoints: '-',
			samplers: '-',
			backendHealthOk: false,
			backendHealthLabel: 'unknown',
			lastRunLabel: new Date().toLocaleTimeString(),
			summary: 'Diagnostics request failed',
			hint: 'Could not reach backend status endpoint.',
		});
	}
}

if (diagCopyBtn) {
	diagCopyBtn.addEventListener('keydown', onDiagnosticsActionsKeydown);
	diagCopyBtn.addEventListener('click', async () => {
		try {
			await copyTextToClipboard(getDiagnosticsStatusSnapshotText());
			appendDiagnosticsConsoleLine('Copied diagnostics snapshot.', 'info');
			showToast('Diagnostics snapshot copied.', 'pos');
		} catch (err) {
			appendDiagnosticsConsoleLine(`Could not copy diagnostics snapshot: ${err.message}`, 'warn');
			showToast('Could not copy diagnostics snapshot.', 'neg');
		}
	});
}

if (diagnosticsRunBtn) {
	diagnosticsRunBtn.addEventListener('keydown', onDiagnosticsActionsKeydown);
	diagnosticsRunBtn.addEventListener('click', async () => {
		await runDiagnosticsChecks(true);
	});
}

if (diagDisableLogRepairBtn) {
	diagDisableLogRepairBtn.addEventListener('keydown', onDiagnosticsActionsKeydown);
	diagDisableLogRepairBtn.addEventListener('click', async () => {
		await repairDisableLogStore();
	});
}

if (diagClearRepairStatusBtn) {
	diagClearRepairStatusBtn.addEventListener('keydown', onDiagnosticsActionsKeydown);
	diagClearRepairStatusBtn.addEventListener('click', () => {
		clearDiagRepairStatusLine();
		appendDiagnosticsConsoleLine('Cleared diagnostics repair status.', 'info');
		showToast('Cleared repair status.', 'pos');
	});
}

if (diagWsRetryBtn) {
	diagWsRetryBtn.addEventListener('keydown', onDiagnosticsActionsKeydown);
	diagWsRetryBtn.addEventListener('click', () => {
		const attempted = forceRetryComfyWebSocket('diagnostics panel');
		if (attempted) {
			appendDiagnosticsConsoleLine('Triggered ComfyUI websocket retry attempt.', 'info');
			showToast('WebSocket retry requested.', 'pos');
		} else {
			appendDiagnosticsConsoleLine('ComfyUI websocket already connected.', 'info');
			showToast('WebSocket already connected.', 'pos');
		}
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

if (diagDrawer) {
	diagDrawer.addEventListener('keydown', (event) => {
		if (event.key !== 'Escape') return;
		event.preventDefault();
		event.stopPropagation();
		setDiagnosticsDrawerOpen(false);
	});
}

if (diagDrawerCommandForm && diagDrawerCommandInput) {
	diagDrawerCommandForm.addEventListener('submit', async (event) => {
		event.preventDefault();
		const raw = diagDrawerCommandInput.value;
		diagDrawerCommandInput.value = '';
		if (raw.trim()) {
			diagHistory.push(raw);
			if (diagHistory.length > 50) diagHistory.shift();
			persistDiagnosticsCommandHistoryState();
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
			diagDrawerCommandInput.setSelectionRange(diagDrawerCommandInput.value.length, diagDrawerCommandInput.value.length);
		} else if (event.key === 'Tab') {
			event.preventDefault();
			const raw = diagDrawerCommandInput.value.trim().toLowerCase();
			if (!raw) return;
			const matches = DIAGNOSTICS_COMMAND_SUGGESTIONS.filter((candidate) => candidate.startsWith(raw));
			if (matches.length === 1) {
				diagDrawerCommandInput.value = matches[0];
				diagDrawerCommandInput.setSelectionRange(matches[0].length, matches[0].length);
				return;
			}
			if (matches.length > 1) {
				appendDiagnosticsConsoleLine(`Matches: ${matches.join(', ')}`);
			}
		} else if (event.key === 'Escape') {
			event.preventDefault();
			diagHistoryIndex = -1;
			diagHistoryDraft = '';
			diagDrawerCommandInput.value = '';
			appendDiagnosticsConsoleLine('Command input cleared.');
		} else if ((event.key === 'l' || event.key === 'L') && event.ctrlKey) {
			event.preventDefault();
			if (diagDrawerOutput) diagDrawerOutput.innerHTML = '';
			appendDiagnosticsConsoleLine('Console cleared.');
		} else if ((event.key === 'r' || event.key === 'R') && event.ctrlKey) {
			event.preventDefault();
			const attempted = forceRetryComfyWebSocket('diagnostics shortcut');
			appendDiagnosticsConsoleLine(attempted ? 'Triggered ComfyUI websocket retry attempt.' : 'ComfyUI websocket already connected.');
		} else if (event.key === 'ArrowDown') {
			event.preventDefault();
			if (diagHistoryIndex <= 0) {
				diagHistoryIndex = -1;
				diagDrawerCommandInput.value = diagHistoryDraft;
			} else {
				diagHistoryIndex--;
				diagDrawerCommandInput.value = diagHistory[diagHistory.length - 1 - diagHistoryIndex];
			}
			diagDrawerCommandInput.setSelectionRange(diagDrawerCommandInput.value.length, diagDrawerCommandInput.value.length);
		} else if (event.key === 'Home' && event.ctrlKey) {
			event.preventDefault();
			if (diagHistory.length === 0) return;
			if (diagHistoryIndex === -1) diagHistoryDraft = diagDrawerCommandInput.value;
			diagHistoryIndex = diagHistory.length - 1;
			diagDrawerCommandInput.value = diagHistory[0];
			diagDrawerCommandInput.setSelectionRange(diagDrawerCommandInput.value.length, diagDrawerCommandInput.value.length);
		} else if (event.key === 'End' && event.ctrlKey) {
			event.preventDefault();
			diagHistoryIndex = -1;
			diagDrawerCommandInput.value = diagHistoryDraft;
			diagDrawerCommandInput.setSelectionRange(diagDrawerCommandInput.value.length, diagDrawerCommandInput.value.length);
		}
	});
}

if (diagDrawerOutput) {
	appendDiagnosticsConsoleLine('Diagnostics console ready. Type help for commands.');
}

// Restore diagnostics drawer open/collapsed state from localStorage
if (diagDrawer && diagDrawerCollapsed !== null) {
	setDiagnosticsDrawerOpen(!diagDrawerCollapsed);
}

if (configSaveBtn) {
	configSaveBtn.addEventListener('click', saveServiceConfig);
}

if (configModelsMigrateBtn) {
	configModelsMigrateBtn.addEventListener('click', migrateSharedModelFolders);
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

if (configModelsBrowseBtn) {
	configModelsBrowseBtn.addEventListener('click', async () => {
		await browseServicePath('models');
	});
}

function onConfigServiceControlsKeydown(event) {
	const key = event.key;
	if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
	const target = event.currentTarget;
	if (!(target instanceof HTMLElement)) return;
	let buttons = [];
	if (target.id.startsWith('config-ollama-')) {
		buttons = [configOllamaStartBtn, configOllamaRestartBtn, configOllamaStopBtn].filter(Boolean);
	} else if (target.id.startsWith('config-comfy-')) {
		buttons = [configComfyStartBtn, configComfyRestartBtn, configComfyStopBtn].filter(Boolean);
	} else {
		buttons = [configFlaskRestartBtn].filter(Boolean);
	}
	if (buttons.length < 2) return;
	const currentIndex = buttons.indexOf(target);
	if (currentIndex < 0) return;
	event.preventDefault();
	let nextIndex = currentIndex;
	if (key === 'Home') {
		nextIndex = 0;
	} else if (key === 'End') {
		nextIndex = buttons.length - 1;
	} else if (key === 'ArrowRight') {
		nextIndex = (currentIndex + 1) % buttons.length;
	} else if (key === 'ArrowLeft') {
		nextIndex = (currentIndex - 1 + buttons.length) % buttons.length;
	}
	const nextButton = buttons[nextIndex];
	if (nextButton) nextButton.focus();
}

if (configOllamaStartBtn) {
	configOllamaStartBtn.addEventListener('click', async () => {
		await controlService('ollama', 'start', configOllamaStatus, [configOllamaStartBtn, configOllamaRestartBtn, configOllamaStopBtn]);
	});
	configOllamaStartBtn.addEventListener('keydown', onConfigServiceControlsKeydown);
}

if (configOllamaRestartBtn) {
	configOllamaRestartBtn.addEventListener('click', async () => {
		await controlService('ollama', 'restart', configOllamaStatus, [configOllamaStartBtn, configOllamaRestartBtn, configOllamaStopBtn]);
	});
	configOllamaRestartBtn.addEventListener('keydown', onConfigServiceControlsKeydown);
}

if (configOllamaStopBtn) {
	configOllamaStopBtn.addEventListener('click', async () => {
		await controlService('ollama', 'stop', configOllamaStatus, [configOllamaStartBtn, configOllamaRestartBtn, configOllamaStopBtn]);
	});
	configOllamaStopBtn.addEventListener('keydown', onConfigServiceControlsKeydown);
}

if (configComfyStartBtn) {
	configComfyStartBtn.addEventListener('click', async () => {
		await controlService('comfyui', 'start', configComfyStatus, [configComfyStartBtn, configComfyRestartBtn, configComfyStopBtn]);
	});
	configComfyStartBtn.addEventListener('keydown', onConfigServiceControlsKeydown);
}

if (configComfyRestartBtn) {
	configComfyRestartBtn.addEventListener('click', async () => {
		await controlService('comfyui', 'restart', configComfyStatus, [configComfyStartBtn, configComfyRestartBtn, configComfyStopBtn]);
	});
	configComfyRestartBtn.addEventListener('keydown', onConfigServiceControlsKeydown);
}

if (configComfyStopBtn) {
	configComfyStopBtn.addEventListener('click', async () => {
		await controlService('comfyui', 'stop', configComfyStatus, [configComfyStartBtn, configComfyRestartBtn, configComfyStopBtn]);
	});
	configComfyStopBtn.addEventListener('keydown', onConfigServiceControlsKeydown);
}

// ComfyUI update handlers
if (configComfyCheckUpdatesBtn) {
	configComfyCheckUpdatesBtn.addEventListener('click', async () => {
		try {
			configComfyCheckUpdatesBtn.disabled = true;
			configComfyVersionInfo.textContent = 'Version info: fetching...';
			const resp = await fetch('/api/service/comfyui/version');
			const data = await resp.json();
			
			if (data.error) {
				configComfyVersionInfo.textContent = `Version info: ${data.error}`;
			} else {
				const versionText = data.current_version || data.current_commit || 'unknown';
				const branchText = data.current_branch ? ` (${data.current_branch})` : '';
				configComfyVersionInfo.textContent = `Version info: ${versionText}${branchText}`;
				configComfyUpdateBtn.disabled = false;
			}
		} catch (err) {
			configComfyVersionInfo.textContent = `Version info: Failed to fetch - ${err.message}`;
		} finally {
			configComfyCheckUpdatesBtn.disabled = false;
		}
	});
}

if (configComfyUpdateBtn) {
	configComfyUpdateBtn.addEventListener('click', async () => {
		try {
			configComfyUpdateBtn.disabled = true;
			configComfyVersionInfo.textContent = 'Version info: updating...';
			
			const resp = await fetch('/api/service/comfyui/update', { method: 'POST' });
			const data = await resp.json();
			
			if (!resp.ok) {
				configComfyVersionInfo.textContent = `Version info: Update failed - ${data.error}`;
				configComfyUpdateBtn.disabled = false;
				return;
			}
			
			const jobId = data.job.id;
			
			// Poll update status
			let finished = false;
			let attempts = 0;
			const maxAttempts = 120; // 2 minutes total
			
			while (!finished && attempts < maxAttempts) {
				await new Promise(resolve => setTimeout(resolve, 1000));
				
				const statusResp = await fetch(`/api/service/comfyui/update-status/${jobId}`);
				const statusData = await statusResp.json();
				
				if (statusData.status === 'done') {
					configComfyVersionInfo.textContent = 'Version info: Update complete! Restarting ComfyUI...';
					
					// Auto-restart ComfyUI
					try {
						await controlService('comfyui', 'restart', configComfyStatus, [configComfyStartBtn, configComfyRestartBtn, configComfyStopBtn]);
					} catch (err) {
						configComfyStatus.textContent = `ComfyUI restart error: ${err.message}`;
					}
					finished = true;
				} else if (statusData.status === 'error') {
					configComfyVersionInfo.textContent = `Version info: Update failed - ${statusData.error}`;
					finished = true;
				} else {
					configComfyVersionInfo.textContent = `Version info: updating... (${attempts}s)`;
				}
				attempts++;
			}
			
			if (!finished) {
				configComfyVersionInfo.textContent = 'Version info: Update timed out';
			}
			
			configComfyUpdateBtn.disabled = true;
		} catch (err) {
			configComfyVersionInfo.textContent = `Version info: Update error - ${err.message}`;
			configComfyUpdateBtn.disabled = false;
		}
	});
}

// Load initial version info when configuration tab loads
async function loadComfyuiVersionInfo() {
	try {
		const resp = await fetch('/api/service/comfyui/version');
		const data = await resp.json();
		
		if (data.error) {
			configComfyVersionInfo.textContent = `Version info: ${data.error}`;
		} else {
			const versionText = data.current_version || data.current_commit || 'unknown';
			const branchText = data.current_branch ? ` (${data.current_branch})` : '';
			configComfyVersionInfo.textContent = `Version info: ${versionText}${branchText}`;
		}
	} catch (err) {
		configComfyVersionInfo.textContent = `Version info: Failed to fetch - ${err.message}`;
	}
}

function renderComfyCustomNodeBrowser() {
	if (!configComfyNodesList || !configComfyNodesStatus) return;
	const query = String(configComfyNodesSearchInput?.value || '').trim().toLowerCase();
	const filtered = query
		? comfyCustomNodeRows.filter((row) => {
			const haystack = `${row.display_name || ''} ${row.type || ''} ${row.category || ''} ${row.python_module || ''}`.toLowerCase();
			return haystack.includes(query);
		})
		: comfyCustomNodeRows;

	if (!filtered.length) {
		configComfyNodesList.innerHTML = '<div class="config-comfy-node-row"><span class="hint">No matching nodes.</span></div>';
	} else {
		configComfyNodesList.innerHTML = filtered.map((row) => {
			const displayName = escHtml(row.display_name || row.type || 'Unnamed node');
			const nodeType = escHtml(row.type || '');
			const category = escHtml(row.category || 'uncategorized');
			const moduleName = escHtml(row.python_module || 'module unknown');
			const chipLabel = row.is_custom ? 'custom' : 'built-in';
			const chipClass = row.is_custom ? 'config-comfy-node-chip is-custom' : 'config-comfy-node-chip';
			return `<div class="config-comfy-node-row"><div class="config-comfy-node-head"><span class="config-comfy-node-name">${displayName}</span><span class="${chipClass}">${chipLabel}</span></div><div class="config-comfy-node-type">type: ${nodeType}</div><div class="config-comfy-node-meta">category: ${category}</div><div class="config-comfy-node-meta">module: ${moduleName}</div></div>`;
		}).join('');
	}

	const customCount = comfyCustomNodeRows.filter((row) => row.is_custom).length;
	const total = comfyCustomNodeRows.length;
	if (query) {
		configComfyNodesStatus.textContent = `Showing ${filtered.length} of ${total} nodes (${customCount} custom) for "${query}".`;
		return;
	}
	configComfyNodesStatus.textContent = `Loaded ${total} nodes (${customCount} custom).`;
}

function renderComfyCustomNodePackages() {
	if (!configComfyPackagesList || !configComfyPackagesStatus) return;
	if (!comfyCustomNodePackages.length) {
		configComfyPackagesList.innerHTML = '<div class="config-comfy-package-row"><span class="hint">No custom-node package folders detected.</span></div>';
		configComfyPackagesStatus.textContent = 'No custom-node package folders found.';
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = 'Select a package for details.';
		return;
	}
	if (!comfyCustomNodePackages.some((row) => row.name === comfySelectedPackageName)) {
		comfySelectedPackageName = '';
	}
	configComfyPackagesList.innerHTML = comfyCustomNodePackages.map((row) => {
		const name = escHtml(row.name || 'unknown');
		const enabled = Boolean(row.enabled);
		const chipClass = enabled ? 'config-comfy-package-chip is-enabled' : 'config-comfy-package-chip';
		const chipText = enabled ? 'enabled' : 'disabled';
		const toggleLabel = enabled ? 'Disable' : 'Enable';
		const selectedClass = row.name === comfySelectedPackageName ? ' is-selected' : '';
		return `<div class="config-comfy-package-row${selectedClass}" data-package-name="${name}"><span class="config-comfy-package-name">${name}</span><span class="config-comfy-package-actions"><span class="${chipClass}">${chipText}</span><button class="btn btn-ghost btn-xs" type="button" data-package-action="details" data-package-name="${name}">Details</button><button class="btn btn-ghost btn-xs" type="button" data-package-action="open" data-package-name="${name}">Open</button><button class="btn btn-ghost btn-xs" type="button" data-package-action="toggle" data-package-enabled="${enabled ? '1' : '0'}" data-package-name="${name}">${toggleLabel}</button><button class="btn btn-ghost btn-xs" type="button" data-package-action="update" data-package-name="${name}">Update</button></span></div>`;
	}).join('');
	const enabledCount = comfyCustomNodePackages.filter((row) => row.enabled).length;
	configComfyPackagesStatus.textContent = `Detected ${comfyCustomNodePackages.length} package folders (${enabledCount} enabled).`;
}

function renderComfyPackageDetails(data) {
	if (!configComfyPackageDetails) return;
	if (!data || !data.ok) {
		configComfyPackageDetails.textContent = 'Select a package for details.';
		return;
	}
	const git = data.git || {};
	if (!git.is_git) {
		configComfyPackageDetails.textContent = `${data.name}: folder tracked, not a git repository.`;
		return;
	}
	const branch = git.branch || 'unknown';
	const commit = git.commit || 'unknown';
	const remote = git.remote || 'no remote';
	const ahead = Number.isFinite(Number(git.ahead)) ? Number(git.ahead) : 0;
	const behind = Number.isFinite(Number(git.behind)) ? Number(git.behind) : 0;
	const dirty = git.dirty ? 'dirty' : 'clean';
	configComfyPackageDetails.textContent = `${data.name}: ${branch}@${commit} • ${dirty} • ahead ${ahead} / behind ${behind} • ${remote}`;
}

async function loadComfyCustomNodePackageDetails(packageName) {
	if (!packageName) return;
	if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Loading details for ${packageName}...`;
	try {
		const resp = await fetch(`/api/comfy/custom-node-packages/details?name=${encodeURIComponent(packageName)}`);
		const data = await resp.json().catch(() => ({}));
		if (!resp.ok) {
			throw new Error(data.error || `HTTP ${resp.status}`);
		}
		renderComfyPackageDetails(data);
	} catch (err) {
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Package details error: ${err.message}`;
	}
}

async function openComfyCustomNodePackageFolder(packageName) {
	if (!packageName) return;
	if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Opening folder for ${packageName}...`;
	try {
		const resp = await fetch('/api/comfy/custom-node-packages/open', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ name: packageName }),
		});
		const data = await resp.json().catch(() => ({}));
		if (!resp.ok) {
			throw new Error(data.error || `HTTP ${resp.status}`);
		}
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Opened folder: ${packageName}`;
	} catch (err) {
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Open folder error: ${err.message}`;
	}
}

async function toggleComfyCustomNodePackageEnabled(packageName, enable) {
	if (!packageName) return;
	if (configComfyPackageDetails) configComfyPackageDetails.textContent = `${enable ? 'Enabling' : 'Disabling'} package ${packageName}...`;
	try {
		const resp = await fetch('/api/comfy/custom-node-packages/toggle', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ name: packageName, enabled: !!enable }),
		});
		const data = await resp.json().catch(() => ({}));
		if (!resp.ok) {
			throw new Error(data.error || `HTTP ${resp.status}`);
		}
		await loadComfyCustomNodePackages();
		comfySelectedPackageName = data.renamed_to || packageName;
		if (configComfyPackageDetails) {
			const state = data.enabled ? 'enabled' : 'disabled';
			configComfyPackageDetails.textContent = `${packageName}: ${state} (renamed to ${comfySelectedPackageName}).`;
		}
		await loadComfyCustomNodePackageDetails(comfySelectedPackageName);
	} catch (err) {
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Toggle package error: ${err.message}`;
	}
}

async function updateComfyCustomNodePackage(packageName) {
	if (!packageName) return;
	if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Updating package ${packageName}...`;
	try {
		const resp = await fetch('/api/comfy/custom-node-packages/update', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ name: packageName }),
		});
		const data = await resp.json().catch(() => ({}));
		if (!resp.ok) {
			throw new Error(data.error || `HTTP ${resp.status}`);
		}
		renderComfyPackageDetails({ ok: true, name: data.name, git: data.git || {} });
		if (configComfyPackageDetails && data.message) {
			configComfyPackageDetails.textContent += ` ${data.message}`;
		}
	} catch (err) {
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Update package error: ${err.message}`;
	}
}

function resetComfyDisablePreview() {
	comfyDisablePreviewReady = false;
	comfyDisablePreviewSelectedNames = new Set();
	comfyDisablePreviewStats = { wouldDisable: 0, skipped: 0, failed: 0 };
	if (configComfyDisablePreview) configComfyDisablePreview.hidden = true;
	if (configComfyDisablePreviewSummary) configComfyDisablePreviewSummary.textContent = 'Preview not loaded.';
	if (configComfyDisablePreviewFilter) configComfyDisablePreviewFilter.value = comfyDisablePreviewFilterQuery;
	if (configComfyDisablePreviewSelectedOnly) configComfyDisablePreviewSelectedOnly.checked = comfyDisablePreviewSelectedOnlyPref;
	if (configComfyDisablePreviewList) configComfyDisablePreviewList.innerHTML = '';
	if (configComfyDisablePreviewConfirmBtn) configComfyDisablePreviewConfirmBtn.disabled = true;
}

function applyComfyDisablePreviewFilter() {
	if (!configComfyDisablePreviewList) return;
	const query = String(configComfyDisablePreviewFilter?.value || '').trim().toLowerCase();
	const selectedOnly = !!configComfyDisablePreviewSelectedOnly?.checked;
	const rows = [...configComfyDisablePreviewList.querySelectorAll('[data-disable-preview-row="1"]')];
	rows.forEach((row) => {
		const name = String(row.getAttribute('data-preview-name') || '').toLowerCase();
		const isSelectable = row.getAttribute('data-disable-preview-selectable') === '1';
		const selected = row.getAttribute('data-disable-preview-selected') === '1';
		const textVisible = query ? name.includes(query) : true;
		const selectionVisible = !selectedOnly || (isSelectable && selected);
		row.hidden = !(textVisible && selectionVisible);
	});
	syncComfyDisablePreviewConfirmLabel();
}

function syncComfyDisablePreviewConfirmLabel() {
	if (!configComfyDisablePreviewConfirmBtn) return;
	const count = comfyDisablePreviewSelectedNames.size;
	const allSelectable = configComfyDisablePreviewList
		? [...configComfyDisablePreviewList.querySelectorAll('input[data-disable-preview-select="1"]')]
		: [];
	const totalSelectable = allSelectable.length;
	const visibleSelectable = allSelectable.filter((box) => !box.closest('[data-disable-preview-row="1"]')?.hidden).length;
	if (configComfyDisablePreviewSummary && comfyDisablePreviewReady) {
		configComfyDisablePreviewSummary.textContent = `Would disable ${comfyDisablePreviewStats.wouldDisable}, skipped ${comfyDisablePreviewStats.skipped}, failed ${comfyDisablePreviewStats.failed}. Selection ${count}/${totalSelectable} (${visibleSelectable} visible).`;
	}
	configComfyDisablePreviewConfirmBtn.textContent = count > 0
		? `Confirm disable selected (${count})`
		: 'Confirm disable selected';
	configComfyDisablePreviewConfirmBtn.disabled = !comfyDisablePreviewReady || count === 0;
}

function getSortedComfyDisablePreviewSelectedNames() {
	return [...comfyDisablePreviewSelectedNames].filter(Boolean).sort((a, b) => a.localeCompare(b));
}

function setComfyDisablePreviewExportStatus(message, persist = true) {
	const text = String(message || '').trim();
	if (configComfyDisablePreviewExportStatus) {
		configComfyDisablePreviewExportStatus.textContent = text || 'No export yet.';
	}
	if (!persist) return;
	if (text) {
		comfyDisablePreviewLastExport = text;
		localStorage.setItem(CONFIG_COMFY_DISABLE_PREVIEW_LAST_EXPORT_KEY, text);
	} else {
		comfyDisablePreviewLastExport = '';
		localStorage.removeItem(CONFIG_COMFY_DISABLE_PREVIEW_LAST_EXPORT_KEY);
	}
}

function syncComfyDisablePreviewExportHistoryClearButtonState() {
	const hasItems = comfyDisablePreviewExportHistory.length > 0;
	if (configComfyDisablePreviewExportHistoryClearBtn) {
		configComfyDisablePreviewExportHistoryClearBtn.disabled = !hasItems;
	}
	if (configComfyDisablePreviewExportHistoryCopyBtn) {
		configComfyDisablePreviewExportHistoryCopyBtn.disabled = !hasItems;
	}
	if (configComfyDisablePreviewExportHistoryCopyJsonBtn) {
		configComfyDisablePreviewExportHistoryCopyJsonBtn.disabled = !hasItems;
	}
	if (configComfyDisablePreviewExportHistoryDownloadBtn) {
		configComfyDisablePreviewExportHistoryDownloadBtn.disabled = !hasItems;
	}
	if (configComfyDisablePreviewExportHistoryDownloadCsvBtn) {
		configComfyDisablePreviewExportHistoryDownloadCsvBtn.disabled = !hasItems;
	}
	if (configComfyDisablePreviewExportHistoryDownloadJsonBtn) {
		configComfyDisablePreviewExportHistoryDownloadJsonBtn.disabled = !hasItems;
	}
}

function renderComfyDisablePreviewExportHistory() {
	if (configComfyDisablePreviewExportHistoryMeta) {
		configComfyDisablePreviewExportHistoryMeta.textContent = `History ${comfyDisablePreviewExportHistory.length}/${CONFIG_COMFY_DISABLE_PREVIEW_EXPORT_HISTORY_MAX}`;
	}
	if (!configComfyDisablePreviewExportHistory) return;
	if (!comfyDisablePreviewExportHistory.length) {
		configComfyDisablePreviewExportHistory.innerHTML = '<li class="hint">No recent exports.</li>';
		syncComfyDisablePreviewExportHistoryClearButtonState();
		return;
	}
	configComfyDisablePreviewExportHistory.innerHTML = comfyDisablePreviewExportHistory
		.map((item) => `<li>${escHtml(item)}</li>`)
		.join('');
	syncComfyDisablePreviewExportHistoryClearButtonState();
}

function recordComfyDisablePreviewExportHistory(entry) {
	const value = String(entry || '').trim();
	if (!value) return;
	comfyDisablePreviewExportHistory = [value, ...comfyDisablePreviewExportHistory.filter((item) => item !== value)].slice(0, CONFIG_COMFY_DISABLE_PREVIEW_EXPORT_HISTORY_MAX);
	localStorage.setItem(CONFIG_COMFY_DISABLE_PREVIEW_EXPORT_HISTORY_KEY, JSON.stringify(comfyDisablePreviewExportHistory));
	renderComfyDisablePreviewExportHistory();
}

function clearComfyDisablePreviewExportHistory() {
	comfyDisablePreviewExportHistory = [];
	localStorage.removeItem(CONFIG_COMFY_DISABLE_PREVIEW_EXPORT_HISTORY_KEY);
	setComfyDisablePreviewExportStatus('', true);
	renderComfyDisablePreviewExportHistory();
}

function renderComfyDisableNonCorePreview(data) {
	if (!configComfyDisablePreview || !configComfyDisablePreviewSummary || !configComfyDisablePreviewList) return;
	const rows = Array.isArray(data?.results) ? data.results : [];
	comfyDisablePreviewSelectedNames = new Set();
	comfyDisablePreviewStats = {
		wouldDisable: Number(data?.success || 0),
		skipped: Number(data?.skipped || 0),
		failed: Number(data?.failed || 0),
	};
	const lines = rows.map((row) => {
		const name = escHtml(row.name || 'unknown');
		const rowNameAttr = escHtml(row.name || 'unknown');
		if (row.would_disable) {
			comfyDisablePreviewSelectedNames.add(row.name || '');
			return `<label class="config-comfy-disable-preview-item is-action" data-disable-preview-row="1" data-disable-preview-selectable="1" data-disable-preview-selected="1" data-preview-name="${rowNameAttr}"><input type="checkbox" data-disable-preview-select="1" data-package-name="${name}" checked /><span class="config-comfy-disable-preview-chip is-action">disable</span> ${name} -> ${escHtml(row.renamed_to || '')}</label>`;
		}
		if (row.skipped) {
			return `<div class="config-comfy-disable-preview-item is-skip" data-disable-preview-row="1" data-disable-preview-selectable="0" data-disable-preview-selected="0" data-preview-name="${rowNameAttr}"><span class="config-comfy-disable-preview-chip is-skip">skip</span> ${name}: ${escHtml(row.reason || 'n/a')}</div>`;
		}
		if (row.ok) {
			return `<div class="config-comfy-disable-preview-item" data-disable-preview-row="1" data-disable-preview-selectable="0" data-disable-preview-selected="0" data-preview-name="${rowNameAttr}"><span class="config-comfy-disable-preview-chip">ok</span> ${name}: ready</div>`;
		}
		return `<div class="config-comfy-disable-preview-item is-error" data-disable-preview-row="1" data-disable-preview-selectable="0" data-disable-preview-selected="0" data-preview-name="${rowNameAttr}"><span class="config-comfy-disable-preview-chip is-error">error</span> ${name}: ${escHtml(row.error || 'unknown')}</div>`;
	});
	configComfyDisablePreview.hidden = false;
	configComfyDisablePreviewSummary.textContent = `Would disable ${comfyDisablePreviewStats.wouldDisable}, skipped ${comfyDisablePreviewStats.skipped}, failed ${comfyDisablePreviewStats.failed}.`;
	configComfyDisablePreviewList.innerHTML = lines.length ? lines.join('') : '<div class="config-comfy-disable-preview-item">No packages found.</div>';
	comfyDisablePreviewReady = true;
	applyComfyDisablePreviewFilter();
	syncComfyDisablePreviewConfirmLabel();
}

function renderComfyDisableOperationLog(data) {
	if (!configComfyDisableLogStatus || !configComfyDisableLogList) return;
	const entries = Array.isArray(data?.entries) ? data.entries : [];
	const pending = entries.filter((entry) => Number(entry?.pending_revert_count || 0) > 0).length;
	const filteredEntries = comfyDisableLogPendingOnly
		? entries.filter((entry) => Number(entry?.pending_revert_count || 0) > 0)
		: entries;
	configComfyDisableLogStatus.textContent = `Disable log: ${entries.length} batch${entries.length === 1 ? '' : 'es'}, ${pending} pending revert${comfyDisableLogPendingOnly ? `, showing ${filteredEntries.length}` : ''}.`;
	if (configComfyDisableLogRevertLastBtn) {
		configComfyDisableLogRevertLastBtn.disabled = pending === 0 || comfyDisableLogRevertLastInFlight;
	}
	if (!filteredEntries.length) {
		configComfyDisableLogList.innerHTML = '<div class="config-comfy-package-row"><span class="hint">No disable operations logged yet.</span></div>';
		return;
	}
	configComfyDisableLogList.innerHTML = filteredEntries.slice(0, 8).map((entry) => {
		const batchId = escHtml(String(entry?.id || 'batch'));
		const rawBatchId = String(entry?.id || '').trim();
		const batchIdAttr = escHtml(rawBatchId);
		const createdAt = escHtml(String(entry?.created_at || 'unknown time'));
		const summary = entry?.summary || {};
		const success = Number(summary?.success || 0);
		const skipped = Number(summary?.skipped || 0);
		const failed = Number(summary?.failed || 0);
		const pendingCount = Number(entry?.pending_revert_count || 0);
		const stateLabel = pendingCount > 0 ? `pending ${pendingCount}` : 'reverted';
		const isReverting = rawBatchId ? comfyDisableLogRevertInFlight.has(rawBatchId) : false;
		const actions = pendingCount > 0 && rawBatchId
			? `<button class="btn btn-ghost btn-xs" type="button" data-disable-log-revert-batch="${batchIdAttr}" data-disable-log-pending-count="${pendingCount}" aria-label="Revert batch ${batchId}" ${isReverting ? 'disabled aria-disabled="true"' : ''}>${isReverting ? 'Reverting...' : 'Revert batch'}</button>`
			: '';
		return `<div class="config-comfy-package-row"><span class="config-comfy-package-chip ${pendingCount > 0 ? 'is-enabled' : ''}">${escHtml(stateLabel)}</span> ${batchId} · ${createdAt} · success ${success}, skipped ${skipped}, failed ${failed} ${actions}</div>`;
	}).join('');
}

async function loadComfyDisableOperationLog() {
	if (!configComfyDisableLogStatus || !configComfyDisableLogList) return;
	configComfyDisableLogStatus.textContent = 'Loading disable operation log...';
	if (configComfyDisableLogRefreshBtn) configComfyDisableLogRefreshBtn.disabled = true;
	if (configComfyDisableLogRevertLastBtn) configComfyDisableLogRevertLastBtn.disabled = true;
	try {
		const resp = await fetch('/api/comfy/custom-node-packages/disable-log');
		const data = await resp.json().catch(() => ({}));
		if (!resp.ok) throw new Error(data.error || `HTTP ${resp.status}`);
		renderComfyDisableOperationLog(data);
	} catch (err) {
		configComfyDisableLogStatus.textContent = `Disable log error: ${err.message}`;
		configComfyDisableLogList.innerHTML = '<div class="config-comfy-package-row"><span class="hint">Disable log unavailable.</span></div>';
	} finally {
		if (configComfyDisableLogRefreshBtn) configComfyDisableLogRefreshBtn.disabled = false;
	}
}

async function revertLastComfyDisableBatch() {
	if (comfyDisableLogRevertLastInFlight) {
		if (configComfyDisableLogStatus) configComfyDisableLogStatus.textContent = 'Revert already in progress for last pending batch.';
		return;
	}
	await revertComfyDisableBatch('', true, 0);
}

async function revertComfyDisableBatch(batchId = '', useLast = false, pendingCount = 0) {
	if (!useLast && !batchId) {
		if (configComfyDisableLogStatus) configComfyDisableLogStatus.textContent = 'Revert error: missing batch id.';
		return;
	}
	if (!useLast && comfyDisableLogRevertInFlight.has(batchId)) {
		if (configComfyDisableLogStatus) configComfyDisableLogStatus.textContent = `Revert already in progress for batch ${batchId}.`;
		return;
	}
	if (useLast && comfyDisableLogRevertLastInFlight) {
		if (configComfyDisableLogStatus) configComfyDisableLogStatus.textContent = 'Revert already in progress for last pending batch.';
		return;
	}
	const targetLabel = useLast ? 'the last pending disable batch' : `disable batch ${batchId}`;
	const moveLabel = pendingCount > 0
		? `${pendingCount} pending move${pendingCount === 1 ? '' : 's'}`
		: 'pending moves';
	if (!window.confirm(`Revert ${targetLabel}? This will attempt to re-enable ${moveLabel}.`)) {
		if (configComfyDisableLogStatus) configComfyDisableLogStatus.textContent = 'Revert canceled.';
		return;
	}
	if (configComfyDisableLogStatus) {
		configComfyDisableLogStatus.textContent = useLast ? 'Reverting last disable batch...' : `Reverting disable batch ${batchId}...`;
	}
	if (!useLast && batchId) {
		comfyDisableLogRevertInFlight.add(batchId);
	}
	if (useLast) {
		comfyDisableLogRevertLastInFlight = true;
	}
	if (configComfyDisableLogRevertLastBtn) configComfyDisableLogRevertLastBtn.disabled = true;
	try {
		const url = useLast ? '/api/comfy/custom-node-packages/revert-last-disable' : '/api/comfy/custom-node-packages/revert-disable-batch';
		const payload = useLast ? {} : { batch_id: batchId };
		const resp = await fetch(url, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload),
		});
		const data = await resp.json().catch(() => ({}));
		if (!resp.ok) throw new Error(data.error || `HTTP ${resp.status}`);
		if (configComfyPackageDetails) {
			const label = useLast ? 'Revert last disable' : `Revert batch ${batchId}`;
			configComfyPackageDetails.textContent = `${label}: ${data.success || 0} succeeded, ${data.skipped || 0} skipped, ${data.failed || 0} failed.`;
		}
		await loadComfyCustomNodePackages();
	} catch (err) {
		if (configComfyDisableLogStatus) configComfyDisableLogStatus.textContent = `Revert error: ${err.message}`;
	} finally {
		if (!useLast && batchId) {
			comfyDisableLogRevertInFlight.delete(batchId);
		}
		if (useLast) {
			comfyDisableLogRevertLastInFlight = false;
		}
		await loadComfyDisableOperationLog();
	}
}

async function runComfyCustomNodePackageBulkAction(action, dryRun = false, selectedNames = null) {
	if (!action) return;
	if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Running bulk action: ${action}${dryRun ? ' (preview)' : ''}...`;
	if (configComfyPackagesUpdateAllBtn) configComfyPackagesUpdateAllBtn.disabled = true;
	if (configComfyPackagesPreviewDisableNonCoreBtn) configComfyPackagesPreviewDisableNonCoreBtn.disabled = true;
	if (configComfyPackagesDisableNonCoreBtn) configComfyPackagesDisableNonCoreBtn.disabled = true;
	try {
		const payload = { action, dry_run: !!dryRun };
		if (Array.isArray(selectedNames) && selectedNames.length) {
			payload.names = selectedNames;
		}
		const resp = await fetch('/api/comfy/custom-node-packages/bulk', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload),
		});
		const data = await resp.json().catch(() => ({}));
		if (!resp.ok) {
			throw new Error(data.error || `HTTP ${resp.status}`);
		}
		const summary = `${action}${dryRun ? ' preview' : ''}: ${data.success || 0} succeeded, ${data.skipped || 0} skipped, ${data.failed || 0} failed.`;
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = summary;
		if (action === 'disable_non_core' && dryRun) {
			renderComfyDisableNonCorePreview(data);
		} else {
			resetComfyDisablePreview();
		}
		await loadComfyCustomNodePackages();
		await loadComfyDisableOperationLog();
	} catch (err) {
		if (action === 'disable_non_core' && dryRun) {
			resetComfyDisablePreview();
		}
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Bulk action error: ${err.message}`;
	} finally {
		if (configComfyPackagesUpdateAllBtn) configComfyPackagesUpdateAllBtn.disabled = false;
		if (configComfyPackagesPreviewDisableNonCoreBtn) configComfyPackagesPreviewDisableNonCoreBtn.disabled = false;
		if (configComfyPackagesDisableNonCoreBtn) configComfyPackagesDisableNonCoreBtn.disabled = false;
	}
}

async function loadComfyCustomNodePackages() {
	if (!configComfyPackagesStatus || !configComfyPackagesList) return;
	configComfyPackagesStatus.textContent = 'Loading installed custom-node packages...';
	try {
		const resp = await fetch('/api/comfy/custom-node-packages');
		const data = await resp.json().catch(() => ({}));
		if (!resp.ok) {
			throw new Error(data.error || `HTTP ${resp.status}`);
		}
		comfyCustomNodePackages = Array.isArray(data.packages) ? data.packages : [];
		renderComfyCustomNodePackages();
	} catch (err) {
		comfyCustomNodePackages = [];
		configComfyPackagesList.innerHTML = '<div class="config-comfy-package-row"><span class="hint">Unable to load package folders.</span></div>';
		configComfyPackagesStatus.textContent = `Package inventory error: ${err.message}`;
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Package inventory error: ${err.message}`;
	}
}

async function loadComfyCustomNodes() {
	if (!configComfyNodesStatus || !configComfyNodesList) return;
	const includeBuiltins = Boolean(configComfyNodesIncludeBuiltinsToggle?.checked);
	configComfyNodesStatus.textContent = 'Loading ComfyUI node metadata...';
	if (configComfyNodesRefreshBtn) configComfyNodesRefreshBtn.disabled = true;
	try {
		const resp = await fetch(`/api/comfy/custom-nodes?include_builtin=${includeBuiltins ? '1' : '0'}`);
		const data = await resp.json().catch(() => ({}));
		if (!resp.ok) {
			throw new Error(data.error || `HTTP ${resp.status}`);
		}
		comfyCustomNodeRows = Array.isArray(data.nodes) ? data.nodes : [];
		renderComfyCustomNodeBrowser();
	} catch (err) {
		comfyCustomNodeRows = [];
		configComfyNodesList.innerHTML = '<div class="config-comfy-node-row"><span class="hint">Unable to load nodes.</span></div>';
		configComfyNodesStatus.textContent = `Node browser error: ${err.message}`;
	} finally {
		if (configComfyNodesRefreshBtn) configComfyNodesRefreshBtn.disabled = false;
	}
	await loadComfyCustomNodePackages();
}

// Load version info on page load
loadComfyuiVersionInfo();

if (configComfyNodesIncludeBuiltinsToggle) {
	configComfyNodesIncludeBuiltinsToggle.checked = comfyCustomNodeIncludeBuiltins;
	configComfyNodesIncludeBuiltinsToggle.addEventListener('change', () => {
		comfyCustomNodeIncludeBuiltins = configComfyNodesIncludeBuiltinsToggle.checked;
		if (comfyCustomNodeIncludeBuiltins) {
			localStorage.setItem(CONFIG_COMFY_NODES_INCLUDE_BUILTINS_KEY, '1');
		} else {
			localStorage.removeItem(CONFIG_COMFY_NODES_INCLUDE_BUILTINS_KEY);
		}
		loadComfyCustomNodes();
	});
}

if (configComfyNodesSearchInput) {
	configComfyNodesSearchInput.addEventListener('input', () => {
		renderComfyCustomNodeBrowser();
	});
}

if (configComfyNodesRefreshBtn) {
	configComfyNodesRefreshBtn.addEventListener('click', loadComfyCustomNodes);
}

if (configComfyPackagesList) {
	configComfyPackagesList.addEventListener('click', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLElement)) return;
		const action = target.getAttribute('data-package-action');
		const packageName = target.getAttribute('data-package-name') || '';
		if (!action || !packageName) return;
		comfySelectedPackageName = packageName;
		renderComfyCustomNodePackages();
		if (action === 'details') {
			loadComfyCustomNodePackageDetails(packageName);
			return;
		}
		if (action === 'open') {
			openComfyCustomNodePackageFolder(packageName);
			return;
		}
		if (action === 'toggle') {
			const currentlyEnabled = target.getAttribute('data-package-enabled') === '1';
			toggleComfyCustomNodePackageEnabled(packageName, !currentlyEnabled);
			return;
		}
		if (action === 'update') {
			updateComfyCustomNodePackage(packageName);
		}
	});
}

if (configComfyPackagesUpdateAllBtn) {
	configComfyPackagesUpdateAllBtn.addEventListener('click', () => {
		runComfyCustomNodePackageBulkAction('update_all');
	});
}

if (configComfyPackagesPreviewDisableNonCoreBtn) {
	configComfyPackagesPreviewDisableNonCoreBtn.addEventListener('click', () => {
		runComfyCustomNodePackageBulkAction('disable_non_core', true);
	});
}

if (configComfyDisablePreviewList) {
	configComfyDisablePreviewList.addEventListener('change', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLInputElement)) return;
		if (target.getAttribute('data-disable-preview-select') !== '1') return;
		const packageName = target.getAttribute('data-package-name') || '';
		if (!packageName) return;
		const row = target.closest('[data-disable-preview-row="1"]');
		if (target.checked) {
			comfyDisablePreviewSelectedNames.add(packageName);
			if (row) row.setAttribute('data-disable-preview-selected', '1');
		} else {
			comfyDisablePreviewSelectedNames.delete(packageName);
			if (row) row.setAttribute('data-disable-preview-selected', '0');
		}
		applyComfyDisablePreviewFilter();
		syncComfyDisablePreviewConfirmLabel();
	});
}

if (configComfyDisablePreviewFilter) {
	configComfyDisablePreviewFilter.value = comfyDisablePreviewFilterQuery;
	configComfyDisablePreviewFilter.addEventListener('input', () => {
		comfyDisablePreviewFilterQuery = configComfyDisablePreviewFilter.value || '';
		if (comfyDisablePreviewFilterQuery) {
			localStorage.setItem(CONFIG_COMFY_DISABLE_PREVIEW_FILTER_KEY, comfyDisablePreviewFilterQuery);
		} else {
			localStorage.removeItem(CONFIG_COMFY_DISABLE_PREVIEW_FILTER_KEY);
		}
		applyComfyDisablePreviewFilter();
	});
}

if (configComfyDisablePreviewSelectedOnly) {
	configComfyDisablePreviewSelectedOnly.checked = comfyDisablePreviewSelectedOnlyPref;
	configComfyDisablePreviewSelectedOnly.addEventListener('change', () => {
		comfyDisablePreviewSelectedOnlyPref = !!configComfyDisablePreviewSelectedOnly.checked;
		if (comfyDisablePreviewSelectedOnlyPref) {
			localStorage.setItem(CONFIG_COMFY_DISABLE_PREVIEW_SELECTED_ONLY_KEY, '1');
		} else {
			localStorage.removeItem(CONFIG_COMFY_DISABLE_PREVIEW_SELECTED_ONLY_KEY);
		}
		applyComfyDisablePreviewFilter();
	});
}

if (configComfyDisablePreviewSelectAllBtn) {
	configComfyDisablePreviewSelectAllBtn.addEventListener('click', () => {
		if (!configComfyDisablePreviewList) return;
		const checkboxes = [...configComfyDisablePreviewList.querySelectorAll('input[data-disable-preview-select="1"]')];
		comfyDisablePreviewSelectedNames = new Set();
		checkboxes.forEach((box) => {
			box.checked = true;
			const name = box.getAttribute('data-package-name') || '';
			const row = box.closest('[data-disable-preview-row="1"]');
			if (row) row.setAttribute('data-disable-preview-selected', '1');
			if (name) comfyDisablePreviewSelectedNames.add(name);
		});
		applyComfyDisablePreviewFilter();
		syncComfyDisablePreviewConfirmLabel();
	});
}

if (configComfyDisablePreviewSelectVisibleBtn) {
	configComfyDisablePreviewSelectVisibleBtn.addEventListener('click', () => {
		if (!configComfyDisablePreviewList) return;
		const checkboxes = [...configComfyDisablePreviewList.querySelectorAll('input[data-disable-preview-select="1"]')]
			.filter((box) => !box.closest('[data-disable-preview-row="1"]')?.hidden);
		checkboxes.forEach((box) => {
			box.checked = true;
			const row = box.closest('[data-disable-preview-row="1"]');
			if (row) row.setAttribute('data-disable-preview-selected', '1');
			const name = box.getAttribute('data-package-name') || '';
			if (name) comfyDisablePreviewSelectedNames.add(name);
		});
		syncComfyDisablePreviewConfirmLabel();
	});
}

if (configComfyDisablePreviewClearBtn) {
	configComfyDisablePreviewClearBtn.addEventListener('click', () => {
		if (!configComfyDisablePreviewList) return;
		const checkboxes = [...configComfyDisablePreviewList.querySelectorAll('input[data-disable-preview-select="1"]')];
		checkboxes.forEach((box) => {
			box.checked = false;
			const row = box.closest('[data-disable-preview-row="1"]');
			if (row) row.setAttribute('data-disable-preview-selected', '0');
		});
		comfyDisablePreviewSelectedNames = new Set();
		applyComfyDisablePreviewFilter();
		syncComfyDisablePreviewConfirmLabel();
	});
}

if (configComfyDisablePreviewCopySelectedBtn) {
	configComfyDisablePreviewCopySelectedBtn.addEventListener('click', async () => {
		const selected = getSortedComfyDisablePreviewSelectedNames();
		if (!selected.length) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = 'No selected packages to copy.';
			return;
		}
		try {
			await copyTextToClipboard(selected.join('\n'));
			const status = `Copied ${selected.length} selected package name${selected.length === 1 ? '' : 's'} to clipboard.`;
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = status;
			const statusWithTime = `${status} (${new Date().toLocaleTimeString()})`;
			setComfyDisablePreviewExportStatus(statusWithTime);
			recordComfyDisablePreviewExportHistory(statusWithTime);
		} catch (err) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Copy selected failed: ${err.message}`;
		}
	});
}

if (configComfyDisablePreviewCopyCsvBtn) {
	configComfyDisablePreviewCopyCsvBtn.addEventListener('click', async () => {
		const selected = getSortedComfyDisablePreviewSelectedNames();
		if (!selected.length) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = 'No selected packages to copy as CSV.';
			return;
		}
		const csvLines = ['package_name', ...selected.map((name) => `"${name.replace(/"/g, '""')}"`)];
		try {
			await copyTextToClipboard(csvLines.join('\n'));
			const status = `Copied CSV for ${selected.length} selected package name${selected.length === 1 ? '' : 's'}.`;
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = status;
			const statusWithTime = `${status} (${new Date().toLocaleTimeString()})`;
			setComfyDisablePreviewExportStatus(statusWithTime);
			recordComfyDisablePreviewExportHistory(statusWithTime);
		} catch (err) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Copy CSV failed: ${err.message}`;
		}
	});
}

if (configComfyDisablePreviewDownloadSelectedBtn) {
	configComfyDisablePreviewDownloadSelectedBtn.addEventListener('click', () => {
		const selected = getSortedComfyDisablePreviewSelectedNames();
		if (!selected.length) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = 'No selected packages to download.';
			return;
		}
		const blob = new Blob([`${selected.join('\n')}\n`], { type: 'text/plain;charset=utf-8' });
		const url = URL.createObjectURL(blob);
		const anchor = document.createElement('a');
		const dateStr = new Date().toISOString().slice(0, 10);
		anchor.href = url;
		anchor.download = `la-disable-selected-${dateStr}.txt`;
		document.body.appendChild(anchor);
		anchor.click();
		document.body.removeChild(anchor);
		URL.revokeObjectURL(url);
		const status = `Downloaded ${selected.length} selected package name${selected.length === 1 ? '' : 's'}.`;
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = status;
		const statusWithTime = `${status} (${new Date().toLocaleTimeString()})`;
		setComfyDisablePreviewExportStatus(statusWithTime);
		recordComfyDisablePreviewExportHistory(statusWithTime);
	});
}

if (configComfyDisablePreviewDownloadCsvBtn) {
	configComfyDisablePreviewDownloadCsvBtn.addEventListener('click', () => {
		const selected = getSortedComfyDisablePreviewSelectedNames();
		if (!selected.length) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = 'No selected packages to download as CSV.';
			return;
		}
		const csvLines = ['package_name', ...selected.map((name) => `"${name.replace(/"/g, '""')}"`)];
		const blob = new Blob([`${csvLines.join('\n')}\n`], { type: 'text/csv;charset=utf-8' });
		const url = URL.createObjectURL(blob);
		const anchor = document.createElement('a');
		const dateStr = new Date().toISOString().slice(0, 10);
		anchor.href = url;
		anchor.download = `la-disable-selected-${dateStr}.csv`;
		document.body.appendChild(anchor);
		anchor.click();
		document.body.removeChild(anchor);
		URL.revokeObjectURL(url);
		const status = `Downloaded CSV for ${selected.length} selected package name${selected.length === 1 ? '' : 's'}.`;
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = status;
		const statusWithTime = `${status} (${new Date().toLocaleTimeString()})`;
		setComfyDisablePreviewExportStatus(statusWithTime);
		recordComfyDisablePreviewExportHistory(statusWithTime);
	});
}

if (configComfyDisablePreviewDownloadJsonBtn) {
	configComfyDisablePreviewDownloadJsonBtn.addEventListener('click', () => {
		const selected = getSortedComfyDisablePreviewSelectedNames();
		if (!selected.length) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = 'No selected packages to download as JSON.';
			return;
		}
		const payload = {
			version: 1,
			action: 'disable_non_core',
			exported_at: new Date().toISOString(),
			selected_count: selected.length,
			packages: selected,
		};
		const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const anchor = document.createElement('a');
		const dateStr = new Date().toISOString().slice(0, 10);
		anchor.href = url;
		anchor.download = `la-disable-selected-${dateStr}.json`;
		document.body.appendChild(anchor);
		anchor.click();
		document.body.removeChild(anchor);
		URL.revokeObjectURL(url);
		const status = `Downloaded JSON for ${selected.length} selected package name${selected.length === 1 ? '' : 's'}.`;
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = status;
		const statusWithTime = `${status} (${new Date().toLocaleTimeString()})`;
		setComfyDisablePreviewExportStatus(statusWithTime);
		recordComfyDisablePreviewExportHistory(statusWithTime);
	});
}

if (configComfyDisablePreviewClearVisibleBtn) {
	configComfyDisablePreviewClearVisibleBtn.addEventListener('click', () => {
		if (!configComfyDisablePreviewList) return;
		const checkboxes = [...configComfyDisablePreviewList.querySelectorAll('input[data-disable-preview-select="1"]')]
			.filter((box) => !box.closest('[data-disable-preview-row="1"]')?.hidden);
		checkboxes.forEach((box) => {
			box.checked = false;
			const row = box.closest('[data-disable-preview-row="1"]');
			if (row) row.setAttribute('data-disable-preview-selected', '0');
			const name = box.getAttribute('data-package-name') || '';
			if (name) comfyDisablePreviewSelectedNames.delete(name);
		});
		syncComfyDisablePreviewConfirmLabel();
	});
}

if (configComfyDisablePreviewInvertBtn) {
	configComfyDisablePreviewInvertBtn.addEventListener('click', () => {
		if (!configComfyDisablePreviewList) return;
		const checkboxes = [...configComfyDisablePreviewList.querySelectorAll('input[data-disable-preview-select="1"]')];
		comfyDisablePreviewSelectedNames = new Set();
		checkboxes.forEach((box) => {
			box.checked = !box.checked;
			const row = box.closest('[data-disable-preview-row="1"]');
			if (row) row.setAttribute('data-disable-preview-selected', box.checked ? '1' : '0');
			if (box.checked) {
				const name = box.getAttribute('data-package-name') || '';
				if (name) comfyDisablePreviewSelectedNames.add(name);
			}
		});
		applyComfyDisablePreviewFilter();
		syncComfyDisablePreviewConfirmLabel();
	});
}

if (configComfyDisablePreviewResetPrefsBtn) {
	configComfyDisablePreviewResetPrefsBtn.addEventListener('click', () => {
		comfyDisablePreviewFilterQuery = '';
		comfyDisablePreviewSelectedOnlyPref = false;
		localStorage.removeItem(CONFIG_COMFY_DISABLE_PREVIEW_FILTER_KEY);
		localStorage.removeItem(CONFIG_COMFY_DISABLE_PREVIEW_SELECTED_ONLY_KEY);
		if (configComfyDisablePreviewFilter) configComfyDisablePreviewFilter.value = '';
		if (configComfyDisablePreviewSelectedOnly) configComfyDisablePreviewSelectedOnly.checked = false;
		applyComfyDisablePreviewFilter();
	});
}

if (configComfyDisablePreviewExportStatus) {
	setComfyDisablePreviewExportStatus(comfyDisablePreviewLastExport || 'No export yet.', false);
}

if (configComfyDisablePreviewExportHistoryClearBtn) {
	configComfyDisablePreviewExportHistoryClearBtn.addEventListener('click', () => {
		clearComfyDisablePreviewExportHistory();
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = 'Export history cleared.';
	});
}

if (configComfyDisablePreviewExportHistoryCopyBtn) {
	configComfyDisablePreviewExportHistoryCopyBtn.addEventListener('click', async () => {
		if (!comfyDisablePreviewExportHistory.length) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = 'No export history to copy.';
			return;
		}
		try {
			await copyTextToClipboard(comfyDisablePreviewExportHistory.join('\n'));
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Copied ${comfyDisablePreviewExportHistory.length} export history entr${comfyDisablePreviewExportHistory.length === 1 ? 'y' : 'ies'}.`;
		} catch (err) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Copy export history failed: ${err.message}`;
		}
	});
}

if (configComfyDisablePreviewExportHistoryCopyJsonBtn) {
	configComfyDisablePreviewExportHistoryCopyJsonBtn.addEventListener('click', async () => {
		if (!comfyDisablePreviewExportHistory.length) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = 'No export history to copy as JSON.';
			return;
		}
		const payload = {
			version: 1,
			exported_at: new Date().toISOString(),
			count: comfyDisablePreviewExportHistory.length,
			history: comfyDisablePreviewExportHistory,
		};
		try {
			await copyTextToClipboard(JSON.stringify(payload, null, 2));
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Copied JSON export history with ${comfyDisablePreviewExportHistory.length} entr${comfyDisablePreviewExportHistory.length === 1 ? 'y' : 'ies'}.`;
		} catch (err) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Copy export history JSON failed: ${err.message}`;
		}
	});
}

if (configComfyDisablePreviewExportHistoryDownloadBtn) {
	configComfyDisablePreviewExportHistoryDownloadBtn.addEventListener('click', () => {
		if (!comfyDisablePreviewExportHistory.length) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = 'No export history to download.';
			return;
		}
		const blob = new Blob([`${comfyDisablePreviewExportHistory.join('\n')}\n`], { type: 'text/plain;charset=utf-8' });
		const url = URL.createObjectURL(blob);
		const anchor = document.createElement('a');
		const dateStr = new Date().toISOString().slice(0, 10);
		anchor.href = url;
		anchor.download = `la-disable-export-history-${dateStr}.txt`;
		document.body.appendChild(anchor);
		anchor.click();
		document.body.removeChild(anchor);
		URL.revokeObjectURL(url);
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Downloaded ${comfyDisablePreviewExportHistory.length} export history entr${comfyDisablePreviewExportHistory.length === 1 ? 'y' : 'ies'}.`;
	});
}

if (configComfyDisablePreviewExportHistoryDownloadCsvBtn) {
	configComfyDisablePreviewExportHistoryDownloadCsvBtn.addEventListener('click', () => {
		if (!comfyDisablePreviewExportHistory.length) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = 'No export history to download as CSV.';
			return;
		}
		const csvLines = ['entry', ...comfyDisablePreviewExportHistory.map((item) => `"${String(item || '').replace(/"/g, '""')}"`)];
		const blob = new Blob([`${csvLines.join('\n')}\n`], { type: 'text/csv;charset=utf-8' });
		const url = URL.createObjectURL(blob);
		const anchor = document.createElement('a');
		const dateStr = new Date().toISOString().slice(0, 10);
		anchor.href = url;
		anchor.download = `la-disable-export-history-${dateStr}.csv`;
		document.body.appendChild(anchor);
		anchor.click();
		document.body.removeChild(anchor);
		URL.revokeObjectURL(url);
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Downloaded CSV export history with ${comfyDisablePreviewExportHistory.length} entr${comfyDisablePreviewExportHistory.length === 1 ? 'y' : 'ies'}.`;
	});
}

if (configComfyDisablePreviewExportHistoryDownloadJsonBtn) {
	configComfyDisablePreviewExportHistoryDownloadJsonBtn.addEventListener('click', () => {
		if (!comfyDisablePreviewExportHistory.length) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = 'No export history to download as JSON.';
			return;
		}
		const payload = {
			version: 1,
			exported_at: new Date().toISOString(),
			count: comfyDisablePreviewExportHistory.length,
			history: comfyDisablePreviewExportHistory,
		};
		const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const anchor = document.createElement('a');
		const dateStr = new Date().toISOString().slice(0, 10);
		anchor.href = url;
		anchor.download = `la-disable-export-history-${dateStr}.json`;
		document.body.appendChild(anchor);
		anchor.click();
		document.body.removeChild(anchor);
		URL.revokeObjectURL(url);
		if (configComfyPackageDetails) configComfyPackageDetails.textContent = `Downloaded JSON export history with ${comfyDisablePreviewExportHistory.length} entr${comfyDisablePreviewExportHistory.length === 1 ? 'y' : 'ies'}.`;
	});
}

renderComfyDisablePreviewExportHistory();

if (configComfyDisablePreviewConfirmBtn) {
	configComfyDisablePreviewConfirmBtn.addEventListener('click', () => {
		if (!comfyDisablePreviewReady) return;
		const selected = [...comfyDisablePreviewSelectedNames].filter(Boolean);
		if (!selected.length) {
			if (configComfyPackageDetails) configComfyPackageDetails.textContent = 'No preview items selected to disable.';
			return;
		}
		runComfyCustomNodePackageBulkAction('disable_non_core', false, selected);
	});
}

if (configComfyDisableLogRefreshBtn) {
	configComfyDisableLogRefreshBtn.addEventListener('click', () => {
		loadComfyDisableOperationLog();
	});
}

if (configComfyDisableLogPendingOnlyToggle) {
	configComfyDisableLogPendingOnlyToggle.checked = comfyDisableLogPendingOnly;
	configComfyDisableLogPendingOnlyToggle.addEventListener('change', () => {
		comfyDisableLogPendingOnly = !!configComfyDisableLogPendingOnlyToggle.checked;
		if (comfyDisableLogPendingOnly) {
			localStorage.setItem(CONFIG_COMFY_DISABLE_LOG_PENDING_ONLY_KEY, '1');
		} else {
			localStorage.removeItem(CONFIG_COMFY_DISABLE_LOG_PENDING_ONLY_KEY);
		}
		loadComfyDisableOperationLog();
	});
}

if (configComfyDisableLogRevertLastBtn) {
	configComfyDisableLogRevertLastBtn.addEventListener('click', () => {
		revertLastComfyDisableBatch();
	});
}

if (configComfyDisableLogList) {
	configComfyDisableLogList.addEventListener('click', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLElement)) return;
		const btn = target.closest('[data-disable-log-revert-batch]');
		if (!(btn instanceof HTMLElement)) return;
		const batchId = String(btn.getAttribute('data-disable-log-revert-batch') || '').trim();
		const pendingCount = Number(btn.getAttribute('data-disable-log-pending-count') || 0);
		if (btn.hasAttribute('disabled')) return;
		if (!batchId) return;
		revertComfyDisableBatch(batchId, false, pendingCount);
	});
}

if (configComfyPackagesDisableNonCoreBtn) {
	configComfyPackagesDisableNonCoreBtn.addEventListener('click', () => {
		runComfyCustomNodePackageBulkAction('disable_non_core');
	});
}

resetComfyDisablePreview();

loadComfyCustomNodes();
loadComfyDisableOperationLog();

if (configFlaskRestartBtn) {
	configFlaskRestartBtn.addEventListener('click', restartFlaskApp);
	configFlaskRestartBtn.addEventListener('keydown', onConfigServiceControlsKeydown);
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
	tagEditorList.addEventListener('keydown', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLElement)) return;
		const hasTagAction = target.hasAttribute('data-tag-save') || target.hasAttribute('data-tag-delete');
		if (!hasTagAction) return;
		const key = event.key;
		if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
		const row = target.closest('.tag-editor-row');
		if (!row) return;
		const actions = Array.from(row.querySelectorAll('[data-tag-save], [data-tag-delete]'));
		if (actions.length < 2) return;
		const currentIndex = actions.indexOf(target);
		if (currentIndex < 0) return;
		event.preventDefault();
		let nextIndex = currentIndex;
		if (key === 'Home') {
			nextIndex = 0;
		} else if (key === 'End') {
			nextIndex = actions.length - 1;
		} else if (key === 'ArrowRight') {
			nextIndex = (currentIndex + 1) % actions.length;
		} else if (key === 'ArrowLeft') {
			nextIndex = (currentIndex - 1 + actions.length) % actions.length;
		}
		const next = actions[nextIndex];
		if (next) next.focus();
	});

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
	saveCurrentTextPromptToHistory(prompt);

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
	if (controlnetWeightVal && controlnetWeight) controlnetWeightVal.textContent = Number(controlnetWeight.value).toFixed(2);
	if (controlnetStartVal && controlnetStart) controlnetStartVal.textContent = Number(controlnetStart.value).toFixed(2);
	if (controlnetEndVal && controlnetEnd) controlnetEndVal.textContent = Number(controlnetEnd.value).toFixed(2);
}

function updateControlnetImagePreview() {
	if (!controlnetImageUpload || !controlnetImagePreviewWrap || !controlnetImagePreview || !controlnetImageName) return;
	if (controlnetPreviewObjectUrl) {
		URL.revokeObjectURL(controlnetPreviewObjectUrl);
		controlnetPreviewObjectUrl = '';
	}
	const file = controlnetImageUpload.files && controlnetImageUpload.files[0] ? controlnetImageUpload.files[0] : null;
	if (!file) {
		controlnetImagePreviewWrap.hidden = true;
		controlnetImagePreview.removeAttribute('src');
		controlnetImageName.textContent = '';
		return;
	}
	controlnetPreviewObjectUrl = URL.createObjectURL(file);
	controlnetImagePreview.src = controlnetPreviewObjectUrl;
	controlnetImageName.textContent = file.name;
	controlnetImagePreviewWrap.hidden = false;
}

imageSteps.addEventListener('input', syncImageControlLabels);
imageCfg.addEventListener('input', syncImageControlLabels);
imageDenoise.addEventListener('input', syncImageControlLabels);
if (controlnetWeight) controlnetWeight.addEventListener('input', syncImageControlLabels);
if (controlnetStart) controlnetStart.addEventListener('input', syncImageControlLabels);
if (controlnetEnd) controlnetEnd.addEventListener('input', syncImageControlLabels);
syncImageControlLabels();
if (imageModelSelect) {
	imageModelSelect.addEventListener('change', () => {
		rememberRecentImageModel(imageModelSelect.value);
		updateModelFavoriteToggleState();
		updateModelStackBadges();
		refreshCompatibilityGroupings();
		applyImageFamilyModeUi();
	});
}
if (imageModelFamilySelect) {
	imageModelFamilySelect.value = imageModelFamilyMode;
	imageModelFamilySelect.addEventListener('change', () => {
		const mode = imageModelFamilySelect.value;
		imageModelFamilyMode = ['auto', 'sd', 'flux'].includes(mode) ? mode : 'auto';
		localStorage.setItem(IMAGE_MODEL_FAMILY_MODE_KEY, imageModelFamilyMode);
		applyImageFamilyModeUi();
	});
}
if (imageModelFilter) {
	imageModelFilter.addEventListener('input', () => {
		renderFilteredImageModels(imageModelFilter.value, imageModelSelect ? imageModelSelect.value : '');
		updateModelFavoriteToggleState();
		updateModelStackBadges();
		updateModelStackCompatibilityHint();
		updateControlnetCompatibilityHint();
	});
}
bindSelectFilterInput(imageSamplerFilter, imageSamplerSelect, IMAGE_SAMPLER_FILTER_QUERY_KEY, imageSamplerFilterStatus, 'samplers');
bindSelectFilterInput(imageSchedulerFilter, imageSchedulerSelect, IMAGE_SCHEDULER_FILTER_QUERY_KEY, imageSchedulerFilterStatus, 'schedulers');
if (imageSamplerSelect) {
	imageSamplerSelect.addEventListener('change', () => {
		updateFluxRecommendationDriftHint();
	});
}
if (imageSchedulerSelect) {
	imageSchedulerSelect.addEventListener('change', () => {
		updateFluxRecommendationDriftHint();
	});
}
if (imageApplyRecommendationBtn) {
	imageApplyRecommendationBtn.addEventListener('click', () => {
		applyCurrentFluxRecommendation({ announce: true });
	});
}
if (imageRecommendationInfoBtn) {
	imageRecommendationInfoBtn.addEventListener('click', () => {
		const recommendation = getFluxWorkflowRecommendation(imageModelSelect?.value || '');
		if (!recommendation?.sampler || !recommendation?.scheduler) return;
		const sourceLabel = recommendation.sourceLabel || (recommendation.source === 'metadata' ? 'model metadata' : 'fallback heuristic');
		const detailText = `Recommended pair ${recommendation.sampler} + ${recommendation.scheduler} from ${sourceLabel}.`;
		if (imageRecommendationStatus) {
			imageRecommendationStatus.textContent = detailText;
			imageRecommendationStatus.hidden = false;
		}
		showToast(detailText, '');
	});
}
if (imageAutoApplyRecommendationToggle) {
	imageAutoApplyRecommendationToggle.checked = imageFluxAutoApplyRecommendation;
	imageAutoApplyRecommendationToggle.addEventListener('change', () => {
		imageFluxAutoApplyRecommendation = imageAutoApplyRecommendationToggle.checked;
		localStorage.setItem(IMAGE_FLUX_AUTO_APPLY_RECOMMENDATION_KEY, imageFluxAutoApplyRecommendation ? '1' : '0');
		lastAutoRecommendationModelKey = '';
		if (imageFluxAutoApplyRecommendation) {
			applyCurrentFluxRecommendation({ announce: false, suppressNoopStatus: true });
		}
	});
}
if (imageLockRecommendationToggle) {
	imageLockRecommendationToggle.checked = imageFluxLockRecommendation;
	imageLockRecommendationToggle.addEventListener('change', () => {
		imageFluxLockRecommendation = imageLockRecommendationToggle.checked;
		imageFluxLockBypassOnce = false;
		localStorage.setItem(IMAGE_FLUX_LOCK_RECOMMENDATION_KEY, imageFluxLockRecommendation ? '1' : '0');
		if (imageFluxLockRecommendation) {
			applyCurrentFluxRecommendation({ announce: false, suppressNoopStatus: true });
		}
		applyImageFamilyModeUi();
	});
}
if (imageUnlockRecommendationOnceBtn) {
	imageUnlockRecommendationOnceBtn.addEventListener('click', () => {
		const activeFamily = resolveActiveImageFamily(imageModelSelect?.value || '');
		if (activeFamily !== 'flux' || !imageFluxLockRecommendation) return;
		imageFluxLockBypassOnce = true;
		applyImageFamilyModeUi();
		if (imageRecommendationStatus) {
			imageRecommendationStatus.textContent = 'Temporary unlock active for next run. Lock will be restored after submit.';
			imageRecommendationStatus.hidden = false;
		}
		showToast('Temporary unlock active for next run.', '');
	});
}
if (imageModelModeAll) imageModelModeAll.addEventListener('click', () => setImageModelFilterMode('all'));
if (imageModelModeRecent) imageModelModeRecent.addEventListener('click', () => setImageModelFilterMode('recent'));
if (imageModelModeFavorites) imageModelModeFavorites.addEventListener('click', () => setImageModelFilterMode('favorites'));
if (imageModelFavoriteToggle) {
	imageModelFavoriteToggle.addEventListener('click', () => {
		toggleFavoriteImageModel(imageModelSelect ? imageModelSelect.value : '');
	});
}
if (refinerModelSelect) {
	refinerModelSelect.addEventListener('change', () => {
		updateModelStackBadges();
		updateModelStackCompatibilityHint();
	});
}
if (vaeModelSelect) {
	vaeModelSelect.addEventListener('change', () => {
		updateModelStackBadges();
		updateModelStackCompatibilityHint();
	});
}
if (controlnetModelSelect) controlnetModelSelect.addEventListener('change', updateControlnetCompatibilityHint);
if (controlnetImageUpload) {
	controlnetImageUpload.addEventListener('change', updateControlnetImagePreview);
}
if (controlnetImageClearBtn && controlnetImageUpload) {
	controlnetImageClearBtn.addEventListener('click', () => {
		controlnetImageUpload.value = '';
		updateControlnetImagePreview();
	});
}
setImageModelFilterMode(imageModelFilterMode);
applyImageFamilyModeUi();

imageRandomSeed.addEventListener('click', () => {
	imageSeed.value = randomSeed();
});

// ---- Aspect ratio presets ------------------------------------------------
document.querySelectorAll('[data-ar]').forEach((btn) => {
	btn.addEventListener('click', () => {
		const parts = (btn.dataset.ar || '').split(':').map(Number);
		if (parts.length !== 2 || !parts[0] || !parts[1]) return;
		if (imageWidth) imageWidth.value = String(parts[0]);
		if (imageHeight) imageHeight.value = String(parts[1]);
	});
});

// ---- Seed helpers: Use Last / Lock ---------------------------------------
const imageUseLastSeedBtn = document.getElementById('image-use-last-seed');
const imageLockSeedBtn = document.getElementById('image-lock-seed');
let _lastGeneratedSeed = null;
let _seedLocked = false;

function setLastGeneratedSeed(seed) {
	if (seed === null || seed === undefined) return;
	_lastGeneratedSeed = String(seed);
	if (imageUseLastSeedBtn) imageUseLastSeedBtn.disabled = false;
	if (_seedLocked && imageSeed) imageSeed.value = _lastGeneratedSeed;
}

if (imageUseLastSeedBtn) {
	imageUseLastSeedBtn.addEventListener('click', () => {
		if (_lastGeneratedSeed && imageSeed) {
			imageSeed.value = _lastGeneratedSeed;
		}
	});
}

if (imageLockSeedBtn) {
	imageLockSeedBtn.addEventListener('click', () => {
		_seedLocked = !_seedLocked;
		imageLockSeedBtn.setAttribute('aria-pressed', String(_seedLocked));
		imageLockSeedBtn.classList.toggle('active', _seedLocked);
		if (_seedLocked && _lastGeneratedSeed && imageSeed) {
			imageSeed.value = _lastGeneratedSeed;
		}
	});
}

function applyImagePreset(preset) {
	const family = resolveActiveImageFamily(imageModelSelect?.value || '');
	const fluxRecommendation = family === 'flux' ? getFluxWorkflowRecommendation(imageModelSelect?.value || '') : null;
	const fluxVariant = family === 'flux' ? inferFluxVariant(imageModelSelect?.value || '') : '';
	const familyPresetMap = {
		sd: {
			fast: { steps: 12, cfg: 5.5, denoise: 0.65, width: 768, height: 768, batch: 1, scheduler: 'normal' },
			quality: { steps: 40, cfg: 7.5, denoise: 0.75, width: 1024, height: 1024, batch: 1, scheduler: 'karras' },
			creative: { steps: 32, cfg: 9.0, denoise: 0.85, width: 1024, height: 1024, batch: 1, scheduler: 'exponential' },
		},
		flux: {
			dev: {
				fast: { steps: 16, cfg: 3.0, denoise: 0.65, width: 1024, height: 1024, batch: 1, scheduler: fluxRecommendation?.scheduler || 'normal' },
				quality: { steps: 28, cfg: 3.5, denoise: 0.72, width: 1024, height: 1024, batch: 1, scheduler: fluxRecommendation?.scheduler || 'normal' },
				creative: { steps: 36, cfg: 4.5, denoise: 0.82, width: 1152, height: 896, batch: 1, scheduler: fluxRecommendation?.scheduler || 'normal' },
			},
			schnell: {
				fast: { steps: 8, cfg: 1.8, denoise: 0.62, width: 1024, height: 1024, batch: 1, scheduler: fluxRecommendation?.scheduler || 'simple' },
				quality: { steps: 12, cfg: 2.2, denoise: 0.70, width: 1024, height: 1024, batch: 1, scheduler: fluxRecommendation?.scheduler || 'simple' },
				creative: { steps: 16, cfg: 2.6, denoise: 0.80, width: 1152, height: 896, batch: 1, scheduler: fluxRecommendation?.scheduler || 'simple' },
			},
		},
	};
	const presetData = family === 'flux'
		? (familyPresetMap.flux[fluxVariant] || familyPresetMap.flux.dev)?.[preset]
		: familyPresetMap.sd[preset];
	if (!presetData) return;

	imageSteps.value = String(presetData.steps);
	imageCfg.value = String(presetData.cfg);
	imageDenoise.value = String(presetData.denoise);
	if (imageWidth) imageWidth.value = String(presetData.width);
	if (imageHeight) imageHeight.value = String(presetData.height);
	if (imageBatchSize) imageBatchSize.value = String(presetData.batch);
	if (family === 'flux' && fluxRecommendation?.sampler) {
		setSelectValueIfOptionExists(imageSamplerSelect, fluxRecommendation.sampler);
	}
	if (refinerModelSelect) refinerModelSelect.value = '';
	if (hiresfixEnable) hiresfixEnable.checked = false;
	setSelectValueIfOptionExists(imageSchedulerSelect, presetData.scheduler || 'normal');
	activeImagePreset = preset;
	lastResolvedPresetFamily = family;
	syncImageControlLabels();
	updateModelStackCompatibilityHint();
}

function setActiveImagePresetButton(activePreset) {
	activeImagePreset = activePreset || '';
	if (!imagePresetButtons || !imagePresetButtons.length) return;
	imagePresetButtons.forEach((btn, index) => {
		const isActive = (btn.dataset.imagePreset || '') === activePreset;
		btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
		btn.setAttribute('tabindex', isActive ? '0' : '-1');
		if (!activePreset && index === 0) {
			btn.setAttribute('tabindex', '0');
		}
	});
}

function onImagePresetKeydown(event) {
	if (!imagePresetButtons || !imagePresetButtons.length) return;
	const key = event.key;
	if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
	const buttons = Array.from(imagePresetButtons);
	const currentIndex = buttons.indexOf(event.currentTarget);
	if (currentIndex < 0) return;
	event.preventDefault();
	let nextIndex = currentIndex;
	if (key === 'Home') {
		nextIndex = 0;
	} else if (key === 'End') {
		nextIndex = buttons.length - 1;
	} else if (key === 'ArrowRight') {
		nextIndex = (currentIndex + 1) % buttons.length;
	} else if (key === 'ArrowLeft') {
		nextIndex = (currentIndex - 1 + buttons.length) % buttons.length;
	}
	const nextButton = buttons[nextIndex];
	if (!nextButton) return;
	const preset = nextButton.dataset.imagePreset || '';
	applyImagePreset(preset);
	setActiveImagePresetButton(preset);
	nextButton.focus();
}

imagePresetButtons.forEach((btn) => {
	btn.addEventListener('click', () => {
		const preset = btn.dataset.imagePreset || '';
		applyImagePreset(preset);
		setActiveImagePresetButton(preset);
	});
	btn.addEventListener('keydown', onImagePresetKeydown);
});

setActiveImagePresetButton('');

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

if (imageProfileExportBtn) {
	imageProfileExportBtn.addEventListener('click', exportPresetsAsJson);
}

if (imageProfileImportBtn && imageProfileImportInput) {
	imageProfileImportBtn.addEventListener('click', () => {
		imageProfileImportInput.value = '';
		imageProfileImportInput.click();
	});
	imageProfileImportInput.addEventListener('change', () => {
		const file = imageProfileImportInput.files?.[0];
		if (file) importPresetsFromJson(file);
	});
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
	const runningPositions = new Map();
	const pendingPositions = new Map();

	running.forEach((item, index) => {
		const pid = item[1] || '';
		if (pid) {
			runningIds.add(pid);
			runningPositions.set(pid, index + 1);
		}
	});
	pending.forEach((item, index) => {
		const pid = item[1] || '';
		if (pid) {
			pendingIds.add(pid);
			pendingPositions.set(pid, index + 1);
		}
	});

	for (const promptId of trackedPromptIds) {
		const meta = queueJobMeta.get(promptId) || {};
		const prevStatus = meta.status || '';
		if (runningIds.has(promptId)) {
			if (prevStatus !== 'running' && !meta.startedAt) {
				meta.startedAt = Date.now();
			}
			meta.status = 'running';
			meta.missCount = 0;
		} else if (pendingIds.has(promptId)) {
			meta.status = 'queued';
			meta.missCount = 0;
		} else if (donePromptIds.has(promptId)) {
			if (prevStatus !== 'completed' && meta.startedAt) {
				meta.generationTimeMs = Date.now() - meta.startedAt;
			}
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
	const persistingCount = Array.from(queueJobMeta.entries()).filter(([promptId, meta]) => (
		trackedPromptIds.has(promptId) &&
		meta.status === 'processing' &&
		meta.failReason === HISTORY_PERSIST_PENDING_REASON
	)).length;
	if (clearFailedQueueBtn) {
		clearFailedQueueBtn.disabled = failedCount === 0;
		clearFailedQueueBtn.textContent = failedCount > 0 ? `Clear failed (${failedCount})` : 'Clear failed';
	}
	if (clearCompletedQueueBtn) {
		clearCompletedQueueBtn.disabled = completedCount === 0;
		clearCompletedQueueBtn.textContent = completedCount > 0 ? `Clear done (${completedCount})` : 'Clear done';
	}
	const visibleLabel = queueFilterFailedOnly ? 'Showing: Failed only' : 'Showing: All';
	queueSummary.textContent = `Running: ${runningCount}  Pending: ${pendingCount}  Persisting: ${persistingCount}  Tracked: ${trackedPromptIds.size}  Failed: ${failedCount}  Done: ${completedCount}  ${visibleLabel}`;
	renderQueueRestoreHint();

	const rows = Array.from(queueJobMeta.entries())
		.filter(([, meta]) => (queueFilterFailedOnly ? meta.status === 'failed' : true))
		.sort((a, b) => (b[1].updatedAt || 0) - (a[1].updatedAt || 0))
		.map(([promptId, meta]) => {
			const status = meta.status || 'queued';
			const promptLabel = escHtml(promptId);
			const snap = meta.snapshot || {};
			const runningPosition = runningPositions.get(promptId) || 0;
			const pendingPosition = pendingPositions.get(promptId) || 0;
			const isFrontQueued = pendingPosition === 1;
			const badge =
				status === 'running' ? `<span class="history-badge positive">RUN${meta.startedAt ? ` <span class="queue-elapsed" data-started-at="${meta.startedAt}">0s</span>` : ''}</span>` :
				status === 'queued' ? '<span class="history-badge">WAIT</span>' :
				(status === 'processing' && meta.failReason === HISTORY_PERSIST_PENDING_REASON) ? '<span class="history-badge">SAVE</span>' :
				status === 'completed' ? '<span class="history-badge positive">DONE</span>' :
				status === 'canceled' ? '<span class="history-badge negative">CANCEL</span>' :
				status === 'failed' ? '<span class="history-badge negative">FAIL</span>' :
				'<span class="history-badge">WORK</span>';

			const canCancel = status === 'queued' || status === 'running' || status === 'processing';
			const canRetry = status === 'failed' || status === 'canceled';
			const canRerun = status === 'completed' && snap.mode !== 'img2img' && !!String(snap.prompt || '').trim();
			const canPrioritize = status === 'queued' && !!String(snap.prompt || '').trim() &&
				(snap.mode !== 'img2img' || !!(snap.image || snap.image_name));
			const cancelBusy = queueActionInFlight.has(`cancel:${promptId}`);
			const retryBusy = queueActionInFlight.has(`retry:${promptId}`);
			const rerunBusy = queueActionInFlight.has(`rerun:${promptId}`);
			const prioritizeBusy = queueActionInFlight.has(`prioritize:${promptId}`);
			const reason = meta.failReason ? `<span class="queue-reason">${escHtml(meta.failReason)}</span>` : '';
			const promptDisplay = escHtml((snap.prompt || promptId).slice(0, 72));
			const actions = [
				canPrioritize ? `<button class="btn btn-ghost btn-xs queue-action" data-action="prioritize" data-prompt-id="${promptLabel}" aria-label="Move job ${promptLabel} to front" aria-keyshortcuts="Alt+ArrowUp" title="Move ${promptLabel} to front (Alt+ArrowUp)" ${prioritizeBusy ? 'disabled' : ''}>${prioritizeBusy ? 'Moving...' : 'Prioritize'}</button>` : '',
				canCancel ? `<button class="btn btn-ghost btn-xs queue-action" data-action="cancel" data-prompt-id="${promptLabel}" aria-label="Cancel job ${promptLabel}" title="Cancel ${promptLabel}" ${cancelBusy ? 'disabled' : ''}>${cancelBusy ? 'Canceling...' : 'Cancel'}</button>` : '',
				canRetry ? `<button class="btn btn-ghost btn-xs queue-action" data-action="retry" data-prompt-id="${promptLabel}" aria-label="Retry job ${promptLabel}" title="Retry ${promptLabel}" ${retryBusy ? 'disabled' : ''}>${retryBusy ? 'Retrying...' : 'Retry'}</button>` : '',
				canRerun ? `<button class="btn btn-ghost btn-xs queue-action" data-action="rerun" data-prompt-id="${promptLabel}" aria-label="Re-run job ${promptLabel}" title="Re-run ${promptLabel}" ${rerunBusy ? 'disabled' : ''}>${rerunBusy ? 'Queuing...' : 'Re-run'}</button>` : '',
			].join('');

			const chips = [
				snap.model ? `<span class="chip">${escHtml(String(snap.model).split('/').pop().split('\\').pop())}</span>` : '',
				status === 'running' && runningPosition ? `<span class="chip" title="Running position in ComfyUI" aria-label="Running position ${runningPosition}">run #${runningPosition}</span>` : '',
				(status === 'queued' || status === 'processing') && pendingPosition ? `<span class="chip" title="Pending queue position in ComfyUI" aria-label="Pending queue position ${pendingPosition}">queue #${pendingPosition}</span>` : '',
				(status === 'queued' || status === 'processing') && isFrontQueued ? '<span class="chip queue-chip-front">front</span>' : '',
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
	persistTrackedQueueState();
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
		queueActionInFlight.delete(`prioritize:${promptId}`);
		cleared += 1;
	}
	persistTrackedQueueState();
	return cleared;
}

async function clearFailedQueueItems() {
	const cleared = _clearQueueByStatus('failed');
	if (!cleared) {
		setQueueLastAction('Clear failed skipped: no failed items.');
		showToast('No failed items to clear.');
		renderQueueStatus([], [], new Set());
		return;
	}
	setQueueLastAction(`Cleared ${cleared} failed item${cleared === 1 ? '' : 's'}.`);
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
		setQueueLastAction('Clear done skipped: no completed items.');
		showToast('No completed items to clear.');
		renderQueueStatus([], [], new Set());
		return;
	}
	setQueueLastAction(`Cleared ${cleared} completed item${cleared === 1 ? '' : 's'}.`);
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
		persistTrackedQueueState();
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
		const isImg2Img = snapshot.mode === 'img2img' && (snapshot.image || snapshot.image_name);
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

		if (data && data.meta && data.meta.seed !== undefined && data.meta.seed !== null) {
			setLastGeneratedSeed(data.meta.seed);
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
		persistTrackedQueueState();
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
		persistTrackedQueueState();
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

async function prioritizeImageJob(promptId) {
	const snapshot = pendingImageJobs.get(promptId) || (queueJobMeta.get(promptId) || {}).snapshot;
	if (!snapshot || !String(snapshot.prompt || '').trim()) {
		showToast('Prioritize unavailable: no job snapshot found.', 'neg');
		return;
	}
	const isImg2Img = snapshot.mode === 'img2img';
	const img2imgImageName = isImg2Img ? (snapshot.image || snapshot.image_name || '') : '';
	if (isImg2Img && !img2imgImageName) {
		showToast('Prioritize unavailable: img2img source image reference not found in snapshot.', 'neg');
		return;
	}

	queueActionInFlight.add(`prioritize:${promptId}`);
	try {
		const cancelRes = await fetch('/api/image/cancel', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ prompt_id: promptId }),
		});
		const cancelData = await cancelRes.json().catch(() => ({}));
		if (!cancelRes.ok) {
			showToast(`Prioritize failed: ${cancelData.error || 'Could not cancel original job.'}`, 'neg');
			return;
		}

		const resubmitUrl = isImg2Img ? '/api/image/img2img-requeue' : '/api/image/generate';
		const resubmitBody = isImg2Img
			? { ...snapshot, image_name: img2imgImageName, queue_front: true }
			: { ...snapshot, queue_front: true };
		const res = await fetch(resubmitUrl, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(resubmitBody),
		});
		const data = await res.json().catch(() => ({}));
		if (!res.ok || !data.prompt_id) {
			showToast(`Prioritize failed: ${data.error || 'Could not submit prioritized job.'}`, 'neg');
			return;
		}

		trackedPromptIds.delete(promptId);
		pendingImageJobs.delete(promptId);
		const oldMeta = queueJobMeta.get(promptId) || {};
		oldMeta.status = 'canceled';
		oldMeta.failReason = `Re-queued at front as ${data.prompt_id}.`;
		oldMeta.updatedAt = Date.now();
		queueJobMeta.set(promptId, oldMeta);

		const nextPromptId = data.prompt_id;
		trackedPromptIds.add(nextPromptId);
		const nextSnapshot = { ...snapshot, ...(data.meta || {}) };
		pendingImageJobs.set(nextPromptId, nextSnapshot);
		queueJobMeta.set(nextPromptId, {
			status: 'queued',
			missCount: 0,
			updatedAt: Date.now(),
			snapshot: nextSnapshot,
		});
		incrementQueueTelemetry('submitted');
		persistTrackedQueueState();
		ensureQueuePolling();
		setQueueLastAction('Moved a job to the front of the queue.');
		showToast('Job moved to the front of the queue.', 'pos');
		await pollQueue();
	} catch (err) {
		showToast(`Prioritize failed: ${err.message}`, 'neg');
	} finally {
		queueActionInFlight.delete(`prioritize:${promptId}`);
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

function onQueueActionKeydown(event) {
	const target = event.target;
	if (!(target instanceof HTMLElement)) return;
	if (!target.classList.contains('queue-action')) return;
	if (event.altKey && event.key === 'ArrowUp') {
		const promptId = target.getAttribute('data-prompt-id') || '';
		if (!promptId) return;
		event.preventDefault();
		const row = target.closest('.queue-item');
		const prioritizeBtn = row ? row.querySelector('.queue-action[data-action="prioritize"]') : null;
		if (!(prioritizeBtn instanceof HTMLButtonElement) || prioritizeBtn.disabled) return;
		if (queueActionInFlight.has(`prioritize:${promptId}`)) return;
		prioritizeBtn.disabled = true;
		prioritizeImageJob(promptId);
		return;
	}
	const key = event.key;
	if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
	const row = target.closest('.queue-item');
	if (!row) return;
	const actions = Array.from(row.querySelectorAll('.queue-action'));
	if (actions.length < 2) return;
	const currentIndex = actions.indexOf(target);
	if (currentIndex < 0) return;
	event.preventDefault();
	let nextIndex = currentIndex;
	if (key === 'Home') {
		nextIndex = 0;
	} else if (key === 'End') {
		nextIndex = actions.length - 1;
	} else if (key === 'ArrowRight') {
		nextIndex = (currentIndex + 1) % actions.length;
	} else if (key === 'ArrowLeft') {
		nextIndex = (currentIndex - 1 + actions.length) % actions.length;
	}
	const nextAction = actions[nextIndex];
	if (nextAction) nextAction.focus();
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
	if (action === 'prioritize') {
		if (queueActionInFlight.has(`prioritize:${promptId}`)) return;
		target.setAttribute('disabled', 'disabled');
		await prioritizeImageJob(promptId);
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

queueList.addEventListener('keydown', onQueueActionKeydown);

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

if (queueUiResetBtn) {
	queueUiResetBtn.addEventListener('click', () => {
		queueFilterFailedOnly = false;
		queueRestoreHintHidden = false;
		if (failedOnlyToggle) failedOnlyToggle.checked = false;
		localStorage.removeItem('queueFilterFailedOnly');
		localStorage.removeItem(QUEUE_RESTORE_HINT_HIDDEN_KEY);
		setQueueLastAction('Queue UI preferences reset.');
		renderQueueStatus([], [], new Set());
		showToast('Queue UI preferences reset.', 'pos');
	});
}

async function saveHistoryEntry(entry) {
	try {
		const res = await fetch('/api/history', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(entry),
		});
		return res.ok;
	} catch {
		return false;
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
	const parts = [];
	if (gallerySearchQuery) parts.push(`prompt "${gallerySearchQuery}"`);
	if (galleryTagFilter && galleryTagFilter !== 'all') parts.push(`#${galleryTagFilter}`);
	if (!parts.length || !total) {
		galleryFilterHint.hidden = true;
		galleryFilterHint.textContent = '';
		return;
	}
	galleryFilterHint.hidden = false;
	const summary = parts.join(' + ');
	galleryFilterHint.textContent = matching
		? `Showing ${matching} of ${total} images matching ${summary}`
		: `No images match ${summary}`;
}

function updateLightboxNav() {
	const total = currentGalleryImages.length;
	if (galleryLightboxPrev) {
		galleryLightboxPrev.hidden = total <= 1;
		galleryLightboxPrev.setAttribute('aria-hidden', total <= 1 ? 'true' : 'false');
	}
	if (galleryLightboxNext) {
		galleryLightboxNext.hidden = total <= 1;
		galleryLightboxNext.setAttribute('aria-hidden', total <= 1 ? 'true' : 'false');
	}
	if (galleryLightboxCounter) {
		galleryLightboxCounter.textContent = total > 1 ? `${lightboxCurrentIndex + 1} / ${total}` : '';
	}
}

function getImg2ImgSourceImageUrl(entry) {
	const imageName = String(entry?.params?.image || entry?.params?.image_name || '').trim();
	if (!imageName) return '';
	return `/api/image/view?filename=${encodeURIComponent(imageName)}&subfolder=&type=input`;
}

function computeGenerationStats(params) {
	if (!params) return null;
	const genTimeMs = Number.isFinite(Number(params.generation_time_ms)) ? Number(params.generation_time_ms) : null;
	const steps = Number.isFinite(Number(params.steps)) ? Number(params.steps) : null;
	if (!genTimeMs || !steps) return null;
	const genTimeSec = genTimeMs / 1000;
	const stepsPerSec = steps / genTimeSec;
	return {
		totalTime: genTimeMs,
		totalTimeSec: genTimeSec,
		steps: steps,
		stepsPerSec: stepsPerSec,
	};
}

function updateLightboxMeta(entry) {
	const hasParams = entry && (entry.model || entry.params);
	if (galleryLightboxMetaToggle) {
		galleryLightboxMetaToggle.hidden = !hasParams;
		galleryLightboxMetaToggle.setAttribute('aria-hidden', hasParams ? 'false' : 'true');
	}
	if (!galleryLightboxMetaChips || !hasParams) return;
	const p = entry.params || {};
	const chips = [];
	const mode = String(p.mode || 'txt2img');
	chips.push(`<span class="chip chip-mode">${escHtml(mode)}</span>`);
	if (entry.model) chips.push(`<span class="chip chip-model" title="${escHtml(entry.model)}">${escHtml(entry.model.split('/').pop() || entry.model)}</span>`);
	if (p.sampler) chips.push(`<span class="chip">sampler: ${escHtml(p.sampler)}</span>`);
	if (p.scheduler && p.scheduler !== 'normal') chips.push(`<span class="chip">scheduler: ${escHtml(p.scheduler)}</span>`);
	if (Number.isFinite(Number(p.steps))) chips.push(`<span class="chip">steps: ${escHtml(String(p.steps))}</span>`);
	if (Number.isFinite(Number(p.cfg))) chips.push(`<span class="chip">cfg: ${escHtml(String(p.cfg))}</span>`);
	if (Number.isFinite(Number(p.batch_size)) && Number(p.batch_size) > 1) chips.push(`<span class="chip">batch: ${escHtml(String(p.batch_size))}</span>`);
	if (Number.isFinite(Number(p.width)) && Number.isFinite(Number(p.height))) {
		chips.push(`<span class="chip">${escHtml(String(p.width))}×${escHtml(String(p.height))}</span>`);
	}
	if (Number.isFinite(Number(p.denoise)) && mode === 'img2img') {
		chips.push(`<span class="chip">denoise: ${escHtml(String(Number(p.denoise).toFixed(2)))}</span>`);
	}
	const seed = p.seed !== undefined && p.seed !== null && p.seed !== '' ? String(p.seed) : '';
	if (seed) chips.push(`<span class="chip">seed: ${escHtml(seed)}</span>`);
	if (entry.model && p.vae) chips.push(`<span class="chip">vae: ${escHtml(p.vae.split('/').pop() || p.vae)}</span>`);
	const loras = Array.isArray(p.loras) ? p.loras : [];
	for (const lora of loras) {
		if (!lora.name) continue;
		const loraLabel = lora.name.split('/').pop() || lora.name;
		const str = Number.isFinite(Number(lora.strength)) ? ` ×${Number(lora.strength).toFixed(2)}` : '';
		chips.push(`<span class="chip chip-lora">LoRA: ${escHtml(loraLabel)}${escHtml(str)}</span>`);
	}
	const genTimeMs = Number.isFinite(Number(p.generation_time_ms)) ? Number(p.generation_time_ms) : null;
	if (genTimeMs) chips.push(`<span class="chip">⏱ ${escHtml(_formatGenTime(genTimeMs))}</span>`);
	if (p.controlnet_model) {
		const cnLabel = p.controlnet_model.split('/').pop() || p.controlnet_model;
		const cnWeight = Number.isFinite(Number(p.controlnet_weight)) ? ` ×${Number(p.controlnet_weight).toFixed(2)}` : '';
		const cnPrep = (p.controlnet_preprocessor && p.controlnet_preprocessor !== 'none') ? ` [${p.controlnet_preprocessor}]` : '';
		chips.push(`<span class="chip chip-controlnet" title="ControlNet: ${escHtml(p.controlnet_model)}">CN: ${escHtml(cnLabel)}${escHtml(cnWeight)}${escHtml(cnPrep)}</span>`);
	}
	const tags = getGalleryTags(entry);
	if (tags.length) chips.push(`<span class="chip" title="Tags">#${escHtml(tags.join(' #'))}</span>`);
	galleryLightboxMetaChips.innerHTML = chips.join('');
	// Populate stats section
	const stats = computeGenerationStats(p);
	if (galleryLightboxStats) {
		if (stats) {
			galleryLightboxStats.hidden = false;
			const timeStr = _formatGenTime(stats.totalTime);
			const throughputStr = stats.stepsPerSec.toFixed(2);
			galleryLightboxStats.innerHTML = `<div class="stats-row" aria-label="Generation stats">Generated in ${escHtml(timeStr)} (${escHtml(String(stats.steps))} steps @ ${escHtml(throughputStr)} step/s)</div>`;
		} else {
			galleryLightboxStats.hidden = true;
			galleryLightboxStats.innerHTML = '';
		}
	}
}

function renderLightboxTags(entry) {
	if (!galleryLightboxTags || !galleryLightboxTagInput || !galleryLightboxAddTagBtn) return;
	const key = getGalleryEntryTagKey(entry);
	const tags = getGalleryTags(entry);
	galleryLightboxAddTagBtn.disabled = !key;
	galleryLightboxTagInput.disabled = !key;
	galleryLightboxTagInput.placeholder = key ? 'Add tag (e.g., portrait, fav, draft)' : 'No taggable entry';
	if (!key) {
		galleryLightboxTags.innerHTML = '<span class="hint">Tags unavailable for this entry.</span>';
		return;
	}
	if (!tags.length) {
		galleryLightboxTags.innerHTML = '<span class="hint">No tags yet.</span>';
		return;
	}
	galleryLightboxTags.innerHTML = tags
		.map((tag) => `<button class="btn btn-ghost btn-xs gallery-tag-chip" type="button" data-gallery-tag-remove="${escHtml(tag)}" title="Remove tag">#${escHtml(tag)} ×</button>`)
		.join('');
}

function resolveLegacyImg2ImgSourceImage(entry) {
	if (!entry || entry?.params?.mode !== 'img2img') return Promise.resolve('');
	const existing = String(entry?.params?.image || entry?.params?.image_name || '').trim();
	if (existing) return Promise.resolve(existing);
	const promptId = String(entry?.params?.prompt_id || '').trim();
	if (!promptId) return Promise.resolve('');
	if (img2imgSourceResolveCache.has(promptId)) {
		return img2imgSourceResolveCache.get(promptId);
	}
	const pending = fetch(`/api/image/source-image?prompt_id=${encodeURIComponent(promptId)}`)
		.then((res) => (res.ok ? res.json() : null))
		.then((data) => {
			const name = String(data?.image || '').trim();
			if (name) {
				entry.params = entry.params || {};
				entry.params.image = name;
				const entryId = String(entry?.id || '').trim();
				fetch('/api/history/img2img-source', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						entry_id: entryId,
						prompt_id: promptId,
						image: name,
					}),
				}).catch(() => {
					// non-fatal history backfill failure
				});
			}
			return name;
		})
		.catch(() => '')
		.finally(() => {
			if (!String(entry?.params?.image || '').trim()) {
				img2imgSourceResolveCache.delete(promptId);
			}
		});
	img2imgSourceResolveCache.set(promptId, pending);
	return pending;
}

function applyLightboxCompareSplit(splitValue) {
	const split = Math.max(0, Math.min(100, Number(splitValue) || 50));
	lightboxCompareSplit = split;
	if (galleryLightboxAfterWrap) {
		galleryLightboxAfterWrap.style.width = `${split}%`;
	}
	if (galleryLightboxCompareSlider && Number(galleryLightboxCompareSlider.value) !== split) {
		galleryLightboxCompareSlider.value = String(split);
	}
}

function updateLightboxMedia(entry, fallbackSrc = '', fallbackAlt = 'Generated image', fallbackCaption = '') {
	if (!galleryLightboxImage) return;
	const firstImage = entry?.images?.[0];
	const outputUrl = firstImage ? imageProxyUrl(firstImage) : fallbackSrc;
	const caption = entry?.prompt || fallbackCaption || 'Untitled generation';
	const isImg2Img = entry?.params?.mode === 'img2img';
	const hasImg2ImgSource = isImg2Img && Boolean(entry?.params?.image || entry?.params?.image_name);
	const sourceUrl = hasImg2ImgSource ? getImg2ImgSourceImageUrl(entry) : '';

	updateLightboxMeta(entry);
	renderLightboxTags(entry);
	updateLightboxStarBtn(entry);

	if (!sourceUrl && isImg2Img) {
		resolveLegacyImg2ImgSourceImage(entry).then((resolvedName) => {
			if (!resolvedName) return;
			if (currentGalleryImages[lightboxCurrentIndex] !== entry) return;
			if (galleryLightbox?.hidden) return;
			updateLightboxMedia(entry, fallbackSrc, fallbackAlt, fallbackCaption);
		});
	}

	if (galleryLightboxCompareToggle) {
		if (sourceUrl) {
			galleryLightboxCompareToggle.hidden = false;
			galleryLightboxCompareToggle.setAttribute('aria-hidden', 'false');
			galleryLightboxCompareToggle.disabled = false;
			galleryLightboxCompareToggle.dataset.mode = 'compare';
			galleryLightboxCompareToggle.textContent = 'Compare';
			galleryLightboxCompareToggle.title = '';
		} else if (isImg2Img) {
			galleryLightboxCompareToggle.hidden = false;
			galleryLightboxCompareToggle.setAttribute('aria-hidden', 'false');
			galleryLightboxCompareToggle.disabled = false;
			galleryLightboxCompareToggle.dataset.mode = 'attach';
			galleryLightboxCompareToggle.textContent = 'Attach source';
			galleryLightboxCompareToggle.title = 'Upload the missing source image to enable Compare for this entry.';
		} else {
			galleryLightboxCompareToggle.hidden = true;
			galleryLightboxCompareToggle.setAttribute('aria-hidden', 'true');
			galleryLightboxCompareToggle.disabled = false;
			galleryLightboxCompareToggle.dataset.mode = '';
			galleryLightboxCompareToggle.textContent = 'Compare';
			galleryLightboxCompareToggle.title = '';
		}
		if (!sourceUrl) {
			lightboxCompareEnabled = false;
			galleryLightboxCompareToggle.setAttribute('aria-pressed', 'false');
		}
	}

	const showCompare = Boolean(sourceUrl && lightboxCompareEnabled && galleryLightboxCompare && galleryLightboxBeforeImage && galleryLightboxAfterImage);
	if (showCompare) {
		galleryLightboxImage.hidden = true;
		galleryLightboxCompare.hidden = false;
		galleryLightboxBeforeImage.src = sourceUrl;
		galleryLightboxAfterImage.src = outputUrl;
		applyLightboxCompareSplit(lightboxCompareSplit);
	} else {
		galleryLightboxImage.hidden = false;
		galleryLightboxImage.src = outputUrl;
		galleryLightboxImage.alt = fallbackAlt || 'Generated image';
		if (galleryLightboxCompare) {
			galleryLightboxCompare.hidden = true;
		}
		if (galleryLightboxBeforeImage) galleryLightboxBeforeImage.removeAttribute('src');
		if (galleryLightboxAfterImage) galleryLightboxAfterImage.removeAttribute('src');
	}

	if (galleryLightboxCaption) {
		galleryLightboxCaption.textContent = caption;
	}
}

function navigateLightbox(delta) {
	const total = currentGalleryImages.length;
	if (total <= 1) return;
	lightboxCurrentIndex = ((lightboxCurrentIndex + delta) % total + total) % total;
	const entry = currentGalleryImages[lightboxCurrentIndex];
	if (!entry) return;
	updateLightboxMedia(entry, '', 'Generated image', entry.prompt || 'Untitled generation');
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

function inferImageModelRole(typeValue = '', folderValue = '') {
	const raw = `${String(typeValue || '')} ${String(folderValue || '')}`.toLowerCase();
	if (raw.includes('lora') || raw.includes('lycoris')) return 'lora';
	return 'checkpoint';
}

function useModelInImageGen(modelLike) {
	if (!modelLike) return;
	showPanel('image');

	const role = inferImageModelRole(modelLike.type, modelLike.folder);
	const name = String(modelLike.name || '').trim();
	if (!name) return;

	if (role === 'lora') {
		if (!loraStackContainer) {
			showToast('LoRA stack is unavailable in this view.', 'neg');
			return;
		}
		// Add a new LoRA row pre-selected with this model
		addLoraRow();
		const lastRow = loraStackContainer.lastElementChild;
		if (lastRow) {
			const sel = lastRow.querySelector('.lora-row-select');
			if (sel) {
				const opt = document.createElement('option');
				opt.value = name;
				opt.textContent = name;
				sel.appendChild(opt);
				sel.value = name;
				sel.dispatchEvent(new Event('change'));
			}
		}
		showToast(`Added LoRA: ${name}`, 'pos');
		return;
	}

	setSelectValueIfOptionExists(imageModelSelect, name);
	showToast(`Selected checkpoint: ${name}`, 'pos');
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
	setSelectValueIfOptionExists(imageSchedulerSelect, payload.scheduler);
	if (loraStackContainer) {
		const incomingLoras = Array.isArray(payload.loras) ? payload.loras : [];
		if (incomingLoras.length) {
			loraStackContainer.innerHTML = '';
			for (const entry of incomingLoras) {
				const name = String(entry?.name || '').trim();
				if (!name) continue;
				addLoraRow();
				const row = loraStackContainer.lastElementChild;
				if (!row) continue;
				const sel = row.querySelector('.lora-row-select');
				const str = row.querySelector('.lora-row-strength');
				const strVal = row.querySelector('.lora-strength-val');
				if (sel) {
					if (![...sel.options].some((o) => o.value === name)) {
						const opt = document.createElement('option');
						opt.value = name;
						opt.textContent = name;
						sel.appendChild(opt);
					}
					sel.value = name;
					sel.dispatchEvent(new Event('change'));
				}
				const n = Number(entry?.strength);
				if (str && Number.isFinite(n)) {
					str.value = String(n);
					if (strVal) strVal.textContent = n.toFixed(2);
				}
			}
		} else {
			const legacyLora = String(payload.lora || '').trim();
			if (legacyLora) {
				let row = [...loraStackContainer.querySelectorAll('.lora-row')]
					.find((r) => !(r.querySelector('.lora-row-select')?.value || '').trim());
				if (!row) {
					addLoraRow();
					row = loraStackContainer.lastElementChild;
				}
				if (row) {
					const sel = row.querySelector('.lora-row-select');
					const str = row.querySelector('.lora-row-strength');
					const strVal = row.querySelector('.lora-strength-val');
					if (sel) {
						if (![...sel.options].some((o) => o.value === legacyLora)) {
							const opt = document.createElement('option');
							opt.value = legacyLora;
							opt.textContent = legacyLora;
							sel.appendChild(opt);
						}
						sel.value = legacyLora;
						sel.dispatchEvent(new Event('change'));
					}
					const n = Number(payload.lora_strength);
					if (str && Number.isFinite(n)) {
						str.value = String(n);
						if (strVal) strVal.textContent = n.toFixed(2);
					}
				}
			}
		}
	}
	setSelectValueIfOptionExists(controlnetModelSelect, payload.controlnet_model);
	setSelectValueIfOptionExists(controlnetPreprocessorSelect, payload.controlnet_preprocessor);

	if (payload.seed !== null && payload.seed !== undefined && payload.seed !== '') {
		imageSeed.value = String(payload.seed);
	}
	setNumericInputIfFinite(controlnetWeight, payload.controlnet_weight);
	setNumericInputIfFinite(controlnetStart, payload.controlnet_start);
	setNumericInputIfFinite(controlnetEnd, payload.controlnet_end);
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
	galleryLightboxLastFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
	lightboxCurrentIndex = index;
	const entry = currentGalleryImages[index];
	updateLightboxMedia(entry, imgSrc, imgAlt || 'Generated image', caption);
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
	galleryLightboxImage.hidden = false;
	if (galleryLightboxCompare) {
		galleryLightboxCompare.hidden = true;
	}
	if (galleryLightboxBeforeImage) galleryLightboxBeforeImage.removeAttribute('src');
	if (galleryLightboxAfterImage) galleryLightboxAfterImage.removeAttribute('src');
	lightboxCompareEnabled = false;
	if (galleryLightboxCompareToggle) {
		galleryLightboxCompareToggle.setAttribute('aria-pressed', 'false');
	}
	lightboxMetaOpen = false;
	if (galleryLightboxMeta) galleryLightboxMeta.hidden = true;
	if (galleryLightboxMetaToggle) {
		galleryLightboxMetaToggle.setAttribute('aria-pressed', 'false');
		galleryLightboxMetaToggle.hidden = true;
		galleryLightboxMetaToggle.setAttribute('aria-hidden', 'true');
	}
	if (galleryLightboxMetaChips) galleryLightboxMetaChips.innerHTML = '';
	if (galleryLightboxStats) {
		galleryLightboxStats.innerHTML = '';
		galleryLightboxStats.hidden = true;
	}
	if (galleryLightboxTags) galleryLightboxTags.innerHTML = '';
	if (galleryLightboxTagInput) galleryLightboxTagInput.value = '';
	if (galleryLightboxCaption) {
		galleryLightboxCaption.textContent = '';
	}
	document.body.classList.remove('gallery-lightbox-open');
	if (galleryLightboxLastFocus && document.contains(galleryLightboxLastFocus)) {
		galleryLightboxLastFocus.focus();
	}
	galleryLightboxLastFocus = null;
}

function loadGalleryFavorites() {
	try {
		return new Set(JSON.parse(localStorage.getItem(GALLERY_FAVORITES_KEY) || '[]'));
	} catch {
		return new Set();
	}
}

function saveGalleryFavorites(favSet) {
	localStorage.setItem(GALLERY_FAVORITES_KEY, JSON.stringify([...favSet]));
}

function isGalleryFavorite(entryId) {
	return Boolean(entryId) && loadGalleryFavorites().has(entryId);
}

function toggleGalleryFavorite(entryId) {
	if (!entryId) return false;
	const favs = loadGalleryFavorites();
	if (favs.has(entryId)) {
		favs.delete(entryId);
	} else {
		favs.add(entryId);
	}
	saveGalleryFavorites(favs);
	return favs.has(entryId);
}

function updateLightboxStarBtn(entry) {
	if (!galleryLightboxStarBtn) return;
	const entryId = entry?.id || '';
	galleryLightboxStarBtn.hidden = !entryId;
	galleryLightboxStarBtn.setAttribute('aria-hidden', entryId ? 'false' : 'true');
	const isFav = isGalleryFavorite(entryId);
	galleryLightboxStarBtn.setAttribute('aria-pressed', String(isFav));
	galleryLightboxStarBtn.setAttribute('aria-label', isFav ? 'Remove from favorites' : 'Add to favorites');
	galleryLightboxStarBtn.textContent = isFav ? '\u2605 Fav' : '\u2606 Fav';
}

function _formatGenTime(ms) {
	const s = ms / 1000;
	if (s < 60) return `${s < 10 ? s.toFixed(1) : Math.round(s)}s`;
	return `${Math.floor(s / 60)}m ${Math.round(s % 60)}s`;
}

function buildGalleryCardHtml(entry, index) {
	const firstImage = entry.images?.[0];
	if (!firstImage) return '';
	const imgUrl = imageProxyUrl(firstImage);
	const eagerLoad = index < GALLERY_EAGER_IMAGE_COUNT ? 'eager' : 'lazy';
	const fetchPriority = index < 2 ? 'high' : 'low';
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
	const genTimeMs = Number.isFinite(Number(entry.params?.generation_time_ms)) ? Number(entry.params.generation_time_ms) : null;
	const genTimeChip = genTimeMs ? `<span class="chip gallery-gentime-chip" title="Generation time">⏱ ${escHtml(_formatGenTime(genTimeMs))}</span>` : '';
	const tags = getGalleryTags(entry);
	const tagsChip = tags.length
		? `<span class="chip gallery-tag-summary" title="${escHtml(tags.join(', '))}">#${escHtml(tags[0])}${tags.length > 1 ? ` +${tags.length - 1}` : ''}</span>`
		: '';
	const entryId = entry.id || '';
	const isFav = isGalleryFavorite(entryId);
	const isSelected = gallerySelectMode && gallerySelectedIds.has(entryId);
	const selectCheck = gallerySelectMode ? `<span class="gallery-select-check" aria-hidden="true">${isSelected ? '\u2713' : ''}</span>` : '';
	return `
		<article class="gallery-card${isSelected ? ' is-selected' : ''}" draggable="${gallerySelectMode ? 'false' : 'true'}" data-preview-payload="${dragPayload}" data-image-ref="${imageRefPayload}" data-export-base-name="${escHtml(exportBaseName)}" data-prompt="${prompt}" data-lightbox-index="${index}" data-entry-id="${escHtml(entryId)}">
			${selectCheck}
			<button class="gallery-star-btn${isFav ? ' is-favorited' : ''}" type="button" aria-pressed="${isFav}" aria-label="${isFav ? 'Remove from favorites' : 'Add to favorites'}" data-entry-id="${escHtml(entryId)}">${isFav ? '\u2605' : '\u2606'}</button>
			<img src="${imgUrl}" alt="Generated image" loading="${eagerLoad}" fetchpriority="${fetchPriority}" decoding="async" data-lightbox-src="${imgUrl}" data-lightbox-caption="${prompt}" draggable="false" />
			<div class="gallery-meta">
				<p class="gallery-prompt" title="${prompt}">${prompt}</p>
				<p class="gallery-chip-row">
					<span class="chip">${model}</span>
					<span class="chip">${sampler}</span>
					<span class="chip">steps ${steps}</span>
					<span class="chip">cfg ${cfg}</span>
					${genTimeChip}
					${tagsChip}
				</p>
			</div>
		</article>
	`;
}

function _getGalleryVirtualMetrics(totalItems) {
	const isGrid = galleryViewMode === 'grid';
	const viewportHeight = Math.max(galleryGrid?.clientHeight || 0, 200);
	const scrollTop = Math.max(galleryGrid?.scrollTop || 0, 0);
	const rowHeight = isGrid ? GALLERY_GRID_EST_CARD_HEIGHT : GALLERY_LIST_EST_CARD_HEIGHT;
	const gap = 12;
	const clientWidth = Math.max(galleryGrid?.clientWidth || 0, GALLERY_GRID_MIN_COL_WIDTH);
	const columns = isGrid
		? Math.max(1, Math.floor((clientWidth + gap) / (GALLERY_GRID_MIN_COL_WIDTH + gap)))
		: 1;
	const totalRows = Math.ceil(totalItems / columns);
	const visibleRows = Math.max(1, Math.ceil(viewportHeight / rowHeight));
	const startRow = Math.max(0, Math.floor(scrollTop / rowHeight) - GALLERY_VIRTUAL_OVERSCAN_ROWS);
	const endRow = Math.min(totalRows, startRow + visibleRows + (GALLERY_VIRTUAL_OVERSCAN_ROWS * 2));
	const startIndex = startRow * columns;
	const endIndex = Math.min(totalItems, endRow * columns);
	const spacerTop = startRow * rowHeight;
	const spacerBottom = Math.max(0, (totalRows - endRow) * rowHeight);
	return { startIndex, endIndex, spacerTop, spacerBottom };
}

function _renderVirtualGalleryWindow() {
	if (!galleryVirtualState || !galleryGrid) return;
	const { entries, seq } = galleryVirtualState;
	if (seq !== galleryRenderSeq) return;
	const { startIndex, endIndex, spacerTop, spacerBottom } = _getGalleryVirtualMetrics(entries.length);
	let html = `<div class="gallery-virtual-spacer" style="height:${spacerTop}px"></div>`;
	for (let i = startIndex; i < endIndex; i += 1) {
		html += buildGalleryCardHtml(entries[i], i);
	}
	html += `<div class="gallery-virtual-spacer" style="height:${spacerBottom}px"></div>`;
	galleryGrid.innerHTML = html;
}

function _scheduleVirtualGalleryWindowRender() {
	if (!galleryVirtualState || galleryVirtualRaf !== null) return;
	galleryVirtualRaf = window.requestAnimationFrame(() => {
		galleryVirtualRaf = null;
		_renderVirtualGalleryWindow();
	});
}

function renderGallery(history) {
	currentFullHistory = history;
	const images = history.filter((item) => item.type === 'image');
	syncGalleryTagFilterOptions(images);
	if (!images.length) {
		galleryVirtualState = null;
		galleryGrid.innerHTML = '<div class="empty-gallery">No image generations yet.</div>';
		currentGalleryImages = [];
		closeGalleryContextMenu();
		updateGalleryFilterHint(0, 0);
		return;
	}

	// Sort: newest (default, already API order), oldest, or favorites first.
	let orderedImages;
	if (gallerySortOrder === 'oldest') {
		orderedImages = [...images].reverse();
	} else if (gallerySortOrder === 'favorites-first') {
		orderedImages = images
			.map((entry, index) => ({ entry, index }))
			.sort((a, b) => {
				const aFav = isGalleryFavorite(a.entry?.id || '');
				const bFav = isGalleryFavorite(b.entry?.id || '');
				if (aFav !== bFav) return aFav ? -1 : 1;
				return a.index - b.index;
			})
			.map((item) => item.entry);
	} else {
		orderedImages = images;
	}

	// Mode filter
	const modeFiltered = galleryModeFilter === 'all'
		? orderedImages
		: galleryModeFilter === 'img2img'
			? orderedImages.filter((e) => e?.params?.mode === 'img2img')
			: galleryModeFilter === 'favorites'
				? orderedImages.filter((e) => isGalleryFavorite(e?.id || ''))
				: orderedImages.filter((e) => e?.params?.mode !== 'img2img');

	const tagFiltered = galleryTagFilter === 'all'
		? modeFiltered
		: modeFiltered.filter((e) => getGalleryTags(e).includes(galleryTagFilter));

	const query = gallerySearchQuery.toLowerCase().trim();
	const filteredImages = query
		? tagFiltered.filter((e) => (e.prompt || '').toLowerCase().includes(query))
		: tagFiltered;

	updateGalleryFilterHint(filteredImages.length, tagFiltered.length);

	if (!filteredImages.length) {
		galleryVirtualState = null;
		galleryGrid.innerHTML = '<div class="empty-gallery">No images match that filter.</div>';
		currentGalleryImages = [];
		return;
	}

	currentGalleryImages = filteredImages;
	galleryGrid.classList.toggle('is-grid-mode', galleryViewMode === 'grid');

	const renderSeq = ++galleryRenderSeq;
	if (filteredImages.length >= GALLERY_VIRTUALIZE_THRESHOLD) {
		galleryVirtualState = {
			entries: filteredImages,
			seq: renderSeq,
		};
		_renderVirtualGalleryWindow();
		return;
	}

	galleryVirtualState = null;
	if (filteredImages.length > GALLERY_RENDER_CHUNK_SIZE) {
		galleryGrid.innerHTML = '<div class="empty-gallery">Rendering gallery...</div>';
	}

	const renderChunk = (startIndex) => {
		if (renderSeq !== galleryRenderSeq) return;
		if (startIndex === 0) {
			galleryGrid.innerHTML = '';
		}
		const endIndex = Math.min(startIndex + GALLERY_RENDER_CHUNK_SIZE, filteredImages.length);
		let html = '';
		for (let i = startIndex; i < endIndex; i += 1) {
			html += buildGalleryCardHtml(filteredImages[i], i);
		}
		if (html) {
			galleryGrid.insertAdjacentHTML('beforeend', html);
		}
		if (endIndex < filteredImages.length) {
			window.requestAnimationFrame(() => renderChunk(endIndex));
		}
	};

	renderChunk(0);
}

function updateGallerySelectToolbar() {
	const count = gallerySelectedIds.size;
	if (gallerySelectCountEl) gallerySelectCountEl.textContent = `${count} selected`;
	if (galleryBulkDeleteBtn) galleryBulkDeleteBtn.disabled = count === 0;
	if (galleryBulkExportBtn) galleryBulkExportBtn.disabled = count === 0;
	if (gallerySelectToolbar) gallerySelectToolbar.hidden = !gallerySelectMode;
	if (gallerySelectModeBtn) {
		gallerySelectModeBtn.setAttribute('aria-pressed', gallerySelectMode ? 'true' : 'false');
		gallerySelectModeBtn.textContent = gallerySelectMode ? 'Exit select' : 'Select';
	}
	if (galleryGrid) galleryGrid.classList.toggle('is-select-mode', gallerySelectMode);
}

function enterGallerySelectMode() {
	gallerySelectMode = true;
	gallerySelectedIds.clear();
	galleryLastSelectedIndex = -1;
	updateGallerySelectToolbar();
	renderGallery(currentFullHistory);
}

function exitGallerySelectMode() {
	gallerySelectMode = false;
	gallerySelectedIds.clear();
	galleryLastSelectedIndex = -1;
	updateGallerySelectToolbar();
	renderGallery(currentFullHistory);
}

function toggleGalleryCardSelection(entryId, index, isShift) {
	if (isShift && galleryLastSelectedIndex >= 0 && currentGalleryImages.length) {
		const start = Math.min(galleryLastSelectedIndex, index);
		const end = Math.max(galleryLastSelectedIndex, index);
		for (let i = start; i <= end; i += 1) {
			const id = currentGalleryImages[i]?.id || '';
			if (id) gallerySelectedIds.add(id);
		}
	} else {
		if (gallerySelectedIds.has(entryId)) {
			gallerySelectedIds.delete(entryId);
		} else {
			gallerySelectedIds.add(entryId);
		}
	}
	galleryLastSelectedIndex = index;
	updateGallerySelectToolbar();
	// Update card classes directly for instant feedback without full re-render
	if (galleryGrid) {
		galleryGrid.querySelectorAll('.gallery-card').forEach((card) => {
			const id = card.dataset.entryId || '';
			const selected = gallerySelectedIds.has(id);
			card.classList.toggle('is-selected', selected);
			const check = card.querySelector('.gallery-select-check');
			if (check) check.textContent = selected ? '\u2713' : '';
		});
	}
}

async function bulkDeleteSelectedGalleryItems() {
	if (!gallerySelectedIds.size) return;
	const ids = Array.from(gallerySelectedIds);
	// Collect image_refs from the current gallery entries matching selected ids
	const imageRefs = currentGalleryImages
		.filter((e) => ids.includes(e.id || ''))
		.flatMap((e) => {
			const imgs = e.images || [];
			return imgs.map((img) => ({
				filename: img.filename || '',
				subfolder: img.subfolder || '',
				type: img.type || 'output',
			}));
		});

	if (!imageRefs.length) return;
	if (!confirm(`Delete ${ids.length} selected image${ids.length === 1 ? '' : 's'} from disk? This cannot be undone.`)) return;

	try {
		const resp = await fetch('/api/gallery/bulk-delete', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ image_refs: imageRefs }),
		});
		const data = await resp.json().catch(() => ({}));
		if (!resp.ok) {
			showToast(data.error || 'Bulk delete failed', 'error');
			return;
		}
		showToast(`Deleted ${data.deleted ?? 0} image${(data.deleted ?? 0) === 1 ? '' : 's'}.`);
		gallerySelectedIds.clear();
		galleryLastSelectedIndex = -1;
		updateGallerySelectToolbar();
		await loadGallery();
	} catch (err) {
		showToast('Bulk delete error: ' + String(err), 'error');
	}
}

async function bulkExportSelectedGalleryItems() {
	if (!gallerySelectedIds.size) return;
	const ids = Array.from(gallerySelectedIds);
	const imageRefs = currentGalleryImages
		.filter((e) => ids.includes(e.id || ''))
		.flatMap((e) => {
			const imgs = e.images || [];
			return imgs.map((img) => ({
				filename: img.filename || '',
				subfolder: img.subfolder || '',
				type: img.type || 'output',
			}));
		});

	if (!imageRefs.length) return;

	try {
		const resp = await fetch('/api/gallery/bulk-export', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ image_refs: imageRefs }),
		});
		if (!resp.ok) {
			const data = await resp.json().catch(() => ({}));
			showToast(data.error || 'Export failed', 'error');
			return;
		}
		const blob = await resp.blob();
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		const cd = resp.headers.get('Content-Disposition') || '';
		const match = cd.match(/filename="?([^"]+)"?/);
		a.download = match ? match[1] : 'gallery_export.zip';
		a.href = url;
		document.body.appendChild(a);
		a.click();
		a.remove();
		URL.revokeObjectURL(url);
		showToast(`Exported ${ids.length} image${ids.length === 1 ? '' : 's'} as ZIP.`);
	} catch (err) {
		showToast('Export error: ' + String(err), 'error');
	}
}

if (galleryGrid) {
	galleryGrid.addEventListener('scroll', () => {
		_scheduleVirtualGalleryWindowRender();
	});
	window.addEventListener('resize', () => {
		_scheduleVirtualGalleryWindowRender();
	});

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

		// In select mode, clicking a card toggles its selection
		if (gallerySelectMode) {
			if (target instanceof HTMLElement && target.classList.contains('gallery-star-btn')) return;
			const card = target instanceof HTMLElement ? target.closest('.gallery-card') : null;
			if (!(card instanceof HTMLElement)) return;
			const entryId = card.dataset.entryId || '';
			const index = parseInt(card.dataset.lightboxIndex || '0', 10);
			if (!entryId) return;
			toggleGalleryCardSelection(entryId, index, event.shiftKey);
			return;
		}

		if (target instanceof HTMLElement && target.classList.contains('gallery-star-btn')) {
			const entryId = target.dataset.entryId || '';
			if (!entryId) return;
			const isFav = toggleGalleryFavorite(entryId);
			target.classList.toggle('is-favorited', isFav);
			target.setAttribute('aria-pressed', String(isFav));
			target.setAttribute('aria-label', isFav ? 'Remove from favorites' : 'Add to favorites');
			target.textContent = isFav ? '\u2605' : '\u2606';
			if (galleryModeFilter === 'favorites') renderGallery(currentFullHistory);
			return;
		}
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

// IMG2IMG drop zone — accept gallery images dragged from gallery grid
if (img2imgDropZone && imageUpload) {
	img2imgDropZone.addEventListener('dragover', (event) => {
		event.preventDefault();
		if (event.dataTransfer) event.dataTransfer.dropEffect = 'copy';
		img2imgDropZone.classList.add('is-drag-over');
	});

	img2imgDropZone.addEventListener('dragleave', (event) => {
		if (!(event.relatedTarget instanceof Node) || !img2imgDropZone.contains(event.relatedTarget)) {
			img2imgDropZone.classList.remove('is-drag-over');
		}
	});

	img2imgDropZone.addEventListener('drop', async (event) => {
		event.preventDefault();
		img2imgDropZone.classList.remove('is-drag-over');
		const rawPayload = event.dataTransfer?.getData('text/plain') || '';
		const payload = parseGalleryPreviewPayload(rawPayload);
		const imgUrl = payload?.image || payload?.filename || '';
		if (!imgUrl) return;
		try {
			const res = await fetch(imgUrl);
			const blob = await res.blob();
			const ext = imgUrl.split('.').pop()?.split('?')[0] || 'png';
			const file = new File([blob], `gallery-drop.${ext}`, { type: blob.type || 'image/png' });
			const dt = new DataTransfer();
			dt.items.add(file);
			imageUpload.files = dt.files;
			if (img2imgDropHint) {
				img2imgDropHint.textContent = `Loaded: ${file.name}`;
				img2imgDropHint.hidden = false;
			}
			showToast('Gallery image loaded as img2img input.', 'pos');
		} catch {
			showToast('Could not load gallery image for img2img.', 'neg');
		}
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

	galleryLightbox.addEventListener('keydown', (event) => {
		if (event.key !== 'Tab' || galleryLightbox.hidden) return;
		const tabStops = getGalleryLightboxTabStops();
		if (!tabStops.length) return;
		const first = tabStops[0];
		const last = tabStops[tabStops.length - 1];
		const active = document.activeElement;
		if (event.shiftKey) {
			if (active === first || !galleryLightbox.contains(active)) {
				event.preventDefault();
				last.focus();
			}
			return;
		}
		if (active === last || !galleryLightbox.contains(active)) {
			event.preventDefault();
			first.focus();
		}
	});
}

if (galleryLightboxCloseBtn) {
	galleryLightboxCloseBtn.addEventListener('click', closeGalleryLightbox);
	galleryLightboxCloseBtn.addEventListener('keydown', onGalleryLightboxControlsKeydown);
}

function isGalleryLightboxInteractiveTarget(target) {
	if (!(target instanceof HTMLElement)) return false;
	return Boolean(target.closest(
		'#gallery-lightbox button, #gallery-lightbox input, #gallery-lightbox select, #gallery-lightbox textarea'
	));
}

function isGalleryLightboxControlVisible(control) {
	if (!(control instanceof HTMLElement)) return false;
	if (control.hidden || control.hasAttribute('hidden') || control.getAttribute('aria-hidden') === 'true') return false;
	if (control.closest('[hidden]')) return false;
	return true;
}

function getGalleryLightboxFocusableControls() {
	return [
		galleryLightboxPrev,
		galleryLightboxMetaToggle,
		galleryLightboxCompareToggle,
		galleryLightboxStarBtn,
		galleryLightboxAddTagBtn,
		galleryLightboxCloseBtn,
		galleryLightboxReuseBtn,
		galleryLightboxNext,
	].filter((control) => control && !control.disabled && isGalleryLightboxControlVisible(control));
}

function getGalleryLightboxTabStops() {
	if (!galleryLightbox) return [];
	const selector = [
		'button:not([disabled])',
		'input:not([disabled]):not([type="hidden"])',
		'select:not([disabled])',
		'textarea:not([disabled])',
		'[tabindex]:not([tabindex="-1"])',
	].join(', ');
	return [...galleryLightbox.querySelectorAll(selector)].filter((el) => {
		if (!(el instanceof HTMLElement)) return false;
		if (!isGalleryLightboxControlVisible(el)) return false;
		return true;
	});
}

function onGalleryLightboxControlsKeydown(event) {
	const key = event.key;
	if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
	const controls = getGalleryLightboxFocusableControls();
	if (controls.length < 2) return;
	const currentIndex = controls.indexOf(event.currentTarget);
	if (currentIndex < 0) return;
	event.preventDefault();
	let nextIndex = currentIndex;
	if (key === 'Home') {
		nextIndex = 0;
	} else if (key === 'End') {
		nextIndex = controls.length - 1;
	} else if (key === 'ArrowRight') {
		nextIndex = (currentIndex + 1) % controls.length;
	} else if (key === 'ArrowLeft') {
		nextIndex = (currentIndex - 1 + controls.length) % controls.length;
	}
	controls[nextIndex]?.focus();
}

document.addEventListener('keydown', (event) => {
	const key = event.key;
	if (key !== 'Escape' && key !== 'ArrowLeft' && key !== 'ArrowRight' && key !== 'c' && key !== 'C') return;

	if (key === 'Escape') {
		if (galleryContextMenu && !galleryContextMenu.hidden) {
			closeGalleryContextMenu();
			return;
		}
		if (mbModelModal && !mbModelModal.hidden) {
			setModelModalOpen(false);
			return;
		}
		if (!galleryLightbox || galleryLightbox.hidden) return;
		closeGalleryLightbox();
		return;
	}

	if (!galleryLightbox || galleryLightbox.hidden) return;
	if (key === 'c' || key === 'C') {
		const target = event.target;
		if (target instanceof HTMLElement && target.closest('#gallery-lightbox input, #gallery-lightbox select, #gallery-lightbox textarea')) return;
		if (!galleryLightboxCompareToggle || galleryLightboxCompareToggle.hidden || galleryLightboxCompareToggle.disabled) return;
		event.preventDefault();
		toggleGalleryLightboxCompare();
		return;
	}

	if (isGalleryLightboxInteractiveTarget(event.target)) return;
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
	if (gallerySearchQuery) gallerySearch.value = gallerySearchQuery;
	let searchDebounceTimer = null;
	gallerySearch.addEventListener('input', () => {
		clearTimeout(searchDebounceTimer);
		searchDebounceTimer = window.setTimeout(() => {
			gallerySearchQuery = gallerySearch.value || '';
			if (gallerySearchQuery) {
				localStorage.setItem(GALLERY_SEARCH_QUERY_KEY, gallerySearchQuery);
			} else {
				localStorage.removeItem(GALLERY_SEARCH_QUERY_KEY);
			}
			renderGallery(currentFullHistory);
		}, 220);
	});
	gallerySearch.addEventListener('keydown', (e) => {
		if (e.key !== 'Escape') return;
		e.stopPropagation();
		gallerySearch.value = '';
		gallerySearchQuery = '';
		localStorage.removeItem(GALLERY_SEARCH_QUERY_KEY);
		renderGallery(currentFullHistory);
	});
}

if (gallerySortSelect) {
	gallerySortSelect.value = gallerySortOrder;
	gallerySortSelect.addEventListener('change', () => {
		gallerySortOrder = gallerySortSelect.value || 'newest';
		if (!VALID_GALLERY_SORT_ORDERS.has(gallerySortOrder)) {
			gallerySortOrder = 'newest';
		}
		localStorage.setItem('gallerySortOrder', gallerySortOrder);
		renderGallery(currentFullHistory);
	});
}

if (galleryModeFilterSelect) {
	galleryModeFilterSelect.value = galleryModeFilter;
	galleryModeFilterSelect.addEventListener('change', () => {
		galleryModeFilter = galleryModeFilterSelect.value || 'all';
		localStorage.setItem('galleryModeFilter', galleryModeFilter);
		renderGallery(currentFullHistory);
	});
}

if (galleryTagFilterSelect) {
	galleryTagFilterSelect.value = galleryTagFilter;
	galleryTagFilterSelect.addEventListener('change', () => {
		galleryTagFilter = galleryTagFilterSelect.value || 'all';
		if (galleryTagFilter === 'all') {
			localStorage.removeItem(GALLERY_TAG_FILTER_KEY);
		} else {
			localStorage.setItem(GALLERY_TAG_FILTER_KEY, galleryTagFilter);
		}
		renderGallery(currentFullHistory);
	});
}

function onGalleryToolbarButtonKeydown(event) {
	const key = event.key;
	if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
	const buttons = [galleryViewToggle, refreshGalleryBtn].filter(Boolean);
	if (buttons.length < 2) return;
	const currentIndex = buttons.indexOf(event.currentTarget);
	if (currentIndex < 0) return;
	event.preventDefault();
	let nextIndex = currentIndex;
	if (key === 'Home') {
		nextIndex = 0;
	} else if (key === 'End') {
		nextIndex = buttons.length - 1;
	} else if (key === 'ArrowRight') {
		nextIndex = (currentIndex + 1) % buttons.length;
	} else if (key === 'ArrowLeft') {
		nextIndex = (currentIndex - 1 + buttons.length) % buttons.length;
	}
	const nextButton = buttons[nextIndex];
	if (nextButton) nextButton.focus();
}

if (galleryViewToggle) {
	galleryViewToggle.addEventListener('click', () => {
		galleryViewMode = galleryViewMode === 'grid' ? 'list' : 'grid';
		localStorage.setItem('galleryViewMode', galleryViewMode);
		galleryViewToggle.textContent = galleryViewMode === 'grid' ? 'List' : 'Grid';
		galleryViewToggle.setAttribute('aria-pressed', String(galleryViewMode === 'grid'));
		galleryGrid.classList.toggle('is-grid-mode', galleryViewMode === 'grid');
	});
	galleryViewToggle.addEventListener('keydown', onGalleryToolbarButtonKeydown);
	galleryViewToggle.textContent = galleryViewMode === 'grid' ? 'List' : 'Grid';
	galleryViewToggle.setAttribute('aria-pressed', String(galleryViewMode === 'grid'));
}

if (gallerySelectModeBtn) {
	gallerySelectModeBtn.addEventListener('click', () => {
		if (gallerySelectMode) { exitGallerySelectMode(); } else { enterGallerySelectMode(); }
	});
}

if (gallerySelectAllBtn) {
	gallerySelectAllBtn.addEventListener('click', () => {
		currentGalleryImages.forEach((e) => { if (e.id) gallerySelectedIds.add(e.id); });
		updateGallerySelectToolbar();
		renderGallery(currentFullHistory);
	});
}

if (galleryDeselectAllBtn) {
	galleryDeselectAllBtn.addEventListener('click', exitGallerySelectMode);
}

if (galleryBulkDeleteBtn) {
	galleryBulkDeleteBtn.addEventListener('click', bulkDeleteSelectedGalleryItems);
}

if (galleryBulkExportBtn) {
	galleryBulkExportBtn.addEventListener('click', bulkExportSelectedGalleryItems);
}

if (refreshGalleryBtn) {
	refreshGalleryBtn.addEventListener('keydown', onGalleryToolbarButtonKeydown);
}

if (galleryLightboxPrev) {
	galleryLightboxPrev.addEventListener('click', () => navigateLightbox(-1));
	galleryLightboxPrev.addEventListener('keydown', onGalleryLightboxControlsKeydown);
}

if (galleryLightboxNext) {
	galleryLightboxNext.addEventListener('click', () => navigateLightbox(1));
	galleryLightboxNext.addEventListener('keydown', onGalleryLightboxControlsKeydown);
}

if (galleryLightboxStarBtn) {
	galleryLightboxStarBtn.addEventListener('keydown', onGalleryLightboxControlsKeydown);
	galleryLightboxStarBtn.addEventListener('click', () => {
		const entry = currentGalleryImages[lightboxCurrentIndex];
		if (!entry?.id) return;
		toggleGalleryFavorite(entry.id);
		updateLightboxStarBtn(entry);
		const cardStarBtn = galleryGrid?.querySelector(`.gallery-card[data-entry-id="${CSS.escape(entry.id)}"] .gallery-star-btn`);
		if (cardStarBtn instanceof HTMLElement) {
			const isFav = isGalleryFavorite(entry.id);
			cardStarBtn.classList.toggle('is-favorited', isFav);
			cardStarBtn.setAttribute('aria-pressed', String(isFav));
			cardStarBtn.setAttribute('aria-label', isFav ? 'Remove from favorites' : 'Add to favorites');
			cardStarBtn.textContent = isFav ? '\u2605' : '\u2606';
		}
		if (galleryModeFilter === 'favorites') renderGallery(currentFullHistory);
	});
}

if (galleryLightboxAddTagBtn) {
	galleryLightboxAddTagBtn.addEventListener('click', () => {
		const entry = currentGalleryImages[lightboxCurrentIndex];
		if (!entry || !galleryLightboxTagInput) return;
		const nextTag = normalizeGalleryTag(galleryLightboxTagInput.value);
		if (!nextTag) return;
		const tags = getGalleryTags(entry);
		if (tags.includes(nextTag)) {
			showToast(`Tag #${nextTag} already exists.`, 'warn');
			galleryLightboxTagInput.select();
			return;
		}
		setGalleryTags(entry, [...tags, nextTag]);
		galleryLightboxTagInput.value = '';
		renderLightboxTags(entry);
		updateLightboxMeta(entry);
		syncGalleryTagFilterOptions(currentFullHistory.filter((item) => item.type === 'image'));
		renderGallery(currentFullHistory);
	});
	galleryLightboxAddTagBtn.addEventListener('keydown', onGalleryLightboxControlsKeydown);
}

if (galleryLightboxTagInput) {
	galleryLightboxTagInput.addEventListener('keydown', (event) => {
		if (event.key !== 'Enter') return;
		event.preventDefault();
		galleryLightboxAddTagBtn?.click();
	});
}

if (galleryLightboxTags) {
	galleryLightboxTags.addEventListener('click', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLElement)) return;
		const removeTag = target.getAttribute('data-gallery-tag-remove');
		if (!removeTag) return;
		const entry = currentGalleryImages[lightboxCurrentIndex];
		if (!entry) return;
		const tags = getGalleryTags(entry).filter((tag) => tag !== removeTag);
		setGalleryTags(entry, tags);
		renderLightboxTags(entry);
		updateLightboxMeta(entry);
		syncGalleryTagFilterOptions(currentFullHistory.filter((item) => item.type === 'image'));
		if (galleryTagFilter !== 'all' && galleryTagFilter === removeTag) {
			galleryTagFilter = 'all';
			localStorage.removeItem(GALLERY_TAG_FILTER_KEY);
			if (galleryTagFilterSelect) galleryTagFilterSelect.value = 'all';
		}
		renderGallery(currentFullHistory);
	});
}

async function attachSourceImageToLightboxEntry(file) {
	const entry = currentGalleryImages[lightboxCurrentIndex];
	if (!entry || entry?.params?.mode !== 'img2img') {
		showToast('Select an img2img history entry first.', 'neg');
		return;
	}
	if (!file) return;
	if (galleryLightboxCompareToggle) {
		galleryLightboxCompareToggle.disabled = true;
		galleryLightboxCompareToggle.textContent = 'Uploading...';
	}
	try {
		const formData = new FormData();
		formData.append('image', file);
		const uploadRes = await fetch('/api/image/upload-image', {
			method: 'POST',
			body: formData,
		});
		const uploadPayload = await uploadRes.json().catch(() => ({}));
		const uploadedName = String(uploadPayload?.name || '').trim();
		if (!uploadRes.ok || !uploadedName) {
			throw new Error(uploadPayload?.error || 'Failed to upload source image');
		}

		entry.params = entry.params || {};
		entry.params.image = uploadedName;
		const promptId = String(entry?.params?.prompt_id || '').trim();
		if (promptId) {
			img2imgSourceResolveCache.set(promptId, Promise.resolve(uploadedName));
		}

		const entryId = String(entry?.id || '').trim();
		if (entryId || promptId) {
			fetch('/api/history/img2img-source', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					entry_id: entryId,
					prompt_id: promptId,
					image: uploadedName,
				}),
			}).catch(() => {
				// non-fatal history backfill failure
			});
		}

		lightboxCompareEnabled = true;
		if (galleryLightboxCompareToggle) {
			galleryLightboxCompareToggle.setAttribute('aria-pressed', 'true');
		}
		updateLightboxMedia(entry, galleryLightboxImage?.src || '', 'Generated image', entry?.prompt || 'Untitled generation');
		showToast('Source image attached. Compare is now available.', 'pos');
	} catch (error) {
		showToast(error.message || 'Failed to attach source image.', 'neg');
		const activeEntry = currentGalleryImages[lightboxCurrentIndex];
		updateLightboxMedia(activeEntry, galleryLightboxImage?.src || '', 'Generated image', activeEntry?.prompt || 'Untitled generation');
	}
}

function toggleGalleryLightboxCompare() {
	if (!galleryLightboxCompareToggle) return;
	const mode = String(galleryLightboxCompareToggle.dataset.mode || '').trim();
	if (mode !== 'compare') return;
	lightboxCompareEnabled = !lightboxCompareEnabled;
	galleryLightboxCompareToggle.setAttribute('aria-pressed', String(lightboxCompareEnabled));
	const entry = currentGalleryImages[lightboxCurrentIndex];
	updateLightboxMedia(entry, galleryLightboxImage?.src || '', 'Generated image', entry?.prompt || 'Untitled generation');
}

if (galleryLightboxCompareToggle) {
	galleryLightboxCompareToggle.addEventListener('keydown', onGalleryLightboxControlsKeydown);
	galleryLightboxCompareToggle.addEventListener('click', () => {
		const mode = String(galleryLightboxCompareToggle.dataset.mode || '').trim();
		if (mode === 'attach') {
			if (!galleryLightboxSourceUploadInput) {
				showToast('Source upload input is unavailable.', 'neg');
				return;
			}
			galleryLightboxSourceUploadInput.value = '';
			galleryLightboxSourceUploadInput.click();
			return;
		}
		toggleGalleryLightboxCompare();
	});
}

if (galleryLightboxSourceUploadInput) {
	galleryLightboxSourceUploadInput.addEventListener('change', async () => {
		const file = galleryLightboxSourceUploadInput.files?.[0];
		if (!file) return;
		await attachSourceImageToLightboxEntry(file);
		galleryLightboxSourceUploadInput.value = '';
	});
}

if (galleryLightboxCompareSlider) {
	galleryLightboxCompareSlider.addEventListener('input', () => {
		applyLightboxCompareSplit(galleryLightboxCompareSlider.value);
	});
}

if (galleryLightboxMetaToggle) {
	galleryLightboxMetaToggle.addEventListener('keydown', onGalleryLightboxControlsKeydown);
	galleryLightboxMetaToggle.addEventListener('click', () => {
		lightboxMetaOpen = !lightboxMetaOpen;
		galleryLightboxMetaToggle.setAttribute('aria-pressed', String(lightboxMetaOpen));
		if (galleryLightboxMeta) {
			galleryLightboxMeta.hidden = !lightboxMetaOpen;
		}
		if (lightboxMetaOpen) {
			const entry = currentGalleryImages[lightboxCurrentIndex];
			updateLightboxMeta(entry);
		}
	});
}

if (galleryLightboxReuseBtn) {
	galleryLightboxReuseBtn.addEventListener('keydown', onGalleryLightboxControlsKeydown);
	galleryLightboxReuseBtn.addEventListener('click', () => {
		const entry = currentGalleryImages[lightboxCurrentIndex];
		if (!entry) return;
		const settings = {
			model: entry.model || '',
			sampler: entry.params?.sampler || '',
			negative_prompt: entry.negative_prompt || '',
			seed: entry.params?.seed !== undefined ? entry.params.seed : '',
			steps: Number(entry.params?.steps || 0),
			cfg: Number(entry.params?.cfg || 0),
			denoise: Number(entry.params?.denoise || 0),
			width: Number(entry.params?.width || 0),
			height: Number(entry.params?.height || 0),
			batch_size: Number(entry.params?.batch_size || 1),
			loras: Array.isArray(entry.params?.loras) ? entry.params.loras : [],
			vae: entry.params?.vae || '',
			refiner_model: entry.params?.refiner_model || '',
			hiresfix_enable: Boolean(entry.params?.hiresfix_enable),
			hiresfix_upscaler: entry.params?.hiresfix_upscaler || '',
			hiresfix_scale: Number(entry.params?.hiresfix_scale || 2),
			hiresfix_steps: Number(entry.params?.hiresfix_steps || 20),
			hiresfix_denoise: Number(entry.params?.hiresfix_denoise || 0.4),
			controlnet_model: entry.params?.controlnet_model || '',
			controlnet_weight: Number(entry.params?.controlnet_weight ?? 1),
			controlnet_start: Number(entry.params?.controlnet_start ?? 0),
			controlnet_end: Number(entry.params?.controlnet_end ?? 1),
		};
		if (typeof entry.prompt === 'string') {
			imagePrompt.value = entry.prompt;
		}
		applyImageSettings(settings);
		closeGalleryLightbox();
		showPanel('image');
		showToast('Settings loaded from gallery entry.', 'pos');
	});
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
let comfyWsCooldownNotified = false;
let comfyWsNextRetryAt = 0;
let comfyWsBlockedUntil = 0;
let comfyWsQuickCloseCount = 0;
let comfyWsLastConnectStartedAt = 0;
let wsTransportStatusTimer = null;
const COMFY_WS_MAX_RETRIES = 4;
const COMFY_WS_COOLDOWN_KEY = 'comfyWsCooldownUntil';
const COMFY_WS_COOLDOWN_MS = 30 * 60 * 1000;
const COMFY_WS_BLOCKED_COOLDOWN_MS = 5 * 60 * 1000;
const COMFY_WS_QUICK_CLOSE_MS = 1500;
const COMFY_WS_QUICK_CLOSE_THRESHOLD = 3;
const comfyWsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const comfyWsHost = window.location.hostname || 'localhost';
const COMFY_WS_URL = `${comfyWsProtocol}://${comfyWsHost}:8188/ws?clientId=${tabInstanceId}`;
const COMFY_HTTP_BASE = `${window.location.protocol === 'https:' ? 'https' : 'http'}://${comfyWsHost}:8188`;

function _getComfyWsCooldownUntil() {
	try {
		const raw = localStorage.getItem(COMFY_WS_COOLDOWN_KEY);
		const value = Number(raw || 0);
		return Number.isFinite(value) ? value : 0;
	} catch {
		return 0;
	}
}

function _setComfyWsCooldownUntil(untilEpochMs) {
	try {
		if (untilEpochMs > Date.now()) {
			localStorage.setItem(COMFY_WS_COOLDOWN_KEY, String(untilEpochMs));
		} else {
			localStorage.removeItem(COMFY_WS_COOLDOWN_KEY);
		}
	} catch {
		// Ignore localStorage failures; polling still covers preview updates.
	}
}

function _isComfyWsCooldownActive() {
	return _getComfyWsCooldownUntil() > Date.now();
}

function _getComfyWsCooldownMinutesLeft() {
	const until = _getComfyWsCooldownUntil();
	if (until <= Date.now()) return 0;
	return Math.max(1, Math.ceil((until - Date.now()) / 60000));
}

function _isComfyWsBlockedActive() {
	return comfyWsBlockedUntil > Date.now();
}

function _getComfyWsBlockedSecondsLeft() {
	if (comfyWsBlockedUntil <= Date.now()) return 0;
	return Math.max(1, Math.ceil((comfyWsBlockedUntil - Date.now()) / 1000));
}

function forceRetryComfyWebSocket(sourceLabel = 'manual') {
	if (isComfyWsOpen()) {
		setPreviewTransportMode('websocket', 'ComfyUI WebSocket already connected.');
		renderWsTransportStatus();
		return false;
	}
	if (comfyWsReconnectTimer) {
		window.clearTimeout(comfyWsReconnectTimer);
		comfyWsReconnectTimer = null;
	}
	comfyWsFailCount = 0;
	comfyWsNextRetryAt = 0;
	comfyWsBlockedUntil = 0;
	comfyWsQuickCloseCount = 0;
	comfyWsLastConnectStartedAt = 0;
	comfyWsCooldownNotified = false;
	_setComfyWsCooldownUntil(0);
	setPreviewTransportMode('polling', `Manual websocket retry requested via ${sourceLabel}. HTTP polling fallback is active until connected.`);
	connectComfyWebSocket();
	return true;
}

function setPreviewTransportMode(mode, titleText = '') {
	if (!previewTransportBadge) return;
	const nextMode = mode === 'websocket' || mode === 'offline' ? mode : 'polling';
	previewTransportBadge.dataset.transport = nextMode;
	if (nextMode === 'websocket') {
		previewTransportBadge.textContent = 'WebSocket';
		previewTransportBadge.title = titleText || 'Live preview is connected to ComfyUI WebSocket.';
		renderWsTransportStatus();
		return;
	}
	if (nextMode === 'offline') {
		previewTransportBadge.textContent = 'Preview offline';
		previewTransportBadge.title = titleText || 'ComfyUI is offline, so live preview updates are unavailable.';
		renderWsTransportStatus();
		return;
	}
	previewTransportBadge.textContent = 'Polling fallback';
	previewTransportBadge.title = titleText || 'Live preview is using HTTP polling fallback.';
	renderWsTransportStatus();
}

if (_isComfyWsCooldownActive()) {
	const minsLeft = _getComfyWsCooldownMinutesLeft();
	setPreviewTransportMode('polling', `ComfyUI WebSocket cooldown active (${minsLeft}m left). HTTP polling fallback is active.`);
} else {
	setPreviewTransportMode('polling');
}
startWsTransportStatusTicker();

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
	if (comfyWs && (comfyWs.readyState === WebSocket.OPEN || comfyWs.readyState === WebSocket.CONNECTING)) {
		if (comfyWs.readyState === WebSocket.OPEN) {
			setPreviewTransportMode('websocket');
		} else {
			setPreviewTransportMode('polling', 'Attempting ComfyUI WebSocket connection. HTTP polling fallback is active until connected.');
		}
		return;
	}
	if (_isComfyWsCooldownActive()) {
		const minsLeft = _getComfyWsCooldownMinutesLeft();
		setPreviewTransportMode('polling', `ComfyUI WebSocket cooldown active (${minsLeft}m left). HTTP polling fallback is active.`);
		return;
	}
	if (_isComfyWsBlockedActive()) {
		const secsLeft = _getComfyWsBlockedSecondsLeft();
		setPreviewTransportMode('polling', `ComfyUI WebSocket appears blocked (${secsLeft}s left). HTTP polling fallback is active.`);
		return;
	}
	if (comfyWsNextRetryAt > Date.now()) {
		const secsLeft = Math.max(1, Math.ceil((comfyWsNextRetryAt - Date.now()) / 1000));
		setPreviewTransportMode('polling', `ComfyUI WebSocket retry scheduled in ${secsLeft}s. HTTP polling fallback is active.`);
		return;
	}
	if (comfyWsFailCount >= COMFY_WS_MAX_RETRIES) {
		setPreviewTransportMode('polling', 'ComfyUI WebSocket unavailable after repeated failures. HTTP polling fallback is active.');
		return; // gave up; reset on tab focus
	}
	if (comfyWsReconnectTimer) {
		window.clearTimeout(comfyWsReconnectTimer);
		comfyWsReconnectTimer = null;
	}
	setPreviewTransportMode('polling', 'Attempting ComfyUI WebSocket connection. HTTP polling fallback is active until connected.');
	try {
		comfyWsLastConnectStartedAt = Date.now();
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

		comfyWs.onopen = () => {
			comfyWsFailCount = 0;
			comfyWsNextRetryAt = 0;
			comfyWsBlockedUntil = 0;
			comfyWsQuickCloseCount = 0;
			comfyWsLastConnectStartedAt = 0;
			_setComfyWsCooldownUntil(0);
			comfyWsCooldownNotified = false;
			setPreviewTransportMode('websocket');
		};
		comfyWs.onerror = () => { /* errors handled in onclose */ };
		comfyWs.onclose = (event) => {
			comfyWs = null;
			comfyWsFailCount++;
			const closedQuickly = comfyWsLastConnectStartedAt > 0 && (Date.now() - comfyWsLastConnectStartedAt) <= COMFY_WS_QUICK_CLOSE_MS;
			comfyWsLastConnectStartedAt = 0;
			if (closedQuickly) {
				comfyWsQuickCloseCount += 1;
			} else {
				comfyWsQuickCloseCount = 0;
			}
			const likelyBlocked = Boolean(event?.code === 1006 && comfyWsQuickCloseCount >= COMFY_WS_QUICK_CLOSE_THRESHOLD);
			if (likelyBlocked) {
				comfyWsBlockedUntil = Date.now() + COMFY_WS_BLOCKED_COOLDOWN_MS;
				comfyWsNextRetryAt = 0;
				setPreviewTransportMode('polling', 'ComfyUI WebSocket appears blocked (likely 403/forbidden). HTTP polling fallback is active.');
				appendDiagnosticsConsoleLine('ComfyUI websocket appears blocked (likely 403/forbidden); pausing websocket retries while polling fallback stays active.', 'warn');
				appendDiagnosticsConsoleLine(`Hint: start ComfyUI with --enable-cors-header * (or use Configurations > Start ComfyUI) so WS origin checks accept the app host. Current WS target: ${COMFY_WS_URL}`, 'warn');
				appendDiagnosticsConsoleLine(`ComfyUI HTTP API base: ${COMFY_HTTP_BASE}`, 'warn');
				return;
			}
			if (comfyWsFailCount >= COMFY_WS_MAX_RETRIES) {
				comfyWsNextRetryAt = 0;
				_setComfyWsCooldownUntil(Date.now() + COMFY_WS_COOLDOWN_MS);
				const minsLeft = _getComfyWsCooldownMinutesLeft();
				setPreviewTransportMode('polling', `ComfyUI WebSocket cooldown active (${minsLeft}m left). HTTP polling fallback is active.`);
				if (!comfyWsCooldownNotified) {
					comfyWsCooldownNotified = true;
					appendDiagnosticsConsoleLine('ComfyUI websocket preview unavailable; switched to HTTP polling fallback for live preview updates.', 'warn');
				}
				// ComfyUI WS unavailable (likely cross-origin 403); HTTP polling covers live preview
				return;
			}
			setPreviewTransportMode('polling', 'ComfyUI WebSocket disconnected. Retrying while HTTP polling fallback remains active.');
			// Reconnect with exponential backoff if page is still visible
			if (!document.hidden) {
				const delay = Math.min(5000 * Math.pow(2, comfyWsFailCount - 1), 60000);
				comfyWsNextRetryAt = Date.now() + delay;
				comfyWsReconnectTimer = window.setTimeout(() => {
					comfyWsNextRetryAt = 0;
					connectComfyWebSocket();
				}, delay);
			}
		};
	} catch {
		comfyWsNextRetryAt = Date.now() + 10000;
		setPreviewTransportMode('polling', 'Browser could not open ComfyUI WebSocket. HTTP polling fallback is active.');
		/* WebSocket unavailable — polling will cover this */
	}
}

document.addEventListener('visibilitychange', () => {
	renderWsTransportStatus();
	if (!document.hidden && !comfyWs) {
		if (_isComfyWsCooldownActive()) {
			const minsLeft = _getComfyWsCooldownMinutesLeft();
			setPreviewTransportMode('polling', `ComfyUI WebSocket cooldown active (${minsLeft}m left). HTTP polling fallback is active.`);
			return;
		}
		if (_isComfyWsBlockedActive()) {
			const secsLeft = _getComfyWsBlockedSecondsLeft();
			setPreviewTransportMode('polling', `ComfyUI WebSocket appears blocked (${secsLeft}s left). HTTP polling fallback is active.`);
			return;
		}
		// Reset failure count on tab re-focus so it can retry after a long pause
		comfyWsFailCount = 0;
		comfyWsNextRetryAt = 0;
		comfyWsQuickCloseCount = 0;
		connectComfyWebSocket();
	}
});

function startLivePreviewAutoRefresh() {
	if (!hasBackgroundPollingOwnership) return;
	if (livePreviewTimer) return;
	livePreviewTimer = window.setInterval(loadLivePreview, 4000);
}

async function loadGallery() {
	const seq = ++galleryLoadSeq;
	if (galleryLoadController) {
		galleryLoadController.abort();
	}
	galleryLoadController = new AbortController();
	try {
		const res = await fetch(`/api/history?type=image&limit=${GALLERY_HISTORY_LIMIT}`, {
			signal: galleryLoadController.signal,
		});
		const data = await res.json();
		if (seq !== galleryLoadSeq) return;
		const history = data.history || [];
		renderGallery(history);
		updateLivePreview(history[0]);
	} catch (err) {
		if (err?.name === 'AbortError') return;
		galleryGrid.innerHTML = '<div class="empty-gallery">Could not load gallery.</div>';
		previewUpdated.textContent = 'Preview unavailable';
	} finally {
		if (seq === galleryLoadSeq) {
			galleryLoadController = null;
		}
	}
}

refreshGalleryBtn.addEventListener('click', loadGallery);

async function pollQueue() {
	const ids = Array.from(trackedPromptIds);
	if (!ids.length) {
		if (imageGenerateBtn) {
			imageGenerateBtn.disabled = false;
			imageGenerateBtn.textContent = 'Generate Image';
		}
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
				const snapshot = pendingImageJobs.get(promptId) || {};
				const meta = queueJobMeta.get(promptId) || {};

				if (images.length) {
					const saved = await saveHistoryEntry({
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
							image: snapshot.image || snapshot.image_name || '',
							prompt_id: promptId,
						...(Number.isFinite(Number(meta.generationTimeMs)) ? { generation_time_ms: meta.generationTimeMs } : {}),
					},
						images,
					});
					if (!saved) {
						meta.status = 'processing';
						meta.updatedAt = Date.now();
						meta.failReason = HISTORY_PERSIST_PENDING_REASON;
						queueJobMeta.set(promptId, meta);
						continue;
					}
				}

				trackedPromptIds.delete(promptId);
				meta.status = 'completed';
				meta.updatedAt = Date.now();
				meta.failReason = '';
				meta.snapshot = snapshot;
				queueJobMeta.set(promptId, meta);
				pendingImageJobs.delete(promptId);
			}
			persistTrackedQueueState();
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
	queuePollTimer = window.setInterval(pollQueue, QUEUE_POLL_INTERVAL_MS);
}

function stopQueuePolling() {
	if (!queuePollTimer) return;
	window.clearInterval(queuePollTimer);
	queuePollTimer = null;
}

function inferCheckpointFamily(modelName) {
	const value = String(modelName || '').toLowerCase();
	if (!value) return '';
	if (value.includes('flux')) {
		return 'flux';
	}
	if (value.includes('sdxl') || value.includes('xl') || value.includes('pony') || value.includes('illustrious')) {
		return 'sdxl';
	}
	if (value.includes('sd15') || value.includes('1.5') || value.includes('v1-5') || value.includes('1_5')) {
		return 'sd15';
	}
	return '';
}

function getBaseCheckpointFamily() {
	return inferCheckpointFamily(imageModelSelect?.value || '');
}

function getImageModelDetails(modelName) {
	if (!modelName || !imageModelDetailsByName || !imageModelDetailsByName.size) return null;
	return imageModelDetailsByName.get(modelName) || null;
}

function inferImageModelFamily(modelName) {
	const details = getImageModelDetails(modelName);
	const detailsFamily = String(details?.family || '').toLowerCase();
	if (detailsFamily === 'flux') return 'flux';
	if (detailsFamily === 'sd15' || detailsFamily === 'sdxl') return 'sd';

	const inferred = inferCheckpointFamily(modelName);
	if (inferred === 'flux') return 'flux';
	if (inferred === 'sd15' || inferred === 'sdxl') return 'sd';
	return 'unknown';
}

function inferFluxVariant(modelName = '') {
	const details = getImageModelDetails(modelName || imageModelSelect?.value || '');
	const detailsVariant = String(details?.flux_variant || '').toLowerCase();
	if (detailsVariant === 'schnell' || detailsVariant === 'dev') return detailsVariant;

	const value = String(modelName || imageModelSelect?.value || '').toLowerCase();
	if (!value.includes('flux')) return '';
	if (value.includes('schnell') || value.includes('flux.1-s') || value.includes('flux1-s') || value.includes('flux_1_s')) {
		return 'schnell';
	}
	if (value.includes('dev') || value.includes('flux.1-d') || value.includes('flux1-d') || value.includes('flux_1_d')) {
		return 'dev';
	}
	return 'dev';
}

function getFluxWorkflowRecommendation(modelName = '') {
	const details = getImageModelDetails(modelName || imageModelSelect?.value || '');
	const sampler = String(details?.recommended_sampler || '').toLowerCase();
	const scheduler = String(details?.recommended_scheduler || '').toLowerCase();
	if (sampler && scheduler) {
		return {
			sampler,
			scheduler,
			source: 'metadata',
			sourceLabel: 'model metadata',
		};
	}
	const variant = inferFluxVariant(modelName || imageModelSelect?.value || '');
	return {
		sampler: 'euler',
		scheduler: variant === 'schnell' ? 'simple' : 'normal',
		source: 'heuristic',
		sourceLabel: variant === 'schnell' ? 'Schnell fallback heuristic' : 'Dev fallback heuristic',
	};
}

function updateFluxRecommendationInfoButton() {
	if (!imageRecommendationInfoBtn) return;
	const selectedModel = imageModelSelect?.value || '';
	const activeFamily = resolveActiveImageFamily(selectedModel);
	if (activeFamily !== 'flux') {
		imageRecommendationInfoBtn.hidden = true;
		imageRecommendationInfoBtn.title = 'Recommendation source details';
		imageRecommendationInfoBtn.setAttribute('aria-label', 'Recommendation source details');
		return;
	}
	const recommendation = getFluxWorkflowRecommendation(selectedModel);
	if (!recommendation?.sampler || !recommendation?.scheduler) {
		imageRecommendationInfoBtn.hidden = true;
		imageRecommendationInfoBtn.title = 'Recommendation source details';
		imageRecommendationInfoBtn.setAttribute('aria-label', 'Recommendation source details');
		return;
	}
	const sourceLabel = recommendation.sourceLabel || (recommendation.source === 'metadata' ? 'model metadata' : 'fallback heuristic');
	const detailText = `Recommended pair ${recommendation.sampler} + ${recommendation.scheduler} from ${sourceLabel}.`;
	imageRecommendationInfoBtn.title = detailText;
	imageRecommendationInfoBtn.setAttribute('aria-label', detailText);
	imageRecommendationInfoBtn.hidden = false;
}

function updateFluxRecommendationSourceTag() {
	if (!imageRecommendationSourceTag) return;
	const selectedModel = imageModelSelect?.value || '';
	const activeFamily = resolveActiveImageFamily(selectedModel);
	if (activeFamily !== 'flux') {
		imageRecommendationSourceTag.hidden = true;
		imageRecommendationSourceTag.textContent = '';
		return;
	}
	const recommendation = getFluxWorkflowRecommendation(selectedModel);
	if (!recommendation?.sampler || !recommendation?.scheduler) {
		imageRecommendationSourceTag.hidden = true;
		imageRecommendationSourceTag.textContent = '';
		return;
	}
	const sourceLabel = recommendation.sourceLabel || (recommendation.source === 'metadata' ? 'model metadata' : 'fallback heuristic');
	imageRecommendationSourceTag.textContent = `Source: ${sourceLabel}`;
	imageRecommendationSourceTag.hidden = false;
}

function applyCurrentFluxRecommendation(options = {}) {
	const announce = options.announce !== false;
	const suppressNoopStatus = options.suppressNoopStatus === true;
	const selectedModel = imageModelSelect?.value || '';
	const activeFamily = resolveActiveImageFamily(selectedModel);
	if (activeFamily !== 'flux') {
		if (imageRecommendationStatus) {
			imageRecommendationStatus.textContent = 'Switch to FLUX mode to apply recommendations.';
			imageRecommendationStatus.hidden = false;
		}
		if (announce) showToast('Flux recommendations apply only in FLUX mode.', '');
		return false;
	}

	const recommendation = getFluxWorkflowRecommendation(selectedModel);
	if (!recommendation?.sampler || !recommendation?.scheduler) {
		if (imageRecommendationStatus) {
			imageRecommendationStatus.textContent = 'No recommendation available for this model.';
			imageRecommendationStatus.hidden = false;
		}
		if (announce) showToast('No Flux recommendation is available for this model.', '');
		return false;
	}

	const prevSampler = imageSamplerSelect?.value || '';
	const prevScheduler = imageSchedulerSelect?.value || '';
	setSelectValueIfOptionExists(imageSamplerSelect, recommendation.sampler);
	setSelectValueIfOptionExists(imageSchedulerSelect, recommendation.scheduler);
	const changed = prevSampler !== (imageSamplerSelect?.value || '') || prevScheduler !== (imageSchedulerSelect?.value || '');

	if (imageRecommendationStatus) {
		if (changed || !suppressNoopStatus) {
			imageRecommendationStatus.textContent = changed
				? `Applied recommendation: ${recommendation.sampler} + ${recommendation.scheduler}`
				: `Recommendation already applied: ${recommendation.sampler} + ${recommendation.scheduler}`;
			imageRecommendationStatus.hidden = false;
		}
	}
	if (announce) {
		showToast(
			changed
				? `Applied Flux recommendation (${recommendation.sampler} + ${recommendation.scheduler}).`
				: `Flux recommendation already active (${recommendation.sampler} + ${recommendation.scheduler}).`,
			changed ? 'pos' : ''
		);
	}
	updateFluxRecommendationDriftHint();
	return changed;
}

function updateFluxRecommendationDriftHint() {
	if (!imageRecommendationDriftHint) return;
	const selectedModel = imageModelSelect?.value || '';
	const activeFamily = resolveActiveImageFamily(selectedModel);
	if (activeFamily !== 'flux') {
		imageRecommendationDriftHint.hidden = true;
		imageRecommendationDriftHint.classList.remove('is-warning');
		updateFluxRecommendationSourceTag();
		return;
	}
	const recommendation = getFluxWorkflowRecommendation(selectedModel);
	if (!recommendation?.sampler || !recommendation?.scheduler) {
		imageRecommendationDriftHint.hidden = true;
		imageRecommendationDriftHint.classList.remove('is-warning');
		updateFluxRecommendationSourceTag();
		return;
	}
	const currentSampler = String(imageSamplerSelect?.value || '').toLowerCase();
	const currentScheduler = String(imageSchedulerSelect?.value || '').toLowerCase();
	const recSampler = recommendation.sampler;
	const recScheduler = recommendation.scheduler;
	const matches = currentSampler === recSampler && currentScheduler === recScheduler;
	if (matches) {
		imageRecommendationDriftHint.textContent = `Using recommended pair: ${recSampler} + ${recScheduler}.`;
		imageRecommendationDriftHint.classList.remove('is-warning');
	} else {
		imageRecommendationDriftHint.textContent = `Custom pair active: ${currentSampler || '(none)'} + ${currentScheduler || '(none)'}. Recommended: ${recSampler} + ${recScheduler}.`;
		imageRecommendationDriftHint.classList.add('is-warning');
	}
	imageRecommendationDriftHint.hidden = false;
	updateFluxRecommendationSourceTag();
}

function resolveActiveImageFamily(modelName = '') {
	const requestedMode = imageModelFamilySelect?.value || imageModelFamilyMode || 'auto';
	if (requestedMode === 'flux') return 'flux';
	if (requestedMode === 'sd') return 'sd';
	const inferred = inferImageModelFamily(modelName || imageModelSelect?.value || '');
	return inferred === 'flux' ? 'flux' : 'sd';
}

function getImageFamilyCapabilities(activeFamily = resolveActiveImageFamily(imageModelSelect?.value || '')) {
	const baseCaps = IMAGE_FAMILY_CAPABILITIES[activeFamily] || IMAGE_FAMILY_CAPABILITIES.sd;
	const details = getImageModelDetails(imageModelSelect?.value || '');
	if (!details || typeof details !== 'object') return { ...baseCaps };

	const cfgMin = Number(details.cfg_min);
	const cfgMax = Number(details.cfg_max);
	const cfgDefault = Number(details.cfg_default);
	return {
		...baseCaps,
		supports_refiner: typeof details.supports_refiner === 'boolean' ? details.supports_refiner : baseCaps.supports_refiner,
		supports_vae: typeof details.supports_vae === 'boolean' ? details.supports_vae : baseCaps.supports_vae,
		supports_controlnet: typeof details.supports_controlnet === 'boolean' ? details.supports_controlnet : baseCaps.supports_controlnet,
		supports_hiresfix: typeof details.supports_hiresfix === 'boolean' ? details.supports_hiresfix : baseCaps.supports_hiresfix,
		cfg_min: Number.isFinite(cfgMin) ? cfgMin : baseCaps.cfg_min,
		cfg_max: Number.isFinite(cfgMax) ? cfgMax : baseCaps.cfg_max,
		cfg_default: Number.isFinite(cfgDefault) ? cfgDefault : baseCaps.cfg_default,
	};
}

function applyImageFamilyModeUi() {
	if (imageModelFamilySelect && imageModelFamilySelect.value !== imageModelFamilyMode) {
		imageModelFamilySelect.value = imageModelFamilyMode;
	}
	if (imageModelSelect) {
		renderFilteredImageModels(imageModelFilter ? imageModelFilter.value : '', imageModelSelect.value || '');
	}
	const selectedModel = imageModelSelect?.value || '';
	const activeFamily = resolveActiveImageFamily(selectedModel);
	const capabilities = getImageFamilyCapabilities(activeFamily);

	if (imageVaeField) imageVaeField.hidden = !capabilities.supports_vae;
	if (imageRefinerField) imageRefinerField.hidden = !capabilities.supports_refiner;
	if (controlnetPanel) controlnetPanel.hidden = !capabilities.supports_controlnet;
	if (hiresfixPanel) hiresfixPanel.hidden = !capabilities.supports_hiresfix;
	if (imageCfgRow) imageCfgRow.hidden = false;

	const isFluxActive = activeFamily === 'flux';
	if (imageCfgLabelText) imageCfgLabelText.textContent = isFluxActive ? 'Guidance' : 'CFG';
	if (imageCfgFluxHint) imageCfgFluxHint.hidden = !isFluxActive;
	if (fluxPromptTips) fluxPromptTips.hidden = !isFluxActive;
	if (imageNegativePromptSection) imageNegativePromptSection.hidden = isFluxActive;
	if (fluxNoNegHint) fluxNoNegHint.hidden = !isFluxActive;
	if (fluxSamplerHint) {
		if (!isFluxActive) {
			fluxSamplerHint.hidden = true;
		} else {
			const variant = inferFluxVariant(selectedModel);
			const recommendation = getFluxWorkflowRecommendation(selectedModel);
			const sampler = recommendation.sampler || 'euler';
			const scheduler = recommendation.scheduler || (variant === 'schnell' ? 'simple' : 'normal');
			if (variant === 'schnell') {
				fluxSamplerHint.textContent = `FLUX Schnell tip: use ${sampler} + ${scheduler} scheduler with lower step counts for fast output.`;
			} else {
				fluxSamplerHint.textContent = `FLUX Dev tip: use ${sampler} + ${scheduler} scheduler for stable quality and detail.`;
			}
			fluxSamplerHint.hidden = false;
		}
	}
	if (imageApplyRecommendationBtn) {
		imageApplyRecommendationBtn.hidden = !isFluxActive;
		imageApplyRecommendationBtn.disabled = !isFluxActive;
	}
	updateFluxRecommendationInfoButton();
	if (imageAutoApplyRecommendationLabel) {
		imageAutoApplyRecommendationLabel.hidden = !isFluxActive;
	}
	if (imageAutoApplyRecommendationToggle) {
		imageAutoApplyRecommendationToggle.checked = imageFluxAutoApplyRecommendation;
	}
	if (imageLockRecommendationLabel) {
		imageLockRecommendationLabel.hidden = !isFluxActive;
	}
	if (imageLockRecommendationToggle) {
		imageLockRecommendationToggle.checked = imageFluxLockRecommendation;
	}
	if (imageUnlockRecommendationOnceBtn) {
		const canUseTemporaryUnlock = isFluxActive && imageFluxLockRecommendation;
		imageUnlockRecommendationOnceBtn.hidden = !canUseTemporaryUnlock;
		imageUnlockRecommendationOnceBtn.textContent = imageFluxLockBypassOnce ? 'Unlocked for next run' : 'Unlock for next run';
		imageUnlockRecommendationOnceBtn.setAttribute('aria-pressed', imageFluxLockBypassOnce ? 'true' : 'false');
	}
	if (imageUnlockExpiryHint) {
		const canUseTemporaryUnlock = isFluxActive && imageFluxLockRecommendation;
		imageUnlockExpiryHint.hidden = !canUseTemporaryUnlock;
		imageUnlockExpiryHint.classList.toggle('is-active', imageFluxLockBypassOnce && canUseTemporaryUnlock);
	}
	if (imageSamplerSelect) {
		imageSamplerSelect.disabled = isFluxActive && imageFluxLockRecommendation && !imageFluxLockBypassOnce;
		imageSamplerSelect.title = imageSamplerSelect.disabled ? 'Locked to recommended Flux sampler.' : '';
	}
	if (imageSchedulerSelect) {
		imageSchedulerSelect.disabled = isFluxActive && imageFluxLockRecommendation && !imageFluxLockBypassOnce;
		imageSchedulerSelect.title = imageSchedulerSelect.disabled ? 'Locked to recommended Flux scheduler.' : '';
	}
	if (imageRecommendationStatus && !isFluxActive) {
		imageRecommendationStatus.hidden = true;
	}
	if (imageRecommendationDriftHint && !isFluxActive) {
		imageRecommendationDriftHint.hidden = true;
		imageRecommendationDriftHint.classList.remove('is-warning');
	}
	if (imageRecommendationSourceTag && !isFluxActive) {
		imageRecommendationSourceTag.hidden = true;
		imageRecommendationSourceTag.textContent = '';
	}
	if (isFluxActive && imageFluxAutoApplyRecommendation) {
		const autoKey = `${selectedModel || ''}|${imageModelFamilyMode}`;
		if (autoKey && autoKey !== lastAutoRecommendationModelKey) {
			applyCurrentFluxRecommendation({ announce: false, suppressNoopStatus: true });
			lastAutoRecommendationModelKey = autoKey;
		}
	} else {
		lastAutoRecommendationModelKey = '';
	}
	if (isFluxActive && imageFluxLockRecommendation && !imageFluxLockBypassOnce) {
		applyCurrentFluxRecommendation({ announce: false, suppressNoopStatus: true });
	}
	updateFluxRecommendationDriftHint();
	if (fluxVariantChip) {
		if (!isFluxActive) {
			fluxVariantChip.hidden = true;
			fluxVariantChip.classList.remove('is-dev', 'is-schnell', 'is-auto');
		} else {
			const variant = inferFluxVariant(selectedModel);
			const variantLabel = variant === 'schnell' ? 'Schnell' : (variant === 'dev' ? 'Dev' : 'Auto');
			fluxVariantChip.classList.remove('is-dev', 'is-schnell', 'is-auto');
			if (variant === 'schnell') {
				fluxVariantChip.classList.add('is-schnell');
			} else if (variant === 'dev') {
				fluxVariantChip.classList.add('is-dev');
			} else {
				fluxVariantChip.classList.add('is-auto');
			}
			fluxVariantChip.textContent = `Flux Variant: ${variantLabel}`;
			fluxVariantChip.hidden = false;
		}
	}

	if (!capabilities.supports_vae && vaeModelSelect) {
		vaeModelSelect.value = '';
	}
	if (!capabilities.supports_refiner && refinerModelSelect) {
		refinerModelSelect.value = '';
	}
	if (!capabilities.supports_controlnet) {
		if (controlnetModelSelect) controlnetModelSelect.value = '';
		if (controlnetImageUpload) controlnetImageUpload.value = '';
		updateControlnetImagePreview();
	}
	if (!capabilities.supports_hiresfix && hiresfixEnable) {
		hiresfixEnable.checked = false;
	}
	if (imageCfg) {
		imageCfg.min = String(capabilities.cfg_min);
		imageCfg.max = String(capabilities.cfg_max);
		const cfgValue = Number(imageCfg.value);
		if (!Number.isFinite(cfgValue) || cfgValue < capabilities.cfg_min || cfgValue > capabilities.cfg_max) {
			imageCfg.value = String(capabilities.cfg_default);
		}
	}

	if (imageModelFamilyHint) {
		if (activeFamily === 'flux') {
			imageModelFamilyHint.textContent = 'Family mode: FLUX. Refiner, VAE, ControlNet, and HiresFix are disabled for this workflow.';
		} else {
			imageModelFamilyHint.textContent = 'Family mode: SD / SDXL. Full model-stack controls are available.';
		}
	}
	if (activeImagePreset && activeFamily !== lastResolvedPresetFamily) {
		applyImagePreset(activeImagePreset);
	}

	syncImageControlLabels();
	updateModelStackBadges();
	updateModelStackCompatibilityHint();
	updateControlnetCompatibilityHint();
}

function normalizeImageRequestByFamily(common) {
	const activeFamily = resolveActiveImageFamily(common.model || '');
	const capabilities = getImageFamilyCapabilities(activeFamily);
	const normalized = { ...common, model_family: activeFamily };

	if (!capabilities.supports_refiner) normalized.refiner_model = '';
	if (!capabilities.supports_vae) normalized.vae = '';
	if (!capabilities.supports_controlnet) {
		normalized.controlnet_model = '';
		normalized.controlnet_image_name = '';
		normalized.controlnet_weight = 1;
		normalized.controlnet_start = 0;
		normalized.controlnet_end = 1;
	}
	if (!capabilities.supports_hiresfix) {
		normalized.hiresfix_enable = false;
		normalized.hiresfix_upscaler = '';
	}

	const cfgValue = Number(normalized.cfg);
	if (Number.isFinite(cfgValue)) {
		normalized.cfg = Math.max(capabilities.cfg_min, Math.min(capabilities.cfg_max, cfgValue));
	} else {
		normalized.cfg = capabilities.cfg_default;
	}

	return normalized;
}

/**
 * Build <option> elements, optionally grouped by compatibility with baseFamily.
 * When baseFamily is known, compatible models appear first, then unknown family,
 * then incompatible. When baseFamily is unknown, returns a flat list.
 */
function buildCompatGroupedOptions(models, baseFamily, inferFn) {
	if (!models.length) return '';
	const toOption = (name) => `<option value="${escHtml(name)}">${escHtml(name)}</option>`;
	if (!baseFamily) {
		return models.map(toOption).join('');
	}
	const compatible = [];
	const unknown = [];
	const incompatible = [];
	for (const name of models) {
		const fam = inferFn(name);
		if (!fam) unknown.push(name);
		else if (fam === baseFamily) compatible.push(name);
		else incompatible.push(name);
	}
	const parts = [];
	if (compatible.length) {
		parts.push(`<optgroup label="Compatible (${baseFamily.toUpperCase()})">${compatible.map(toOption).join('')}</optgroup>`);
	}
	if (unknown.length) {
		parts.push(`<optgroup label="Unknown family">${unknown.map(toOption).join('')}</optgroup>`);
	}
	if (incompatible.length) {
		parts.push(`<optgroup label="Possibly incompatible">${incompatible.map(toOption).join('')}</optgroup>`);
	}
	return parts.join('');
}

function refreshCompatibilityGroupings() {
	const baseFamily = getBaseCheckpointFamily();
	if (refinerModelSelect) {
		const cur = refinerModelSelect.value;
		const models = [...refinerModelSelect.options]
			.filter((o) => o.value && !o.closest('optgroup[label="Possibly incompatible"]') !== undefined)
			.map((o) => o.value)
			.filter(Boolean);
		// collect all non-empty option values across any current optgroups
		const allModels = [...refinerModelSelect.querySelectorAll('option')]
			.map((o) => o.value).filter(Boolean);
		if (allModels.length) {
			refinerModelSelect.innerHTML = '<option value="">None</option>' +
				buildCompatGroupedOptions(allModels, baseFamily, inferCheckpointFamily);
			if (cur && [...refinerModelSelect.options].some((o) => o.value === cur)) {
				refinerModelSelect.value = cur;
			}
		}
	}
	if (vaeModelSelect) {
		const cur = vaeModelSelect.value;
		const allModels = [...vaeModelSelect.querySelectorAll('option')]
			.map((o) => o.value).filter(Boolean);
		if (allModels.length) {
			vaeModelSelect.innerHTML = '<option value="">Default</option>' +
				buildCompatGroupedOptions(allModels, baseFamily, inferCheckpointFamily);
			if (cur && [...vaeModelSelect.options].some((o) => o.value === cur)) {
				vaeModelSelect.value = cur;
			}
		}
	}
	if (controlnetModelSelect) {
		const cur = controlnetModelSelect.value;
		const allModels = [...controlnetModelSelect.querySelectorAll('option')]
			.map((o) => o.value).filter(Boolean);
		if (allModels.length) {
			controlnetModelSelect.innerHTML = '<option value="">None</option>' +
				buildCompatGroupedOptions(allModels, baseFamily, inferControlnetFamily);
			if (cur && [...controlnetModelSelect.options].some((o) => o.value === cur)) {
				controlnetModelSelect.value = cur;
			}
		}
	}
	if (loraStackContainer) {
		loraStackContainer.querySelectorAll('.lora-row-select').forEach((sel) => {
			const cur = sel.value;
			const allModels = [...sel.querySelectorAll('option')]
				.map((o) => o.value).filter(Boolean);
			if (allModels.length) {
				sel.innerHTML = '<option value="">None</option>' +
					buildCompatGroupedOptions(allModels, baseFamily, inferCheckpointFamily);
				if (cur && [...sel.options].some((o) => o.value === cur)) sel.value = cur;
			}
		});
	}
	updateModelStackCompatibilityHint();
	updateControlnetCompatibilityHint();
}

function getModelStackCompatibilityMessage(baseModel, refinerModel, vaeModel) {
	if (!baseModel) {
		return 'Tip: select a Base checkpoint to validate Refiner/VAE family alignment.';
	}
	const baseFamily = inferCheckpointFamily(baseModel);
	if (baseFamily === 'flux') {
		return 'FLUX family active. Refiner/VAE stack is typically not used in this workflow.';
	}
	const issues = [];
	if (refinerModel) {
		const refinerFamily = inferCheckpointFamily(refinerModel);
		if (baseFamily && refinerFamily && baseFamily !== refinerFamily) {
			issues.push(`Refiner looks ${refinerFamily.toUpperCase()} while Base looks ${baseFamily.toUpperCase()}.`);
		}
	}
	if (vaeModel) {
		const vaeFamily = inferCheckpointFamily(vaeModel);
		if (baseFamily && vaeFamily && baseFamily !== vaeFamily) {
			issues.push(`VAE looks ${vaeFamily.toUpperCase()} while Base looks ${baseFamily.toUpperCase()}.`);
		}
	}
	if (issues.length) {
		return `${issues.join(' ')} Mixing families can reduce quality or fail workflow stages.`;
	}
	return 'Tip: keep Base, Refiner, and VAE in the same family (SD1.5 vs SDXL) when possible.';
}

function updateModelStackCompatibilityHint() {
	if (!modelStackCompatHint) return;
	const message = getModelStackCompatibilityMessage(
		imageModelSelect ? imageModelSelect.value : '',
		refinerModelSelect ? refinerModelSelect.value : '',
		vaeModelSelect ? vaeModelSelect.value : '',
	);
	const isWarning = /mixing families can reduce quality or fail workflow stages/i.test(message);
	modelStackCompatHint.setAttribute('title', message);
	modelStackCompatHint.setAttribute('aria-label', `Model stack compatibility: ${message}`);
	modelStackCompatHint.classList.toggle('is-warning', isWarning);
}

function inferControlnetFamily(controlnetName) {
	const value = String(controlnetName || '').toLowerCase();
	if (!value) return '';
	if (value.includes('xl') || value.includes('sdxl')) return 'sdxl';
	if (value.includes('sd15') || value.includes('1.5') || value.includes('v1-5') || value.includes('1_5')) return 'sd15';
	return '';
}

function getControlnetCompatibilityMessage(modelName, controlnetName) {
	if (!controlnetName) return '';
	const checkpointFamily = inferCheckpointFamily(modelName);
	const controlnetFamily = inferControlnetFamily(controlnetName);
	if (!checkpointFamily || !controlnetFamily || checkpointFamily === controlnetFamily) {
		return '';
	}
	const checkpointLabel = checkpointFamily.toUpperCase();
	const controlnetLabel = controlnetFamily.toUpperCase();
	return `Selected checkpoint appears to be ${checkpointLabel}, but ControlNet model looks ${controlnetLabel}. Choose matching families to avoid queue stalls/failures.`;
}

function updateControlnetCompatibilityHint() {
	if (!controlnetModelSelect) return;
	const warning = getControlnetCompatibilityMessage(imageModelSelect?.value || '', controlnetModelSelect.value || '');
	const titleText = warning || 'Pick a ControlNet model that matches your checkpoint family (SD1.5 vs SDXL) for best reliability.';
	controlnetModelSelect.title = titleText;
	if (warning && queueSummary && !trackedPromptIds.size) {
		queueSummary.textContent = `Warning: ${warning}`;
	}
}

function validateImageInputs(common) {
	if (!common.model) {
		return 'Select a checkpoint model before generating.';
	}
	const capabilities = getImageFamilyCapabilities(common.model_family || resolveActiveImageFamily(common.model));
	if (capabilities.supports_controlnet) {
		const compatibilityWarning = getControlnetCompatibilityMessage(common.model, common.controlnet_model);
		if (compatibilityWarning) {
			return compatibilityWarning;
		}
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
	if (common.cfg < capabilities.cfg_min || common.cfg > capabilities.cfg_max) {
		return `CFG must be between ${capabilities.cfg_min} and ${capabilities.cfg_max}.`;
	}
	if (common.denoise < 0.05 || common.denoise > 1) {
		return 'Denoise must be between 0.05 and 1.0.';
	}
	if (common.lora_strength != null && (common.lora_strength < 0 || common.lora_strength > 2)) {
		return 'LoRA strength must be between 0 and 2.';
	}
	if (common.controlnet_weight != null && (common.controlnet_weight < 0 || common.controlnet_weight > 2)) {
		return 'ControlNet weight must be between 0 and 2.';
	}
	if (common.controlnet_start != null && (common.controlnet_start < 0 || common.controlnet_start > 1)) {
		return 'ControlNet start must be between 0 and 1.';
	}
	if (common.controlnet_end != null && (common.controlnet_end < 0 || common.controlnet_end > 1)) {
		return 'ControlNet end must be between 0 and 1.';
	}
	if (common.controlnet_start != null && common.controlnet_end != null && common.controlnet_start > common.controlnet_end) {
		return 'ControlNet start cannot be greater than end.';
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
			: '';
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
					<span class="tag-editor-actions" role="group" aria-label="Tag ${index + 1} actions">
						<button class="btn btn-ghost btn-xs" type="button" data-tag-save="${index}">Save</button>
						<button class="btn btn-ghost btn-xs" type="button" data-tag-delete="${index}">Delete</button>
					</span>
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
			target.setAttribute('aria-hidden', target.hidden ? 'true' : 'false');
			btn.textContent = target.hidden ? 'Show' : 'Hide';
			btn.setAttribute('aria-expanded', target.hidden ? 'false' : 'true');
		});
		btn.setAttribute('aria-controls', targetId);
		btn.setAttribute('aria-expanded', target.hidden ? 'false' : 'true');
		target.setAttribute('aria-hidden', target.hidden ? 'true' : 'false');
	});
}

// ─── Model Browser ────────────────────────────────────────────────────────────

let mbCurrentPage = 1;
let mbTotalPages  = 1;
let mbHasNextPage = false;
let mbQueryMode = false;
let mbCursorByPage = { 1: '' };
let mbPollTimer   = null;
let mbDownloadsMinimized = false;
let mbLocalInstalledNames = new Set();
let mbLastSearchItems = [];
let mbLibraryAllModels = [];
let mbLibraryRoot = '';
var mbActiveView = localStorage.getItem('mbActiveView') === 'library' ? 'library' : 'search';
let mbCurrentModelDetails = null;
let mbCurrentVersionIndex = 0;
let mbResetStatusTimer = null;
let mbModelModalLastFocus = null;
let mbReportTargetTimer = null;
let mbSearchAbortController = null;
let mbSearchRequestSeq = 0;
let mbSearchInFlight = false;
let mbSearchCancelRequested = false;
let mbSearchStatusTimer = null;
const MB_SEARCH_TIMEOUT_MS = 25000;
const MB_CANCEL_STATUS_CLEAR_MS = 2500;

function updateModelSearchControls() {
	if (mbSearchBtn) mbSearchBtn.disabled = mbSearchInFlight;
	if (mbCancelSearchBtn) mbCancelSearchBtn.disabled = !mbSearchInFlight;
}

function cancelModelSearch() {
	if (!mbSearchInFlight || !mbSearchAbortController) return;
	mbSearchCancelRequested = true;
	mbSearchAbortController.abort();
}

function onModelSearchControlKeydown(event) {
	if (event.key !== 'Escape') return;
	if (!mbSearchInFlight) return;
	event.preventDefault();
	cancelModelSearch();
}

if (mbLocalQuery) {
	mbLocalQuery.value = localStorage.getItem('mbLocalQuery') || '';
}
if (mbLocalType) {
	const savedType = localStorage.getItem('mbLocalType') || '';
	mbLocalType.value = Array.from(mbLocalType.options).some((opt) => opt.value === savedType) ? savedType : '';
}
if (mbLocalBaseModel) {
	const savedBaseModel = localStorage.getItem('mbLocalBaseModel') || '';
	mbLocalBaseModel.value = Array.from(mbLocalBaseModel.options).some((opt) => opt.value === savedBaseModel) ? savedBaseModel : '';
}
if (mbLocalSort) {
	const savedSort = localStorage.getItem('mbLocalSort') || 'name-asc';
	mbLocalSort.value = Array.from(mbLocalSort.options).some((opt) => opt.value === savedSort) ? savedSort : 'name-asc';
}
if (mbLocalHideEmbeddings) {
	mbLocalHideEmbeddings.setAttribute('aria-pressed', localStorage.getItem('mbLocalHideEmbeddings') === '1' ? 'true' : 'false');
}
if (mbLocalMatchedOnly) {
	mbLocalMatchedOnly.setAttribute('aria-pressed', localStorage.getItem('mbLocalMatchedOnly') === '1' ? 'true' : 'false');
}
if (mbCompareProviderCivitai) {
	mbCompareProviderCivitai.checked = localStorage.getItem('mbCompareProviderCivitai') !== '0';
}
if (mbCompareProviderHuggingface) {
	mbCompareProviderHuggingface.checked = localStorage.getItem('mbCompareProviderHuggingface') !== '0';
}
if (mbProvider) {
	const savedProvider = localStorage.getItem('mbProvider') || 'civitai';
	mbProvider.value = Array.from(mbProvider.options).some((opt) => opt.value === savedProvider) ? savedProvider : 'civitai';
}
if (mbSearchQuery) {
	mbSearchQuery.value = localStorage.getItem('mbSearchQuery') || '';
}
if (mbSearchType) {
	const savedType = localStorage.getItem('mbSearchType') || '';
	mbSearchType.value = Array.from(mbSearchType.options).some((opt) => opt.value === savedType) ? savedType : '';
}
if (mbBaseModel) {
	const savedBaseModel = localStorage.getItem('mbBaseModel') || '';
	mbBaseModel.value = Array.from(mbBaseModel.options).some((opt) => opt.value === savedBaseModel) ? savedBaseModel : '';
}
if (mbSort) {
	const savedSort = localStorage.getItem('mbSort') || 'highest-rated';
	mbSort.value = Array.from(mbSort.options).some((opt) => opt.value === savedSort) ? savedSort : 'highest-rated';
}
if (mbPageSize) {
	const savedPageSize = localStorage.getItem('mbPageSize') || '20';
	mbPageSize.value = Array.from(mbPageSize.options).some((opt) => opt.value === savedPageSize) ? savedPageSize : '20';
}
if (mbHideInstalledToggle) {
	mbHideInstalledToggle.setAttribute('aria-pressed', localStorage.getItem('mbHideInstalled') === '1' ? 'true' : 'false');
}
if (mbShowInstalledOnlyToggle) {
	mbShowInstalledOnlyToggle.setAttribute('aria-pressed', localStorage.getItem('mbShowInstalledOnly') === '1' ? 'true' : 'false');
}
if (mbHideEarlyAccessToggle) {
	mbHideEarlyAccessToggle.setAttribute('aria-pressed', localStorage.getItem('mbHideEarlyAccess') === '1' ? 'true' : 'false');
}
if (mbShowNsfwToggle) {
	mbShowNsfwToggle.setAttribute('aria-pressed', localStorage.getItem('mbShowNsfw') === '1' ? 'true' : 'false');
}
applyModelBrowserProviderFilters();

function setElementHiddenState(element, isHidden) {
	if (!element) return;
	element.hidden = Boolean(isHidden);
	element.setAttribute('aria-hidden', isHidden ? 'true' : 'false');
}

function setModelBrowserView(view) {
	const savedView = localStorage.getItem('mbActiveView') === 'library' ? 'library' : 'search';
	const nextView = view === 'library' || view === 'search' ? view : savedView;
	mbActiveView = nextView;
	localStorage.setItem('mbActiveView', mbActiveView);
	if (mbViewSearchBtn) {
		const selected = nextView === 'search';
		mbViewSearchBtn.classList.toggle('is-active', selected);
		mbViewSearchBtn.setAttribute('aria-selected', selected ? 'true' : 'false');
		mbViewSearchBtn.setAttribute('tabindex', selected ? '0' : '-1');
	}
	if (mbViewLibraryBtn) {
		const selected = nextView === 'library';
		mbViewLibraryBtn.classList.toggle('is-active', selected);
		mbViewLibraryBtn.setAttribute('aria-selected', selected ? 'true' : 'false');
		mbViewLibraryBtn.setAttribute('tabindex', selected ? '0' : '-1');
	}
	setElementHiddenState(mbRemoteControls, nextView !== 'search');
	setElementHiddenState(mbLocalControls, nextView !== 'library');
	setElementHiddenState(mbRemoteView, nextView !== 'search');
	setElementHiddenState(mbLocalView, nextView !== 'library');
}

function onModelBrowserViewTabKeydown(event) {
	if (!mbViewSearchBtn || !mbViewLibraryBtn) return;
	const key = event.key;
	if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
	event.preventDefault();
	if (key === 'ArrowLeft' || key === 'Home') {
		setModelBrowserView('search');
		mbViewSearchBtn.focus();
		return;
	}
	setModelBrowserView('library');
	mbViewLibraryBtn.focus();
}

function setModelBrowserResetStatus(message) {
	if (!mbResetStatus) return;
	if (mbResetStatusTimer) {
		clearTimeout(mbResetStatusTimer);
		mbResetStatusTimer = null;
	}
	if (!message) {
		setElementHiddenState(mbResetStatus, true);
		mbResetStatus.textContent = '';
		return;
	}
	mbResetStatus.textContent = message;
	setElementHiddenState(mbResetStatus, false);
	mbResetStatusTimer = setTimeout(() => {
		setElementHiddenState(mbResetStatus, true);
	}, 2400);
}

function onModelBrowserFilterTogglesKeydown(event) {
	const key = event.key;
	if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
	const toggles = [mbHideInstalledToggle, mbShowInstalledOnlyToggle, mbHideEarlyAccessToggle, mbShowNsfwToggle].filter(Boolean);
	if (toggles.length < 2) return;
	const currentIndex = toggles.indexOf(event.currentTarget);
	if (currentIndex < 0) return;
	event.preventDefault();
	let nextIndex = currentIndex;
	if (key === 'Home') {
		nextIndex = 0;
	} else if (key === 'End') {
		nextIndex = toggles.length - 1;
	} else if (key === 'ArrowRight') {
		nextIndex = (currentIndex + 1) % toggles.length;
	} else if (key === 'ArrowLeft') {
		nextIndex = (currentIndex - 1 + toggles.length) % toggles.length;
	}
	const nextToggle = toggles[nextIndex];
	if (nextToggle) nextToggle.focus();
}

function onLocalLibraryQuickFiltersKeydown(event) {
	const key = event.key;
	if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
	const toggles = [mbLocalHideEmbeddings, mbLocalMatchedOnly].filter(Boolean);
	if (toggles.length < 2) return;
	const currentIndex = toggles.indexOf(event.currentTarget);
	if (currentIndex < 0) return;
	event.preventDefault();
	let nextIndex = currentIndex;
	if (key === 'Home') {
		nextIndex = 0;
	} else if (key === 'End') {
		nextIndex = toggles.length - 1;
	} else if (key === 'ArrowRight') {
		nextIndex = (currentIndex + 1) % toggles.length;
	} else if (key === 'ArrowLeft') {
		nextIndex = (currentIndex - 1 + toggles.length) % toggles.length;
	}
	const nextToggle = toggles[nextIndex];
	if (nextToggle) nextToggle.focus();
}

function onModelPaginationKeydown(event) {
	const key = event.key;
	if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
	const actions = [mbPrevPage, mbNextPage].filter((btn) => btn && !btn.disabled);
	if (actions.length < 2) return;
	const currentIndex = actions.indexOf(event.currentTarget);
	if (currentIndex < 0) return;
	event.preventDefault();
	let nextIndex = currentIndex;
	if (key === 'Home') {
		nextIndex = 0;
	} else if (key === 'End') {
		nextIndex = actions.length - 1;
	} else if (key === 'ArrowRight') {
		nextIndex = (currentIndex + 1) % actions.length;
	} else if (key === 'ArrowLeft') {
		nextIndex = (currentIndex - 1 + actions.length) % actions.length;
	}
	const nextAction = actions[nextIndex];
	if (nextAction) nextAction.focus();
}

function resetModelBrowserFilters() {
	const keys = [
		'mbProvider',
		'mbSearchQuery',
		'mbSearchType',
		'mbBaseModel',
		'mbSort',
		'mbPageSize',
		'mbHideInstalled',
		'mbShowInstalledOnly',
		'mbHideEarlyAccess',
		'mbShowNsfw',
		'mbLocalQuery',
		'mbLocalType',
		'mbLocalBaseModel',
		'mbLocalSort',
		'mbLocalHideEmbeddings',
		'mbLocalMatchedOnly',
		'mbCompareProviderCivitai',
		'mbCompareProviderHuggingface',
	];
	keys.forEach((key) => localStorage.removeItem(key));

	if (mbProvider) mbProvider.value = 'civitai';
	if (mbSearchQuery) mbSearchQuery.value = '';
	if (mbSearchType) mbSearchType.value = '';
	if (mbBaseModel) mbBaseModel.value = '';
	if (mbSort) mbSort.value = 'highest-rated';
	if (mbPageSize) mbPageSize.value = '20';
	setMbToggleState(mbHideInstalledToggle, false);
	setMbToggleState(mbShowInstalledOnlyToggle, false);
	setMbToggleState(mbHideEarlyAccessToggle, false);
	setMbToggleState(mbShowNsfwToggle, false);

	if (mbLocalQuery) mbLocalQuery.value = '';
	if (mbLocalType) mbLocalType.value = '';
	if (mbLocalBaseModel) mbLocalBaseModel.value = '';
	if (mbLocalSort) mbLocalSort.value = 'name-asc';
	setMbToggleState(mbLocalHideEmbeddings, false);
	setMbToggleState(mbLocalMatchedOnly, false);
	if (mbCompareProviderCivitai) mbCompareProviderCivitai.checked = true;
	if (mbCompareProviderHuggingface) mbCompareProviderHuggingface.checked = true;

	if (mbActiveView === 'search') {
		if (mbResultsSection && !mbResultsSection.hidden) {
			runCivitaiSearch(1);
		} else {
			renderSearchResults(mbLastSearchItems, null);
		}
	} else {
		renderLocalLibraryFromState();
	}
}

function getSelectedCompareProviders() {
	const providers = [];
	if (mbCompareProviderCivitai && mbCompareProviderCivitai.checked) providers.push('civitai');
	if (mbCompareProviderHuggingface && mbCompareProviderHuggingface.checked) providers.push('huggingface');
	return providers;
}

function formatBytes(bytes) {
	if (!bytes || bytes === 0) return '—';
	const units = ['B', 'KB', 'MB', 'GB'];
	let v = bytes;
	let i = 0;
	while (v >= 1024 && i < units.length - 1) { v /= 1024; i++; }
	return v.toFixed(i === 0 ? 0 : 1) + ' ' + units[i];
}

function mbToggleIsOn(toggleBtn) {
	return !!toggleBtn && toggleBtn.getAttribute('aria-pressed') === 'true';
}

function setMbToggleState(toggleBtn, isOn) {
	if (!toggleBtn) return;
	toggleBtn.setAttribute('aria-pressed', isOn ? 'true' : 'false');
}

function getMbServerSortLabel() {
	const value = mbSort ? String(mbSort.value || 'highest-rated') : 'highest-rated';
	if (value === 'most-downloaded') return 'Most Downloaded';
	if (value === 'newest') return 'Newest';
	return 'Highest Rated';
}

function getMbPageSize() {
	const value = mbPageSize ? Number(mbPageSize.value || '20') : 20;
	if (!Number.isFinite(value)) return 20;
	return Math.max(20, Math.min(80, Math.trunc(value)));
}

function applyModelBrowserProviderFilters() {
	const isHuggingFace = mbProvider && mbProvider.value === 'huggingface';
	const baseModelSection = document.getElementById('mb-base-model-section');
	const nsfwSection = document.getElementById('mb-show-nsfw-section');
	const hfHint = document.getElementById('mb-hf-filter-hint');
	if (baseModelSection) {
		setElementHiddenState(baseModelSection, isHuggingFace);
	}
	if (nsfwSection) {
		setElementHiddenState(nsfwSection, isHuggingFace);
	}
	if (hfHint) {
		setElementHiddenState(hfHint, !isHuggingFace);
	}
}

function modelPublishedTs(item) {
	const raw = String(item?.published_at || '');
	const ts = raw ? Date.parse(raw) : NaN;
	return Number.isNaN(ts) ? 0 : ts;
}

function modelIsInstalled(item) {
	const fileName = String(item?.file_name || '').toLowerCase();
	return isInstalledFileName(fileName);
}

function isInstalledFileName(fileName) {
	const raw = String(fileName || '').trim().toLowerCase();
	if (!raw) return false;
	if (mbLocalInstalledNames.has(raw)) return true;
	const normalized = raw.replace(/\\/g, '/');
	if (!normalized.includes('/')) return false;
	const baseName = normalized.split('/').pop() || '';
	return !!baseName && mbLocalInstalledNames.has(baseName);
}

function inferModelFolderFromTypeLabel(typeLabel) {
	const value = String(typeLabel || '').toLowerCase();
	if (!value) return '';
	if (value.includes('lora')) return 'Lora';
	if (value.includes('vae')) return 'VAE';
	if (value.includes('textualinversion') || value.includes('embedding')) return 'Embeddings';
	if (value.includes('controlnet')) return 'ControlNet';
	if (value.includes('upscaler') || value.includes('esrgan')) return 'ESRGAN';
	if (value.includes('checkpoint')) return 'StableDiffusion';
	return '';
}

function inferModelFolderFromFileName(fileName) {
	const name = String(fileName || '').toLowerCase();
	if (!name) return '';
	if (name.includes('lora')) return 'Lora';
	if (name.includes('vae')) return 'VAE';
	if (name.includes('embedding') || name.endsWith('.pt') || name.endsWith('.bin')) {
		if (name.includes('control')) return 'ControlNet';
		if (name.includes('upscale') || name.includes('esrgan') || name.includes('4x')) return 'ESRGAN';
		if (name.includes('textual') || name.includes('embedding') || name.includes('negative')) return 'Embeddings';
	}
	if (name.includes('controlnet') || name.includes('control_') || name.includes('_control_')) return 'ControlNet';
	if (name.includes('upscale') || name.includes('esrgan')) return 'ESRGAN';
	if (name.endsWith('.ckpt') || name.endsWith('.safetensors') || name.endsWith('.gguf')) return 'StableDiffusion';
	return '';
}

function getVersionFileDownloadTarget(item, version, file) {
	const folderFromFileType = inferModelFolderFromTypeLabel(file?.type || '');
	if (folderFromFileType) return folderFromFileType;
	const folderFromModelType = inferModelFolderFromTypeLabel(item?.type || '');
	if (folderFromModelType) return folderFromModelType;
	const folderFromVersionType = inferModelFolderFromTypeLabel(version?.base_model || '');
	if (folderFromVersionType) return folderFromVersionType;
	const folderFromName = inferModelFolderFromFileName(file?.name || '');
	if (folderFromName) return folderFromName;
	return String(item?.model_type_folder || 'StableDiffusion');
}

function setModelModalDownloadStatus(message, level = '') {
	if (!mbModelModalDownloadStatus) return;
	mbModelModalDownloadStatus.classList.remove('is-ok', 'is-error');
	if (!message) {
		mbModelModalDownloadStatus.textContent = '';
		mbModelModalDownloadStatus.hidden = true;
		return;
	}
	if (level === 'ok') mbModelModalDownloadStatus.classList.add('is-ok');
	if (level === 'error') mbModelModalDownloadStatus.classList.add('is-error');
	mbModelModalDownloadStatus.textContent = message;
	mbModelModalDownloadStatus.hidden = false;
}

function setModelSearchStatus(message = '', isVisible = false) {
	if (!mbSearchStatus) return;
	if (mbSearchStatusTimer) {
		clearTimeout(mbSearchStatusTimer);
		mbSearchStatusTimer = null;
	}
	mbSearchStatus.textContent = message;
	setElementHiddenState(mbSearchStatus, !isVisible);
	if (message === 'Search cancelled.' && isVisible) {
		mbSearchStatusTimer = setTimeout(() => {
			if (!mbSearchStatus) return;
			if (mbSearchInFlight) return;
			if (mbSearchStatus.textContent !== 'Search cancelled.') return;
			setModelSearchStatus('', false);
		}, MB_CANCEL_STATUS_CLEAR_MS);
	}
}

function applyModelBrowserClientFilters(items) {
	let filtered = Array.isArray(items) ? items.slice() : [];
	const baseModelFilter = mbBaseModel ? String(mbBaseModel.value || '').trim().toLowerCase() : '';
	if (baseModelFilter) {
		filtered = filtered.filter((item) => String(item.base_model || '').toLowerCase().includes(baseModelFilter));
	}
	if (mbToggleIsOn(mbHideInstalledToggle)) {
		filtered = filtered.filter((item) => !modelIsInstalled(item));
	}
	if (mbToggleIsOn(mbShowInstalledOnlyToggle)) {
		filtered = filtered.filter((item) => modelIsInstalled(item));
	}
	if (mbToggleIsOn(mbHideEarlyAccessToggle)) {
		filtered = filtered.filter((item) => !item.is_early_access);
	}

	const sortValue = mbSort ? String(mbSort.value || 'highest-rated') : 'highest-rated';
	if (sortValue === 'installed') {
		filtered.sort((a, b) => Number(modelIsInstalled(b)) - Number(modelIsInstalled(a)) || String(a.name || '').localeCompare(String(b.name || '')));
	} else if (sortValue === 'favorites') {
		filtered.sort((a, b) => Number(b.likes || 0) - Number(a.likes || 0));
	} else if (sortValue === 'type') {
		filtered.sort((a, b) => String(a.type || '').localeCompare(String(b.type || '')) || String(a.name || '').localeCompare(String(b.name || '')));
	} else if (sortValue === 'newest') {
		filtered.sort((a, b) => modelPublishedTs(b) - modelPublishedTs(a));
	}

	return filtered;
}

// --- Model notes ---
function loadAllModelNotes() {
	try { return JSON.parse(localStorage.getItem(MB_MODEL_NOTES_KEY) || '{}'); }
	catch { return {}; }
}
function getModelNote(key) {
	return loadAllModelNotes()[key] || '';
}
function saveModelNote(key, text) {
	if (!key) return;
	const all = loadAllModelNotes();
	const trimmed = String(text || '').trimEnd();
	if (trimmed) {
		all[key] = trimmed;
	} else {
		delete all[key];
	}
	localStorage.setItem(MB_MODEL_NOTES_KEY, JSON.stringify(all));
}
function populateModelNote(key) {
	mbCurrentModelNoteKey = key || '';
	if (mbModelModalNotes) {
		mbModelModalNotes.value = key ? getModelNote(key) : '';
	}
}
function flushModelNote() {
	if (mbCurrentModelNoteKey && mbModelModalNotes) {
		saveModelNote(mbCurrentModelNoteKey, mbModelModalNotes.value);
	}
	mbCurrentModelNoteKey = '';
	if (mbModelModalNotes) mbModelModalNotes.value = '';
}

function setModelModalOpen(isOpen) {
	if (!mbModelModal) return;
	if (isOpen) {
		mbModelModalLastFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
	} else {
		flushModelNote();
	}
	mbModelModal.hidden = !isOpen;
	mbModelModal.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
	if (isOpen) {
		document.body.classList.add('gallery-lightbox-open');
		if (mbModelModalClose) mbModelModalClose.focus();
	} else {
		document.body.classList.remove('gallery-lightbox-open');
		const active = document.activeElement;
		if (active instanceof HTMLElement && mbModelModal.contains(active) && mbModelModalLastFocus && document.contains(mbModelModalLastFocus)) {
			mbModelModalLastFocus.focus();
		}
		mbModelModalLastFocus = null;
	}
}

function getModelModalTabStops() {
	if (!mbModelModal) return [];
	const selector = [
		'button:not([disabled])',
		'input:not([disabled]):not([type="hidden"])',
		'select:not([disabled])',
		'textarea:not([disabled])',
		'[tabindex]:not([tabindex="-1"])',
	].join(', ');
	return [...mbModelModal.querySelectorAll(selector)].filter((el) => {
		if (!(el instanceof HTMLElement)) return false;
		if (el.hidden || el.getAttribute('aria-hidden') === 'true') return false;
		if (el.closest('[hidden]')) return false;
		return true;
	});
}

function isVideoUrl(url) {
	const u = String(url || '').toLowerCase().split('?')[0];
	return u.endsWith('.mp4') || u.endsWith('.webm') || u.endsWith('.mov') || u.endsWith('.avi');
}

function renderModelModalPreview(images, selectedIndex = 0) {
	if (!mbModelModalPreview || !mbModelModalThumbs) return;
	const safeImages = Array.isArray(images) ? images.filter((img) => img && img.url) : [];
	if (!safeImages.length) {
		mbModelModalPreview.src = '';
		mbModelModalPreview.alt = 'No preview available';
		if (mbModelModalPreviewVideo) { mbModelModalPreviewVideo.src = ''; mbModelModalPreviewVideo.hidden = true; }
		mbModelModalPreview.hidden = false;
		mbModelModalThumbs.innerHTML = '<p class="hint">No example images.</p>';
		return;
	}
	const idx = Math.max(0, Math.min(selectedIndex, safeImages.length - 1));
	const selectedUrl = safeImages[idx].url;
	const selectedIsVideo = isVideoUrl(selectedUrl);
	if (selectedIsVideo && mbModelModalPreviewVideo) {
		mbModelModalPreviewVideo.src = selectedUrl;
		mbModelModalPreviewVideo.hidden = false;
		mbModelModalPreview.src = '';
		mbModelModalPreview.hidden = true;
	} else {
		mbModelModalPreview.src = selectedUrl;
		mbModelModalPreview.alt = 'Model example image';
		mbModelModalPreview.hidden = false;
		if (mbModelModalPreviewVideo) { mbModelModalPreviewVideo.src = ''; mbModelModalPreviewVideo.hidden = true; }
	}
	mbModelModalThumbs.innerHTML = safeImages.map((img, i) => {
		const isVid = isVideoUrl(img.url);
		const activeClass = i === idx ? 'is-active' : '';
		if (isVid) {
			return `<div class="mb-model-modal-thumb mb-model-modal-thumb-video ${activeClass}" data-index="${i}" role="button" tabindex="0" aria-label="Video preview ${i + 1}">▶</div>`;
		}
		return `<img class="mb-model-modal-thumb ${activeClass}" src="${escHtml(img.url)}" alt="Model example ${i + 1}" data-index="${i}">`;
	}).join('');
	mbModelModalThumbs.querySelectorAll('.mb-model-modal-thumb').forEach((thumb) => {
		const activate = () => renderModelModalPreview(safeImages, Number(thumb.dataset.index || 0));
		thumb.addEventListener('click', activate);
		if (thumb.tagName !== 'IMG') {
			thumb.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(); } });
		}
	});
}

function getVersionPreviewUrls(version, fallbackPreview = '') {
	const urls = [];
	const images = Array.isArray(version?.images) ? version.images : [];
	images.forEach((img) => {
		const url = String(img?.url || '').trim();
		if (!url || urls.includes(url)) return;
		urls.push(url);
	});
	const fallback = String(fallbackPreview || '').trim();
	if (fallback && !urls.includes(fallback)) {
		urls.unshift(fallback);
	}
	return urls;
}

async function bulkUpdateInstalledSearchMetadata() {
	if (mbSearchBulkRefreshInstalledBtn) mbSearchBulkRefreshInstalledBtn.disabled = true;
	if (mbSearchStatus) {
		mbSearchStatus.textContent = 'Scanning installed models in current search results...';
		setElementHiddenState(mbSearchStatus, false);
	}

	const searchItems = Array.isArray(mbLastSearchItems) ? mbLastSearchItems : [];
	const installedItems = searchItems.filter((item) => modelIsInstalled(item));
	if (!installedItems.length) {
		showToast('No installed models were found in current search results.', 'neg');
		if (mbSearchStatus) {
			mbSearchStatus.textContent = 'No installed models found in current search results.';
			setElementHiddenState(mbSearchStatus, false);
		}
		if (mbSearchBulkRefreshInstalledBtn) mbSearchBulkRefreshInstalledBtn.disabled = false;
		return;
	}

	let updatedModels = 0;
	let updatedFiles = 0;
	let failedModels = 0;
	const updatedModelNames = [];
	const failedModelNames = [];

	for (const item of installedItems) {
		const provider = String(item?.provider || 'civitai').toLowerCase();
		const modelId = String(item?.id || '').trim();
		if (!modelId) {
			failedModels += 1;
			failedModelNames.push(String(item?.name || 'unknown model'));
			continue;
		}

		try {
			const detailsPath = provider === 'huggingface'
				? '/api/models/huggingface/model/'
				: '/api/models/civitai/model/';
			const detailsResp = await fetch(detailsPath + encodeURIComponent(modelId));
			const details = await detailsResp.json();
			if (!detailsResp.ok || !details.ok) throw new Error(details.error || detailsResp.statusText);

			const versions = Array.isArray(details.versions) ? details.versions : [];
			let modelUpdated = false;

			for (const version of versions) {
				const files = Array.isArray(version?.files) ? version.files : [];
				const installedFileNames = files
					.map((f) => String(f?.name || '').trim())
					.filter((name) => isInstalledFileName(name));
				if (!installedFileNames.length) continue;

				const previewUrls = getVersionPreviewUrls(version, details.preview_url || item.preview_url || '');
				const updateResp = await fetch('/api/models/library/update-version-metadata', {
					method: 'POST',
					headers: {'Content-Type': 'application/json'},
					body: JSON.stringify({
						provider,
						model_id: modelId,
						model_name: String(details.name || item.name || ''),
						model_type: String(details.type || item.type || ''),
						base_model: String(version?.base_model || details.base_model || item.base_model || ''),
						model_url: String(details.model_url || item.model_url || ''),
						version_name: String(version?.name || ''),
						preview_url: previewUrls[0] || '',
						preview_urls: previewUrls,
						installed_files: installedFileNames,
					}),
				});
				const updatePayload = await updateResp.json();
				if (!updateResp.ok || !updatePayload.ok) throw new Error(updatePayload.error || updateResp.statusText);
				const changed = Number(updatePayload.updated || 0);
				if (changed > 0) {
					updatedFiles += changed;
					modelUpdated = true;
				}
			}

			if (modelUpdated) {
				updatedModels += 1;
				updatedModelNames.push(String(item?.name || modelId));
			}
		} catch (err) {
			failedModels += 1;
			failedModelNames.push(String(item?.name || modelId));
		}
	}

	const summary = `Bulk installed update complete: ${updatedModels} model(s), ${updatedFiles} file record(s) updated, ${failedModels} failed.`;
	showToast(summary, failedModels > 0 ? 'neg' : 'pos');
	renderLocalLibraryActionReport('Search Bulk Installed Update', summary, [
		{
			label: 'Updated Models',
			items: buildReportItemsFromSamples(updatedModelNames, (sample) => {
				const name = String(sample || '').trim();
				return createReportItem(name, name);
			}),
		},
		{
			label: 'Failed Models',
			items: buildReportItemsFromSamples(failedModelNames, (sample) => {
				const name = String(sample || '').trim();
				return createReportItem(name, name);
			}),
		},
	]);

	if (mbSearchStatus) {
		mbSearchStatus.textContent = summary;
		setElementHiddenState(mbSearchStatus, false);
	}

	await loadModelLibrary();
	if (mbSearchBulkRefreshInstalledBtn) mbSearchBulkRefreshInstalledBtn.disabled = false;
}

async function refreshInstalledVersionMetadata(version, installedFiles, btn) {
	const provider = String(mbCurrentModelDetails?.provider || 'civitai').toLowerCase();
	const modelId = String(mbCurrentModelDetails?.id || '');
	if (!provider || !modelId || !Array.isArray(installedFiles) || installedFiles.length === 0) {
		setModelModalDownloadStatus('No installed files found for this version.', 'error');
		return;
	}
	if (btn) btn.disabled = true;
	const versionLabel = String(version?.name || 'Selected version');
	setModelModalDownloadStatus(`Updating local metadata and previews for ${versionLabel}...`);
	try {
		const previewUrls = getVersionPreviewUrls(version, mbCurrentModelDetails?.preview_url || '');
		const resp = await fetch('/api/models/library/update-version-metadata', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({
				provider,
				model_id: modelId,
				model_name: String(mbCurrentModelDetails?.name || ''),
				model_type: String(mbCurrentModelDetails?.type || ''),
				base_model: String(version?.base_model || mbCurrentModelDetails?.base_model || ''),
				model_url: String(mbCurrentModelDetails?.model_url || ''),
				version_name: versionLabel,
				preview_url: previewUrls[0] || '',
				preview_urls: previewUrls,
				installed_files: installedFiles,
			}),
		});
		const data = await resp.json();
		if (!resp.ok || !data.ok) throw new Error(data.error || resp.statusText);
		setModelModalDownloadStatus(`Updated ${Number(data.updated || 0)} local file(s) with ${Number(data.preview_count || 0)} preview image(s).`, 'ok');
		await loadModelLibrary();
	} catch (err) {
		setModelModalDownloadStatus('Failed to update preview + metadata: ' + err.message, 'error');
	} finally {
		if (btn) btn.disabled = false;
	}
}

function renderModelVersionDetails(version) {
	if (!version || !mbModelModalFiles || !mbModelModalDefaults || !mbModelModalVersionStatus) return;
	const files = Array.isArray(version.files) ? version.files : [];
	const versionInstalled = files.some((f) => isInstalledFileName(f.name || ''));
	const installedFileNames = files
		.map((f) => String(f.name || '').trim())
		.filter((name) => isInstalledFileName(name));
	const provider = String(mbCurrentModelDetails?.provider || 'civitai').toLowerCase();
	const modelId = String(mbCurrentModelDetails?.id || '');
	const previewUrl = (() => {
		if (Array.isArray(version.images) && version.images.length && version.images[0] && version.images[0].url) {
			return String(version.images[0].url || '');
		}
		return String(mbCurrentModelDetails?.preview_url || '');
	})();
	mbModelModalVersionStatus.textContent = versionInstalled ? 'Installed version detected' : 'Not installed';

	if (!files.length) {
		mbModelModalFiles.innerHTML = `
			<div class="mb-model-modal-file">
				<div class="mb-model-modal-file-main">
					<span class="mb-model-modal-file-name">Apply this model to Image Gen</span>
					<span class="mb-model-modal-file-meta">Use this selection in the Image tab controls.</span>
				</div>
				<div class="mb-model-modal-file-actions">
					<button class="btn btn-sm btn-ghost mb-model-modal-use-btn" data-name="${escHtml(String(mbCurrentModelDetails?.name || ''))}" data-type="${escHtml(String(mbCurrentModelDetails?.type || ''))}">Use in Image Gen</button>
				</div>
			</div>
			<p class="hint">No files listed for this version.</p>`;
	} else {
		mbModelModalFiles.innerHTML = `
			<div class="mb-model-modal-file">
				<div class="mb-model-modal-file-main">
					<span class="mb-model-modal-file-name">Apply this model to Image Gen</span>
					<span class="mb-model-modal-file-meta">Use this selection in the Image tab controls.</span>
				</div>
				<div class="mb-model-modal-file-actions">
					<button class="btn btn-sm btn-ghost mb-model-modal-use-btn" data-name="${escHtml(String(mbCurrentModelDetails?.name || ''))}" data-type="${escHtml(String(mbCurrentModelDetails?.type || ''))}">Use in Image Gen</button>
				</div>
			</div>
		` + files.map((f) => {
			const installed = isInstalledFileName(f.name || '');
			const sizeLabel = formatBytes(f.size_bytes || 0);
			const targetFolder = getVersionFileDownloadTarget(mbCurrentModelDetails, version, f);
			const canDownload = Boolean(f.download_url) || provider === 'huggingface';
			const buttonLabel = installed ? 'Installed' : 'Download';
			const disabledReason = installed ? 'Already installed' : (!canDownload ? 'No download URL available' : '');
			const disabledAttrs = disabledReason ? `disabled title="${escHtml(disabledReason)}"` : '';
			return `
				<div class="mb-model-modal-file">
					<div class="mb-model-modal-file-main">
						<span class="mb-model-modal-file-name">${escHtml(f.name || 'unnamed file')}</span>
						<span class="mb-model-modal-file-meta">${escHtml(f.type || 'model')} · ${escHtml(sizeLabel)} · ${escHtml(targetFolder)}${installed ? ' · Installed' : ''}</span>
					</div>
					<div class="mb-model-modal-file-actions">
						<button
							class="btn btn-sm btn-primary mb-model-modal-download-btn"
							data-url="${escHtml(f.download_url || '')}"
							data-name="${escHtml(f.name || '')}"
							data-folder="${escHtml(targetFolder)}"
							data-version-name="${escHtml(version.name || 'Selected version')}"
							data-provider="${escHtml(provider)}"
							data-model-id="${escHtml(modelId)}"
							data-model-name="${escHtml(String(mbCurrentModelDetails?.name || ''))}"
							data-model-type="${escHtml(String(mbCurrentModelDetails?.type || ''))}"
							data-base-model="${escHtml(String(version.base_model || mbCurrentModelDetails?.base_model || ''))}"
							data-model-url="${escHtml(String(mbCurrentModelDetails?.model_url || ''))}"
							data-preview-url="${escHtml(previewUrl)}"
							${disabledAttrs}>
							${buttonLabel}
						</button>
						${installed ? '<button class="btn btn-sm btn-ghost mb-model-modal-refresh-btn" type="button">Update Preview + Metadata</button>' : ''}
					</div>
				</div>`;
		}).join('');

		mbModelModalFiles.querySelectorAll('.mb-model-modal-download-btn').forEach((btn) => {
			btn.addEventListener('click', () => {
				const versionName = btn.dataset.versionName || 'Selected version';
				const fileLabel = btn.dataset.name || 'file';
				setModelModalDownloadStatus(`Queueing ${fileLabel} from ${versionName}...`);
				startModelDownload(
					btn.dataset.url,
					btn.dataset.name,
					btn.dataset.folder,
					btn,
					btn.dataset.provider,
					btn.dataset.modelId,
					versionName,
					btn.dataset.modelName,
					btn.dataset.modelType,
					btn.dataset.baseModel,
					btn.dataset.modelUrl,
					btn.dataset.previewUrl,
				);
			});
		});

		mbModelModalFiles.querySelectorAll('.mb-model-modal-refresh-btn').forEach((btn) => {
			btn.addEventListener('click', () => {
				refreshInstalledVersionMetadata(version, installedFileNames, btn);
			});
		});
	}

	mbModelModalFiles.querySelectorAll('.mb-model-modal-use-btn').forEach((btn) => {
		btn.addEventListener('click', () => {
			useModelInImageGen({
				name: btn.dataset.name || '',
				type: btn.dataset.type || '',
				folder: '',
			});
		});
	});

	const defaults = version.defaults || {};
	const trainedWords = Array.isArray(defaults.trained_words) ? defaults.trained_words.slice(0, 12).join(', ') : '';
	const rows = [
		['Base model', defaults.base_model || version.base_model || 'Not provided'],
		['Sampler', defaults.sampler || 'Not provided'],
		['Steps', defaults.steps || 'Not provided'],
		['CFG', defaults.cfg || 'Not provided'],
		['Clip skip', defaults.clip_skip || 'Not provided'],
		['Trained words', trainedWords || 'Not provided'],
	];
	mbModelModalDefaults.innerHTML = rows.map(([label, value]) => (
		`<div class="mb-model-modal-file"><span class="mb-model-modal-file-name">${escHtml(String(label))}</span><span>${escHtml(String(value))}</span></div>`
	)).join('');

	renderModelModalPreview(version.images || [], 0);
}

function openLocalModelDetailsModal(item) {
	if (!item || !mbModelModal) return;
	const typeLabel = String(item.type || item.folder || 'Model');
	const folderLabel = String(item.folder || 'Unknown');
	const sizeLabel = formatBytes(item.size_bytes || 0);
	const baseModelLabel = String(item.base_model || 'Not provided');
	const versionLabel = String(item.version_name || '');
	const pathLabel = String(item.path || 'Not provided');

	mbCurrentModelDetails = null;
	mbCurrentVersionIndex = 0;
	setModelModalOpen(true);
	populateModelNote(`local:${item.name || ''}`);
	if (mbModelModalTitle) mbModelModalTitle.textContent = item.name || 'Local model details';
	if (mbModelModalMeta) mbModelModalMeta.textContent = `${typeLabel} · Local library · ${folderLabel}${versionLabel ? ` · ${versionLabel}` : ''}`;
	if (mbModelModalDescription) {
		mbModelModalDescription.textContent = versionLabel
			? `Installed local model file in ${folderLabel}. Matched version: ${versionLabel}.`
			: `Installed local model file in ${folderLabel}.`;
	}
	if (mbModelModalVersion) {
		mbModelModalVersion.disabled = true;
		mbModelModalVersion.innerHTML = '<option value="0">Local file</option>';
	}
	if (mbModelModalVersionStatus) mbModelModalVersionStatus.textContent = 'Installed local model';
	setModelModalDownloadStatus('');

	if (mbModelModalFiles) {
		mbModelModalFiles.innerHTML = `
			<div class="mb-model-modal-file">
				<div class="mb-model-modal-file-main">
					<span class="mb-model-modal-file-name">${escHtml(item.name || 'unnamed file')}</span>
					<span class="mb-model-modal-file-meta">${escHtml(typeLabel)} · ${escHtml(sizeLabel)} · ${escHtml(folderLabel)}</span>
				</div>
				<div class="mb-model-modal-file-actions">
					<button class="btn btn-sm btn-ghost mb-local-modal-use-btn" data-name="${escHtml(item.name || '')}" data-type="${escHtml(item.type || '')}" data-folder="${escHtml(item.folder || '')}">Use in Image Gen</button>
					<button class="btn btn-sm btn-danger mb-local-modal-delete-btn" data-name="${escHtml(item.name || '')}" data-folder="${escHtml(item.folder || '')}">Delete</button>
				</div>
			</div>`;
		const useBtn = mbModelModalFiles.querySelector('.mb-local-modal-use-btn');
		if (useBtn) {
			useBtn.addEventListener('click', () => {
				useModelInImageGen({
					name: useBtn.dataset.name || '',
					type: useBtn.dataset.type || '',
					folder: useBtn.dataset.folder || '',
				});
			});
		}
		const deleteBtn = mbModelModalFiles.querySelector('.mb-local-modal-delete-btn');
		if (deleteBtn) {
			deleteBtn.addEventListener('click', async () => {
				await deleteLocalModel(deleteBtn.dataset.name || '', deleteBtn.dataset.folder || '', deleteBtn);
				setModelModalOpen(false);
			});
		}
	}

	if (mbModelModalDefaults) {
		const rows = [
			['Folder', folderLabel],
			['Type', typeLabel],
			['Matched version', versionLabel || 'Not provided'],
			['Base model', baseModelLabel],
			['File size', sizeLabel],
			['Path', pathLabel],
		];
		mbModelModalDefaults.innerHTML = rows.map(([label, value]) => (
			`<div class="mb-model-modal-file"><span class="mb-model-modal-file-name">${escHtml(String(label))}</span><span>${escHtml(String(value))}</span></div>`
		)).join('');
	}

	const previewUrls = Array.isArray(item.preview_urls)
		? item.preview_urls.map((url) => String(url || '').trim()).filter(Boolean)
		: [];
	const previewItems = previewUrls.length
		? previewUrls.map((url) => ({url}))
		: (item.preview_url ? [{url: item.preview_url}] : []);
	renderModelModalPreview(previewItems, 0);
}

async function openModelDetailsModal(item) {
	if (!item || !item.id || !mbModelModal) return;
	const provider = String(item.provider || 'civitai').toLowerCase();
	setModelModalOpen(true);
	populateModelNote(`${provider}:${item.id}`);
	if (mbModelModalTitle) mbModelModalTitle.textContent = item.name || 'Model details';
	if (mbModelModalMeta) mbModelModalMeta.textContent = 'Loading model details...';
	if (mbModelModalDescription) mbModelModalDescription.textContent = '';
	if (mbModelModalFiles) mbModelModalFiles.innerHTML = '<p class="hint">Loading files...</p>';
	if (mbModelModalDefaults) mbModelModalDefaults.innerHTML = '<p class="hint">Loading defaults...</p>';
	if (mbModelModalVersion) {
		mbModelModalVersion.disabled = false;
		mbModelModalVersion.innerHTML = '';
	}
	if (mbModelModalThumbs) mbModelModalThumbs.innerHTML = '';
	setModelModalDownloadStatus('');

	try {
		const detailsPath = provider === 'huggingface'
			? '/api/models/huggingface/model/'
			: '/api/models/civitai/model/';
		const resp = await fetch(detailsPath + encodeURIComponent(String(item.id)));
		const data = await resp.json();
		if (!resp.ok || !data.ok) throw new Error(data.error || resp.statusText);

		const fallbackType = String(item?.type || '');
		const resolvedType = data.type && data.type !== 'Checkpoint'
			? data.type
			: (fallbackType || data.type || 'Checkpoint');
		mbCurrentModelDetails = {
			...data,
			type: resolvedType,
			preview_url: data.preview_url || item?.preview_url || '',
			model_type_folder: data.model_type_folder || item?.model_type_folder || '',
		};
		mbCurrentVersionIndex = 0;
		if (mbModelModalTitle) mbModelModalTitle.textContent = data.name || item.name || 'Model details';
		if (mbModelModalMeta) {
			const rating = Number(data?.stats?.rating || 0).toFixed(1);
			const likes = Number(data?.stats?.likes || 0).toLocaleString();
			const downloads = Number(data?.stats?.downloads || 0).toLocaleString();
			mbModelModalMeta.textContent = `${resolvedType || ''} · by ${data.creator || 'unknown'} · ★ ${rating} · ❤ ${likes} · ${downloads} downloads`;
		}
		if (mbModelModalDescription) {
			mbModelModalDescription.textContent = data.description || 'No model description provided.';
		}

		const versions = Array.isArray(data.versions) ? data.versions : [];
		if (mbModelModalVersion) {
			mbModelModalVersion.innerHTML = versions.map((v, idx) => {
				const installed = Array.isArray(v.files) && v.files.some((f) => isInstalledFileName(f.name || ''));
				const suffix = installed ? ' (installed)' : '';
				return `<option value="${idx}">${escHtml((v.name || `Version ${idx + 1}`) + suffix)}</option>`;
			}).join('');
		}

		if (!versions.length) {
			if (mbModelModalVersionStatus) mbModelModalVersionStatus.textContent = 'No versions available';
			if (mbModelModalFiles) mbModelModalFiles.innerHTML = '<p class="hint">No files listed for this model.</p>';
			if (mbModelModalDefaults) mbModelModalDefaults.innerHTML = '<p class="hint">No defaults available.</p>';
			setModelModalDownloadStatus('');
			renderModelModalPreview([], 0);
			return;
		}

		renderModelVersionDetails(versions[0]);
	} catch (err) {
		if (mbModelModalMeta) mbModelModalMeta.textContent = `Failed to load model details: ${err.message}`;
		if (mbModelModalFiles) mbModelModalFiles.innerHTML = '<p class="hint">Could not load files.</p>';
		if (mbModelModalDefaults) mbModelModalDefaults.innerHTML = '<p class="hint">Could not load defaults.</p>';
		setModelModalDownloadStatus('Could not load version download options.', 'error');
		renderModelModalPreview([], 0);
	}
}

function mbOnTabActivate() {
	setModelBrowserView(mbActiveView);
	loadModelLibrary();
}

async function loadModelLibrary() {
	if (!mbLibraryGrid) return;
	if (mbLibraryStatus) { mbLibraryStatus.textContent = 'Scanning local models…'; setElementHiddenState(mbLibraryStatus, false); }
	mbLibraryGrid.innerHTML = '';
	try {
		const resp = await fetch('/api/models/library');
		const data = await resp.json();
		if (!resp.ok) throw new Error(data.error || resp.statusText);
		mbLibraryAllModels = Array.isArray(data.models) ? data.models : [];
		mbLibraryRoot = String(data.models_root || '');
		renderLocalLibraryFromState();
	} catch (err) {
		if (mbLibraryStatus) { mbLibraryStatus.textContent = 'Could not load local models: ' + err.message; setElementHiddenState(mbLibraryStatus, false); }
	}
}

async function enrichLocalLibraryPreviews() {
	if (mbLibraryEnrichPreviewsBtn) mbLibraryEnrichPreviewsBtn.disabled = true;
	if (mbLibraryStatus) {
		mbLibraryStatus.textContent = 'Looking up missing previews…';
		setElementHiddenState(mbLibraryStatus, false);
	}
	try {
		const resp = await fetch('/api/models/library/enrich-previews', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({limit: 40}),
		});
		const data = await resp.json();
		if (!resp.ok || !data.ok) throw new Error(data.error || resp.statusText);
		const updated = Number(data.updated || 0);
		const failed = Number(data.failed || 0);
		const skipped = Number(data.skipped || 0);
		const noMatchSkips = Number(((data.skip_reasons || {}).no_civitai_match) || 0);
		const toastMessage = `Preview lookup complete: ${updated} updated, ${failed} failed, ${skipped} skipped (${noMatchSkips} no match).`;
		showToast(toastMessage, failed > 0 ? 'neg' : 'pos');
		renderLocalLibraryActionReport('Preview Lookup', toastMessage, [
			{
				label: 'Updated',
				items: buildReportItemsFromSamples(data.updated_samples, (sample) => {
					const fileName = String(sample || '').trim();
					return createReportItem(fileName, fileName);
				}),
			},
			{
				label: 'Skipped',
				items: buildReportItemsFromSamples(data.skipped_samples, (sample) => {
					if (!sample || typeof sample !== 'object') return '';
					const fileName = String(sample.file || '').trim();
					return createReportItem(`${fileName} (${formatReportReason(sample.reason)})`, fileName);
				}),
			},
			{
				label: 'Failed',
				items: buildReportItemsFromSamples(data.failed_samples, (sample) => {
					if (!sample || typeof sample !== 'object') return '';
					const fileName = String(sample.file || '').trim();
					const errorText = String(sample.error || '').trim();
					return createReportItem(`${fileName}${errorText ? ` (${errorText})` : ''}`, fileName);
				}),
			},
		]);
		if (mbLibraryStatus) {
			mbLibraryStatus.textContent = toastMessage;
			setElementHiddenState(mbLibraryStatus, false);
		}
		await loadModelLibrary();
	} catch (err) {
		showToast('Preview lookup failed: ' + err.message, 'neg');
		renderLocalLibraryActionReport('Preview Lookup', 'Preview lookup failed: ' + err.message, []);
		if (mbLibraryStatus) {
			mbLibraryStatus.textContent = 'Could not enrich local previews: ' + err.message;
			setElementHiddenState(mbLibraryStatus, false);
		}
	} finally {
		if (mbLibraryEnrichPreviewsBtn) mbLibraryEnrichPreviewsBtn.disabled = false;
	}
}

async function compareLocalLibraryMetadata() {
	if (mbLibraryCompareMetadataBtn) mbLibraryCompareMetadataBtn.disabled = true;
	if (mbLibraryStatus) {
		mbLibraryStatus.textContent = 'Comparing missing metadata with providers…';
		setElementHiddenState(mbLibraryStatus, false);
	}
	let providerSummary = '';
	try {
		const selectedProviders = getSelectedCompareProviders();
		if (!selectedProviders.length) throw new Error('Select at least one provider for compare.');
		providerSummary = selectedProviders
			.map((p) => p === 'civitai' ? 'CivitAI' : 'Hugging Face')
			.join(', ');
		const resp = await fetch('/api/models/library/compare-metadata', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({limit: 80, providers: selectedProviders, overwrite: false}),
		});
		const data = await resp.json();
		if (!resp.ok || !data.ok) throw new Error(data.error || resp.statusText);
		const updated = Number(data.updated || 0);
		const failed = Number(data.failed || 0);
		const skipped = Number(data.skipped || 0);
		const civitaiHits = Number(((data.matched_by_provider || {}).civitai) || 0);
		const huggingfaceHits = Number(((data.matched_by_provider || {}).huggingface) || 0);
		const toastMessage = `Metadata compare complete (${providerSummary}): ${updated} updated (${civitaiHits} CivitAI, ${huggingfaceHits} Hugging Face), ${failed} failed, ${skipped} skipped.`;
		showToast(toastMessage, failed > 0 ? 'neg' : 'pos');
		renderLocalLibraryActionReport('Metadata Compare', toastMessage, [
			{
				label: 'Updated',
				items: buildReportItemsFromSamples(data.updated_samples, (sample) => {
					if (!sample || typeof sample !== 'object') return '';
					const fileName = String(sample.file || '').trim();
					const provider = String(sample.provider || '').trim();
					const versionName = String(sample.version_name || '').trim();
					const details = [provider, versionName].filter(Boolean).join(' · ');
					return createReportItem(`${fileName}${details ? ` (${details})` : ''}`, fileName);
				}),
			},
			{
				label: 'Skipped',
				items: buildReportItemsFromSamples(data.skipped_samples, (sample) => {
					if (!sample || typeof sample !== 'object') return '';
					const fileName = String(sample.file || '').trim();
					return createReportItem(`${fileName} (${formatReportReason(sample.reason)})`, fileName);
				}),
			},
			{
				label: 'Failed',
				items: buildReportItemsFromSamples(data.failed_samples, (sample) => {
					if (!sample || typeof sample !== 'object') return '';
					const fileName = String(sample.file || '').trim();
					const errorText = String(sample.error || '').trim();
					return createReportItem(`${fileName}${errorText ? ` (${errorText})` : ''}`, fileName);
				}),
			},
		]);
		if (mbLibraryStatus) {
			mbLibraryStatus.textContent = toastMessage;
			setElementHiddenState(mbLibraryStatus, false);
		}
		await loadModelLibrary();
	} catch (err) {
		const errorPrefix = providerSummary ? `Metadata compare failed (${providerSummary}): ` : 'Metadata compare failed: ';
		showToast(errorPrefix + err.message, 'neg');
		renderLocalLibraryActionReport('Metadata Compare', errorPrefix + err.message, []);
		if (mbLibraryStatus) {
			mbLibraryStatus.textContent = (providerSummary ? `Could not compare metadata (${providerSummary}): ` : 'Could not compare metadata: ') + err.message;
			setElementHiddenState(mbLibraryStatus, false);
		}
	} finally {
		if (mbLibraryCompareMetadataBtn) mbLibraryCompareMetadataBtn.disabled = false;
	}
}

async function recoverLocalLibraryMetadataAndPreviews() {
	if (mbLibraryRecoverMetadataBtn) mbLibraryRecoverMetadataBtn.disabled = true;
	if (mbLibraryCompareMetadataBtn) mbLibraryCompareMetadataBtn.disabled = true;
	if (mbLibraryEnrichPreviewsBtn) mbLibraryEnrichPreviewsBtn.disabled = true;
	if (mbLibraryStatus) {
		mbLibraryStatus.textContent = 'Recovering missing metadata and previews…';
		setElementHiddenState(mbLibraryStatus, false);
	}
	let providerSummary = '';
	try {
		const selectedProviders = getSelectedCompareProviders();
		if (!selectedProviders.length) throw new Error('Select at least one provider for recovery.');
		providerSummary = selectedProviders
			.map((p) => p === 'civitai' ? 'CivitAI' : 'Hugging Face')
			.join(', ');
		const resp = await fetch('/api/models/library/recover-metadata', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({
				compare_limit: 80,
				preview_limit: 40,
				providers: selectedProviders,
				overwrite: false,
			}),
		});
		const data = await resp.json();
		if (!resp.ok || !data.ok) throw new Error(data.error || resp.statusText);

		const compare = data.compare || {};
		const preview = data.preview || {};
		const compareUpdated = Number(compare.updated || 0);
		const compareFailed = Number(compare.failed || 0);
		const compareSkipped = Number(compare.skipped || 0);
		const previewUpdated = Number(preview.updated || 0);
		const previewFailed = Number(preview.failed || 0);
		const previewSkipped = Number(preview.skipped || 0);
		const failedTotal = Number(data.failed_total || 0);

		const summary = `Recovery complete (${providerSummary}): metadata ${compareUpdated} updated, ${compareFailed} failed, ${compareSkipped} skipped; previews ${previewUpdated} updated, ${previewFailed} failed, ${previewSkipped} skipped.`;
		showToast(summary, failedTotal > 0 ? 'neg' : 'pos');
		renderLocalLibraryActionReport('Metadata + Preview Recovery', summary, [
			{
				label: 'Metadata Updated',
				items: buildReportItemsFromSamples(compare.updated_samples, (sample) => {
					if (!sample || typeof sample !== 'object') return '';
					const fileName = String(sample.file || '').trim();
					const provider = String(sample.provider || '').trim();
					const versionName = String(sample.version_name || '').trim();
					const details = [provider, versionName].filter(Boolean).join(' · ');
					return createReportItem(`${fileName}${details ? ` (${details})` : ''}`, fileName);
				}),
			},
			{
				label: 'Metadata Skipped',
				items: buildReportItemsFromSamples(compare.skipped_samples, (sample) => {
					if (!sample || typeof sample !== 'object') return '';
					const fileName = String(sample.file || '').trim();
					return createReportItem(`${fileName} (${formatReportReason(sample.reason)})`, fileName);
				}),
			},
			{
				label: 'Metadata Failed',
				items: buildReportItemsFromSamples(compare.failed_samples, (sample) => {
					if (!sample || typeof sample !== 'object') return '';
					const fileName = String(sample.file || '').trim();
					const errorText = String(sample.error || '').trim();
					return createReportItem(`${fileName}${errorText ? ` (${errorText})` : ''}`, fileName);
				}),
			},
			{
				label: 'Previews Updated',
				items: buildReportItemsFromSamples(preview.updated_samples, (sample) => {
					const fileName = String(sample || '').trim();
					return createReportItem(fileName, fileName);
				}),
			},
			{
				label: 'Previews Skipped',
				items: buildReportItemsFromSamples(preview.skipped_samples, (sample) => {
					if (!sample || typeof sample !== 'object') return '';
					const fileName = String(sample.file || '').trim();
					return createReportItem(`${fileName} (${formatReportReason(sample.reason)})`, fileName);
				}),
			},
			{
				label: 'Previews Failed',
				items: buildReportItemsFromSamples(preview.failed_samples, (sample) => {
					if (!sample || typeof sample !== 'object') return '';
					const fileName = String(sample.file || '').trim();
					const errorText = String(sample.error || '').trim();
					return createReportItem(`${fileName}${errorText ? ` (${errorText})` : ''}`, fileName);
				}),
			},
		]);
		if (mbLibraryStatus) {
			mbLibraryStatus.textContent = summary;
			setElementHiddenState(mbLibraryStatus, false);
		}
		await loadModelLibrary();
	} catch (err) {
		const errorPrefix = providerSummary ? `Recovery failed (${providerSummary}): ` : 'Recovery failed: ';
		showToast(errorPrefix + err.message, 'neg');
		renderLocalLibraryActionReport('Metadata + Preview Recovery', errorPrefix + err.message, []);
		if (mbLibraryStatus) {
			mbLibraryStatus.textContent = (providerSummary ? `Could not recover metadata and previews (${providerSummary}): ` : 'Could not recover metadata and previews: ') + err.message;
			setElementHiddenState(mbLibraryStatus, false);
		}
	} finally {
		if (mbLibraryRecoverMetadataBtn) mbLibraryRecoverMetadataBtn.disabled = false;
		if (mbLibraryCompareMetadataBtn) mbLibraryCompareMetadataBtn.disabled = false;
		if (mbLibraryEnrichPreviewsBtn) mbLibraryEnrichPreviewsBtn.disabled = false;
	}
}

function applyLocalLibraryClientFilters(models) {
	let filtered = Array.isArray(models) ? models.slice() : [];
	const query = mbLocalQuery ? String(mbLocalQuery.value || '').trim().toLowerCase() : '';
	const type = mbLocalType ? String(mbLocalType.value || '').trim().toLowerCase() : '';
	const baseModel = mbLocalBaseModel ? String(mbLocalBaseModel.value || '').trim().toLowerCase() : '';
	const hideEmbeddings = mbToggleIsOn(mbLocalHideEmbeddings);
	const matchedOnly = mbToggleIsOn(mbLocalMatchedOnly);
	if (query) {
		filtered = filtered.filter((item) => {
			const name = String(item.name || '').toLowerCase();
			const folder = String(item.folder || '').toLowerCase();
			const itemType = String(item.type || '').toLowerCase();
			const itemBaseModel = String(item.base_model || '').toLowerCase();
			const itemProvider = String(item.provider || '').toLowerCase();
			const itemModelId = String(item.model_id || '').toLowerCase();
			const itemModelName = String(item.model_name || '').toLowerCase();
			const itemVersionName = String(item.version_name || '').toLowerCase();
			return name.includes(query)
				|| folder.includes(query)
				|| itemType.includes(query)
				|| itemBaseModel.includes(query)
				|| itemProvider.includes(query)
				|| itemModelId.includes(query)
				|| itemModelName.includes(query)
				|| itemVersionName.includes(query);
		});
	}
	if (type) {
		filtered = filtered.filter((item) => String(item.type || '').toLowerCase() === type);
	}
	if (baseModel) {
		filtered = filtered.filter((item) => String(item.base_model || '').toLowerCase().includes(baseModel));
	}
	if (hideEmbeddings) {
		filtered = filtered.filter((item) => !String(item.folder || '').toLowerCase().includes('embedding') && !String(item.type || '').toLowerCase().includes('textualinversion'));
	}
	if (matchedOnly) {
		filtered = filtered.filter((item) => {
			const provider = String(item.provider || '').trim();
			const modelId = String(item.model_id || '').trim();
			const modelName = String(item.model_name || '').trim();
			const versionName = String(item.version_name || '').trim();
			return Boolean(provider || modelId || modelName || versionName);
		});
	}
	const sort = mbLocalSort ? String(mbLocalSort.value || 'name-asc') : 'name-asc';
	if (sort === 'name-desc') {
		filtered.sort((a, b) => String(b.name || '').localeCompare(String(a.name || '')));
	} else if (sort === 'size-desc') {
		filtered.sort((a, b) => Number(b.size_bytes || 0) - Number(a.size_bytes || 0));
	} else if (sort === 'size-asc') {
		filtered.sort((a, b) => Number(a.size_bytes || 0) - Number(b.size_bytes || 0));
	} else if (sort === 'folder') {
		filtered.sort((a, b) => String(a.folder || '').localeCompare(String(b.folder || '')) || String(a.name || '').localeCompare(String(b.name || '')));
	} else {
		filtered.sort((a, b) => String(a.name || '').localeCompare(String(b.name || '')));
	}
	return filtered;
}

function refreshLocalBaseModelOptions(models) {
	if (!mbLocalBaseModel) return;
	const STATIC_VALUES = new Set(['', 'SD 1.5', 'SDXL 1.0', 'SDXL Turbo', 'Pony', 'Flux.1 D', 'Flux.1 S']);
	const currentValue = mbLocalBaseModel.value;
	// remove previously-added dynamic options
	Array.from(mbLocalBaseModel.options).forEach((opt) => {
		if (!STATIC_VALUES.has(opt.value)) opt.remove();
	});
	// collect unique non-static base models from the full library
	const seen = new Set(STATIC_VALUES);
	const dynamic = [];
	(models || []).forEach((m) => {
		const bm = String(m.base_model || '').trim();
		if (bm && !seen.has(bm)) { seen.add(bm); dynamic.push(bm); }
	});
	dynamic.sort((a, b) => a.localeCompare(b));
	dynamic.forEach((bm) => {
		const opt = document.createElement('option');
		opt.value = bm;
		opt.textContent = bm;
		mbLocalBaseModel.appendChild(opt);
	});
	// restore selected value if still available
	if (Array.from(mbLocalBaseModel.options).some((o) => o.value === currentValue)) {
		mbLocalBaseModel.value = currentValue;
	}
}

function renderLocalLibraryFromState() {
	renderLocalLibrary(mbLibraryAllModels, mbLibraryRoot);
}

function formatReportReason(reason) {
	const raw = String(reason || '').trim();
	if (!raw) return 'unknown';
	return raw.replace(/_/g, ' ');
}

function createReportItem(label, file = '') {
	const itemLabel = String(label || '').trim();
	if (!itemLabel) return null;
	return {
		label: itemLabel,
		file: String(file || '').trim(),
	};
}

function buildReportItemsFromSamples(samples, mapper) {
	if (!Array.isArray(samples)) return [];
	return samples
		.map((sample) => mapper(sample))
		.filter((item) => {
			if (!item) return false;
			if (typeof item === 'object') {
				return Boolean(String(item.label || item.file || '').trim());
			}
			return Boolean(String(item).trim());
		})
		.slice(0, 5);
}

function focusLocalLibraryReportItem(fileName) {
	const targetName = String(fileName || '').trim();
	if (!targetName) return;
	setModelBrowserView('library');
	if (mbLocalQuery) {
		mbLocalQuery.value = targetName;
		localStorage.setItem('mbLocalQuery', targetName);
	}
	if (mbLocalType) {
		mbLocalType.value = '';
		localStorage.setItem('mbLocalType', '');
	}
	if (mbLocalBaseModel) {
		mbLocalBaseModel.value = '';
		localStorage.setItem('mbLocalBaseModel', '');
	}
	if (mbLocalHideEmbeddings) {
		setMbToggleState(mbLocalHideEmbeddings, false);
		localStorage.setItem('mbLocalHideEmbeddings', '0');
	}
	if (mbLocalMatchedOnly) {
		setMbToggleState(mbLocalMatchedOnly, false);
		localStorage.setItem('mbLocalMatchedOnly', '0');
	}
	renderLocalLibraryFromState();
	if (!mbLibraryGrid) return;
	const targetKey = targetName.toLowerCase();
	const targetCard = Array.from(mbLibraryGrid.querySelectorAll('.mb-local-card')).find((card) => (
		String(card.dataset.modelName || '').toLowerCase() === targetKey
	));
	if (!targetCard) {
		if (mbLibraryStatus) {
			mbLibraryStatus.textContent = `Filtered Local Library to report item: ${targetName}`;
			setElementHiddenState(mbLibraryStatus, false);
		}
		return;
	}
	if (mbReportTargetTimer) {
		window.clearTimeout(mbReportTargetTimer);
		mbReportTargetTimer = null;
	}
	mbLibraryGrid.querySelectorAll('.mb-local-card.is-report-target').forEach((card) => {
		card.classList.remove('is-report-target');
	});
	targetCard.classList.add('is-report-target');
	targetCard.scrollIntoView({behavior: 'smooth', block: 'center'});
	targetCard.focus();
	if (mbLibraryStatus) {
		mbLibraryStatus.textContent = `Focused report item in Local Library: ${targetName}`;
		setElementHiddenState(mbLibraryStatus, false);
	}
	mbReportTargetTimer = window.setTimeout(() => {
		targetCard.classList.remove('is-report-target');
		mbReportTargetTimer = null;
	}, 2200);
}

function renderLocalLibraryActionReport(title, summary, groups = []) {
	if (!mbLibraryActionReport) return;
	if (!summary && (!Array.isArray(groups) || !groups.length)) {
		setElementHiddenState(mbLibraryActionReport, true);
		return;
	}
	const groupMarkup = (Array.isArray(groups) ? groups : [])
		.filter((group) => group && group.label && Array.isArray(group.items) && group.items.length)
		.map((group) => {
			const items = group.items.map((item) => {
				if (item && typeof item === 'object') {
					const label = String(item.label || item.file || '').trim();
					const file = String(item.file || '').trim();
					if (file) {
						return `<li><button class="mb-library-action-report-link" type="button" data-report-file="${escHtml(file)}">${escHtml(label)}</button></li>`;
					}
					return `<li>${escHtml(label)}</li>`;
				}
				return `<li>${escHtml(String(item || ''))}</li>`;
			}).join('');
			return `
				<div class="mb-library-action-report-group">
					<div class="mb-library-action-report-label">${escHtml(String(group.label || ''))}</div>
					<ul class="mb-library-action-report-list">${items}</ul>
				</div>`;
		}).join('');
	mbLibraryActionReport.innerHTML = `
		<div class="mb-library-action-report-head">
			<button class="btn btn-ghost btn-xs" id="mb-library-action-report-clear" type="button">Clear Report</button>
		</div>
		<p class="mb-library-action-report-title">${escHtml(String(title || 'Local library action'))}</p>
		<p class="mb-library-action-report-summary">${escHtml(String(summary || ''))}</p>
		${groupMarkup}`;
	const clearBtn = document.getElementById('mb-library-action-report-clear');
	if (clearBtn) {
		clearBtn.addEventListener('click', () => renderLocalLibraryActionReport('', '', []));
	}
	mbLibraryActionReport.querySelectorAll('.mb-library-action-report-link').forEach((button) => {
		button.addEventListener('click', () => focusLocalLibraryReportItem(button.dataset.reportFile || ''));
	});
	setElementHiddenState(mbLibraryActionReport, false);
}

function renderLocalLibrary(models, root) {
	if (!mbLibraryGrid) return;
	mbLibraryGrid.innerHTML = '';
	mbLocalInstalledNames = new Set((models || []).map((m) => String(m.name || '').toLowerCase()));
	refreshLocalBaseModelOptions(models);
	if (models.length === 0) {
		if (mbLibraryStatus) {
			mbLibraryStatus.textContent = root ? 'No models found in ' + root : 'ComfyUI path not configured — set it on the Configurations tab.';
			setElementHiddenState(mbLibraryStatus, false);
		}
		return;
	}
	const displayModels = applyLocalLibraryClientFilters(models);
	if (!displayModels.length) {
		if (mbLibraryStatus) {
			mbLibraryStatus.textContent = 'No local files match your filters.';
			setElementHiddenState(mbLibraryStatus, false);
		}
		return;
	}
	if (mbLibraryStatus) {
		mbLibraryStatus.textContent = `Showing ${displayModels.length} of ${models.length} local files`;
		setElementHiddenState(mbLibraryStatus, false);
	}
	displayModels.forEach(m => {
		const card = document.createElement('div');
		card.className = 'mb-result-card mb-local-card';
		card.dataset.modelName = String(m.name || '');
		card.setAttribute('role', 'button');
		card.setAttribute('tabindex', '0');
		card.setAttribute('aria-label', `Open local model ${m.name || 'details'}`);
		const previewUrls = Array.isArray(m.preview_urls)
			? m.preview_urls.map((url) => String(url || '').trim()).filter(Boolean)
			: [];
		const cardPreviewUrls = previewUrls.slice();
		if (m.preview_url && !cardPreviewUrls.includes(String(m.preview_url))) {
			cardPreviewUrls.unshift(String(m.preview_url));
		}
		const activePreview = cardPreviewUrls[0] || '';
		const thumb = activePreview
			? `<img class="mb-result-thumb" src="${escHtml(activePreview)}" alt="" loading="lazy" data-preview-main="1">`
			: '<div class="mb-result-thumb-placeholder" role="img" aria-label="No preview available"><span class="mb-result-thumb-placeholder-badge">Local model</span></div>';
		const previewStrip = cardPreviewUrls.length > 1
			? `<div class="mb-local-card-preview-strip">${cardPreviewUrls.slice(0, 6).map((url, idx) => (`<button class="mb-local-card-preview-thumb ${idx === 0 ? 'is-active' : ''}" type="button" data-preview-src="${escHtml(url)}" aria-label="Show preview ${idx + 1}"><img src="${escHtml(url)}" alt="" loading="lazy"></button>`)).join('')}</div>`
			: '';
		const sizeLabel = formatBytes(m.size_bytes);
		const filePath = String(m.path || '');
		const versionLabel = String(m.version_name || '').trim();
		card.innerHTML = `
			${thumb}
			${previewStrip}
			<div class="mb-result-body">
				<div class="mb-result-name-row">
					<div class="mb-result-name" title="${escHtml(m.name)}">${escHtml(m.name)}</div>
				</div>
				<div class="mb-result-meta">
					<span class="mb-result-type-chip">Local</span>
					<span class="mb-result-type-chip">${escHtml(m.type || m.folder || 'Model')}</span>
					${m.base_model ? `<span>${escHtml(m.base_model)}</span>` : ''}
					<span>${escHtml(sizeLabel)}</span>
				</div>
				${versionLabel ? `<div class="mb-local-card-version" title="Matched provider version">Matched version: ${escHtml(versionLabel)}</div>` : ''}
				${filePath ? `<div class="mb-result-version" title="${escHtml(filePath)}">${escHtml(filePath)}</div>` : ''}
				<div class="mb-local-card-actions">
					<button class="btn btn-sm btn-ghost mb-use-image-btn" data-name="${escHtml(m.name || '')}" data-type="${escHtml(m.type || '')}" data-folder="${escHtml(m.folder || '')}">Use in Image Gen</button>
					<button class="btn btn-sm btn-danger mb-delete-btn" data-name="${escHtml(m.name)}" data-folder="${escHtml(m.folder)}">Delete</button>
				</div>
			</div>`;
		mbLibraryGrid.appendChild(card);
		card.addEventListener('click', (event) => {
			const target = event.target;
			if (!(target instanceof HTMLElement)) return;
			if (target.closest('.mb-delete-btn')) return;
			openLocalModelDetailsModal(m);
		});
		card.addEventListener('keydown', (event) => {
			if (event.key !== 'Enter' && event.key !== ' ') return;
			event.preventDefault();
			openLocalModelDetailsModal(m);
		});
		card.querySelectorAll('.mb-local-card-preview-thumb').forEach((thumbBtn) => {
			thumbBtn.addEventListener('click', (event) => {
				event.preventDefault();
				event.stopPropagation();
				const targetSrc = String(thumbBtn.dataset.previewSrc || '').trim();
				if (!targetSrc) return;
				const mainPreview = card.querySelector('[data-preview-main="1"]');
				if (mainPreview instanceof HTMLImageElement) {
					mainPreview.src = targetSrc;
				}
				card.querySelectorAll('.mb-local-card-preview-thumb').forEach((node) => node.classList.remove('is-active'));
				thumbBtn.classList.add('is-active');
			});
		});
	});
	mbLibraryGrid.querySelectorAll('.mb-delete-btn').forEach(btn => {
		btn.addEventListener('click', () => deleteLocalModel(btn.dataset.name, btn.dataset.folder, btn));
	});
	mbLibraryGrid.querySelectorAll('.mb-use-image-btn').forEach((btn) => {
		btn.addEventListener('click', (event) => {
			event.stopPropagation();
			useModelInImageGen({
				name: btn.dataset.name || '',
				type: btn.dataset.type || '',
				folder: btn.dataset.folder || '',
			});
		});
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
	const requestId = ++mbSearchRequestSeq;
	if (mbSearchAbortController) {
		mbSearchAbortController.abort();
	}
	const controller = new AbortController();
	mbSearchAbortController = controller;
	const { signal } = controller;
	let timeoutHandle = null;
	let searchTimedOut = false;
	mbSearchCancelRequested = false;
	mbSearchInFlight = true;
	updateModelSearchControls();
	const provider = mbProvider ? String(mbProvider.value || 'civitai') : 'civitai';
	const query = mbSearchQuery ? mbSearchQuery.value.trim() : '';
	const type  = mbSearchType  ? mbSearchType.value : '';
	const baseModel = mbBaseModel ? mbBaseModel.value.trim() : '';
	const showNsfw = mbToggleIsOn(mbShowNsfwToggle);
	const sortLabel = getMbServerSortLabel();
	const isQueryMode = provider === 'civitai' && Boolean(query);
	mbCurrentPage = page || 1;
	if (mbCurrentPage <= 1) {
		mbCursorByPage = { 1: '' };
	}
	updatePagination();
	setModelSearchStatus(provider === 'huggingface' ? 'Searching Hugging Face…' : 'Searching CivitAI…', true);
	if (mbResultsCount) mbResultsCount.textContent = '';
	mbResultsGrid.innerHTML = '';
	setElementHiddenState(mbResultsSection, false);
	try {
		timeoutHandle = setTimeout(() => {
			if (requestId !== mbSearchRequestSeq) return;
			searchTimedOut = true;
			controller.abort();
		}, MB_SEARCH_TIMEOUT_MS);
		const params = new URLSearchParams({page: mbCurrentPage});
		params.set('limit', String(getMbPageSize()));
		if (query) params.set('query', query);
		if (type)  params.set('type', type);
		if (provider === 'civitai' && baseModel) params.set('base_model', baseModel);
		params.set('sort', sortLabel);
		if (provider === 'civitai') params.set('nsfw', showNsfw ? 'true' : 'false');
		if (isQueryMode) {
			const cursor = mbCursorByPage[mbCurrentPage] || '';
			if (cursor) params.set('cursor', cursor);
		}
		const endpoint = provider === 'huggingface' ? '/api/models/huggingface/search?' : '/api/models/civitai/search?';
		const resp = await fetch(endpoint + params.toString(), { signal });
		const data = await resp.json();
		if (requestId !== mbSearchRequestSeq) return;
		if (!resp.ok) throw new Error(data.error || resp.statusText);
		mbQueryMode = isQueryMode;
		mbTotalPages = data.total_pages || 1;
		mbHasNextPage = Boolean(data.has_next);
		if (mbQueryMode) {
			if (data.next_cursor) {
				mbCursorByPage[mbCurrentPage + 1] = data.next_cursor;
			} else {
				delete mbCursorByPage[mbCurrentPage + 1];
			}
			Object.keys(mbCursorByPage).forEach((k) => {
				const n = Number(k);
				if (!Number.isNaN(n) && n > mbCurrentPage + 1) {
					delete mbCursorByPage[n];
				}
			});
		} else {
			mbHasNextPage = mbCurrentPage < mbTotalPages;
			mbCursorByPage = { 1: '' };
		}
		mbLastSearchItems = data.items || [];
		const hasProviderTotal = Object.prototype.hasOwnProperty.call(data || {}, 'total_items');
		renderSearchResults(mbLastSearchItems, data.total_items, hasProviderTotal);
	} catch (err) {
		if (requestId !== mbSearchRequestSeq) return;
		if (err && err.name === 'AbortError') {
			if (mbSearchCancelRequested) {
				setModelSearchStatus('Search cancelled.', true);
				setElementHiddenState(mbPagination, true);
				mbHasNextPage = false;
				return;
			}
			if (searchTimedOut) {
				mbHasNextPage = false;
				setElementHiddenState(mbPagination, true);
				setModelSearchStatus(`Search timed out after ${Math.round(MB_SEARCH_TIMEOUT_MS / 1000)}s. Please try again.`, true);
			}
			return;
		}
		mbHasNextPage = false;
		setElementHiddenState(mbPagination, true);
		setModelSearchStatus('Search failed: ' + err.message, true);
	} finally {
		if (timeoutHandle) {
			clearTimeout(timeoutHandle);
		}
		if (requestId === mbSearchRequestSeq) {
			mbSearchInFlight = false;
			mbSearchCancelRequested = false;
			mbSearchAbortController = null;
			updateModelSearchControls();
			updatePagination();
		}
	}
}

function renderSearchResults(items, totalItems, hasProviderTotal = false) {
	if (!mbResultsGrid) return;
	mbResultsGrid.innerHTML = '';
	setModelSearchStatus('', false);
	setElementHiddenState(mbPagination, false);
	const displayItems = applyModelBrowserClientFilters(items || []);
	if (mbResultsCount) {
		const shown = displayItems.length.toLocaleString();
		if (totalItems != null) {
			mbResultsCount.textContent = `(${shown} shown / ${totalItems.toLocaleString()} total)`;
		} else if (hasProviderTotal) {
			mbResultsCount.textContent = `(${shown} shown - total unavailable)`;
		} else {
			mbResultsCount.textContent = `(${shown} shown)`;
		}
	}
	if (displayItems.length === 0) {
		mbResultsGrid.innerHTML = '<p class="mb-library-status">No results found.</p>';
		updatePagination();
		return;
	}
	displayItems.forEach(item => {
		const installed = modelIsInstalled(item);
		const provider = String(item.provider || '').toLowerCase();
		const card = document.createElement('div');
		card.className = 'mb-result-card';
		card.dataset.modelId = String(item.id || '');
		card.setAttribute('role', 'button');
		card.setAttribute('tabindex', '0');
		card.setAttribute('aria-label', `Open model ${item.name || 'details'}`);
		const thumb = item.preview_url
			? `<img class="mb-result-thumb" src="${escHtml(item.preview_url)}" alt="" loading="lazy">`
			: `<div class="mb-result-thumb-placeholder" role="img" aria-label="No preview available"><span class="mb-result-thumb-placeholder-badge">No preview</span></div>`;
		const sourceLink = item.model_url
			? `<a class="mb-result-source-link" href="${escHtml(item.model_url)}" target="_blank" rel="noopener noreferrer" title="Open on source site" aria-label="Open on source site">↗</a>`
			: '';
		card.innerHTML = `
			${thumb}
			<div class="mb-result-body">
				<div class="mb-result-name-row">
					<div class="mb-result-name" title="${escHtml(item.name)}">${escHtml(item.name)}</div>
					${sourceLink}
				</div>
				<div class="mb-result-meta">
					${item.provider ? `<span class="mb-result-type-chip">${escHtml(item.provider)}</span>` : ''}
					<span class="mb-result-type-chip">${escHtml(item.type || '')}</span>
					${item.base_model ? `<span>${escHtml(item.base_model)}</span>` : ''}
					${item.rating != null ? `<span>&#9733; ${item.rating.toFixed(1)}</span>` : ''}
					${item.likes != null ? `<span>❤ ${Number(item.likes).toLocaleString()}</span>` : ''}
					${item.download_count != null ? `<span>${item.download_count.toLocaleString()} downloads</span>` : ''}
					${installed ? '<span>Installed</span>' : ''}
					${item.is_early_access ? '<span>Early access</span>' : ''}
				</div>
				${item.version_name ? `<div class="mb-result-version">v: ${escHtml(item.version_name)}</div>` : ''}
			</div>`;
		mbResultsGrid.appendChild(card);
		card.addEventListener('click', (event) => {
			const target = event.target;
			if (!(target instanceof HTMLElement)) return;
			if (target.closest('.mb-result-source-link')) return;
			openModelDetailsModal(item);
		});
		card.addEventListener('keydown', (event) => {
			if (event.key !== 'Enter' && event.key !== ' ') return;
			event.preventDefault();
			openModelDetailsModal(item);
		});
	});
	updatePagination();
}

function updatePagination() {
	if (mbPrevPage) {
		mbPrevPage.disabled = mbSearchInFlight || mbCurrentPage <= 1;
	}
	if (mbNextPage) {
		mbNextPage.disabled = mbSearchInFlight || (mbQueryMode ? !mbHasNextPage : (mbCurrentPage >= mbTotalPages));
	}
	if (mbPageInfo) {
		mbPageInfo.textContent = mbQueryMode
			? (mbHasNextPage ? `Page ${mbCurrentPage} (more available)` : `Page ${mbCurrentPage}`)
			: `Page ${mbCurrentPage} of ${mbTotalPages}`;
	}
}

async function startModelDownload(url, fileName, folder, btn, provider = 'civitai', modelId = '', versionName = '', modelName = '', modelType = '', baseModel = '', modelUrl = '', previewUrl = '') {
	if (!url && String(provider || '').toLowerCase() !== 'huggingface') return;
	if (btn) btn.disabled = true;
	try {
		const resp = await fetch('/api/models/download', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({
				url,
				file_name: fileName,
				folder,
				provider,
				model_id: modelId,
				model_name: modelName,
				model_type: modelType,
				base_model: baseModel,
				model_url: modelUrl,
				preview_url: previewUrl,
			})
		});
		const data = await resp.json();
		if (!resp.ok) throw new Error(data.error || resp.statusText);
		setElementHiddenState(mbDownloadsSection, false);
		if (data.download_id) {
			addDownloadRow(data.download_id, data.file_name || fileName);
		}
		if (btn && btn.classList.contains('mb-model-modal-download-btn')) {
			const label = data.file_name || fileName || 'file';
			const versionLabel = versionName || 'selected version';
			setModelModalDownloadStatus(`Queued ${label} from ${versionLabel}.`, 'ok');
		}
		ensureDownloadPoll();
	} catch (err) {
		if (btn && btn.classList.contains('mb-model-modal-download-btn')) {
			const versionLabel = versionName || 'selected version';
			setModelModalDownloadStatus(`Failed to queue download for ${versionLabel}: ${err.message}`, 'error');
		}
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

function setDownloadsMinimized(minimized) {
	mbDownloadsMinimized = Boolean(minimized);
	if (mbDownloadsSection) {
		mbDownloadsSection.classList.toggle('is-minimized', mbDownloadsMinimized);
	}
	if (mbDownloadsBody) {
		mbDownloadsBody.hidden = mbDownloadsMinimized;
		mbDownloadsBody.setAttribute('aria-hidden', mbDownloadsMinimized ? 'true' : 'false');
	}
	if (mbDownloadsToggleBtn) {
		mbDownloadsToggleBtn.textContent = mbDownloadsMinimized ? 'Expand' : 'Minimize';
		mbDownloadsToggleBtn.setAttribute('aria-expanded', mbDownloadsMinimized ? 'false' : 'true');
	}
}

function onModelDownloadsActionsKeydown(event) {
	const key = event.key;
	if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
	const actions = [mbClearFinishedDownloadsBtn, mbDownloadsToggleBtn].filter(Boolean);
	if (actions.length < 2) return;
	const currentIndex = actions.indexOf(event.currentTarget);
	if (currentIndex < 0) return;
	event.preventDefault();
	let nextIndex = currentIndex;
	if (key === 'Home') {
		nextIndex = 0;
	} else if (key === 'End') {
		nextIndex = actions.length - 1;
	} else if (key === 'ArrowRight') {
		nextIndex = (currentIndex + 1) % actions.length;
	} else if (key === 'ArrowLeft') {
		nextIndex = (currentIndex - 1 + actions.length) % actions.length;
	}
	const nextAction = actions[nextIndex];
	if (nextAction) nextAction.focus();
}

function updateDownloadControlsState() {
	if (!mbDownloadsList) return;
	const rows = mbDownloadsList.querySelectorAll('[data-dl-id]');
	const activeCount = Array.from(rows).filter((row) => {
		const status = String(row.dataset.status || '').toLowerCase();
		return status === 'downloading' || status === 'cancelling';
	}).length;
	const pendingCount = Array.from(rows).filter((row) => {
		const status = String(row.dataset.status || '').toLowerCase();
		return status === 'queued';
	}).length;
	if (mbClearFinishedDownloadsBtn) {
		const hasFinished = Array.from(rows).some((row) =>
			row.classList.contains('is-done') ||
			row.classList.contains('is-error') ||
			row.classList.contains('is-cancelled'));
		mbClearFinishedDownloadsBtn.disabled = !hasFinished;
	}
	if (mbDownloadsCounter) {
		const hasInFlight = (activeCount + pendingCount) > 0;
		const hasActiveTransfer = activeCount > 0;
		mbDownloadsCounter.textContent = hasInFlight
			? `${activeCount} active • ${pendingCount} pending`
			: 'Idle';
		mbDownloadsCounter.classList.toggle('is-busy', hasInFlight);
		mbDownloadsCounter.classList.toggle('is-active', hasActiveTransfer);
		setElementHiddenState(mbDownloadsCounter, !mbDownloadsMinimized);
	}
	if (mbDownloadsSection) {
		setElementHiddenState(mbDownloadsSection, rows.length === 0);
	}
}

function clearFinishedDownloadRows() {
	if (!mbDownloadsList) return;
	const rows = mbDownloadsList.querySelectorAll('[data-dl-id]');
	rows.forEach((row) => {
		if (
			row.classList.contains('is-done') ||
			row.classList.contains('is-error') ||
			row.classList.contains('is-cancelled')
		) {
			row.remove();
		}
	});
	updateDownloadControlsState();
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
	row.dataset.status = 'queued';
	row.innerHTML = `
		<div class="mb-download-row-head">
			<span class="mb-download-name">${escHtml(fileName)}</span>
			<span class="mb-download-status">queued</span>
			<button class="btn btn-sm mb-cancel-dl-btn" data-id="${escHtml(downloadId)}">Cancel</button>
		</div>
		<div class="mb-progress"><div class="mb-progress-bar" style="width:0%"></div></div>`;
	mbDownloadsList.appendChild(row);
	row.querySelector('.mb-cancel-dl-btn').addEventListener('click', () => cancelDownload(downloadId, row));
	updateDownloadControlsState();
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
	if (statusEl) {
		let statusText = '';
		if (state.status === 'downloading') {
			statusText = `${state.downloaded_bytes != null ? formatBytes(state.downloaded_bytes) : ''}${state.total_bytes ? ' / ' + formatBytes(state.total_bytes) : ''}`;
		} else if (state.status === 'error') {
			const reason = String(state.error || '').trim();
			statusText = reason ? `error: ${reason}` : 'error';
		} else {
			statusText = state.status;
		}
		statusEl.textContent = statusText;
		statusEl.title = statusText;
	}
	row.dataset.status = String(state.status || '').toLowerCase();
	const pct = state.total_bytes && state.total_bytes > 0 ? (state.downloaded_bytes / state.total_bytes) * 100 : 0;
	if (bar) bar.style.width = pct.toFixed(1) + '%';
	row.classList.toggle('is-done',      state.status === 'done');
	row.classList.toggle('is-error',     state.status === 'error');
	row.classList.toggle('is-cancelled', state.status === 'cancelled');
	if (cancelBtn) {
		const showCancel = state.status === 'downloading';
		cancelBtn.hidden = !showCancel;
		cancelBtn.style.display = showCancel ? '' : 'none';
	}
	if (state.status === 'done') loadModelLibrary();
	updateDownloadControlsState();
}

async function cancelDownload(downloadId, row) {
	const cancelBtn = row ? row.querySelector('.mb-cancel-dl-btn') : null;
	const statusEl = row ? row.querySelector('.mb-download-status') : null;
	if (cancelBtn) {
		cancelBtn.disabled = true;
		cancelBtn.hidden = true;
		cancelBtn.style.display = 'none';
	}
	if (row) row.dataset.status = 'cancelling';
	if (statusEl) {
		statusEl.textContent = 'cancelling...';
		statusEl.title = 'cancelling...';
	}
	try {
		const resp = await fetch('/api/models/download/' + encodeURIComponent(downloadId) + '/cancel', {method: 'POST'});
		if (!resp.ok) throw new Error('cancel failed');
		if (row) row.classList.add('is-cancelled');
		if (row) row.dataset.status = 'cancelled';
		if (statusEl) {
			statusEl.textContent = 'cancelled';
			statusEl.title = 'cancelled';
		}
	} catch (_) {
		if (cancelBtn) {
			cancelBtn.disabled = false;
			cancelBtn.hidden = false;
			cancelBtn.style.display = '';
		}
		if (statusEl) {
			statusEl.textContent = 'cancel failed';
			statusEl.title = 'cancel failed';
		}
		if (row) row.dataset.status = 'error';
	}
	updateDownloadControlsState();
}

// Wire model browser events
function rerunModelBrowserSearchIfVisible() {
	if (mbActiveView === 'search' && mbResultsSection && !mbResultsSection.hidden) {
		runCivitaiSearch(1);
	}
}

if (mbViewSearchBtn) {
	mbViewSearchBtn.addEventListener('click', () => setModelBrowserView('search'));
	mbViewSearchBtn.addEventListener('keydown', onModelBrowserViewTabKeydown);
}
if (mbViewLibraryBtn) {
	mbViewLibraryBtn.addEventListener('click', () => setModelBrowserView('library'));
	mbViewLibraryBtn.addEventListener('keydown', onModelBrowserViewTabKeydown);
}

if (mbSearchBtn) {
	mbSearchBtn.addEventListener('click', () => runCivitaiSearch(1));
}
if (mbCancelSearchBtn) {
	mbCancelSearchBtn.addEventListener('click', cancelModelSearch);
}
if (mbSearchBulkRefreshInstalledBtn) {
	mbSearchBulkRefreshInstalledBtn.addEventListener('click', bulkUpdateInstalledSearchMetadata);
}
updateModelSearchControls();
if (mbSearchQuery) {
	mbSearchQuery.addEventListener('input', () => {
		localStorage.setItem('mbSearchQuery', mbSearchQuery.value || '');
	});
	mbSearchQuery.addEventListener('keydown', (e) => {
		if (e.key === 'Escape') return onModelSearchControlKeydown(e);
		if (e.key === 'Enter') runCivitaiSearch(1);
	});
}
if (mbSearchType) {
	mbSearchType.addEventListener('keydown', onModelSearchControlKeydown);
	mbSearchType.addEventListener('change', () => {
		localStorage.setItem('mbSearchType', mbSearchType.value || '');
		rerunModelBrowserSearchIfVisible();
	});
}
if (mbProvider) {
	mbProvider.addEventListener('keydown', onModelSearchControlKeydown);
	mbProvider.addEventListener('change', () => {
		localStorage.setItem('mbProvider', mbProvider.value || 'civitai');
		applyModelBrowserProviderFilters();
		rerunModelBrowserSearchIfVisible();
	});
}
if (mbBaseModel) {
	mbBaseModel.addEventListener('keydown', onModelSearchControlKeydown);
	mbBaseModel.addEventListener('change', () => {
		localStorage.setItem('mbBaseModel', mbBaseModel.value || '');
		rerunModelBrowserSearchIfVisible();
	});
}
if (mbSort) {
	mbSort.addEventListener('keydown', onModelSearchControlKeydown);
	mbSort.addEventListener('change', () => {
		localStorage.setItem('mbSort', mbSort.value || 'highest-rated');
		if ((mbSort.value || '').toString() === 'highest-rated' || (mbSort.value || '').toString() === 'most-downloaded' || (mbSort.value || '').toString() === 'newest') {
			rerunModelBrowserSearchIfVisible();
			return;
		}
		renderSearchResults(mbLastSearchItems, null);
	});
}
if (mbPageSize) {
	mbPageSize.addEventListener('keydown', onModelSearchControlKeydown);
	mbPageSize.addEventListener('change', () => {
		localStorage.setItem('mbPageSize', String(getMbPageSize()));
		rerunModelBrowserSearchIfVisible();
	});
}
if (mbHideInstalledToggle) {
	mbHideInstalledToggle.addEventListener('click', () => {
		setMbToggleState(mbHideInstalledToggle, !mbToggleIsOn(mbHideInstalledToggle));
		if (mbToggleIsOn(mbHideInstalledToggle) && mbShowInstalledOnlyToggle) {
			setMbToggleState(mbShowInstalledOnlyToggle, false);
			localStorage.setItem('mbShowInstalledOnly', '0');
		}
		localStorage.setItem('mbHideInstalled', mbToggleIsOn(mbHideInstalledToggle) ? '1' : '0');
		renderSearchResults(mbLastSearchItems, null);
	});
	mbHideInstalledToggle.addEventListener('keydown', onModelBrowserFilterTogglesKeydown);
}
if (mbShowInstalledOnlyToggle) {
	mbShowInstalledOnlyToggle.addEventListener('click', () => {
		setMbToggleState(mbShowInstalledOnlyToggle, !mbToggleIsOn(mbShowInstalledOnlyToggle));
		if (mbToggleIsOn(mbShowInstalledOnlyToggle) && mbHideInstalledToggle) {
			setMbToggleState(mbHideInstalledToggle, false);
			localStorage.setItem('mbHideInstalled', '0');
		}
		localStorage.setItem('mbShowInstalledOnly', mbToggleIsOn(mbShowInstalledOnlyToggle) ? '1' : '0');
		renderSearchResults(mbLastSearchItems, null);
	});
	mbShowInstalledOnlyToggle.addEventListener('keydown', onModelBrowserFilterTogglesKeydown);
}
if (mbHideEarlyAccessToggle) {
	mbHideEarlyAccessToggle.addEventListener('click', () => {
		setMbToggleState(mbHideEarlyAccessToggle, !mbToggleIsOn(mbHideEarlyAccessToggle));
		localStorage.setItem('mbHideEarlyAccess', mbToggleIsOn(mbHideEarlyAccessToggle) ? '1' : '0');
		renderSearchResults(mbLastSearchItems, null);
	});
	mbHideEarlyAccessToggle.addEventListener('keydown', onModelBrowserFilterTogglesKeydown);
}
if (mbShowNsfwToggle) {
	mbShowNsfwToggle.addEventListener('click', () => {
		setMbToggleState(mbShowNsfwToggle, !mbToggleIsOn(mbShowNsfwToggle));
		localStorage.setItem('mbShowNsfw', mbToggleIsOn(mbShowNsfwToggle) ? '1' : '0');
		rerunModelBrowserSearchIfVisible();
	});
	mbShowNsfwToggle.addEventListener('keydown', onModelBrowserFilterTogglesKeydown);
}
let mbTypeInfoLastFocus = null;
function setMbTypeInfoPanelOpen(isOpen) {
	if (!mbTypeInfoBtn || !mbTypeInfoPanel) return;
	if (isOpen) {
		mbTypeInfoLastFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
	}
	mbTypeInfoPanel.hidden = !isOpen;
	mbTypeInfoPanel.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
	mbTypeInfoBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
	if (isOpen) {
		mbTypeInfoPanel.focus();
		return;
	}
	if (mbTypeInfoLastFocus && document.contains(mbTypeInfoLastFocus)) {
		mbTypeInfoLastFocus.focus();
	}
	mbTypeInfoLastFocus = null;
}
if (mbTypeInfoBtn && mbTypeInfoPanel) {
	mbTypeInfoBtn.addEventListener('click', () => {
		setMbTypeInfoPanelOpen(mbTypeInfoPanel.hidden);
	});
	mbTypeInfoBtn.addEventListener('keydown', (event) => {
		if (event.key === 'ArrowDown') {
			event.preventDefault();
			setMbTypeInfoPanelOpen(true);
		} else if (event.key === 'Escape' && mbTypeInfoBtn.getAttribute('aria-expanded') === 'true') {
			event.preventDefault();
			setMbTypeInfoPanelOpen(false);
		}
	});
	mbTypeInfoPanel.addEventListener('keydown', (event) => {
		if (event.key === 'Escape' && !mbTypeInfoPanel.hidden) {
			event.preventDefault();
			setMbTypeInfoPanelOpen(false);
		}
	});
	mbTypeInfoPanel.setAttribute('aria-hidden', mbTypeInfoPanel.hidden ? 'true' : 'false');
}
if (mbLibraryRefreshBtn) {
	mbLibraryRefreshBtn.addEventListener('click', loadModelLibrary);
}
if (mbLibraryEnrichPreviewsBtn) {
	mbLibraryEnrichPreviewsBtn.addEventListener('click', enrichLocalLibraryPreviews);
}
if (mbLibraryRecoverMetadataBtn) {
	mbLibraryRecoverMetadataBtn.addEventListener('click', recoverLocalLibraryMetadataAndPreviews);
}
if (mbCompareProviderCivitai) {
	mbCompareProviderCivitai.addEventListener('change', () => {
		localStorage.setItem('mbCompareProviderCivitai', mbCompareProviderCivitai.checked ? '1' : '0');
	});
}
if (mbCompareProviderHuggingface) {
	mbCompareProviderHuggingface.addEventListener('change', () => {
		localStorage.setItem('mbCompareProviderHuggingface', mbCompareProviderHuggingface.checked ? '1' : '0');
	});
}
if (mbLibraryCompareMetadataBtn) {
	mbLibraryCompareMetadataBtn.addEventListener('click', compareLocalLibraryMetadata);
}
if (mbResetFiltersBtn) {
	mbResetFiltersBtn.addEventListener('click', () => {
		resetModelBrowserFilters();
		setModelBrowserResetStatus('Defaults restored.');
		showToast('Model browser filters reset to defaults.', 'pos');
	});
}
if (mbLocalQuery) {
	mbLocalQuery.addEventListener('input', () => {
		localStorage.setItem('mbLocalQuery', mbLocalQuery.value || '');
		renderLocalLibraryFromState();
	});
}
if (mbLocalType) {
	mbLocalType.addEventListener('change', () => {
		localStorage.setItem('mbLocalType', mbLocalType.value || '');
		renderLocalLibraryFromState();
	});
}
if (mbLocalBaseModel) {
	mbLocalBaseModel.addEventListener('change', () => {
		localStorage.setItem('mbLocalBaseModel', mbLocalBaseModel.value || '');
		renderLocalLibraryFromState();
	});
}
if (mbLocalSort) {
	mbLocalSort.addEventListener('change', () => {
		localStorage.setItem('mbLocalSort', mbLocalSort.value || 'name-asc');
		renderLocalLibraryFromState();
	});
}
if (mbLocalHideEmbeddings) {
	mbLocalHideEmbeddings.addEventListener('click', () => {
		setMbToggleState(mbLocalHideEmbeddings, !mbToggleIsOn(mbLocalHideEmbeddings));
		localStorage.setItem('mbLocalHideEmbeddings', mbToggleIsOn(mbLocalHideEmbeddings) ? '1' : '0');
		renderLocalLibraryFromState();
	});
	mbLocalHideEmbeddings.addEventListener('keydown', onLocalLibraryQuickFiltersKeydown);
}
if (mbLocalMatchedOnly) {
	mbLocalMatchedOnly.addEventListener('click', () => {
		setMbToggleState(mbLocalMatchedOnly, !mbToggleIsOn(mbLocalMatchedOnly));
		localStorage.setItem('mbLocalMatchedOnly', mbToggleIsOn(mbLocalMatchedOnly) ? '1' : '0');
		renderLocalLibraryFromState();
	});
	mbLocalMatchedOnly.addEventListener('keydown', onLocalLibraryQuickFiltersKeydown);
}
if (mbPrevPage) {
	mbPrevPage.addEventListener('click', () => {
		if (mbSearchInFlight) return;
		if (mbCurrentPage > 1) runCivitaiSearch(mbCurrentPage - 1);
	});
	mbPrevPage.addEventListener('keydown', onModelPaginationKeydown);
}
if (mbNextPage) {
	mbNextPage.addEventListener('click', () => {
		if (mbSearchInFlight) return;
		if (mbQueryMode) {
			if (mbHasNextPage) runCivitaiSearch(mbCurrentPage + 1);
			return;
		}
		if (mbCurrentPage < mbTotalPages) runCivitaiSearch(mbCurrentPage + 1);
	});
	mbNextPage.addEventListener('keydown', onModelPaginationKeydown);
}
if (mbClearFinishedDownloadsBtn) {
	mbClearFinishedDownloadsBtn.addEventListener('click', clearFinishedDownloadRows);
	mbClearFinishedDownloadsBtn.addEventListener('keydown', onModelDownloadsActionsKeydown);
}
if (mbDownloadsToggleBtn) {
	mbDownloadsToggleBtn.addEventListener('click', () => {
		setDownloadsMinimized(!mbDownloadsMinimized);
		updateDownloadControlsState();
	});
	mbDownloadsToggleBtn.addEventListener('keydown', onModelDownloadsActionsKeydown);
}
if (mbModelModalClose) {
	mbModelModalClose.addEventListener('click', () => setModelModalOpen(false));
}
if (mbModelModal) {
	mbModelModal.addEventListener('click', (event) => {
		const target = event.target;
		if (!(target instanceof HTMLElement)) return;
		if (target.dataset.mbModalClose === 'backdrop') {
			setModelModalOpen(false);
		}
	});

	mbModelModal.addEventListener('keydown', (event) => {
		if (event.key !== 'Tab' || mbModelModal.hidden) return;
		const tabStops = getModelModalTabStops();
		if (!tabStops.length) return;
		const first = tabStops[0];
		const last = tabStops[tabStops.length - 1];
		const active = document.activeElement;
		if (event.shiftKey) {
			if (active === first || !mbModelModal.contains(active)) {
				event.preventDefault();
				last.focus();
			}
			return;
		}
		if (active === last || !mbModelModal.contains(active)) {
			event.preventDefault();
			first.focus();
		}
	});
}
if (mbModelModalVersion) {
	mbModelModalVersion.addEventListener('change', () => {
		if (!mbCurrentModelDetails || !Array.isArray(mbCurrentModelDetails.versions)) return;
		mbCurrentVersionIndex = Number(mbModelModalVersion.value || 0);
		const selected = mbCurrentModelDetails.versions[mbCurrentVersionIndex];
		if (selected) renderModelVersionDetails(selected);
	});
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

// --- Prompt Recent History & Saved Presets ---
const PROMPT_RECENT_MAX = 20;
const PROMPT_RECENT_KEY = 'promptRecentHistory';
const PROMPT_SAVED_KEY = 'promptSavedPresets';
const PROMPT_SAVED_FAVORITES_ONLY_KEY = 'promptSavedFavoritesOnlyV1';
const PROMPT_RECENT_CHIPS_MAX = 8;

function loadPromptRecentHistory() {
	try { return JSON.parse(localStorage.getItem(PROMPT_RECENT_KEY) || '[]'); }
	catch { return []; }
}

function setPromptRecentDropdownOpen(isOpen, focusFirst = false) {
	if (!promptRecentDropdown) return;
	if (isOpen) {
		renderPromptRecentDropdown();
	}
	promptRecentDropdown.hidden = !isOpen;
	promptRecentDropdown.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
	if (promptRecentBtn) {
		promptRecentBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
	}
	if (!isOpen) return;
	if (!focusFirst) return;
	const first = promptRecentDropdown.querySelector('.prompt-recent-item');
	if (first instanceof HTMLElement) {
		first.focus();
	}
}

function applyRecentPromptByIndex(index) {
	const value = loadPromptRecentHistory()[index] || '';
	if (!value) return;
	imagePrompt.value = value;
	imagePrompt.focus();
	setPromptRecentDropdownOpen(false);
}
function saveCurrentPromptToHistory(text) {
	const t = String(text || '').trim();
	if (!t) return;
	let list = loadPromptRecentHistory().filter((p) => p !== t);
	list.unshift(t);
	list = list.slice(0, PROMPT_RECENT_MAX);
	localStorage.setItem(PROMPT_RECENT_KEY, JSON.stringify(list));
	renderPromptRecentDropdown();
	renderPromptRecentChips();
}
function renderPromptRecentDropdown() {
	if (!promptRecentDropdown) return;
	const list = loadPromptRecentHistory();
	if (!list.length) {
		promptRecentDropdown.innerHTML = '<li class="prompt-recent-empty">No recent prompts</li>';
		return;
	}
	promptRecentDropdown.innerHTML = list.map((p, i) => {
		const preview = p.length > 80 ? p.slice(0, 80) + '\u2026' : p;
		return `<li class="prompt-recent-item" data-index="${i}" role="option" tabindex="0">${escHtml(preview)}</li>`;
	}).join('');
	promptRecentDropdown.querySelectorAll('.prompt-recent-item').forEach((li) => {
		const apply = () => {
			applyRecentPromptByIndex(Number(li.dataset.index));
		};
		li.addEventListener('click', apply);
		li.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); apply(); } });
	});
}
function renderPromptRecentChips() {
	if (!promptRecentChips) return;
	const list = loadPromptRecentHistory().slice(0, PROMPT_RECENT_CHIPS_MAX);
	if (!list.length) {
		promptRecentChips.innerHTML = '<span class="hint">No recent prompts yet.</span>';
		if (promptRecentClearBtn) promptRecentClearBtn.disabled = true;
		return;
	}
	promptRecentChips.innerHTML = list.map((p, i) => {
		const preview = p.length > 66 ? `${p.slice(0, 66)}\u2026` : p;
		return `<button class="prompt-recent-chip" type="button" data-index="${i}" title="${escHtml(p)}">${escHtml(preview)}</button>`;
	}).join('');
	if (promptRecentClearBtn) promptRecentClearBtn.disabled = false;
	promptRecentChips.querySelectorAll('.prompt-recent-chip').forEach((btn) => {
		btn.addEventListener('click', () => {
			applyRecentPromptByIndex(Number(btn.dataset.index));
		});
		btn.addEventListener('keydown', onPromptRecentControlsKeydown);
	});
}
function onPromptRecentControlsKeydown(event) {
	const key = event.key;
	if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(key)) return;
	if (!(event.currentTarget instanceof HTMLElement)) return;

	const controls = [];
	if (promptRecentChips) {
		controls.push(...promptRecentChips.querySelectorAll('.prompt-recent-chip'));
	}
	if (promptRecentClearBtn && !promptRecentClearBtn.disabled) {
		controls.push(promptRecentClearBtn);
	}
	if (controls.length < 2) return;

	const currentIndex = controls.indexOf(event.currentTarget);
	if (currentIndex < 0) return;

	event.preventDefault();
	let nextIndex = currentIndex;
	if (key === 'Home') {
		nextIndex = 0;
	} else if (key === 'End') {
		nextIndex = controls.length - 1;
	} else if (key === 'ArrowRight') {
		nextIndex = (currentIndex + 1) % controls.length;
	} else if (key === 'ArrowLeft') {
		nextIndex = (currentIndex - 1 + controls.length) % controls.length;
	}
	controls[nextIndex]?.focus();
}
function _migratePresetV1ToV2(value) {
	if (typeof value === 'string') {
		return { text: value, tags: [], favorite: false, created_at: 0, notes: '' };
	}
	if (value && typeof value === 'object') {
		return {
			text: String(value.text || ''),
			tags: Array.isArray(value.tags) ? value.tags : [],
			favorite: Boolean(value.favorite),
			created_at: Number(value.created_at) || 0,
			notes: String(value.notes || ''),
		};
	}
	return { text: '', tags: [], favorite: false, created_at: 0, notes: '' };
}
function loadPromptSavedPresets() {
	let raw = {};
	try { raw = JSON.parse(localStorage.getItem(PROMPT_SAVED_KEY) || '{}'); }
	catch { raw = {}; }
	const result = {};
	for (const [k, v] of Object.entries(raw)) {
		result[k] = _migratePresetV1ToV2(v);
	}
	return result;
}
function _getActiveTagFilter() {
	return promptTagFilter ? promptTagFilter.value : '';
}
function _getFavoritesOnlyFilter() {
	try { return localStorage.getItem(PROMPT_SAVED_FAVORITES_ONLY_KEY) === '1'; }
	catch { return false; }
}
function _setFavoritesOnlyFilter(enabled) {
	try { localStorage.setItem(PROMPT_SAVED_FAVORITES_ONLY_KEY, enabled ? '1' : '0'); }
	catch {}
	_updateFavoritesOnlyToggleUi();
}
function _updateFavoritesOnlyToggleUi() {
	if (!promptFavoritesOnlyToggle) return;
	const isActive = _getFavoritesOnlyFilter();
	promptFavoritesOnlyToggle.setAttribute('aria-pressed', isActive ? 'true' : 'false');
	promptFavoritesOnlyToggle.classList.toggle('is-active', isActive);
	promptFavoritesOnlyToggle.title = isActive ? 'Showing favorites only' : 'Show favorites only';
}
function _renderPresetFilterStatus(filteredCount, totalCount) {
	if (!promptPresetFilterStatus) return;
	const parts = [];
	const activeTag = _getActiveTagFilter();
	if (_getFavoritesOnlyFilter()) parts.push('favorites');
	if (activeTag) parts.push(`tag:${activeTag}`);
	if (!parts.length) {
		promptPresetFilterStatus.textContent = `No filters active. Showing ${filteredCount}/${totalCount}.`;
		if (promptPresetClearFilters) promptPresetClearFilters.disabled = true;
		return;
	}
	promptPresetFilterStatus.textContent = `Filters: ${parts.join(', ')}. Showing ${filteredCount}/${totalCount}.`;
	if (promptPresetClearFilters) promptPresetClearFilters.disabled = false;
}
function renderPromptSavedSelect() {
	if (!promptSavedSelect) return;
	const presets = loadPromptSavedPresets();
	const totalCount = Object.keys(presets).length;
	const activeTag = _getActiveTagFilter();
	const favoritesOnly = _getFavoritesOnlyFilter();
	let keys = Object.keys(presets).sort((a, b) => {
		const fa = presets[a].favorite ? 0 : 1;
		const fb = presets[b].favorite ? 0 : 1;
		if (fa !== fb) return fa - fb;
		return a.localeCompare(b);
	});
	if (favoritesOnly) {
		keys = keys.filter((k) => presets[k].favorite);
	}
	if (activeTag) {
		keys = keys.filter((k) => presets[k].tags.includes(activeTag));
	}
	if (!keys.length) {
		promptSavedSelect.innerHTML = '<option value="">No saved prompts</option>';
		renderPresetTagChips('');
		renderPresetNotesPreview('');
		_renderPresetFilterStatus(0, totalCount);
		return;
	}
	promptSavedSelect.innerHTML = keys.map((k) => {
		const starPrefix = presets[k].favorite ? '\u2605 ' : '';
		return `<option value="${escHtml(k)}">${escHtml(starPrefix + k)}</option>`;
	}).join('');
	renderPresetTagChips(keys[0]);
	renderPresetNotesPreview(keys[0]);
	_renderPresetFilterStatus(keys.length, totalCount);
}
function renderPresetTagChips(name) {
	if (!promptPresetTagChips) return;
	const n = String(name || '').trim();
	if (!n) { promptPresetTagChips.innerHTML = ''; return; }
	const presets = loadPromptSavedPresets();
	const preset = presets[n];
	if (!preset || !preset.tags.length) { promptPresetTagChips.innerHTML = ''; return; }
	const activeTag = _getActiveTagFilter();
	promptPresetTagChips.innerHTML = preset.tags.map((t) =>
		`<button class="preset-tag-chip preset-tag-chip-btn${activeTag === t ? ' is-active' : ''}" data-tag="${escHtml(t)}" type="button" title="Filter presets by tag ${escHtml(t)}">${escHtml(t)}</button>`
	).join('');
}
function renderPresetNotesPreview(name) {
	if (!promptPresetNotesPreview) return;
	const n = String(name || '').trim();
	if (!n) { promptPresetNotesPreview.textContent = ''; return; }
	const presets = loadPromptSavedPresets();
	const preset = presets[n];
	const notes = preset ? String(preset.notes || '').trim() : '';
	if (!notes) {
		promptPresetNotesPreview.textContent = '';
		return;
	}
	const compact = notes.replace(/\s+/g, ' ').trim();
	const preview = compact.length > 140 ? `${compact.slice(0, 140)}\u2026` : compact;
	promptPresetNotesPreview.textContent = `Notes: ${preview}`;
}
function refreshPromptTagFilterOptions() {
	if (!promptTagFilter) return;
	const presets = loadPromptSavedPresets();
	const allTags = new Set();
	for (const v of Object.values(presets)) {
		for (const t of v.tags) allTags.add(t);
	}
	const currentVal = promptTagFilter.value;
	const sorted = [...allTags].sort();
	promptTagFilter.innerHTML = '<option value="">All tags</option>' +
		sorted.map((t) => `<option value="${escHtml(t)}"${t === currentVal ? ' selected' : ''}>${escHtml(t)}</option>`).join('');
}
function saveNamedPromptPreset(name, text, tagsRaw) {
	const n = String(name || '').trim();
	const t = String(text || '').trim();
	if (!n || !t) { showToast('Enter a preset name and prompt text.', 'neg'); return; }
	const presets = loadPromptSavedPresets();
	const existing = presets[n];
	const tags = String(tagsRaw || '').split(',').map((s) => s.trim()).filter(Boolean);
	const favorite = existing ? existing.favorite : false;
	const notes = existing ? existing.notes : '';
	presets[n] = { text: t, tags, favorite, created_at: existing ? existing.created_at : Date.now(), notes };
	localStorage.setItem(PROMPT_SAVED_KEY, JSON.stringify(presets));
	refreshPromptTagFilterOptions();
	renderPromptSavedSelect();
	showToast(`Saved prompt preset "${n}".`, 'pos');
}
function togglePresetFavorite(name) {
	const n = String(name || '').trim();
	if (!n) return;
	const presets = loadPromptSavedPresets();
	if (!presets[n]) return;
	presets[n].favorite = !presets[n].favorite;
	localStorage.setItem(PROMPT_SAVED_KEY, JSON.stringify(presets));
	renderPromptSavedSelect();
	const label = presets[n].favorite ? 'Favorited' : 'Unfavorited';
	showToast(`${label} preset "${n}".`, 'pos');
	_updateFavToggleBtn(n, presets[n].favorite);
}
function _updateFavToggleBtn(name, isFav) {
	if (!promptFavToggle) return;
	promptFavToggle.textContent = isFav ? '\u2605' : '\u2606';
	promptFavToggle.title = isFav ? 'Remove from favorites' : 'Add to favorites';
	promptFavToggle.setAttribute('aria-pressed', isFav ? 'true' : 'false');
	promptFavToggle.classList.toggle('is-favorited', Boolean(isFav));
}
function deleteNamedPromptPreset(name) {
	const n = String(name || '').trim();
	if (!n) return;
	const presets = loadPromptSavedPresets();
	delete presets[n];
	localStorage.setItem(PROMPT_SAVED_KEY, JSON.stringify(presets));
	refreshPromptTagFilterOptions();
	renderPromptSavedSelect();
	showToast(`Deleted prompt preset "${n}".`, 'pos');
}

// --- Preset Edit Modal ---
let _presetEditOriginalName = '';

function openPresetEditModal(name) {
	const n = String(name || '').trim();
	if (!n || !presetEditModal) return;
	const presets = loadPromptSavedPresets();
	const preset = presets[n];
	if (!preset) { showToast('Preset not found.', 'neg'); return; }
	_presetEditOriginalName = n;
	if (presetEditName) presetEditName.value = n;
	if (presetEditText) presetEditText.value = preset.text;
	if (presetEditTags) presetEditTags.value = preset.tags.join(', ');
	if (presetEditNotes) presetEditNotes.value = preset.notes || '';
	if (presetEditCreated) {
		const d = preset.created_at ? new Date(preset.created_at).toLocaleString() : 'unknown';
		presetEditCreated.textContent = `Created: ${d}`;
	}
	presetEditModal.hidden = false;
	presetEditModal.setAttribute('aria-hidden', 'false');
	if (presetEditName) presetEditName.focus();
}

function closePresetEditModal() {
	if (!presetEditModal) return;
	presetEditModal.hidden = true;
	presetEditModal.setAttribute('aria-hidden', 'true');
	_presetEditOriginalName = '';
}

function savePresetEditModal() {
	const newName = presetEditName ? presetEditName.value.trim() : '';
	const text = presetEditText ? presetEditText.value.trim() : '';
	const tagsRaw = presetEditTags ? presetEditTags.value : '';
	const notes = presetEditNotes ? presetEditNotes.value.trim() : '';
	if (!newName || !text) { showToast('Name and prompt text are required.', 'neg'); return; }
	const presets = loadPromptSavedPresets();
	const original = _presetEditOriginalName;
	const existing = presets[original];
	if (!existing) { showToast('Preset no longer exists.', 'neg'); closePresetEditModal(); return; }
	if (newName !== original && presets[newName]) {
		const accepted = window.confirm(`Preset "${newName}" already exists. Overwrite it?`);
		if (!accepted) {
			showToast('Rename canceled.', 'neg');
			return;
		}
	}
	const tags = tagsRaw.split(',').map((s) => s.trim()).filter(Boolean);
	const updated = {
		text,
		tags,
		favorite: existing.favorite,
		created_at: existing.created_at,
		notes,
	};
	if (newName !== original) {
		delete presets[original];
	}
	presets[newName] = updated;
	localStorage.setItem(PROMPT_SAVED_KEY, JSON.stringify(presets));
	refreshPromptTagFilterOptions();
	renderPromptSavedSelect();
	if (promptSavedSelect && newName) {
		promptSavedSelect.value = newName;
		renderPresetTagChips(newName);
		renderPresetNotesPreview(newName);
		_updateFavToggleBtn(newName, updated.favorite);
	}
	closePresetEditModal();
	showToast(`Saved preset "${newName}".`, 'pos');
}

// --- Text Prompt Recent History ---
const TEXT_PROMPT_RECENT_KEY = 'textPromptRecentHistory';
const TEXT_PROMPT_RECENT_MAX = 20;
const TEXT_PROMPT_RECENT_CHIPS_MAX = 8;

function loadTextPromptRecentHistory() {
	try { return JSON.parse(localStorage.getItem(TEXT_PROMPT_RECENT_KEY) || '[]'); }
	catch { return []; }
}

function setTextPromptRecentDropdownOpen(isOpen, focusFirst = false) {
	if (!textPromptRecentDropdown) return;
	if (isOpen) {
		renderTextPromptRecentDropdown();
	}
	textPromptRecentDropdown.hidden = !isOpen;
	textPromptRecentDropdown.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
	if (textPromptRecentBtn) {
		textPromptRecentBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
	}
	if (!isOpen) return;
	if (!focusFirst) return;
	const first = textPromptRecentDropdown.querySelector('.prompt-recent-item');
	if (first instanceof HTMLElement) {
		first.focus();
	}
}

function applyRecentTextPromptByIndex(index) {
	const value = loadTextPromptRecentHistory()[index] || '';
	if (!value) return;
	chatInput.value = value;
	chatInput.focus();
	setTextPromptRecentDropdownOpen(false);
}

function saveCurrentTextPromptToHistory(text) {
	const t = String(text || '').trim();
	if (!t) return;
	let list = loadTextPromptRecentHistory().filter((p) => p !== t);
	list.unshift(t);
	list = list.slice(0, TEXT_PROMPT_RECENT_MAX);
	localStorage.setItem(TEXT_PROMPT_RECENT_KEY, JSON.stringify(list));
	renderTextPromptRecentDropdown();
	renderTextPromptRecentChips();
}

function renderTextPromptRecentDropdown() {
	if (!textPromptRecentDropdown) return;
	const list = loadTextPromptRecentHistory();
	if (!list.length) {
		textPromptRecentDropdown.innerHTML = '<li class="prompt-recent-empty">No recent prompts</li>';
		return;
	}
	textPromptRecentDropdown.innerHTML = list.map((p, i) => {
		const preview = p.length > 80 ? p.slice(0, 80) + '\u2026' : p;
		return `<li class="prompt-recent-item" data-index="${i}" role="option" tabindex="0">${escHtml(preview)}</li>`;
	}).join('');
	textPromptRecentDropdown.querySelectorAll('.prompt-recent-item').forEach((li) => {
		const apply = () => {
			applyRecentTextPromptByIndex(Number(li.dataset.index));
		};
		li.addEventListener('click', apply);
		li.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); apply(); } });
	});
}

function renderTextPromptRecentChips() {
	if (!textPromptRecentChips) return;
	const list = loadTextPromptRecentHistory().slice(0, TEXT_PROMPT_RECENT_CHIPS_MAX);
	if (!list.length) {
		textPromptRecentChips.innerHTML = '<span class="hint">No recent prompts yet.</span>';
		return;
	}
	textPromptRecentChips.innerHTML = list.map((p, i) => {
		const preview = p.length > 66 ? `${p.slice(0, 66)}\u2026` : p;
		return `<button class="prompt-recent-chip" type="button" data-index="${i}" title="${escHtml(p)}">${escHtml(preview)}</button>`;
	}).join('');
	textPromptRecentChips.querySelectorAll('.prompt-recent-chip').forEach((btn) => {
		btn.addEventListener('click', () => {
			applyRecentTextPromptByIndex(Number(btn.dataset.index));
		});
		btn.addEventListener('keydown', onPromptRecentControlsKeydown);
	});
}
// --- End Text Prompt Recent History ---

// --- End Prompt Recent History & Saved Presets ---

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
	enhancedPromptSuggestBtn.classList.add('is-thinking');
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
		enhancedPromptSuggestBtn.classList.remove('is-thinking');
	}
}

if (enhancedPromptToggle) {
	enhancedPromptToggle.addEventListener('change', () => {
		setEnhancedPromptBreakdownVisible(enhancedPromptToggle.checked);
	});
	const saved = localStorage.getItem('enhancedPromptBreakdownEnabled') === '1';
	setEnhancedPromptBreakdownVisible(saved);
}

setupImageSidebarSectionCollapse();

// Prompt syntax popup
function getPromptSyntaxTabStops() {
	if (!promptSyntaxPopup) return [];
	const selector = [
		'button:not([disabled])',
		'input:not([disabled]):not([type="hidden"])',
		'select:not([disabled])',
		'textarea:not([disabled])',
		'[tabindex]:not([tabindex="-1"])',
	].join(', ');
	return [...promptSyntaxPopup.querySelectorAll(selector)].filter((el) => {
		if (!(el instanceof HTMLElement)) return false;
		if (el.hidden || el.getAttribute('aria-hidden') === 'true') return false;
		if (el.closest('[hidden]')) return false;
		return true;
	});
}

function setPromptSyntaxPopupOpen(isOpen) {
	if (!promptSyntaxPopup) return;
	if (isOpen) {
		promptSyntaxLastFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
	}
	promptSyntaxPopup.hidden = !isOpen;
	promptSyntaxPopup.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
	if (promptSyntaxInfoBtn) {
		promptSyntaxInfoBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
	}
	if (isOpen) {
		if (promptSyntaxCloseBtn) promptSyntaxCloseBtn.focus();
		return;
	}
	const active = document.activeElement;
	if (active instanceof HTMLElement && promptSyntaxPopup.contains(active) && promptSyntaxLastFocus && document.contains(promptSyntaxLastFocus)) {
		promptSyntaxLastFocus.focus();
	}
	promptSyntaxLastFocus = null;
}

if (promptSyntaxInfoBtn && promptSyntaxPopup) {
	promptSyntaxInfoBtn.addEventListener('click', () => {
		setPromptSyntaxPopupOpen(promptSyntaxPopup.hidden);
	});
}
if (promptSyntaxCloseBtn && promptSyntaxPopup) {
	promptSyntaxCloseBtn.addEventListener('click', () => {
		setPromptSyntaxPopupOpen(false);
	});
}
if (promptSyntaxPopup) {
	promptSyntaxPopup.addEventListener('keydown', (event) => {
		if (promptSyntaxPopup.hidden) return;
		if (event.key === 'Escape') {
			event.preventDefault();
			setPromptSyntaxPopupOpen(false);
			return;
		}
		if (event.key !== 'Tab') return;
		const tabStops = getPromptSyntaxTabStops();
		if (!tabStops.length) return;
		const first = tabStops[0];
		const last = tabStops[tabStops.length - 1];
		const active = document.activeElement;
		if (event.shiftKey) {
			if (active === first || !promptSyntaxPopup.contains(active)) {
				event.preventDefault();
				last.focus();
			}
			return;
		}
		if (active === last || !promptSyntaxPopup.contains(active)) {
			event.preventDefault();
			first.focus();
		}
	});
}

// Default negative prompt button
if (negativePromptDefaultBtn && imageNegativePrompt) {
	negativePromptDefaultBtn.addEventListener('click', () => {
		const def = localStorage.getItem('defaultNegativePrompt') || '';
		if (def) {
			imageNegativePrompt.value = def;
			showToast('Default negative prompt applied.', 'pos');
		} else {
			showToast('No default negative prompt set — configure one in Configurations.', 'neg');
		}
	});
}

// HiresFix denoise live display
if (hiresfixDenoise && hiresfixDenoiseVal) {
	hiresfixDenoise.addEventListener('input', () => {
		hiresfixDenoiseVal.textContent = Number(hiresfixDenoise.value).toFixed(2);
	});
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

if (promptRecentBtn) {
	promptRecentBtn.addEventListener('click', (e) => {
		e.stopPropagation();
		const isOpen = promptRecentDropdown ? !promptRecentDropdown.hidden : false;
		setPromptRecentDropdownOpen(!isOpen);
	});
	promptRecentBtn.addEventListener('keydown', (event) => {
		if (event.key === 'Escape') {
			event.preventDefault();
			setPromptRecentDropdownOpen(false);
			return;
		}
		if (!['ArrowDown', 'Enter', ' '].includes(event.key)) return;
		event.preventDefault();
		setPromptRecentDropdownOpen(true, true);
	});
}

if (promptRecentDropdown) {
	promptRecentDropdown.addEventListener('keydown', (event) => {
		if (promptRecentDropdown.hidden) return;
		if (event.key === 'Escape') {
			event.preventDefault();
			setPromptRecentDropdownOpen(false);
			if (promptRecentBtn) promptRecentBtn.focus();
			return;
		}
		if (!['ArrowDown', 'ArrowUp'].includes(event.key)) return;
		const items = [...promptRecentDropdown.querySelectorAll('.prompt-recent-item')].filter((el) => el instanceof HTMLElement);
		if (!items.length) return;
		event.preventDefault();
		const active = document.activeElement;
		const currentIndex = items.indexOf(active);
		const delta = event.key === 'ArrowDown' ? 1 : -1;
		const nextIndex = currentIndex < 0 ? (delta > 0 ? 0 : items.length - 1) : (currentIndex + delta + items.length) % items.length;
		items[nextIndex].focus();
	});
}

document.addEventListener('click', (e) => {
	if (promptRecentDropdown && !promptRecentDropdown.hidden) {
		if (!promptRecentDropdown.contains(e.target) && e.target !== promptRecentBtn) {
			setPromptRecentDropdownOpen(false);
		}
	}
});

if (promptSaveBtn) {
	promptSaveBtn.addEventListener('click', () => {
		const tagsVal = promptSavedTags ? promptSavedTags.value : '';
		saveNamedPromptPreset(promptSavedName?.value, imagePrompt.value.trim(), tagsVal);
	});
}
if (promptLoadBtn) {
	promptLoadBtn.addEventListener('click', () => {
		if (!promptSavedSelect?.value) { showToast('Select a preset to load.', 'neg'); return; }
		const presets = loadPromptSavedPresets();
		const preset = presets[promptSavedSelect.value];
		if (preset) {
			imagePrompt.value = preset.text;
			imagePrompt.focus();
			if (promptSavedTags) {
				promptSavedTags.value = preset.tags.join(', ');
			}
			showToast(`Loaded preset "${promptSavedSelect.value}".`, 'pos');
		}
	});
}
if (promptDeleteSavedBtn) {
	promptDeleteSavedBtn.addEventListener('click', () => {
		if (!promptSavedSelect?.value) { showToast('Select a preset to delete.', 'neg'); return; }
		deleteNamedPromptPreset(promptSavedSelect.value);
	});
}
if (promptFavToggle) {
	promptFavToggle.addEventListener('click', () => {
		if (!promptSavedSelect?.value) { showToast('Select a preset first.', 'neg'); return; }
		togglePresetFavorite(promptSavedSelect.value);
	});
}
if (promptSavedSelect) {
	promptSavedSelect.addEventListener('change', () => {
		const name = promptSavedSelect.value;
		renderPresetTagChips(name);
		renderPresetNotesPreview(name);
		const presets = loadPromptSavedPresets();
		const preset = presets[name];
		_updateFavToggleBtn(name, preset ? preset.favorite : false);
	});
}
if (promptTagFilter) {
	promptTagFilter.addEventListener('change', () => {
		renderPromptSavedSelect();
	});
}
if (promptFavoritesOnlyToggle) {
	promptFavoritesOnlyToggle.addEventListener('click', () => {
		_setFavoritesOnlyFilter(!_getFavoritesOnlyFilter());
		renderPromptSavedSelect();
	});
}
if (promptPresetTagChips) {
	promptPresetTagChips.addEventListener('click', (e) => {
		const btn = e.target.closest('.preset-tag-chip-btn');
		if (!btn || !promptTagFilter) return;
		const tag = btn.dataset.tag || '';
		promptTagFilter.value = promptTagFilter.value === tag ? '' : tag;
		renderPromptSavedSelect();
	});
}
if (promptPresetClearFilters) {
	promptPresetClearFilters.addEventListener('click', () => {
		if (promptTagFilter) promptTagFilter.value = '';
		_setFavoritesOnlyFilter(false);
		renderPromptSavedSelect();
		showToast('Preset filters cleared.', 'pos');
	});
}
if (promptEditPresetBtn) {
	promptEditPresetBtn.addEventListener('click', () => {
		if (!promptSavedSelect?.value) { showToast('Select a preset to edit.', 'neg'); return; }
		openPresetEditModal(promptSavedSelect.value);
	});
}
if (presetEditModalClose) {
	presetEditModalClose.addEventListener('click', closePresetEditModal);
}
if (presetEditCancel) {
	presetEditCancel.addEventListener('click', closePresetEditModal);
}
if (presetEditSave) {
	presetEditSave.addEventListener('click', savePresetEditModal);
}
if (presetEditDelete) {
	presetEditDelete.addEventListener('click', () => {
		const name = _presetEditOriginalName;
		if (!name) return;
		closePresetEditModal();
		deleteNamedPromptPreset(name);
	});
}
if (presetEditModal) {
	presetEditModal.addEventListener('click', (e) => {
		if (e.target === presetEditModal || e.target.classList.contains('preset-edit-modal-backdrop')) {
			closePresetEditModal();
		}
	});
}
document.addEventListener('keydown', (e) => {
	if (e.key === 'Escape' && presetEditModal && !presetEditModal.hidden) {
		closePresetEditModal();
	}
});
if (promptRecentClearBtn) {
	promptRecentClearBtn.addEventListener('click', () => {
		localStorage.removeItem(PROMPT_RECENT_KEY);
		renderPromptRecentDropdown();
		renderPromptRecentChips();
		showToast('Cleared recent prompt history.', 'pos');
	});
	promptRecentClearBtn.addEventListener('keydown', onPromptRecentControlsKeydown);
}

renderPromptRecentDropdown();
renderPromptRecentChips();
refreshPromptTagFilterOptions();
_updateFavoritesOnlyToggleUi();
renderPromptSavedSelect();

// Text prompt history event listeners
if (textPromptRecentBtn) {
	textPromptRecentBtn.addEventListener('click', (e) => {
		e.stopPropagation();
		const isOpen = textPromptRecentDropdown ? !textPromptRecentDropdown.hidden : false;
		setTextPromptRecentDropdownOpen(!isOpen);
	});
	textPromptRecentBtn.addEventListener('keydown', (event) => {
		if (event.key === 'Escape') {
			event.preventDefault();
			setTextPromptRecentDropdownOpen(false);
			return;
		}
		if (!['ArrowDown', 'Enter', ' '].includes(event.key)) return;
		event.preventDefault();
		setTextPromptRecentDropdownOpen(true, true);
	});
}

if (textPromptRecentDropdown) {
	textPromptRecentDropdown.addEventListener('keydown', (event) => {
		if (textPromptRecentDropdown.hidden) return;
		if (event.key === 'Escape') {
			event.preventDefault();
			setTextPromptRecentDropdownOpen(false);
			if (textPromptRecentBtn) textPromptRecentBtn.focus();
			return;
		}
		if (!['ArrowDown', 'ArrowUp'].includes(event.key)) return;
		const items = [...textPromptRecentDropdown.querySelectorAll('.text-prompt-recent-item')].filter((el) => el instanceof HTMLElement);
		if (!items.length) return;
		event.preventDefault();
		const active = document.activeElement;
		const currentIndex = items.indexOf(active);
		const delta = event.key === 'ArrowDown' ? 1 : -1;
		const nextIndex = currentIndex < 0 ? (delta > 0 ? 0 : items.length - 1) : (currentIndex + delta + items.length) % items.length;
		items[nextIndex].focus();
	});
}

// Close text prompt dropdown when clicking outside
document.addEventListener('click', (e) => {
	if (textPromptRecentDropdown && !textPromptRecentDropdown.hidden) {
		if (!textPromptRecentDropdown.contains(e.target) && e.target !== textPromptRecentBtn) {
			setTextPromptRecentDropdownOpen(false);
		}
	}
});

// Render text prompt history on page load
renderTextPromptRecentDropdown();
renderTextPromptRecentChips();

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

async function uploadControlnetImageIfNeeded() {
	if (!controlnetImageUpload || !controlnetImageUpload.files || !controlnetImageUpload.files[0]) return '';
	const data = new FormData();
	data.append('image', controlnetImageUpload.files[0]);
	const res = await fetch('/api/image/upload-image', {
		method: 'POST',
		body: data,
	});
	const payload = await res.json().catch(() => ({}));
	if (!res.ok || !payload.name) {
		throw new Error(payload.error || 'ControlNet image upload failed');
	}
	return String(payload.name || '');
}

function applyPromptWeightHelper(action) {
	if (!imagePrompt) return;
	const value = imagePrompt.value || '';
	const start = Number.isInteger(imagePrompt.selectionStart) ? imagePrompt.selectionStart : value.length;
	const end = Number.isInteger(imagePrompt.selectionEnd) ? imagePrompt.selectionEnd : start;
	const selected = value.slice(start, end);

	let insert = '';
	let selStart = null;
	let selEnd = null;
	if (action === 'up') {
		if (selected) {
			insert = `(${selected}:1.2)`;
		} else {
			insert = '(text:1.2)';
			selStart = start + 1;
			selEnd = start + 5;
		}
	} else if (action === 'down') {
		if (selected) {
			insert = `[${selected}:0.8]`;
		} else {
			insert = '[text:0.8]';
			selStart = start + 1;
			selEnd = start + 5;
		}
	} else if (action === 'break') {
		insert = selected ? `BREAK ${selected} BREAK` : ' BREAK ';
	}
	if (!insert) return;

	imagePrompt.value = `${value.slice(0, start)}${insert}${value.slice(end)}`;
	imagePrompt.focus();
	if (Number.isInteger(selStart) && Number.isInteger(selEnd)) {
		imagePrompt.setSelectionRange(selStart, selEnd);
	} else {
		const caret = start + insert.length;
		imagePrompt.setSelectionRange(caret, caret);
	}
}

if (imagePrompt) {
	imagePrompt.addEventListener('keydown', (event) => {
		if ((event.ctrlKey || event.metaKey) && event.key === 'Enter' && !imageGenerateBtn?.disabled) {
			event.preventDefault();
			imageForm.requestSubmit();
		}
	});
}

if (promptWeightUpBtn) {
	promptWeightUpBtn.addEventListener('click', () => applyPromptWeightHelper('up'));
}

if (promptWeightDownBtn) {
	promptWeightDownBtn.addEventListener('click', () => applyPromptWeightHelper('down'));
}

if (promptBreakWrapBtn) {
	promptBreakWrapBtn.addEventListener('click', () => applyPromptWeightHelper('break'));
}

imageForm.addEventListener('submit', async (e) => {
	e.preventDefault();
	const prompt = resolvePromptForSubmission();
	if (prompt) saveCurrentPromptToHistory(prompt);
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
		const controlnetModel = controlnetModelSelect?.value || '';
		const hasControlnetImage = Boolean(controlnetImageUpload?.files && controlnetImageUpload.files[0]);
		if (controlnetModel && !hasControlnetImage) {
			queueSummary.textContent = 'Error: Choose a ControlNet image when a ControlNet model is selected.';
			imageGenerateBtn.disabled = false;
			imageGenerateBtn.textContent = 'Generate Image';
			return;
		}
		if (!controlnetModel && hasControlnetImage) {
			queueSummary.textContent = 'Error: Choose a ControlNet model when a ControlNet image is uploaded.';
			imageGenerateBtn.disabled = false;
			imageGenerateBtn.textContent = 'Generate Image';
			return;
		}

		let controlnetImageName = '';
		if (controlnetModel && hasControlnetImage) {
			controlnetImageName = await uploadControlnetImageIfNeeded();
		}

		const common = {
			prompt,
			negative_prompt: imageNegativePrompt.value.trim(),
			model: imageModelSelect.value,
			model_family: resolveActiveImageFamily(imageModelSelect?.value || ''),
			refiner_model: refinerModelSelect?.value || '',
			vae: vaeModelSelect?.value || '',
			sampler: imageSamplerSelect.value,
			scheduler: imageSchedulerSelect?.value || 'normal',
			loras: collectLoraStack(),
			controlnet_model: controlnetModel,
			controlnet_image_name: controlnetImageName,
			controlnet_preprocessor: controlnetPreprocessorSelect?.value || 'none',
			controlnet_weight: Number(controlnetWeight?.value || 1),
			controlnet_start: Number(controlnetStart?.value || 0),
			controlnet_end: Number(controlnetEnd?.value || 1),
			seed: imageSeed.value.trim() || null,
			steps: Number(imageSteps.value),
			cfg: Number(imageCfg.value),
			width: Number(imageWidth.value),
			height: Number(imageHeight.value),
			batch_size: Number(imageBatchSize.value),
			denoise: Number(imageDenoise.value),
			hiresfix_enable: hiresfixEnable?.checked || false,
			hiresfix_upscaler: hiresfixUpscalerSelect?.value || '',
			hiresfix_scale: Number(hiresfixScale?.value || 2),
			hiresfix_steps: Number(hiresfixSteps?.value || 20),
			hiresfix_denoise: Number(hiresfixDenoise?.value || 0.4),
		};

		const validationError = validateImageInputs(common);
		if (validationError) {
			queueSummary.textContent = `Error: ${validationError}`;
			imageGenerateBtn.disabled = false;
			imageGenerateBtn.textContent = 'Generate Image';
			return;
		}

		const normalizedCommon = normalizeImageRequestByFamily(common);

		let res;
		if (imageUpload.files && imageUpload.files[0]) {
			const formData = new FormData();
			formData.append('image', imageUpload.files[0]);
			formData.append('prompt', normalizedCommon.prompt);
			formData.append('negative_prompt', normalizedCommon.negative_prompt);
			formData.append('model', normalizedCommon.model);
			formData.append('model_family', normalizedCommon.model_family || '');
			formData.append('sampler', normalizedCommon.sampler);
			formData.append('loras', JSON.stringify(normalizedCommon.loras));
			formData.append('controlnet_model', normalizedCommon.controlnet_model || '');
			formData.append('controlnet_image_name', normalizedCommon.controlnet_image_name || '');
			formData.append('controlnet_weight', String(normalizedCommon.controlnet_weight));
			formData.append('controlnet_start', String(normalizedCommon.controlnet_start));
			formData.append('controlnet_end', String(normalizedCommon.controlnet_end));
			formData.append('seed', normalizedCommon.seed || '');
			formData.append('steps', String(normalizedCommon.steps));
			formData.append('cfg', String(normalizedCommon.cfg));
			formData.append('denoise', String(normalizedCommon.denoise));
			res = await fetch('/api/image/img2img', {
				method: 'POST',
				body: formData,
			});
		} else {
			res = await fetch('/api/image/generate', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(normalizedCommon),
			});
		}

		const data = await res.json();
		if (!res.ok) {
			queueSummary.textContent = `Error: ${data.error || 'Image request failed'}`;
			imageGenerateBtn.disabled = false;
			imageGenerateBtn.textContent = 'Generate Image';
			return;
		}

		if (data && data.meta && data.meta.seed !== undefined && data.meta.seed !== null) {
			setLastGeneratedSeed(data.meta.seed);
		} else if (normalizedCommon.seed) {
			setLastGeneratedSeed(normalizedCommon.seed);
		}

		const promptId = data.prompt_id;
		imageState.currentPromptId = promptId;
		trackedPromptIds.add(promptId);
		incrementQueueTelemetry('submitted');
		const snapshot = {
			prompt: normalizedCommon.prompt,
			negative_prompt: normalizedCommon.negative_prompt,
			model: normalizedCommon.model,
			model_family: normalizedCommon.model_family,
			loras: normalizedCommon.loras,
			controlnet_model: normalizedCommon.controlnet_model,
			controlnet_weight: normalizedCommon.controlnet_weight,
			controlnet_start: normalizedCommon.controlnet_start,
			controlnet_end: normalizedCommon.controlnet_end,
			sampler: normalizedCommon.sampler,
			seed: normalizedCommon.seed,
			steps: normalizedCommon.steps,
			cfg: normalizedCommon.cfg,
			denoise: normalizedCommon.denoise,
			width: normalizedCommon.width,
			height: normalizedCommon.height,
			batch_size: normalizedCommon.batch_size,
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
		persistTrackedQueueState();
		ensureQueuePolling();

		queueSummary.textContent = `Submitted: ${promptId}`;
		if (imageFluxLockBypassOnce) {
			imageFluxLockBypassOnce = false;
			applyImageFamilyModeUi();
			if (imageRecommendationStatus) {
				imageRecommendationStatus.textContent = 'Recommendation lock restored after submit.';
				imageRecommendationStatus.hidden = false;
			}
		}
		imageGenerateBtn.textContent = 'Queued';
				if (data.meta && data.meta.seed !== undefined) setLastGeneratedSeed(data.meta.seed);
		await pollQueue();
	} catch (err) {
		queueSummary.textContent = `Error: ${err.message}`;
		imageGenerateBtn.disabled = false;
		imageGenerateBtn.textContent = 'Generate Image';
	}
});

restoreTrackedQueueState();
loadGallery();
loadLivePreview();
loadServiceConfig();
startPollingLeaseHeartbeat();
syncBackgroundPollingOwnership();

// Live elapsed timer for running queue jobs
window.setInterval(() => {
	document.querySelectorAll('.queue-elapsed[data-started-at]').forEach((el) => {
		const startedAt = parseInt(el.dataset.startedAt, 10);
		if (!startedAt) return;
		const sec = Math.floor((Date.now() - startedAt) / 1000);
		el.textContent = sec >= 60 ? `${Math.floor(sec / 60)}m${String(sec % 60).padStart(2, '0')}s` : `${sec}s`;
	});
}, 1000);

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
	stopQueueRestoreHintTicker();
	stopQueueLastActionTicker();
	stopWsTransportStatusTicker();
	releaseBackgroundPollingOwnership();
});


