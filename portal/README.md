# Samasya Radar Portal

A complaint website with an officer desk. Citizens file complaints in Bengali, English or Banglish
and track them with an ID. Officers see hotspots, a heat map and a priority list, then respond.

## Run locally

From this folder, keep the project in a short path on Windows:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app:app --port 8000
```

Open http://localhost:8000. Officers sign in at `/officer.html`, using the `ADMIN_EMAIL` and
`ADMIN_PASSWORD` in `.env.local`. Without a `DATABASE_URL`, data goes in a local `portal.db` file.

`python scripts/seed_demo.py` loads simulated complaints for local testing. It refuses to run on a real database.

## Deploy on Vercel

1. Upload the contents of this `portal` folder to a GitHub repository. If you upload the whole
   project instead, set **Root Directory** to `portal` in step 2.
2. In Vercel, choose **Add New > Project** and import the repository. It detects FastAPI by itself.
3. In the project, open **Storage** and connect a Postgres database such as Neon, in a Mumbai
   region. Check that it added `DATABASE_URL` to the environment variables.
4. Add `SESSION_SECRET`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` and the `SMTP_` settings, as explained in `.env.example`.
5. Redeploy, then open `/api/health`. It should show `"status":"ok"` and `"officer_login_ready":true`.
6. File a test complaint, answer it from `/officer.html`, and check the reply on the tracking page.
7. Add an officer using an email address you can open, and check that the code arrives and activates the account.

The app runs in Mumbai (`bom1`, set in `vercel.json`) so it sits close to the database.

## Adding officers

An admin enters a name and email on the Team tab. The officer gets a 6-digit code by email, which works for
30 minutes and for 5 attempts, then enters it at `/activate.html` and chooses a password. The account only
exists after that.

Without `SMTP_HOST`, a local run shows the code on screen for testing and sends nothing. On Vercel, adding
an officer is refused until email is set up.

## Changing a password

Signed-in officers use the **My account** tab, entering their current password and a new one of at least
12 characters. That session continues, and any others made with the old password end.

## Forgotten passwords

Officers use **Forgot your password?** on the sign-in page. They get a 6-digit code by email, which works for
30 minutes and for 5 attempts, and at most 3 codes are sent to an address per hour. Changing the password
ends every session made with the old one. The page answers the same for any email, so it does not reveal
who is an officer.

This needs the `SMTP_` settings. Set them before you need them: without email on Vercel, nobody can reset a
password, including the only admin. Without `SMTP_HOST`, a local run shows the code on screen, but only to
requests from that same computer.

## Before this becomes an official service

Do not name a government authority in `OPERATOR_NAME` until all of these are true. Whoever runs the site should set it to their own name, with `OPERATOR_CONTACT`, because the privacy notice tells people to contact the operator named in the footer. While it is empty, the footer names nobody and shows a browser tip in that spot.

- [ ] A government authority has agreed in writing to run it and to respond to complaints
- [ ] That authority has approved its name, branding and domain (a `.gov.in` domain comes through NIC)
- [ ] Named officers are assigned, and the `RESPONSE_DAYS` target is one they have agreed to
- [ ] Legal has reviewed the privacy notice and data handling against the DPDP Act
- [ ] The authority's IT team has approved hosting on Vercel and the database provider
- [ ] Models are retrained and scored on real complaints (`real_test.csv`)
- [ ] `server/model/villages.json` holds the district's full village list, checked against LGD
- [ ] A Bengali reader has checked all Bengali text in `public/assets/site.js` and the village names

## Not built yet

- SMS or WhatsApp updates, so citizens must check the tracking page themselves
- Two-factor sign-in
- Limiting officers to their own department or block, so every officer sees every complaint
- Automatic deletion of old complaints

## Retraining

After retraining in the main project, run `python portal/scripts/export_models.py` from `samasya-radar/`,
then `python -m pytest tests -q` from here. The tests check that exported models match the originals.
