// Tap-to-fill starter suggestions for the free-text inputs.
//
// Chosen to match what the corpus actually covers well — patentability
// exclusions, TKDL prior art, formulation classification under the D&C Act,
// ABS duties under the BD Act/Rules, and trade marks. Topics the retrieval
// pipeline still handles poorly (the 2024 Form 27/Form 3 amendment cycle,
// cross-jurisdiction comparisons) are deliberately left out: a starter chip
// is an implicit promise that the system can answer it.
//
// `label` is what the chip shows; `value` is what lands in the input.

export const CHAT_SUGGESTIONS = [
  {
    label: 'Patent a classical formulation?',
    value:
      'Can I patent a formulation I prepared exactly as described in a classical Samhita text?',
  },
  {
    label: 'Classical vs proprietary medicine',
    value:
      'What is the difference between a classical Ayurvedic medicine and a patent or proprietary medicine, and how is each licensed?',
  },
  {
    label: 'NBA approval before filing?',
    value:
      'Do I need National Biodiversity Authority approval before filing a patent that uses an Indian medicinal plant?',
  },
  {
    label: 'Two-herb combination',
    value:
      'I combined two well-known herbs in a fixed ratio. Does Section 3(e) of the Patents Act bar a patent on it?',
  },
  {
    label: 'Trademark a Sanskrit name',
    value: 'Can I register a Sanskrit or descriptive Ayurvedic term as a trade mark in India?',
  },
];

export const WIZARD_QUERY_SUGGESTIONS = [
  {
    label: 'Novel extraction process',
    value:
      'We modified a classical formulation using a novel extraction process. Is the result patentable, and what regulatory category does it fall into?',
  },
  {
    label: 'Wild-collected sourcing',
    value:
      'We source wild-collected medicinal plants from forest land for commercial manufacture. What access and benefit-sharing obligations apply to us?',
  },
  {
    label: 'Standardised extract',
    value:
      'We standardised a plant extract to a fixed marker-compound content for clinical trials. How is it classified and what approvals does it need?',
  },
  {
    label: 'Food supplement or drug?',
    value:
      'We want to sell a herbal powder as a wellness supplement without therapeutic claims. Is it a food or a drug, and who licenses it?',
  },
];

export const LAW_QUESTION_SUGGESTIONS = [
  {
    label: 'Patent filing fee',
    value: 'What is the fee for filing a patent application in India?',
  },
  {
    label: 'Term of a patent',
    value: 'What is the term of a patent in India and when does it start?',
  },
  {
    label: 'Non-patentable subject matter',
    value: 'Which inventions are excluded from patentability under Section 3 of the Patents Act?',
  },
];

export const INGREDIENT_SUGGESTIONS = [
  { label: 'Ashwagandha', value: 'Withania somnifera' },
  { label: 'Turmeric', value: 'Curcuma longa' },
  { label: 'Giloy', value: 'Tinospora cordifolia' },
  { label: 'Tulsi', value: 'Ocimum sanctum' },
  { label: 'Shatavari', value: 'Asparagus racemosus' },
];

export const BIOLOGICAL_RESOURCE_SUGGESTIONS = [
  { label: 'Wild-collected Kutki', value: 'Picrorhiza kurroa (wild-collected, Himalayan)' },
  { label: 'Cultivated turmeric', value: 'Curcuma longa rhizome (cultivated)' },
  { label: 'Forest-sourced bark', value: 'Forest-sourced bark from a state forest area' },
];
