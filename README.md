# Resume Builder

A beautiful, fully client-side resume builder web app. Users fill in their details, see a live preview, and download a polished A4 PDF — no backend, no database, no signup required.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Language** | HTML5 | App structure and resume template markup |
| **Styling** | CSS3 | UI design (glassmorphism form panel, resume layout) |
| **Logic** | Vanilla JavaScript (ES6+) | Live preview rendering, form state management |
| **PDF Export** | [html2pdf.js](https://github.com/eKoopmans/html2pdf.js) v0.10.1 | Converts the rendered HTML resume to a downloadable PDF |
| **PDF Renderer** | html2canvas + jsPDF (bundled in html2pdf.js) | Rasterises the HTML and generates A4 PDF |
| **Web Server** | Nginx (Alpine) | Serves the static HTML file inside Docker |
| **Container** | Docker | Packages and runs the app in any environment |

---

## Features

- Live resume preview that updates as you type
- Sections: Personal Info, Summary, Skills (category table), Certifications, Work History, Education, Languages
- Resume layout matches a professional PDF format — dark navy header, skills table, bullet-point work history, star-rated languages
- One-click PDF download (A4, print-ready)
- Pre-filled with sample data for quick testing
- Zero dependencies to install — everything runs in the browser

---

## Project Structure

```
resume maker/
├── resume-builder.html   # The entire app (HTML + CSS + JS in one file)
├── Dockerfile            # Docker image using Nginx to serve the app
└── README.md             # This file
```

---

## Run Locally (No Docker)

Just open the file in any modern browser:

```bash
# On Windows — double-click the file, or:
start resume-builder.html

# On Mac/Linux
open resume-builder.html
```

> Works best in **Chrome** or **Edge** for accurate PDF export.

---

## Run with Docker

### 1. Build the image

```bash
docker build -t resume-builder .
```

### 2. Run the container

```bash
docker run -d -p 8080:80 --name resume-builder resume-builder
```

### 3. Open in browser

```
http://localhost:8080
```

### Stop the container

```bash
docker stop resume-builder
docker rm resume-builder
```

---

## Deploy to Static Hosting (No Docker needed)

Since this is a single HTML file, you can host it for free on:

| Platform | Command / Steps |
|---|---|
| **GitHub Pages** | Push to a repo → Settings → Pages → Deploy from branch |
| **Netlify** | Drag and drop the `resume-builder.html` file at [netlify.com/drop](https://app.netlify.com/drop) |
| **Vercel** | `vercel --prod` in the project folder |

---

## How the PDF Export Works

1. The resume is rendered as a live HTML `<div>` inside the browser
2. On clicking **Download PDF**, `html2pdf.js` uses `html2canvas` to take a high-resolution screenshot of the resume div
3. That screenshot is embedded into an A4 PDF using `jsPDF`
4. The PDF is downloaded directly to the user's machine — no server involved

---

## Author

**Sainudeen Safar** — DevOps Engineer  
sainudeensaffar@gmail.com
