/**
 * Unit tests for CraAnnexVii.svelte
 *
 * Covers:
 *   Loading state — spinner while fetching
 *   Error state — error banner on API failure
 *   Metadata panel — product name, classification, conformity route, support period, deadline
 *   Completeness — % value and action-required counter vs "All sections have data"
 *   Appendix counts — assets, damage scenarios, compensating controls, SBOMs
 *   Section list — titles/article refs rendered, action-required badge
 *   Section toggle — body hidden by default, revealed on click, collapsed again on re-click
 *   Download — disabled without doc, calls craApi.downloadAnnexViiMarkdown on click
 *   Refresh — button calls load() again (getAnnexVii called a second time)
 */
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/svelte';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import CraAnnexVii from './CraAnnexVii.svelte';

vi.mock('$lib/api/craApi', () => ({
  craApi: {
    getAnnexVii: vi.fn(),
    downloadAnnexViiMarkdown: vi.fn(),
  },
}));

import { craApi } from '$lib/api/craApi';

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const MOCK_SECTIONS = [
  { number: '1', title: 'Product Description', article_ref: 'Annex VII §1', body: 'ECU description body.', is_action_required: false },
  { number: '2', title: 'Intended Purpose', article_ref: 'Annex VII §2', body: 'Controls brake actuation.', is_action_required: false },
  { number: '3', title: 'Cybersecurity Risks', article_ref: 'Annex VII §3', body: 'Risk body text.', is_action_required: true },
  { number: '4', title: 'Security Requirements', article_ref: 'Annex VII §4', body: 'Requirements body.', is_action_required: false },
  { number: '5', title: 'Vulnerability Management', article_ref: 'Annex VII §5', body: '', is_action_required: true },
  { number: '6', title: 'Software Bill of Materials', article_ref: 'Annex VII §6', body: 'SBOM body.', is_action_required: false },
  { number: '7', title: 'Security Evaluation', article_ref: 'Annex VII §7', body: 'Evaluation body.', is_action_required: false },
];

const MOCK_DOC = {
  assessment_id: 'a1',
  product_name: 'Brake Control ECU',
  product_id: 'prod-ecu',
  classification: 'Class I',
  conformity_assessment: 'Module B+C',
  support_period_years: 5,
  support_period_justification: null,
  compliance_deadline: '2027-12-31',
  generated_at: '2025-05-01T12:00:00Z',
  intended_purpose: 'Brake actuation',
  product_description: 'Main ECU',
  safety_level: 'ASIL B',
  interfaces: [],
  access_points: [],
  assets: [
    { asset_id: 'a1', name: 'Firmware', asset_type: 'Firmware', confidentiality: 'High', integrity: 'High', availability: 'High' },
    { asset_id: 'a2', name: 'Config', asset_type: 'Data', confidentiality: 'Medium', integrity: 'Medium', availability: 'Low' },
  ],
  damage_scenarios: [
    { scenario_id: 'ds1', name: 'Unintended braking', description: 'Desc', severity: 'Critical', safety_impact: 'High', financial_impact: 'Medium', operational_impact: 'High', privacy_impact: 'Low', threat_count: 2 },
  ],
  requirements: [],
  compensating_controls: [
    { control_id: 'cc1', name: 'CAN bus filtering', description: 'Filter CAN frames', status: 'implemented', requirement_id: null },
    { control_id: 'cc2', name: 'Secure boot', description: 'Verify firmware', status: 'planned', requirement_id: 'req-1' },
    { control_id: 'cc3', name: 'Rate limiting', description: 'Limit message rate', status: 'implemented', requirement_id: null },
  ],
  sboms: [
    { sbom_id: 's1', sbom_format: 'CycloneDX', spec_version: '1.4', component_count: 42, primary_component_name: 'brake-fw', primary_component_version: '2.1.0', uploaded_at: '2025-04-01T00:00:00Z' },
  ],
  sections: MOCK_SECTIONS,
  completeness_pct: 72,
};

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('CraAnnexVii', () => {
  beforeEach(() => {
    vi.mocked(craApi.getAnnexVii).mockResolvedValue(MOCK_DOC as any);
    vi.mocked(craApi.downloadAnnexViiMarkdown).mockResolvedValue(undefined as any);
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  // ── Loading ───────────────────────────────────────────────────────────────

  it('shows a loading spinner while the document is being fetched', () => {
    vi.mocked(craApi.getAnnexVii).mockReturnValue(new Promise(() => {}));
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    expect(document.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('calls getAnnexVii on mount with the assessmentId', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');
    expect(craApi.getAnnexVii).toHaveBeenCalledWith('a1');
    expect(craApi.getAnnexVii).toHaveBeenCalledOnce();
  });

  // ── Error ─────────────────────────────────────────────────────────────────

  it('shows an error banner when getAnnexVii rejects', async () => {
    vi.mocked(craApi.getAnnexVii).mockRejectedValue(new Error('Network error'));
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    expect(await screen.findByText('Network error')).toBeInTheDocument();
  });

  it('shows a fallback message for non-Error rejections', async () => {
    vi.mocked(craApi.getAnnexVii).mockRejectedValue('oops');
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    expect(await screen.findByText('Failed to load Annex VII')).toBeInTheDocument();
  });

  // ── Metadata ──────────────────────────────────────────────────────────────

  it('renders the product name after loading', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    expect(await screen.findByText('Brake Control ECU')).toBeInTheDocument();
  });

  it('renders classification and conformity route', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');
    expect(screen.getByText('Class I')).toBeInTheDocument();
    expect(screen.getByText('Module B+C')).toBeInTheDocument();
  });

  it('renders support period in years', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');
    expect(screen.getByText('5 years')).toBeInTheDocument();
  });

  it('renders compliance deadline', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');
    expect(screen.getByText('2027-12-31')).toBeInTheDocument();
  });

  it('renders completeness percentage', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');
    expect(screen.getByText('72%')).toBeInTheDocument();
  });

  // ── Completeness / action count ───────────────────────────────────────────

  it('shows action-required count when some sections need input', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');
    // 2 sections have is_action_required === true in MOCK_SECTIONS
    expect(screen.getByText(/2 sections need input/i)).toBeInTheDocument();
  });

  it('shows "All sections have data" when no section needs input', async () => {
    const allGood = {
      ...MOCK_DOC,
      sections: MOCK_DOC.sections.map((s) => ({ ...s, is_action_required: false })),
      completeness_pct: 100,
    };
    vi.mocked(craApi.getAnnexVii).mockResolvedValue(allGood as any);
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');
    expect(screen.getByText(/all sections have data/i)).toBeInTheDocument();
  });

  it('shows singular "1 section needs input" for exactly one action-required section', async () => {
    const oneAction = {
      ...MOCK_DOC,
      sections: MOCK_DOC.sections.map((s, i) => ({ ...s, is_action_required: i === 0 })),
    };
    vi.mocked(craApi.getAnnexVii).mockResolvedValue(oneAction as any);
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');
    expect(screen.getByText(/1 section need input/i)).toBeInTheDocument();
  });

  // ── Appendix counts ───────────────────────────────────────────────────────

  it('renders appendix count cards correctly', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');

    expect(screen.getByText('Assets')).toBeInTheDocument();
    expect(screen.getByText('Damage scenarios')).toBeInTheDocument();
    expect(screen.getByText('Compensating controls')).toBeInTheDocument();
    expect(screen.getByText('SBOMs')).toBeInTheDocument();
  });

  // ── Section list ──────────────────────────────────────────────────────────

  it('renders all 7 section titles', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');

    for (const s of MOCK_SECTIONS) {
      expect(screen.getByText(s.title)).toBeInTheDocument();
    }
  });

  it('renders article refs for each section', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');

    for (const s of MOCK_SECTIONS) {
      expect(screen.getByText(s.article_ref)).toBeInTheDocument();
    }
  });

  it('shows "Action required" badge on sections that need it', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');

    // Two sections have is_action_required: true
    expect(screen.getAllByText(/action required/i)).toHaveLength(2);
  });

  // ── Section toggle ────────────────────────────────────────────────────────

  it('section body is hidden by default', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');

    expect(screen.queryByText('ECU description body.')).not.toBeInTheDocument();
  });

  it('clicking a section header expands the body', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Product Description');

    await fireEvent.click(screen.getByText('Product Description').closest('button')!);

    await waitFor(() => {
      expect(screen.getByText('ECU description body.')).toBeInTheDocument();
    });
  });

  it('clicking an expanded section collapses it again', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Product Description');

    const btn = screen.getByText('Product Description').closest('button')!;
    await fireEvent.click(btn);
    await waitFor(() => expect(screen.getByText('ECU description body.')).toBeInTheDocument());

    await fireEvent.click(btn);
    await waitFor(() => expect(screen.queryByText('ECU description body.')).not.toBeInTheDocument());
  });

  // ── Download ──────────────────────────────────────────────────────────────

  it('Download Markdown button is disabled while loading', () => {
    vi.mocked(craApi.getAnnexVii).mockReturnValue(new Promise(() => {}));
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    expect(screen.getByRole('button', { name: /download markdown/i })).toBeDisabled();
  });

  it('Download Markdown button is enabled after document loads', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');
    expect(screen.getByRole('button', { name: /download markdown/i })).not.toBeDisabled();
  });

  it('clicking Download Markdown calls craApi.downloadAnnexViiMarkdown', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');

    await fireEvent.click(screen.getByRole('button', { name: /download markdown/i }));

    await waitFor(() => {
      expect(craApi.downloadAnnexViiMarkdown).toHaveBeenCalledWith('a1', 'Brake Control ECU');
    });
  });

  it('shows "Downloading…" label while the download is in progress', async () => {
    vi.mocked(craApi.downloadAnnexViiMarkdown).mockReturnValue(new Promise(() => {}));
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');

    await fireEvent.click(screen.getByRole('button', { name: /download markdown/i }));

    await waitFor(() => {
      expect(screen.getByText('Downloading…')).toBeInTheDocument();
    });
  });

  // ── Refresh ───────────────────────────────────────────────────────────────

  it('clicking Refresh calls getAnnexVii a second time', async () => {
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    await screen.findByText('Brake Control ECU');
    expect(craApi.getAnnexVii).toHaveBeenCalledOnce();

    await fireEvent.click(screen.getByRole('button', { name: /refresh/i }));

    await waitFor(() => {
      expect(craApi.getAnnexVii).toHaveBeenCalledTimes(2);
    });
  });

  it('Refresh button is disabled while loading', () => {
    vi.mocked(craApi.getAnnexVii).mockReturnValue(new Promise(() => {}));
    render(CraAnnexVii, { props: { assessmentId: 'a1' } });
    expect(screen.getByRole('button', { name: /refresh/i })).toBeDisabled();
  });
});
