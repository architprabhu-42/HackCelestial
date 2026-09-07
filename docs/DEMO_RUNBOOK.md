# ResiliTrip demo runbook

All schedules, inventory, fares and booking references in this demo are **synthetic and not bookable**. Adopting an option saves only a proposed local journey; it does not contact or change any provider.

## Setup and verification (Windows PowerShell)

```powershell
./scripts/bootstrap.ps1
./scripts/test-all.ps1
```

Required locally: Windows PowerShell, Node 22, Python 3.12, `uv`, and npm. Docker Desktop is optional; this demo runs directly with local SQLite.

To launch the built app:

```powershell
Push-Location apps/web; npm run build; Pop-Location
Push-Location apps/api
..\..\.venv\Scripts\python.exe -m uvicorn resilitrip.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`; stop with `Ctrl+C`.

```powershell
./scripts/demo-reset.ps1
./scripts/test-offline.ps1
./scripts/test-performance.ps1
./scripts/verify-clean-install.ps1
```

## 2–3 minute live script

1. Click **Try Mumbai to Goa demo**. Point out Asha at CSMT, the complete train–hotel–wedding journey, and the synthetic/not-bookable notice.
2. Select Train T1, choose **Report a problem**, then **Apply delay**. Read the server-derived impact: wedding arrival is 8:50 PM, 95 minutes late, while the hotel remains valid.
3. Select **Find another way**. Under Lowest cost, show F3 before F2: F3 needs ₹6,500 and reaches the wedding at 5:20 PM. Switch to Earliest arrival to show F2 first.
4. Expand rejected options and point out F4: it is cheaper but arrives 50 minutes late, so it cannot be used.
5. Return to Lowest cost, preview F3, accept the simulation acknowledgement and select **Use simulated plan**. Read: “No external booking was changed.”
6. Select **Reset scenario** to restore the baseline.

## Troubleshooting

- **Port 8000 is in use:** stop the owning process, or use another uvicorn `--port` and open that local URL.
- **Fresh local database:** stop the server and remove only `data/local/resilitrip.sqlite3` plus its `-wal`/`-shm` companions, then restart. Do not remove other data.
- **Map unavailable:** choose **Use map-free route list**; the timeline and fallback are complete offline route views.
- **Missing Playwright browser:** run `Push-Location apps/web; npx playwright install chromium; Pop-Location`.

## Manual release checklist — not automated

- [ ] Five unfamiliar people complete the comprehension check without coaching: identify current/next travel, report T1 delay, choose F3, explain F4’s deadline failure, and state that adoption made no booking. Record only completion/time/answer accuracy and confusion; target 5/5.
- [ ] Record a 1080p backup demo video at 100% browser zoom with notifications disabled, following the script above.

These human-only requirements remain incomplete until performed and recorded.
