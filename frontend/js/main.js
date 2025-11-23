document.addEventListener('DOMContentLoaded', function () {
	// --- Check availability on index.html ---
	const checkBtn = document.getElementById('checkBtn');
	const select = document.getElementById('check-bg');
	const out = document.getElementById('availability');
	if (checkBtn && select && out) {
		checkBtn.addEventListener('click', async () => {
			const bg = select.value;
			out.textContent = 'Checking...';
			try {
				const res = await fetch(`/api/inventory/${encodeURIComponent(bg)}`);
				if (!res.ok) {
					const err = await res.json();
					out.textContent = err.error || 'Error fetching availability';
					return;
				}
				const data = await res.json();
				out.innerHTML = `<div class="card"><strong>${data.bloodGroup}</strong>: ${data.unitsAvailable} unit(s) available</div>`;
			} catch (e) {
				out.textContent = 'Network error';
			}
		});
	}

	// --- Request blood form on requestblood.html ---
	const requestForm = document.getElementById('requestForm');
	const reqMsg = document.getElementById('req-msg');
	if (requestForm) {
		requestForm.addEventListener('submit', async (ev) => {
			ev.preventDefault();
			const form = new FormData(requestForm);
			const payload = Object.fromEntries(form.entries());
			try {
				const res = await fetch('/api/requests', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
				const data = await res.json();
				if (!res.ok) {
					reqMsg.textContent = data.error || 'Error submitting request';
				} else {
					reqMsg.textContent = 'Request submitted. ID: ' + data.id;
					requestForm.reset();
				}
			} catch (e) {
				reqMsg.textContent = 'Network error';
			}
		});
	}

	// --- Admin inventory form ---
	const invForm = document.getElementById('invForm');
	if (invForm) {
		invForm.addEventListener('submit', async (ev) => {
			ev.preventDefault();
			const form = new FormData(invForm);
			const payload = Object.fromEntries(form.entries());
			try {
				const res = await fetch('/api/inventory', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
				const data = await res.json();
				if (!res.ok) {
					alert(data.error || 'Error updating inventory');
				} else {
					alert('Inventory updated');
					invForm.reset();
					loadRequests();
				}
			} catch (e) {
				alert('Network error');
			}
		});
	}

	// --- Donor form (optional) ---
	const donorForm = document.getElementById('donorForm');
	const donorMsg = document.getElementById('msg');
	if (donorForm) {
		donorForm.addEventListener('submit', (ev) => {
			ev.preventDefault();
			donorMsg.textContent = 'Thanks for registering (demo only).';
			donorForm.reset();
		});
	}

	// --- Admin: load and render pending requests ---
	async function loadRequests() {
		const container = document.getElementById('requests');
		if (!container) return;
		container.textContent = 'Loading...';
		try {
			const res = await fetch('/api/requests');
			const data = await res.json();
			if (!res.ok) {
				container.textContent = 'Error loading requests';
				return;
			}
			if (!data.length) {
				container.innerHTML = '<div class="muted">No requests</div>';
				return;
			}
			container.innerHTML = data.map(r => {
				return `<div class="card" data-id="${r.id}"><div><strong>${r.hospitalId}</strong> — ${r.bloodGroup} (${r.unitsRequired})</div><div class="small muted">${r.requestedAt}</div><div class="actions">` +
							 (r.status === 'pending' ? `<button class="approve">Approve</button> <button class="reject">Reject</button>` : `<span class="muted">${r.status}</span>`) +
							 `</div></div>`;
			}).join('');
			// attach event listeners
			container.querySelectorAll('.approve').forEach(btn => {
				btn.addEventListener('click', async (ev) => {
					const card = ev.target.closest('.card');
					const id = card.getAttribute('data-id');
					try {
						const res = await fetch(`/api/requests/${id}/approve`, {method: 'POST'});
						const d = await res.json();
						if (!res.ok) alert(d.error || 'Error approving');
						loadRequests();
					} catch (e) { alert('Network error'); }
				});
			});
			container.querySelectorAll('.reject').forEach(btn => {
				btn.addEventListener('click', async (ev) => {
					const card = ev.target.closest('.card');
					const id = card.getAttribute('data-id');
					try {
						const res = await fetch(`/api/requests/${id}/reject`, {method: 'POST'});
						const d = await res.json();
						if (!res.ok) alert(d.error || 'Error rejecting');
						loadRequests();
					} catch (e) { alert('Network error'); }
				});
			});
		} catch (e) {
			container.textContent = 'Network error';
		}
	}

	// load requests on admin page
	if (document.getElementById('requests')) {
		loadRequests();
	}
});

