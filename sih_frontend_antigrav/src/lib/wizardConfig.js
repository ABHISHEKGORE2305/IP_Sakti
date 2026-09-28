// src/lib/wizardConfig.js
// Static config for the Sprint 5 guided wizard — mirrors the backend
// contracts exactly (engines.classifier, agents.supervisor SPECIALISTS,
// engines.intl_engine) so the UI never invents options the backend
// doesn't understand.

export const JURISDICTIONS = [
  { value: 'India', flag: '🇮🇳', label: 'India', desc: 'Indian Patents Act, D&C Act, BD Act, AYUSH/FSSAI/CDSCO.' },
  { value: 'International', flag: '🌍', label: 'International', desc: 'WIPO, US FDA, EU THMPD, PCT and export-market pathways.' },
];

export const INTENDED_USE_OPTIONS = [
  { value: 'therapeutic', label: 'Therapeutic / cure / disease treatment' },
  { value: 'nutritional', label: 'Nutritional / dietary supplement' },
  { value: 'general_food', label: 'General food / beverage' },
  { value: 'topical', label: 'Topical / beautification / cleansing' },
];

// Mirrors agents.supervisor.SPECIALISTS / agents.state.AgentName exactly.
export const ISSUE_REGIMES = [
  {
    agent: 'patent_agent',
    label: 'Patent & Traditional Knowledge',
    desc: 'Novelty, inventive step, Section 3(p)/3(e)/3(d) exclusions.',
  },
  {
    agent: 'tm_gi_agent',
    label: 'Trademark & Geographical Indication',
    desc: 'Brand distinctiveness, NICE classes, GI registration.',
  },
  {
    agent: 'abs_agent',
    label: 'Biological Diversity & ABS',
    desc: 'NBA/SBB jurisdiction, Form I–IV, benefit sharing.',
  },
  {
    agent: 'reg_agent',
    label: 'Regulatory (AYUSH / FSSAI / CDSCO)',
    desc: 'Licensing pathway, clinical evidence, advertising compliance.',
  },
  {
    agent: 'intl_agent',
    label: 'International & Export',
    desc: 'WIPO, US FDA, EU THMPD, PCT, GRATK disclosure.',
  },
  {
    agent: 'classifier_agent',
    label: 'Product Classification only',
    desc: 'Just the statutory category — see the previous step.',
  },
];

export const TARGET_MARKETS = [
  { value: 'US', label: '🇺🇸 United States', desc: 'FDA Botanical Drug / DSHEA, USPTO §101.' },
  { value: 'EU', label: '🇪🇺 European Union', desc: 'THMPD traditional-use / well-established-use.' },
  { value: 'UK', label: '🇬🇧 United Kingdom', desc: 'MHRA Traditional Herbal Registration.' },
];

export const US_ROUTES = [
  { value: 'botanical_drug', label: 'Botanical Drug (FDA 2016 Guidance)' },
  { value: 'dietary_supplement', label: 'Dietary Supplement (DSHEA 1994)' },
];

export const EU_EVIDENCE_BASES = [
  { value: 'traditional_use', label: 'Traditional Use (THMPD, 30y/15y)' },
  { value: 'well_established_use', label: 'Well-Established Use (10y bibliographic)' },
];

// Mirrors engines.abs_engine.EntityType exactly.
export const ABS_ENTITY_TYPES = [
  { value: 'indian_individual', label: 'Indian individual' },
  { value: 'indian_company', label: 'Indian company (wholly Indian-owned)' },
  { value: 'nri', label: 'NRI' },
  { value: 'foreign_entity', label: 'Foreign entity' },
];

// Mirrors engines.abs_engine.ActivityType exactly.
export const ABS_ACTIVITY_TYPES = [
  { value: 'commercial_utilization', label: 'Commercial utilisation' },
  { value: 'non_commercial_research', label: 'Non-commercial research' },
  { value: 'bio_survey', label: 'Bio-survey / bio-utilisation' },
];

// Mirrors engines.classifier.ProductCategory exactly — engines.reg_engine
// takes the same category codes as engines.classifier's output.
export const REG_PRODUCT_CATEGORIES = [
  { value: 'classical_ayurvedic_medicine', label: 'Classical Ayurvedic Medicine' },
  { value: 'patent_or_proprietary_medicine', label: 'Patent or Proprietary Medicine' },
  { value: 'new_ayurvedic_drug', label: 'New Ayurvedic Drug / Phytopharmaceutical' },
  { value: 'ayurveda_aahar', label: 'Ayurveda-Aahar (Dietary Supplement)' },
  { value: 'general_food', label: 'General Food / Beverage' },
  { value: 'ayurvedic_cosmetic', label: 'Ayurvedic Cosmetic' },
];

// Mirrors engines.ipr_router.Regime exactly (trademark handled separately
// in StepIssuePicker since it has its own NICE-class/distinctiveness sub-form).
export const IPR_REGIMES = [
  { value: 'trademark', label: 'Trademark' },
  { value: 'geographical_indication', label: 'Geographical Indication' },
  { value: 'industrial_design', label: 'Industrial Design' },
  { value: 'trade_secret', label: 'Trade Secret' },
  { value: 'copyright', label: 'Copyright' },
  { value: 'ppv_fr', label: 'Plant Variety Protection (PPV&FR)' },
];

export const NICE_PRODUCT_TYPES = [
  { value: 'medicine', label: 'Medicine / supplement (Class 5)' },
  { value: 'cosmetic', label: 'Cosmetic (Class 3)' },
  { value: 'herbal_tea', label: 'Herbal tea / confection (Class 30)' },
  { value: 'clinic_services', label: 'Clinic / Panchakarma services (Class 44)' },
];

export const PPVFR_CATEGORIES = [
  { value: 'extant', label: 'Extant variety' },
  { value: 'farmers', label: "Farmers' variety" },
  { value: 'novel', label: 'Novel variety' },
];

// ISO code -> display name, matching src/api.py's _LANGUAGE_NAMES exactly.
export const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिन्दी (Hindi)' },
  { code: 'mr', label: 'मराठी (Marathi)' },
  { code: 'ta', label: 'தமிழ் (Tamil)' },
  { code: 'te', label: 'తెలుగు (Telugu)' },
  { code: 'kn', label: 'ಕನ್ನಡ (Kannada)' },
  { code: 'bn', label: 'বাংলা (Bengali)' },
  { code: 'gu', label: 'ગુજરાતી (Gujarati)' },
  { code: 'ml', label: 'മലയാളം (Malayalam)' },
  { code: 'pa', label: 'ਪੰਜਾਬੀ (Punjabi)' },
];

export const WIZARD_STEPS = [
  { key: 'jurisdiction', label: 'Jurisdiction' },
  { key: 'classification', label: 'Classification' },
  { key: 'issue', label: 'Issue Routing' },
  { key: 'analysis', label: 'Analysis' },
  { key: 'sources', label: 'Sources' },
  { key: 'action', label: 'Action Plan' },
];

// Simulated progressive stage labels for the Analysis step. The backend
// call is a single request/response (no SSE/websocket infra exists), so
// this is a UI-only progression timed against typical latency, replaced
// by the real result the moment the fetch resolves.
export const ANALYSIS_STAGES = [
  'Sanitizing input…',
  'Routing to specialist agent…',
  'Retrieving grounded legal sources…',
  'Drafting grounded answer…',
  'Verifying citations (zero-hallucination check)…',
  'Scoring confidence…',
];
