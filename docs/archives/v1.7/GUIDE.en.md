> **Older version of this guide** (Mes outils 1.7). Current guide: [docs/GUIDE.en.md](../../GUIDE.en.md).

# Mes outils: guide

[Français](GUIDE.md) · **English**

Mes outils ("my tools") is a work tool for Windows. A small bubble floats on
the screen; one click opens your dashboard: tasks, clients, quotes and
invoices, expenses, calendar, mail, documents, and tools for developers. On
first launch you pick your role and the apps you need, like in an ERP.
Everything runs on your PC, with no account and no online service.

![Mes outils home page](images/en/accueil.webp)

## Contents

- [Installation](#installation)
- [First launch: your role and your apps](#first-launch-your-role-and-your-apps)
- [The Apps page](#the-apps-page)
- [The bubble](#the-bubble)
- [Getting around](#getting-around)
- [Home](#home)
- Everyday: [Email](#email) · [Notes](#notes) · [Tasks](#tasks) ·
  [Calendar](#calendar) · [Passwords](#passwords)
- Clients & sales: [Contacts](#contacts) · [Quotes & invoices](#quotes--invoices) ·
  [Expenses](#expenses) · [Time](#time)
- Organisation: [Documents](#documents) · [Meetings and trips](#meetings-and-trips) ·
  [Due dates](#due-dates) · [Message templates](#message-templates) ·
  [Clipboard](#clipboard)
- Development: [Servers](#servers) · [Projects](#projects) · [GitHub](#github) ·
  [Ports](#ports) · [Docker](#docker) · [API tester](#api-tester) · [SSH](#ssh)
- Handy tools: [Toolbox](#toolbox) · [Snippets](#snippets)
- [Settings](#settings)
- [Security and privacy](#security-and-privacy)
- [FAQ](#faq)
- [Adding an app](#adding-an-app)

## Installation

### The easy way: the installer (nothing else to install)

1. Download **[Mes-outils-Setup.exe](https://github.com/rarianaAina/mes-outils/releases/latest/download/Mes-outils-Setup.exe)** (Windows 10 or 11).
2. Run it. Windows may show "Windows protected your PC": the installer is not
   signed (signing costs money). Click **More info**, then **Run anyway**.
3. Choose the options (Desktop shortcut, start with Windows), then
   **Install**. The bubble appears.

No administrator rights and no Python needed: everything is included. The
program is installed in `%LOCALAPPDATA%\Programs\Mes outils`. Your settings
and data are in `%APPDATA%\Mes outils` and stay on your PC: they are kept
during updates, and even after uninstalling.
To uninstall: Windows Settings › Apps › Mes outils.

### On Linux (Ubuntu 24.04 and others)

1. Download **[Mes-outils-x86_64.AppImage](https://github.com/rarianaAina/mes-outils/releases/latest/download/Mes-outils-x86_64.AppImage)**.
2. Make it executable: right-click › Properties › "Executable as program",
   or `chmod +x Mes-outils-x86_64.AppImage`.
3. Double-click it. The bubble appears, along with an icon at the top right of
   the screen; "Mes outils" is added to the applications menu.

A single file, no installation and no administrator rights. Your settings and
data are in `~/.config/mes-outils`. Email passwords and the GitHub access go
into the desktop keyring (GNOME Keyring, KWallet). The window without an
address bar and invoice PDFs need Google Chrome or Chromium
(`sudo snap install chromium`); without them, Mes outils opens in the default
browser. File pickers use zenity (already on Ubuntu). On GNOME with Wayland,
the bubble may go behind other windows: the icon at the top right is always
there (Settings › Linux: bubble and icon, bubble only or icon only).

### For developers: from the source code

You need Python 3.10 or later (with tkinter) and Git.

```bat
git clone https://github.com/rarianaAina/mes-outils.git
cd mes-outils
installer.bat
```

`installer.bat` checks Python, installs the libraries (`requirements.txt`),
creates the shortcuts and starts the bubble. The data then sits next to the
code (`outils.json`, `donnees\`) and never goes to GitHub. If you later switch
to the installer, your settings and data are picked up on first launch (they
are copied; the original stays).

On Linux: `sudo apt install python3-tk zenity`, then
`pip install -r requirements.txt` and `python3 outil/bulle.py`.

## First launch: your role and your apps

On first launch, a three-step assistant sets the tool up for you.

1. **Your first name and the language** (French or English).
2. **Your role**: Freelancer, Virtual assistant, Executive assistant,
   Developer, or "I'll choose myself". The role only pre-ticks the useful
   apps.

![Assistant: choosing your role](images/en/assistant-metier.webp)

3. **Your apps**: tick the ones you use. The others stay available later, on
   the Apps page.

![Assistant: choosing your apps](images/en/assistant-applications.webp)

The menu then shows only your apps. Nothing is lost if you change your mind:
everything changes in one click.

## The Apps page

Menu › **Apps** (at the bottom of the menu). Every app of Mes outils, grouped
as in the menu, with one sentence on what each one does.

![Apps page](images/en/applications.webp)

- One **switch** per app: on, it appears in the menu, on Home, in Ctrl + K and
  in the bubble's right-click menu.
- An app switched off disappears everywhere, but **its data stays**. Switch it
  back on: everything is there.
- Filters **All / On / Off**.
- **Start from a role…**: ticks again the apps planned for a role.

Home, the Apps page and Settings are always there.

## The bubble

A bubble floats above the other windows, with no button in the taskbar. It
starts with Windows.

| Gesture | Effect |
|---|---|
| **Click** | opens the dashboard (or brings it to the front if already open) |
| **Drag** | moves the bubble; it comes back to the same place next time |
| **Right-click** | quick access to your active apps (quick note, email, calendar, tasks, contacts, invoices, projects, servers…), your tools, "Hide for 15 minutes", "Quit the bubble" |

The badges around the bubble:

- **green** (top right): number of dev servers running;
- **coral** (top left): number of unread emails;
- **red** (bottom): failed GitHub Actions tests.

**Reminders.** When a reminder is due, a card appears next to the bubble with
a sound: note, appointment, Pomodoro, task with a time, contact to follow up,
overdue invoice, budget exceeded, expiring document, due date to pay or
cancellation notice, meeting about to start, trip leaving tomorrow. Only
active apps send reminders.

The dashboard opens in an Edge window without an address bar. Closing it stops
nothing: the bubble stays. If you quit the bubble, start it again with the
"Mes outils" shortcut on the Desktop.

## Getting around

- **Menu on the left**: apps are grouped (Everyday, Clients & sales,
  Organisation, Development, Handy tools); Apps and Settings are at the
  bottom. When there are many, the menu shrinks to icons; the name shows on
  hover.
- **Ctrl + K** (or "Search…" at the top): the command palette. Type a few
  letters to go to an app, create a task, an invoice or a contact, open a
  document, start one of your tools or change the theme, then press Enter.
- **Theme**: light, dark or automatic (follows Windows).
- **Language**: French or English, in Settings.

![Command palette (Ctrl + K)](images/en/palette.webp)

The same dashboard in the dark theme:

![Home in the dark theme](images/en/accueil-sombre.webp)

## Home

The landing page (see the screenshot at the top of this guide). Each active
app adds its card, only when it has something to say:

- **Today**: today's and tomorrow's appointments;
- **Pinned notes**, **unread emails**, **running timer**;
- **Tasks** overdue and due today; **To follow up** (contacts);
- **Invoices**: amount to collect, overdue invoices;
- **Expenses**: spent this month against the budget, expense reports;
- **Documents to renew**, this week's **due dates**, next **meeting** and
  next **trip**;
- for developers, **Code**: projects to push, modified, behind, failed GitHub
  tests.

At the bottom, **My tools**: your tiles (folder, file, program, web page or
local app). "Edit" to add, change or remove them.

![Home with the Developer role](images/en/accueil-dev.webp)

## Everyday

### Email

Your mailbox: Gmail, Yahoo, iCloud, Zoho, Fastmail, GMX, OVH, Orange, Free,
La Poste or any IMAP/SMTP server.

![Email](images/en/mails.webp)

- Read received and sent emails, search.
- Reply, forward, write a new email.
- **Template** button in the compose window: inserts one of your
  [message templates](#message-templates), with its variables filled in. The
  email you are writing is kept.
- Remote images are blocked (they are used to know whether you read the
  email): "Show images" button.
- The provider's guide shows at the first sign-in; the password is kept in the
  Windows credential vault.

![New email filled from a template](images/en/mails-modele.webp)

### Notes

![Notes](images/en/notes.webp)

- Notes as coloured cards or **checklists**.
- **Pin** a note: it shows on Home.
- **Reminder** at a date and time: the bubble lets you know.
- Search and filters. Saved automatically as you type.

### Tasks

Your to-dos, with due date, priority and client.

![Tasks as a list](images/en/taches.webp)

- **List** grouped by Overdue, Today, This week, Later, No due date. Quick
  add: type the title, then press Enter.
- A task has a due date (with or without a time), a priority (low, normal,
  high), tags, a client, a description and **sub-steps** to tick.
- **Repeat** every day, week or month: once marked "Done", the task comes
  back at the next date.
- **Board**: To do, In progress and Done columns, with drag and drop.
- Filters by tag, client and priority.
- The bubble reminds you 15 minutes before a task that has a time.

![Tasks as a board](images/en/taches-tableau.webp)

### Calendar

![Calendar](images/en/agenda.webp)

- **Week** and **month** views.
- Click a slot to create an appointment.
- **Drag** an appointment to move it; **Ctrl + drag** to duplicate it.
- Reminder from the bubble: on time, 5, 15, 30 minutes or 1 hour before, or
  the day before.

### Passwords

An encrypted vault, opened with a master password.

![Passwords](images/en/motsdepasse.webp)

- Store your credentials by category, with an encrypted note.
- **Copy** a password: it is cleared from the clipboard after 30 seconds and
  does not enter the Windows clipboard history (Win + V).
- **Show** a password for 15 seconds.
- Strong password **generator**.
- The vault locks itself after 5 minutes without use.

> The master password is not stored anywhere: if you forget it, the vault is
> lost. Write it down on paper.

## Clients & sales

### Contacts

Your clients, prospects and suppliers: people and companies.

![Contacts, with a record open](images/en/contacts.webp)

- One record per person or company; a person can be linked to their company.
- Contact details, status (prospect, client, former client, supplier, other)
  and tags.
- **History of exchanges**: call, email, meeting or note, with the date.
- **Follow-up**: a date and a reason. "Done", or "In 3 days / 1 week /
  1 month". The bubble reminds you on the day.
- Filters by status, "To follow up" and tag. Search also finds a phone number
  typed without spaces.
- On hover: write, call, copy, edit, delete.
- **CSV import and export** (Excel-friendly). On import, an existing record is
  completed, never overwritten.

The other apps (Tasks, Invoices, Expenses, Documents, Due dates, Meetings,
Templates) offer your contacts in their "Client" fields.

### Quotes & invoices

Numbered quotes, invoices and credit notes, with totals exact to the cent.

![Quotes & invoices](images/en/factures.webp)

- **First launch**: enter your business (name, address, identifiers such as a
  company or tax number, logo, VAT, currency, payment terms).
- **Automatic numbering** when a document is issued, for example
  `INV-2026-001`, reset to 1 each year. Choose your prefixes for quotes,
  invoices and credit notes in the settings (gear icon).
- Lines with quantity, price and VAT rate; discount as a percentage or an
  amount; several VAT rates in one document.
- **Issue**: the document gets its number and date, then it is locked. The
  PDF is created in `Documents\Mes outils\Factures\<year>\`.
- Quotes: accepted, declined, then **Convert to invoice** in one click.
- Invoices: partial payments, status (sent, partly paid, paid, overdue). To
  correct an issued invoice, create a **credit note**.
- **Import hours** from the Time app, at the hourly rate you choose.
- **Send by email**: your mail app opens with the text; attach the PDF (its
  folder opens at the same time).
- At the top: invoiced and collected this month, unpaid, overdue. **CSV
  export**.

![An issued quote](images/en/factures-document.webp)

### Expenses

Your budget and your expense reports.

![Expenses: dashboard](images/en/depenses.webp)

- **Dashboard**: spent this month, budget, left per day, end-of-month
  forecast, latest expenses, top categories.
- **Fixed costs** (rent, subscriptions…): added by themselves every month.
- Monthly **budget**, carried over until you change it.
- **Savings**: when you go over budget, you can take from the savings of past
  months, or add the expense without touching them.
- **Statistics**: by period, by category, trend over 6 months.
- **For professionals**: "Business expense" box, client to re-invoice, status
  (to be reimbursed, reimbursed, re-invoiced), **receipt** as a photo or PDF.
  The **Expense reports** tab adds them up.
- Editable categories. Currencies: euro, dollar, ariary. CSV export.
- The bubble warns you once a month if the budget is exceeded.

### Time

Time spent on each project or client.

![Time](images/en/temps.webp)

- **Timer** per project (one at a time), with a note.
- **Pomodoro**: the bubble lets you know at the end of each period.
- Sessions by day, week or month, totals per project.
- Add a forgotten session, edit or delete a session.
- **CSV export**, and import of hours into an invoice.

## Organisation

### Documents

A binder for your important documents: contracts, signed quotes,
certificates, insurance…

![Documents](images/en/documents.webp)

- **Add a file** (several at once) or **a folder**. The file stays where it
  is: the binder only keeps its location. You can also make a copy in
  `Documents\Mes outils\Classeur\<client>\`.
- Type, client or project, tags, document date, **expiry date**.
- View by client or by type; "Expiring soon" and "Missing" filters.
- Reminder from the bubble before expiry (30 days by default, adjustable).
- Open the file, or show it in File Explorer. "Remove from the list" never
  deletes the file. A moved file is flagged "Missing", with "Locate…".

### Meetings and trips

Prepare, follow up and sum up your meetings; organise your trips.

![A past meeting, with its notes](images/en/reunions.webp)

- **Meeting**: date, duration, place, video link, participants (from
  Contacts), agenda to tick, notes, decisions and **action items** (who, what,
  by when).
- **Create the task** for an action item in one click (when Tasks is on).
- **Minutes**: the text is ready, to copy or to email to the participants.
- **Add to calendar**: the meeting, or the legs of a trip.
- Reminder from the bubble 15 minutes before.

![A trip](images/en/deplacements.webp)

- **Trip**: destination, dates, travellers, legs (plane, train, car),
  accommodation, documents (tickets, bookings), packing list, budget.
- Printable **itinerary**.
- The bubble reminds you the day before you leave.

### Due dates

Everything that renews or expires: subscriptions, contracts, insurance,
domain names, rent…

![Due dates](images/en/echeances.webp)

- Grouped by This week, This month, Later; overdue ones in red.
- Monthly, quarterly, yearly, every N months, or a single date.
- **Paid / renewed**: the next due date moves forward by one period
  (January 31 goes to February 28, then back to March 31).
- **Automatic renewal** with notice: a second reminder arrives before the
  cancellation deadline.
- **Costs** panel: per month and per year, by currency and by category.
- Statuses active, to cancel, cancelled, ended. CSV export.
- A card number or an IBAN is refused in "Payment method": write something
  like "Business card (ending 1234)" instead.

### Message templates

Ready-to-use texts: standard replies, payment reminders, appointment
confirmations, meeting minutes… Twelve examples are included.

![Message templates](images/en/modeles.webp)

- **Variables** in braces: `{first_name}`, `{date}`, `{amount}`, or any you
  make up.
- **Use**: pick a contact (the matching fields and the address fill in by
  themselves), fill in the rest, check the preview. Then **Copy** or **Write
  the email**.
- Favourites, categories, sort by use. Import and export.
- From Email: **Template** button in the compose window.

![Using a template](images/en/modeles-utiliser.webp)

### Clipboard

The last 50 texts you copied.

![Clipboard](images/en/presse-papiers.webp)

- Copy an old text again in one click; pin the ones to keep at hand.
- Search the history; **Pause** to stop recording for a while.
- The history is kept **in memory only** and cleared on exit; passwords
  copied from the vault never enter it.

## Development

These apps are pre-ticked with the "Developer" role.

### Servers

![Servers: Odoo servers and project dev servers](images/en/serveurs.webp)

All your servers in one place: your projects' dev servers (the commands set
in Projects) and, if you use it, the Odoo servers of an external gadget
(`gestion_serveurs.py`, path in `outils.json`, key `serveurs_odoo` ›
`gadget`).

- Start, stop, open in the browser, read the log.
- Green dot: running; orange: starting; red: port taken by another program.
- An Odoo database marked "reference" asks for confirmation before it starts.

### Projects

The projects found in your project folders, with their type (Node, Next.js,
Vite, Python, Django, Docker, Odoo…).

![Projects](images/en/projets.webp)

- Open a project in one click: **Folder**, **VS Code**, **Terminal**.
- See the **Git status**: to push, to pull, modified. "Check all" runs a
  `git fetch` on every project.
- **Set up** the dev commands: the tool suggests some based on the project
  (`npm run dev`, `manage.py runserver`, `docker compose up`…).
- **Start** and **Stop** a dev server, open the site, read its **log** live.
- Back up `.env` files in the encrypted vault and restore them in one click.

![A project's commands](images/en/projets-commandes.webp)

![A dev server's log](images/en/projets-journal.webp)

### GitHub

All your repositories (public, private, your organisations'). You sign in
once, with a code to confirm on github.com, without a password.

![GitHub: repositories](images/en/github.webp)

- Search and filter your repositories (private, public, on this PC or not).
- **Clone** a repository, or open it in its folder or in VS Code.
- **New repository** from a folder: the content is checked before upload
  (`.gitignore` respected, sensitive files such as `.env` flagged, files over
  100 MB refused).
- **Pull requests**: yours and those waiting for your review.
- **Issues** assigned to you.
- **Actions**: the status of the latest tests; a failure lights the bubble's
  red badge.

![Actions (dark theme)](images/en/github-actions-sombre.webp)

### Ports

Which program is using port 3000? The answer at a glance.

![Ports](images/en/ports.webp)

- Every listening port, with the program, its command line and its memory.
- Search for a port or a program; "Development" filter.
- Open a web port in the browser.
- **Stop** a program after confirmation. System processes and Mes outils
  itself are protected.

### Docker

Your containers, grouped by compose project.

![Docker (dark theme)](images/en/docker-sombre.webp)

- Start, stop, restart or remove a container.
- "Start all" or "Stop all" for a whole compose project.
- Read a container's log; open the published ports.
- "Images and disk space": the room taken by Docker.

### API tester

A mini Postman, right in the dashboard.

![API tester](images/en/api.webp)

- Method, URL, parameters, headers, body (JSON, text, form) and
  authentication (Bearer, Basic).
- Formatted response, with its status, duration and headers.
- **Variables** (`{{base_url}}`), **history** (without secrets) and saved
  requests.
- Copy a request as a **cURL** command.

### SSH

One key per server, installed in one click.

![SSH](images/en/ssh.webp)

- "New server": name, address, port, user name and password. The tool creates
  the key, installs it on the server, then checks the connection.
- The password is only used this once: it is not stored anywhere.
- Then, in a terminal: `ssh <short-name>` (a click on the row copies it).
- Test the connection, open a terminal on the server, remove the key.

## Handy tools

### Toolbox

Small everyday tools. Nothing leaves the page.

![Toolbox](images/en/boite.webp)

- **JWT**: read a token's header, payload and dates.
- **Base64**, **JSON** (formatting, sorting), **URL encoding**.
- Unix **timestamp** and date, **UUID**.
- **Regular expressions** tested live.
- **Hashing** (SHA) of a text or a file, **colours**.

### Snippets

Your favourite commands and code snippets.

![Snippets](images/en/extraits.webp)

- One click on **Copy**: the snippet is in the clipboard.
- Sort by language and tag, pin the most useful ones.
- Order by use, title or date. Also from the bubble's right-click menu.

## Settings

![Settings](images/en/reglages.webp)

- First name (for the greeting), **language** (French, English), **theme**.
- **Apps**: your role and the "Choose my apps" button, which opens the Apps
  page.
- **Project folders**: where Projects and GitHub look for your projects.
- Start with Windows, Desktop shortcut.
- **About**: "Check for updates".

## Security and privacy

- **Everything stays on your PC.** The dashboard server only listens on
  `127.0.0.1` (this PC only). No account, no online service, no statistics
  sent.
- **The server refuses orders coming from other sites**: a web page open in
  your browser cannot talk to it.
- **Password vault encrypted** with AES-256-GCM; the key is derived from the
  master password with scrypt. The master password is not stored anywhere.
- **GitHub token and mail passwords** are kept in the Windows credential vault
  (Credential Manager), never in a plain-text file.
- **Clients, invoices, expenses, documents**: files on your PC, in
  `%APPDATA%\Mes outils`. Documents stay where they are; only their paths are
  saved.
- **Due dates**: a card number or an IBAN is refused.
- **Clipboard**: the history stays in memory; it is never written to disk.
- **API tester**: tokens and passwords are masked in the history.
- **SSH**: the server password is only used to install the key; it is not
  stored.

## FAQ

**An app is no longer in the menu.**
It is probably switched off: Menu › Apps, turn its switch on. Its data is
intact.

**I picked the wrong role on first launch.**
Menu › Apps › "Start from a role…", or Settings › Apps.

**Where are the PDFs of my quotes and invoices?**
In `Documents\Mes outils\Factures\<year>\`. On a quote or an invoice: "Open
PDF" or "Open folder".

**An invoice's PDF was not created.**
It is made with Microsoft Edge. If Edge is missing, the invoice is still
issued: install Edge, then create the PDF again from the invoice.

**Outlook or Hotmail will not connect.**
They are not supported yet: Microsoft requires a different sign-in method. The
other providers (Gmail, Yahoo, iCloud…) work with an app password or the usual
password, as explained by the guide on screen.

**How do I update Mes outils?**
Settings › About › "Check for updates". With the installer, click
**Install**: the new version downloads, installs and Mes outils restarts by
itself (your settings and data are kept). When installed with `git clone`, the
update runs `git pull`; then restart the bubble (right-click › "Quit the
bubble", then the shortcut).

**The bubble has disappeared.**
It may be hidden for 15 minutes, or you quit it: start the "Mes outils"
shortcut on the Desktop again.

**My projects do not show up.**
Add their folder in Settings › Project folders. The tool looks in that folder
and its direct subfolders; a project elsewhere can be added with "Add a
project".

**The Docker app says Docker is missing.**
Install Docker Desktop and start it; the app offers to download it or start
it. Without Docker, the rest works normally.

**Where is my data?**
With the installer: `%APPDATA%\Mes outils`. From the source code: next to the
code, `outils.json` (settings and tiles) and `donnees\` (notes, tasks,
contacts, invoices, encrypted vault…). Remember to back them up.

## Adding an app

An app = one Python file and one JavaScript file, without touching the rest.
It shows up by itself in the menu, on the Apps page and, if it wants, on Home.
Everything is explained in [MODULES.md](../../MODULES.md) (in French).

---

Older versions of this guide: [version 1.5](../v1.5/GUIDE.en.md) · [version 1.4](../v1.4/GUIDE.en.md) · [version 1.3](../v1.3/GUIDE.en.md).
