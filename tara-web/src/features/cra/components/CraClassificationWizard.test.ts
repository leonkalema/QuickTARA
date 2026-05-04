/**
 * Unit tests for CraClassificationWizard.svelte
 *
 * Covers the 3-step classification wizard:
 *   Step 1 — category selection + search
 *   Step 2 — harmonised standard / open-source / automotive checkboxes
 *   Step 3 — review summary + submit
 *   Result — classification result screen
 */
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/svelte';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import CraClassificationWizard from './CraClassificationWizard.svelte';

// ---------------------------------------------------------------------------
// Mock the API module — replaces the module for every test in this file.
// The factory runs synchronously before any import resolves, so the component
// receives the mock when it executes `import { craApi } from '$lib/api/craApi'`.
// ---------------------------------------------------------------------------
vi.mock('$lib/api/craApi', () => ({
  craApi: {
    getProductCategories: vi.fn(),
    classify: vi.fn(),
  },
}));

import { craApi } from '$lib/api/craApi';

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const MOCK_CATEGORIES = [
  {
    id: 'cat-nw',
    name: 'Network Devices',
    classification: 'class_i',
    description: 'Managed switches and routers',
    examples: 'router, switch, firewall',
    annex_ref: 'Annex III(1)',
  },
  {
    id: 'cat-hsm',
    name: 'HSMs and Smartcards',
    classification: 'class_ii',
    description: 'Hardware security modules',
    examples: 'HSM, smartcard, TPM',
    annex_ref: 'Annex III(7)',
  },
];

const MOCK_RESULT = {
  classification: 'class_i',
  category_id: 'cat-nw',
  category_name: 'Network Devices',
  conformity_assessment: 'Module B+C',
  conformity_module: {
    module_id: 'BC',
    name: 'Module B+C',
    description: 'Third-party conformity assessment',
    mandatory: false,
    alternatives: [],
    rationale: 'Standard path for Class I products.',
  },
  compliance_deadline: '2027-12-31',
  reporting_deadline: '2025-06-01',
  cost_estimate_min: 50_000,
  cost_estimate_max: 150_000,
  automotive_exception: false,
  rationale: 'Product is a managed network device (Annex III §1).',
};

// ---------------------------------------------------------------------------
// Helper — advance the wizard from step 1 through to step N
// ---------------------------------------------------------------------------
async function advanceTo(step: 2 | 3): Promise<void> {
  // Step 1 → 2
  await screen.findByText('Step 1: Select Category');
  await fireEvent.click(screen.getByRole('button', { name: /^next$/i }));
  if (step === 2) return;
  // Step 2 → 3
  await screen.findByText('Step 2: Options');
  await fireEvent.click(screen.getByRole('button', { name: /^next$/i }));
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('CraClassificationWizard', () => {
  beforeEach(() => {
    vi.mocked(craApi.getProductCategories).mockResolvedValue(MOCK_CATEGORIES as any);
    vi.mocked(craApi.classify).mockResolvedValue(MOCK_RESULT as any);
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  // ── Loading state ─────────────────────────────────────────────────────────

  it('shows a loading spinner while categories are being fetched', () => {
    vi.mocked(craApi.getProductCategories).mockReturnValue(new Promise(() => {}));
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });
    expect(document.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('calls getProductCategories on mount', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });
    await screen.findByText('Step 1: Select Category');
    expect(craApi.getProductCategories).toHaveBeenCalledOnce();
  });

  // ── Step 1 — category selection ───────────────────────────────────────────

  it('shows step 1 heading and category list after loading', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });

    await screen.findByText('Step 1: Select Category');
    expect(screen.getByText('Network Devices')).toBeInTheDocument();
    expect(screen.getByText('HSMs and Smartcards')).toBeInTheDocument();
    expect(screen.getByText(/None of the below/i)).toBeInTheDocument();
  });

  it('displays Class I and Class II section headers', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });
    await screen.findByText('Step 1: Select Category');

    // Use word-boundary to avoid /class i/ matching "Class II"
    expect(screen.getByText(/class i\b/i)).toBeInTheDocument();
    expect(screen.getByText(/class ii/i)).toBeInTheDocument();
  });

  it('search query hides non-matching categories', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });
    await screen.findByText('Network Devices');

    const input = screen.getByPlaceholderText(/search categories/i);
    await fireEvent.input(input, { target: { value: 'HSM' } });

    await waitFor(() => {
      expect(screen.queryByText('Network Devices')).not.toBeInTheDocument();
    });
    expect(screen.getByText('HSMs and Smartcards')).toBeInTheDocument();
  });

  it('clearing the search restores the full list', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });
    await screen.findByText('Network Devices');

    const input = screen.getByPlaceholderText(/search categories/i);
    await fireEvent.input(input, { target: { value: 'xyz-no-match' } });
    await waitFor(() => expect(screen.queryByText('Network Devices')).not.toBeInTheDocument());

    await fireEvent.input(input, { target: { value: '' } });
    await waitFor(() => expect(screen.getByText('Network Devices')).toBeInTheDocument());
  });

  // ── Step navigation ───────────────────────────────────────────────────────

  it('Next button advances from step 1 to step 2', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });
    await advanceTo(2);

    expect(screen.getByText('Step 2: Options')).toBeInTheDocument();
  });

  it('Back button on step 2 returns to step 1', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });
    await advanceTo(2);
    await screen.findByText('Step 2: Options');

    await fireEvent.click(screen.getByRole('button', { name: /^back$/i }));

    expect(await screen.findByText('Step 1: Select Category')).toBeInTheDocument();
  });

  it('Back button is disabled on step 1', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });
    await screen.findByText('Step 1: Select Category');

    expect(screen.getByRole('button', { name: /^back$/i })).toBeDisabled();
  });

  // ── Step 2 — options ──────────────────────────────────────────────────────

  it('step 2 shows the three compliance option checkboxes', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });
    await advanceTo(2);

    // Match the label headings (not the description paragraphs that share the same keywords)
    expect(screen.getByText(/will you apply a harmonised standard/i)).toBeInTheDocument();
    expect(screen.getByText(/free\/open-source with public technical docs/i)).toBeInTheDocument();
    expect(screen.getByText(/automotive exception/i)).toBeInTheDocument();
  });

  it('checkboxes start unchecked', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });
    await advanceTo(2);

    const checkboxes = screen.getAllByRole('checkbox');
    checkboxes.forEach((cb) => expect(cb).not.toBeChecked());
  });

  // ── Step 3 — review ───────────────────────────────────────────────────────

  it('step 3 shows the review summary', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });
    await advanceTo(3);

    await screen.findByText('Step 3: Review');
    expect(screen.getByText(/selected category/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /classify product/i })).toBeInTheDocument();
  });

  it('review summary reflects default category when nothing is selected', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });
    await advanceTo(3);
    await screen.findByText('Step 3: Review');

    // Default text appears when selectedCategoryId is null
    expect(screen.getByText(/default.*no matching/i)).toBeInTheDocument();
  });

  // ── Submit & result ───────────────────────────────────────────────────────

  it('Classify Product calls craApi.classify with the assessmentId', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'assessment-42' } });
    await advanceTo(3);
    await screen.findByText('Step 3: Review');

    await fireEvent.click(screen.getByRole('button', { name: /classify product/i }));

    await waitFor(() => {
      expect(craApi.classify).toHaveBeenCalledWith(
        'assessment-42',
        expect.objectContaining({
          uses_harmonised_standard: false,
          is_open_source_public: false,
          automotive_exception: false,
        }),
      );
    });
  });

  it('shows the result screen after a successful classification', async () => {
    render(CraClassificationWizard, { props: { assessmentId: 'a1' } });
    await advanceTo(3);
    await screen.findByText('Step 3: Review');
    await fireEvent.click(screen.getByRole('button', { name: /classify product/i }));

    expect(await screen.findByText('Important Class I')).toBeInTheDocument();
    expect(screen.getByText('Module B+C')).toBeInTheDocument();
  });

  it('fires oncomplete with the classification result', async () => {
    const oncomplete = vi.fn();
    render(CraClassificationWizard, { props: { assessmentId: 'a1', oncomplete } });
    await advanceTo(3);
    await fireEvent.click(screen.getByRole('button', { name: /classify product/i }));

    await waitFor(() => expect(oncomplete).toHaveBeenCalledWith(MOCK_RESULT));
  });

  // ── Cancel ────────────────────────────────────────────────────────────────

  it('fires oncancel when the Cancel button is clicked', async () => {
    const oncancel = vi.fn();
    render(CraClassificationWizard, { props: { assessmentId: 'a1', oncancel } });
    await screen.findByText('Step 1: Select Category');

    await fireEvent.click(screen.getByRole('button', { name: /^cancel$/i }));

    expect(oncancel).toHaveBeenCalledOnce();
  });
});
