import { requireAdmin } from '$lib/guards/auth';

export async function load() {
	await requireAdmin();
	return {};
}
